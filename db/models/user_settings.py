from datetime import datetime
from typing import Dict, List

from sqlalchemy import (Column, String, select, BigInteger, DateTime, func, Boolean, Integer, ForeignKey)
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class UserSettings(Base):
    __tablename__ = 'user_settings'

    # id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    # user_id = Column(Integer, ForeignKey('user.id'), index=True, primary_key=True)
    id = Column(Integer, ForeignKey('user.id'), index=True, primary_key=True)

    market_cap_max = Column(BigInteger, nullable=True, default=500000)
    market_cap_min = Column(BigInteger, nullable=True, default=50000)
    volume_5_minute_min = Column(BigInteger, nullable=True, default=15000)
    volume_1_hour_min = Column(BigInteger, nullable=True, default=15000)

    liquidity_min = Column(BigInteger, nullable=True, default=20000)
    liquidity_max = Column(BigInteger, nullable=True, default=200000)

    lp_locked = Column(Boolean, nullable=False, default=False)
    lp_burned = Column(Boolean, nullable=False, default=False)

    price_change_5_minute_min = Column(Integer, nullable=True, default=100)
    price_change_1_hour_min = Column(Integer, nullable=True, default=100)

    transaction_count_5_minute_min = Column(BigInteger, nullable=True, default=10)
    transaction_count_1_hour_min = Column(BigInteger, nullable=True, default=10)

    holders_min = Column(BigInteger, nullable=True, default=25)
    renounced = Column(Boolean, nullable=True, default=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserSettingsCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(UserSettings)

    @db_session
    async def get_all(self, session):
        result = await session.execute(select(UserSettings))
        return result.scalars().all()

    async def get_matching_users(self, token_data: Dict) -> List[int]:
        user_settings = await self.get_all()
        matching_users = []
        for settings in user_settings:
            if self.token_matches_settings(token_data, settings):
                matching_users.append(settings.id)
        return matching_users

    @staticmethod
    def token_matches_settings(token_data: Dict, settings: UserSettings) -> bool:
        return (
                settings.market_cap_min <= token_data["market_cap"] <= settings.market_cap_max and
                settings.volume_5_minute_min <= token_data["volume_5m"] and
                settings.volume_1_hour_min <= token_data["volume_1h"] and
                settings.liquidity_min <= token_data["liquidity_usd"] <= settings.liquidity_max and
                settings.price_change_5_minute_min <= token_data["price_change_5m"] and
                settings.price_change_1_hour_min <= token_data["price_change_1h"] and
                settings.transaction_count_5_minute_min <= token_data["transaction_count_5_minute_min"] and
                settings.transaction_count_1_hour_min <= token_data["transaction_count_1_hour_min"] and
                (datetime.now().timestamp() - token_data["pair_created_at"]) <= 86400
        )

    async def second_check(self, token_data: Dict, user_id) -> bool:
        user_settings = await self.read(user_id)
        user_settings = user_settings.as_dict()
        checks = {
            'renounced': (user_settings.get('renounced', False) == token_data.get('renounced', False)),
            'holders': (user_settings.get('holders_min', 1) <= token_data.get('holders', 1)),
            'lp_burned': (user_settings.get('lp_burned', False) <= token_data.get('lp_burned', False)),
            'lp_locked': (user_settings.get('lp_locked', False) <= token_data.get('lp_locked', False))
        }
        return all(checks.values())
