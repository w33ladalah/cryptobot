from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schema.platform import Platform, PlatformCreate

class TokenBase(BaseModel):
    id: int
    alias_id: str
    url: str
    address: str
    symbol: str
    name: str
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    class Config:
        orm_mode = True
        from_attributes = True


class Token(TokenBase):
    address: Optional[str] = None
    url: Optional[str] = None


class TokenCreate(TokenBase):
    id: Optional[int] = None
    address: Optional[str] = None
    url: Optional[str] = None
    platforms: Optional[List[PlatformCreate]] = []


class TokenRead(TokenBase):
    address: Optional[str] = None
    url: Optional[str] = None
    platforms: Optional[List[Platform]] = []

    class Config:
        orm_mode = True
        from_attributes = True


class TokenUpdate(TokenBase):
    pass


class TokenResponse(BaseModel):
    token: TokenRead
    status: str
