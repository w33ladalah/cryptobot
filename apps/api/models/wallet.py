from sqlalchemy import BigInteger, Column, String, DateTime, func, ForeignKey
from models import Base
from sqlalchemy.orm import relationship


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(BigInteger, primary_key=True, index=True)    # Unique identifier
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)    # Foreign key to users table
    wallet_name = Column(String(100), index=True)    # Wallet name
    wallet_address = Column(String(42), nullable=True, index=True)    # Wallet address
    wallet_currency = Column(String(50), nullable=True, index=True)    # Wallet currency
    created_at = Column(DateTime, default=func.now(), nullable=True)    # Creation date
    updated_at = Column(DateTime, default=func.now(), nullable=True)    # Last update date

    # user = relationship("User", back_populates="wallets")    # Relationship to User model
