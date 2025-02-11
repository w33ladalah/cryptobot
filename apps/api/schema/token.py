from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TokenBase(BaseModel):
    id: Optional[int]
    url: str
    address: str
    symbol: str
    name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class TokenCreate(TokenBase):
    pass


class TokenRead(TokenBase):
    pass


class TokenUpdate(TokenBase):
    pass


class TokenResponse(BaseModel):
    token: TokenRead
    status: str
