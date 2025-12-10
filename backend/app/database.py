import os
from typing import Annotated, AsyncGenerator

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

load_dotenv()
USER = os.environ["POSTGRES_USER"]
PASSWORD = os.environ["POSTGRES_PASSWORD"]
HOST = os.environ["POSTGRES_HOST"]
DB = os.environ["POSTGRES_DB"]
PORT = os.environ["POSTGRES_PORT"]


DATABASE_URL = (
    f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
)

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=engine)
Base = declarative_base()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            print(e)
            await session.rollback()
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
