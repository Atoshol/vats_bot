from sqlalchemy import (Column, String, select, BigInteger, DateTime, func)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class Admin(Base):
    __tablename__ = 'admin'

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AdminCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Admin)

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(Admin))
        return result.scalars().all()
