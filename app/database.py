from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from typing import Annotated, AsyncGenerator, Generator
from fastapi import Depends
from dotenv import load_dotenv
from redis.asyncio import Redis as AsyncRedis
from redis import Redis as SyncRedis
from app.logging_config import get_logger
import os

logger = get_logger(__name__)

load_dotenv()

ASYNC_DATABASE_URL = os.environ["ASYNC_DATABASE_URL"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])

async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=async_engine)

SYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace('asyncpg', 'psycopg2')
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)

Base = declarative_base()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("database_session_error", error=str(e), error_type=type(e).__name__, exc_info=True)
            await session.rollback()
            raise e
        finally:
            await session.close()

def get_sync_db_session() -> Generator[Session, None]:
    with SyncSession() as session:
        try:
            yield session
        except Exception as e:
            logger.error("sync_database_session_error", error=str(e), error_type=type(e).__name__, exc_info=True)
            session.rollback()
            raise e
        finally:
            session.close()

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
SyncSessionDep = Annotated[Session, Depends(get_sync_db_session)]

try:
    redis_client = AsyncRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    sync_redis_client = SyncRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
except Exception as e:
    redis_client = None
    sync_redis_client = None