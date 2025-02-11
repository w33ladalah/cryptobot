from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_serializer
from datetime import datetime

class TokenPairBase(BaseModel):
    id: int
    pair_address: str
    base_symbol: str
    base_address: str
    quote_symbol: str
    quote_address: str
    exchange_name: str
    price: float
    volume_24h: float
    liquidity: float
    created_at: datetime
    updated_at: datetime


class TokenPairResponse(TokenPairBase):
    updated_at: Optional[datetime]


class TokenPairsResponse(BaseModel):
    token_pairs: List[TokenPairResponse] = []


class TokenPairCreate(TokenPairBase):
    pass


class TokenPairUpdate(TokenPairBase):
    base_symbol: Optional[str]
    base_address: Optional[str]
    quote_symbol: Optional[str]
    quote_address: Optional[str]
    exchange_name: Optional[str]
    price: Optional[float]
    volume_24h: Optional[float]
    liquidity: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
