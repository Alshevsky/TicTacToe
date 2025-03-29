import uuid

from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import Column, ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import relationship

from database.models.base_model import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    username: str = Column(String, nullable=False, unique=True, index=True)

    @classmethod
    def objects(session) -> SQLAlchemyUserDatabase:
        return SQLAlchemyUserDatabase()


class UserStatistic(Base):
    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Uuid, ForeignKey(User.id, ondelete="CASCADE"))
    user = relationship(User, uselist=False)

    games_total = Column(Integer, default=0)
    games_win = Column(Integer, default=0)
    games_loose = Column(Integer, default=0)
    
    __table_args__ = (
        Index("idx_user_statistic", 'user_id'),
    )
