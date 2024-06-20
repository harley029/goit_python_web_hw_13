from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    avatar = None
    try:
        avatar = Gravatar(body.email).get_image()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
    
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token: str | None, db: AsyncSession):
    user.refresh_token = refresh_token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession):
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()
    await db.refresh(user)


async def update_avatar(email, url: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_password(user: User, new_password: str, db: AsyncSession):
    async with db as session:
        user.password = new_password
        await session.commit()
        await session.refresh(user)
        return user
