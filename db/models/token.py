from sqlalchemy import (Column, Integer, String, Boolean, select, BigInteger, DateTime, func, ForeignKey)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class Token(Base):
    __tablename__ = 'Token'
    id = Column(Integer, primary_key=True)  # token address
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TokenCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Token)
