from sqlalchemy import BigInteger, Column, String, DateTime, func

from models import Base
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship
from models.platform import Platform


class Token(Base):
    __tablename__ = "tokens"

    id = Column(BigInteger, primary_key=True, index=True)    # Unique identifier
    alias_id = Column(String(100), index=True)    # Alias identifier
    url = Column(String(255), nullable=False, index=True)    # Token URL
    address = Column(String(42), nullable=False, index=True)   # Ethereum-style address
    symbol = Column(String(50), nullable=False, index=True)    # Token symbol
    name = Column(String(100), nullable=False, index=True)    # Token name
    created_at = Column(DateTime, default=func.now(), nullable=False)    # Creation date
    updated_at = Column(DateTime, default=func.now(), nullable=True)    # Last update date


    # Association table for many-to-many relationship between Token and Platform
token_platform_association = Table(
    'token_platform', Base.metadata,
    Column('token_id', BigInteger, ForeignKey('tokens.id'), primary_key=True),
    Column('platform_id', BigInteger, ForeignKey('platforms.id'), primary_key=True)
)

# Add relationships to Token and Platform models
Token.platforms = relationship('Platform', secondary=token_platform_association, back_populates='tokens')
Platform.tokens = relationship('Token', secondary=token_platform_association, back_populates='platforms')
