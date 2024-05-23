from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Float, ForeignKey
from sqlalchemy.orm import relationship

from db.crud import AsyncCRUD
from db.engine import Base


class TokenPair(Base):
    __tablename__ = 'token_pairs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    chain_id = Column(String, nullable=False)
    dex_id = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    price_change_5m = Column(Float, nullable=False)
    price_change_1h = Column(Float, nullable=False)
    price_change_24h = Column(Float, nullable=False)
    volume_1h = Column(Float, nullable=False)
    volume_24h = Column(Float, nullable=False)
    liquidity_usd = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    tax_buy = Column(Float, nullable=False)
    tax_sell = Column(Float, nullable=False)
    tax_transfer = Column(Float, nullable=False)
    liquidity_lock = Column(Float, nullable=False)
    holders = Column(Integer, nullable=False)
    clog = Column(Float, nullable=False)
    owner_supply = Column(Float, nullable=False)
    pair_age_minutes = Column(Integer, nullable=False)
    renounced = Column(Boolean, default=False)
    contract_address = Column(String, nullable=False)
    links = relationship("TokenLink", back_populates="token_pair")
    pair_created_at = Column(BigInteger, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TokenLink(Base):
    __tablename__ = 'token_links'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    token_pair_id = Column(Integer, ForeignKey('token_pairs.id'))
    token_pair = relationship("TokenPair", back_populates="links")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TokenPairCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(TokenPair)


class TokenLinkCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(TokenLink)

