from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Float, ForeignKey, func, DateTime, select
from sqlalchemy.orm import relationship
from db.crud import AsyncCRUD
from db.engine import Base
from decorators.db_session import db_session


class TokenPair(Base):
    __tablename__ = 'token_pairs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, default="")
    symbol = Column(String, nullable=False, default="")
    contract_address = Column(String, nullable=False, default="", unique=True)
    chain_name = Column(String, nullable=False, default="")
    dex_id = Column(String, nullable=False, default="")
    price = Column(Float, nullable=False, default=0.0)
    price_change_5m = Column(Float, nullable=False, default=0.0)
    price_change_1h = Column(Float, nullable=False, default=0.0)
    price_change_24h = Column(Float, nullable=False, default=0.0)
    volume_1h = Column(Float, nullable=False, default=0.0)
    volume_5m = Column(Float, nullable=False, default=0.0)
    volume_24h = Column(Float, nullable=False, default=0.0)
    liquidity_usd = Column(Float, nullable=False, default=0.0)
    market_cap = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String, nullable=False, default="low")
    transaction_count_5_minute_min = Column(Integer, nullable=False, default=0)
    transaction_count_1_hour_min = Column(Integer, nullable=False, default=0)
    tax_buy = Column(Float, nullable=False, default=0.0)
    tax_sell = Column(Float, nullable=False, default=0.0)
    tax_transfer = Column(Float, nullable=False, default=0.0)
    liquidity_lock = Column(Float, nullable=False, default=0.0)
    holders = Column(Integer, nullable=False, default=0)
    clog = Column(Float, nullable=False, default=0.0)
    owner_supply = Column(Float, nullable=False, default=0.0)
    renounced = Column(Boolean, default=False)
    links = relationship("TokenLink", back_populates="token_pair")
    pair_created_at = Column(BigInteger, nullable=False, default=0)
    added_time = Column(DateTime, nullable=False, default=func.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TokenLink(Base):
    __tablename__ = 'token_links'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    token_pair_id = Column(Integer, ForeignKey('token_pairs.id'))
    token_pair = relationship("TokenPair", back_populates="links")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TokenPairCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(TokenPair)

    @db_session
    async def check_contract(self, session, contract_address):
        query = select(TokenPair).where(TokenPair.contract_address == contract_address)
        result = await session.execute(query)
        instance = result.scalars().one_or_none()
        if instance:
            return True
        return False


class TokenLinkCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(TokenLink)
