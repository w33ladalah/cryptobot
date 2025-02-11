from sqlalchemy import BigInteger, Column, String, DateTime, func

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
