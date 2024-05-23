from sqlalchemy import (Column, String, select, BigInteger, DateTime, func, Boolean, Integer, ForeignKey)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class UserSettings(Base):
    __tablename__ = 'user_settings'

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), index=True)

    market_cap_max = Column(BigInteger, nullable=True, default=500000)
    market_cap_min = Column(BigInteger, nullable=True, default=50000)
    volume_5_minute_min = Column(BigInteger, nullable=True, default=15000)
    volume_1_hour_min = Column(BigInteger, nullable=True, default=15000)

    liquidity_min = Column(BigInteger, nullable=True, default=20000)
    liquidity_max = Column(BigInteger, nullable=True, default=200000)

    price_change_5_minute_min = Column(Integer, nullable=True, default=100)
    price_change_1_hour_min = Column(Integer, nullable=True, default=100)

    transaction_count_5_minute_min = Column(BigInteger, nullable=True, default=10)
    transaction_count_1_hour_min = Column(BigInteger, nullable=True, default=10)

    holders_min = Column(BigInteger, nullable=True, default=25)
    renounced = Column(Boolean, nullable=True, default=True)

    include_old_pairs = Column(DateTime, nullable=True, default=func.now())

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserSettingsCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(UserSettings)

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(UserSettings))
        return result.scalars().all()
