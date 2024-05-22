from sqlalchemy import (Column, String, BigInteger, DateTime, func, select)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class Client(Base):
    __tablename__ = 'client'

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ClientCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Client)

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(Client))
        return result.scalars().all()
