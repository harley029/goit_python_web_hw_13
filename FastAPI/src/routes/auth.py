from fastapi.responses import JSONResponse
from redis.asyncio.client import Redis

from fastapi import APIRouter, Form, HTTPException, Depends, Security, status, BackgroundTasks, Request

from fastapi.templating import Jinja2Templates

from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.email import send_email, send_password_reset_email
from src.entity.models import User
from src.database.db import get_db, get_redis_client
from src.repository import users as repositories_users
from src.schemas.user import RequestEmail, UserSchema, TokenSchema, UserResponseSchema
from src.services.auth import auth_serviсe
from src.conf.config import conf


router = APIRouter(prefix="/auth", tags=["auth"])

get_refresh_token = HTTPBearer()

# Ініціалізація Jinja2Templates з вказівкою на папку з шаблонами
templates = Jinja2Templates(directory=conf.TEMPLATE_FOLDER)

@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_serviсe.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") # Invalid email
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") # Not confirmed
    if not auth_serviсe.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") # Invalid password
    # Generate JWT
    access_token = await auth_serviсe.create_access_token(data={"sub": user.email})
    refresh_token = await auth_serviсe.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_serviсe.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user=user, refresh_token=None, db=db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_serviсe.create_access_token(data={"sub": email})
    refresh_token = await auth_serviсe.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_serviсe.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repositories_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post("/request_password_reset")
async def request_password_reset(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repositories_users.get_user_by_email(body.email, db)
    if user:
        background_tasks.add_task(
            send_password_reset_email, user.email, user.username, str(request.base_url)
        )
        return {"message": "Check your email to reset password."}
    else:
        return {"message": "User not found."}


@router.get("/reset_password/{token}")
async def confirmed_reset_password_email(
    token: str, request: Request, db: AsyncSession = Depends(get_db)
):
    email = await auth_serviсe.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    return templates.TemplateResponse(
        "reset_password_form.html",
        {"request": request, "token": token},
    )


@router.post("/reset-password/")
async def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    email = await auth_serviсe.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_hashed_password = auth_serviсe.get_password_hash(new_password)
    await repositories_users.update_password(user, new_hashed_password, db)
    return JSONResponse(
        content={"message": "Password reset successful"}, status_code=200
    )


@router.post("/cash/set")
async def set_cash(
    key: str,
    value: str,
    redis_client: Redis = Depends(get_redis_client),
    user: User = Depends(auth_serviсe.get_current_user),
):
    await redis_client.set(key, value)


@router.get("/cash/get/{key}")
async def get_cash(
    key: str,
    redis_client: Redis = Depends(get_redis_client),
    user: User = Depends(auth_serviсe.get_current_user),
):
    value = await redis_client.get(key)
    return {key, value}
