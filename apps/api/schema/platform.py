from pydantic import BaseModel
from datetime import datetime

class PlatformBase(BaseModel):
    name: str
    address: str

class PlatformCreate(PlatformBase):
    pass

class PlatformUpdate(PlatformBase):
    pass

class PlatformResponse(BaseModel):
    platform: PlatformBase
    status: str

class PlatformInDBBase(PlatformBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode: True

class Platform(PlatformInDBBase):
    pass

class PlatformInDB(PlatformInDBBase):
    pass
