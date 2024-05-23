from sqlalchemy import (Column, Integer, String, Boolean, select, BigInteger, DateTime, func, ForeignKey)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class MessageLastIndex(Base):
    __tablename__ = 'messages_last_index'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Message(Base):
    __tablename__ = 'message'

    id = Column(BigInteger, primary_key=True, index=True)
    text = Column(String, nullable=False)
    url = Column(String, nullable=True)
    expire_time = Column(BigInteger, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MessageCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Message)

    @db_session
    async def get_all_active(self, session):
        result = await session.execute(select(Message).filter(Message.active == True))
        return result.scalars().all()

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(Message))
        return result.scalars().all()

    @db_session
    async def get_messages_by_clients(self, session):
        result = await session.execute(select(Message).order_by(Message.client_id))
        messages = result.scalars().all()

        client_dict = {}
        for msg in messages:
            if msg.client_id not in client_dict:
                client_dict[msg.id] = {}
            client_dict[msg.id] = {
                'text': msg.text,
                'url': msg.url,
                'expire_time': msg.expire_time,
                'client_id': msg.client_id
            }

        return client_dict


class MessageLastIndexCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(MessageLastIndex)

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(MessageLastIndex))
        return result.scalars().all()
