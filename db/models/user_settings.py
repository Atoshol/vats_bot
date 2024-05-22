from sqlalchemy import (Column, String, select, BigInteger, DateTime, func)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class UserSettings(Base):
    __tablename__ = 'user_settings'

    id = Column(BigInteger, primary_key=True, index=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserSettingsCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(UserSettings)

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(UserSettings))
        return result.scalars().all()
