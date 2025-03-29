import logging
from typing import AsyncGenerator, Coroutine

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, User
from app.settings import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL)
logger.info("Database connection established")
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables() -> None:
    logger.info("Creating tables")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    logger.info("Tables created")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
    

def session_connection(method: Coroutine):
    async def wrapper(*args, **kwargs):
        async with Session.begin() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    return wrapper
