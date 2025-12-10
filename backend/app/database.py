from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from typing import Annotated, AsyncGenerator
from fastapi import Depends

DATABASE_URL = (
    "postgresql+asyncpg://postgres:password@localhost:5432/news_service"
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
