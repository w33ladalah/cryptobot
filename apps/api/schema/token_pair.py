from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class TokenPairBase(BaseModel):
    base_symbol: str
    base_address: str
    quote_symbol: str
    quote_address: str
    pair_address: str
    exchange_name: str
    price: float
    volume_24h: float
    liquidity: float


class TokenPair(TokenPairBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenPairCreate(TokenPairBase):
    # Base token
    base_token_id: Optional[int] = None
    base_symbol: str
    base_address: str

    # Quote token
    quote_token_id: Optional[int] = None
    quote_symbol: str
    quote_address: str


class TokenPairResponse(TokenPair):
    base_token_id: int
    quote_token_id: int


class TokenPairsResponse(BaseModel):
    token_pairs: List[TokenPairResponse] = []


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
