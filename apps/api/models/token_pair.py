from itertools import chain
from shlex import quote
from sqlalchemy import BigInteger, Column, String, Float, DateTime, Integer, func

from models import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(BigInteger, primary_key=True, index=True)    # Unique identifier
    url = Column(String(255), nullable=False, index=True)    # Token URL
    address = Column(String(42), nullable=False, index=True)   # Ethereum-style address
    symbol = Column(String(50), nullable=False, index=True)    # Token symbol
    name = Column(String(100), nullable=False, index=True)    # Token name
    created_at = Column(DateTime, default=func.now(), nullable=False)    # Creation date
    updated_at = Column(DateTime, default=func.now(), nullable=False)    # Last update date


class TokenPair(Base):
    __tablename__ = "token_pairs"

    id = Column(BigInteger, primary_key=True, index=True)   # Unique identifier
    chain_id = Column(String(50), nullable=False, index=True)   # Chain ID
    dex_id = Column(String(50), nullable=False, index=True)   # Dex ID
    pair_url = Column(String(100), nullable=False, index=True)   # Pair URL
    pair_address = Column(String(50), nullable=False, index=True)  # Ethereum-style address
    base_token_id = Column(BigInteger, nullable=False, index=True)   # Token ID
    quote_token_id = Column(BigInteger, nullable=False, index=True)    # Token ID
    exchange_name = Column(String(100), nullable=True)
    price = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)  # 24-hour trading volume
    liquidity = Column(Float, nullable=True)  # Liquidity pool size
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
