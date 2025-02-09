from sqlalchemy import Column, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TokenPair(Base):
    __tablename__ = "token_pairs"

    id = Column(String(100), primary_key=True, index=True)   # Unique identifier
    pair_address = Column(String(50), primary_key=True, index=True)  # Ethereum-style address
    base_symbol = Column(String(50), nullable=True)
    base_address = Column(String(42), nullable=True)
    quote_symbol = Column(String(50), nullable=True)
    quote_address = Column(String(42), nullable=True)
    exchange_name = Column(String(100), nullable=True)
    price = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)  # 24-hour trading volume
    liquidity = Column(Float, nullable=True)  # Liquidity pool size
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return (f"<TokenPair(pair_address='{self.pair_address}', base='{self.base_symbol}', "
                f"quote='{self.quote_symbol}', price={self.price}, exchange='{self.exchange_name}')>")
