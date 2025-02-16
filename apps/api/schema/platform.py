import token
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PlatformBase(BaseModel):
    name: str
    address: str


class Platform(PlatformBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class PlatformCreate(PlatformBase):
    id: Optional[int] = None
    token_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PlatformResponse(Platform):
    pass


class PlatformListResponse(BaseModel):
    data: list[PlatformResponse] = []
    total: int
    limit: int
    page: int


class PlatformUpdate(PlatformBase):
    pass


class PlatformPullDataResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None
