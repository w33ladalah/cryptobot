from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schema.users import UserRead


class WalletBase(BaseModel):
    id: int
    user_id: int
    wallet_name: Optional[str] = None
    wallet_address: Optional[str] = None
    wallet_currency: Optional[str] = None
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()


class Wallet(WalletBase):
    pass

    class Config:
        from_attributes = True

class WalletCreate(BaseModel):
    user_id: int
    wallet_name: Optional[str] = None
    wallet_address: Optional[str] = None
    wallet_currency: Optional[str] = None


class WalletRead(WalletBase):
    user: UserRead

    class Config:
        from_attributes = True


class WalletUpdate(BaseModel):
    wallet_name: Optional[str] = None
    wallet_address: Optional[str] = None
    wallet_currency: Optional[str] = None


class WalletResponse(BaseModel):
    wallet: WalletRead
    status: str


class WalletsResponse(BaseModel):
    wallets: list[WalletRead]
    page: int
    limit: int
    total: int
    status: str
