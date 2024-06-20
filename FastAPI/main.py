from pathlib import Path
import time
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from redis import Redis
import redis.asyncio as redis
from sqlalchemy import text


from ipaddress import ip_address
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db, get_redis_client
from src.routes import contacts, auth, users
from src.conf.config import settings

async def lifespan(app: FastAPI):
    redis_client = await redis.from_url(
        f"{settings.redis_url}/0"
    )
    await FastAPILimiter.init(redis_client)
    yield
    await redis_client.close()

BASE_DIR = Path(".")

templates = Jinja2Templates(directory=BASE_DIR / "src" / "templates")

app = FastAPI(lifespan=lifespan)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


banned_ips = [
    ip_address("192.168.1.1"),
    ip_address("192.168.1.2"),
    # ip_address("127.0.0.1"),
]
@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip in banned_ips:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}
        )
    response = await call_next(request)
    return response


app.mount("/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ------ method is depricated, lifespan instead ---------------
# @app.on_event("startup")
# async def startup():
#     r = await redis.Redis(
#         host=settings.redis_host,
#         port=settings.redis_port,
#         db=0
#     )
#     await FastAPILimiter.init(r)


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "our": "Build group PythonWeb #22"}
    )


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Connection to database is established. Welcome to fastapi"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to database")


@app.get("/api/redis_healthchecker")
async def redis_healthchecker(
    key="test", value="test", redis_client: Redis = Depends(get_redis_client)
):
    try:
        await redis_client.set(key, value, ex=5)
        value = await redis_client.get(key)
        if value is None:
            raise HTTPException(
                status_code=500, detail="Radis Database is not configured correctly"
            )
        return {"message": "Connection to Radis is established."}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to Radis")
