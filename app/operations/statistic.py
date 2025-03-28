from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Statistic
from database.base import session_connection


@session_connection
async def get_statistic(user_id: str, session: AsyncSession) -> Statistic:
    stmt = select(Statistic).where(Statistic.user_id == user_id)
    return await session.execute(stmt)


@session_connection
async def update_statistic(user_id: str, session: AsyncSession, winner: bool = False, looses: bool = False) -> Statistic:
    stmt = update(Statistic).where(Statistic.user_id == user_id).values(
        total_games=Statistic.total_games + 1,
        wins=Statistic.wins + 1 if winner else 1,
        losses=Statistic.losses + 1 if Statistic.losses else 1,
    )
    return await session.execute(stmt)

@session_connection
async def create_statistic(user_id: str, session: AsyncSession) -> Statistic:
    stmt = insert(Statistic).values(
        user_id=user_id,
        total_games=0,
        wins=0,
        losses=0,
    )
    return await session.execute(stmt)
