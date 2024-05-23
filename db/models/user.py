from sqlalchemy import (Column, String, select, BigInteger, DateTime, func)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)
    payed = Column(String, nullable=True)
    sub_expire_time = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(User)

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(User))
        return result.scalars().all()
