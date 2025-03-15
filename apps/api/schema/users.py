from numpy import full
from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    id: int
    fullname: Optional[str] = None
    username: str
    email: Optional[EmailStr] = None
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()


class User(UserBase):
    password: Optional[SecretStr] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    user: UserRead
    status: str


class UserLoginResponse(BaseModel):
    user: UserRead
    access_token: str
    refresh_token: str
    status: str


class UsersResponse(BaseModel):
    users: List[UserRead]
    page: int
    limit: int
    total: int
    status: str
