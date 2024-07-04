from sqlalchemy import (Column, String, select, BigInteger, DateTime, func, Integer)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class UserTokenNotifications(Base):
    __tablename__ = 'user_token_notifications'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, index=True, nullable=False)
    token_address = Column(String, index=True, nullable=False)
    sent_at = Column(DateTime, default=func.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserTokenNotificationsCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(UserTokenNotifications)

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(UserTokenNotifications))
        return result.scalars().all()

    @db_session
    async def get_users_by_token_address(self, session, token_address: str):
        result = await session.execute(
            select(UserTokenNotifications).where(UserTokenNotifications.token_address == token_address))
        notifications = result.scalars().all()
        if notifications:
            return [notification.user_id for notification in notifications]
        return []
