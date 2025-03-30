from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UserStatisticRead
from database.base import session_connection
from database.models import UserStatistic


@session_connection
async def get_statistic(user_id: str, session: AsyncSession) -> UserStatisticRead:
    stmt = select(UserStatistic).where(UserStatistic.user_id == user_id)
    result = await session.execute(stmt)
    statistic = result.scalar_one_or_none()
    if statistic is None:
        await create_statistic(user_id, session)
        return await get_statistic(user_id, session)
    return UserStatisticRead.model_validate(statistic)


@session_connection
async def update_statistic(user_id: str, session: AsyncSession, winner: bool = False, looses: bool = False) -> None:
    stmt = (
        update(UserStatistic)
        .where(UserStatistic.user_id == user_id)
        .values(
            games_total=UserStatistic.games_total + 1,
            games_win=UserStatistic.games_win + 1 if winner else UserStatistic.games_win,
            games_loose=UserStatistic.games_loose + 1 if looses else UserStatistic.games_loose,
        )
    )
    await session.execute(stmt)
    await session.commit()


@session_connection
async def create_statistic(user_id: str, session: AsyncSession) -> None:
    stmt = insert(UserStatistic).values(
        user_id=user_id,
        games_total=0,
        games_win=0,
        games_loose=0,
    )
    await session.execute(stmt)
    await session.commit()
