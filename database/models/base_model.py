from sqlalchemy import UUID, Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    id = Column(UUID, primary_key=True, index=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
