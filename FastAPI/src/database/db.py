import redis.asyncio as aioredis
from sqlalchemy.exc import SQLAlchemyError

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.conf.config import settings

DB_URL = settings.sqlalchemy_database_url
REDIS_URL = settings.redis_url

engine = create_async_engine(DB_URL)
local_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db():
    try:
        async with local_session() as session:
            yield session
    except SQLAlchemyError as e:
        print(f"Database session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Database session creation failed")

async def get_redis_client():
    redis_client = aioredis.from_url(REDIS_URL)
    try:
        yield redis_client
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Database is not configured correctly!")
    finally:
        await redis_client.close()
