from sqlalchemy import (Column, Integer, Boolean, BigInteger, Float, select)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class Settings(Base):
    __tablename__ = 'default_settings'

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    market_cap_min = Column(BigInteger, nullable=False, default=10000)
    market_cap_max = Column(BigInteger, nullable=False, default=4000000)
    volume_5_minute_min = Column(Float, nullable=False, default=10)
    volume_1_hour_min = Column(Float, nullable=False, default=10)
    liquidity_min = Column(BigInteger, nullable=False, default=15000)
    liquidity_max = Column(BigInteger, nullable=False, default=400000)
    lp_locked = Column(Boolean, nullable=False, default=False)
    lp_burned = Column(Boolean, nullable=False, default=False)
    price_change_5_minute_min = Column(Float, nullable=False, default=10)
    price_change_1_hour_min = Column(Float, nullable=False, default=10)
    transaction_count_5_minute_min = Column(Integer, nullable=False, default=10)
    transaction_count_1_hour_min = Column(Integer, nullable=False, default=10)
    holders_min = Column(Integer, nullable=False, default=25)
    renounced = Column(Boolean, nullable=False, default=False)
    pair_age_max = Column(Integer, nullable=False, default=86400)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SettingsCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Settings)

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(Settings))
        return result.scalars().all()

    @db_session
    async def get_by_id(self, session, settings_id):
        result = await session.execute(select(Settings).where(Settings.id == settings_id))
        return result.scalar_one_or_none()
