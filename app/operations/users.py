from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.operations.statistic import get_statistic
from database.base import session_connection
from database.models import User, UserStatistic


@session_connection
async def get_user_by_id(uid: str, session: AsyncSession) -> User | None:
    stmt = select(User).where(User.id == uid)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    print(user)
    return user


@session_connection
async def get_user_by_username(username: str, session: AsyncSession) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


@session_connection
async def get_user_and_statistic_by_username(username: str, session: AsyncSession) -> tuple[User, UserStatistic] | None:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return
    statistic = await get_statistic(user.id, session)
    return user, statistic
