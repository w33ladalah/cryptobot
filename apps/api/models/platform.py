from sqlalchemy import BigInteger, Column, String, DateTime, func, Text

from models import Base


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(BigInteger, primary_key=True, index=True)    # Unique identifier
    name = Column(String(100), nullable=False, index=True)    # Platform name
    address = Column(Text, nullable=False, index=True)    # Ethereum-style address
    created_at = Column(DateTime, default=func.now(), nullable=False)    # Creation date
    updated_at = Column(DateTime, default=func.now(), nullable=True)    # Last update date
