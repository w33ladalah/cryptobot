from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PlatformBase(BaseModel):
    name: str
    address: str


class PlatformCreate(PlatformBase):
    pass


class PlatformResponse(PlatformBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PlatformListResponse(BaseModel):
    data: list[PlatformResponse]
    total: int
    limit: int
    page: int

class PlatformUpdate(PlatformBase):
    pass
