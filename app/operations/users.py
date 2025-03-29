from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import session_connection
from database.models import User


@session_connection
async def get_user_by_id(uid: str, session: AsyncSession) -> User | None:
    stmt = select(User).where(User.id == uid)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    print(user)
    return user
