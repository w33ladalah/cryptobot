from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schema.platform import Platform, PlatformCreate

class TokenBase(BaseModel):
    id: Optional[int]
    url: str
    address: str
    symbol: str
    name: str
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    class Config:
        orm_mode = True


class TokenCreate(TokenBase):
    platforms: Optional[List[PlatformCreate]] = []


class TokenRead(TokenBase):
    pass


class TokenUpdate(TokenBase):
    pass


class TokenResponse(BaseModel):
    token: TokenRead
    platforms: Optional[List[Platform]] = []
    status: str
