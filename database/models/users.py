from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import Column, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import relationship

from database.models.base_model import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    username: str = Column(String, nullable=False, unique=True, index=True)

    @classmethod
    def objects(session) -> SQLAlchemyUserDatabase:
        return SQLAlchemyUserDatabase()


class UserStatistic(Base):
    user_id = Column(Uuid, ForeignKey(User.id, ondelete="CASCADE"))
    user = relationship(User, uselist=False)

    games_win = Column(Integer, default=0)
    games_loose = Column(Integer, default=0)
