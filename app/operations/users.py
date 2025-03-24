from sqlalchemy import select

from database.base import session_connection
from database.models import User


@session_connection
async def get_user_by_id(uid: str, session) -> User | None:
    stmt = select(User).where(User.id == uid)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user
