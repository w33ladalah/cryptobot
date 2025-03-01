from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.wallet import Wallet
from schema import WalletCreate, WalletRead, WalletUpdate, WalletResponse, WalletsResponse
from datetime import datetime
import traceback

class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_wallet(self, wallet: WalletCreate) -> WalletResponse:
        try:
            db_wallet = Wallet(
                user_id=wallet.user_id,
                wallet_name=wallet.wallet_name,
                wallet_address=wallet.wallet_address,
                wallet_currency=wallet.wallet_currency,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(db_wallet)
            self.db.commit()
            self.db.refresh(db_wallet)

            wallet_read = WalletRead(
                id=db_wallet.id,
                user_id=db_wallet.user_id,
                wallet_name=db_wallet.wallet_name,
                wallet_address=db_wallet.wallet_address,
                wallet_currency=db_wallet.wallet_currency,
                created_at=db_wallet.created_at,
                updated_at=db_wallet.updated_at
            )
            return WalletResponse(wallet=wallet_read, status="success")
        except Exception as e:
            self.db.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    def read_wallet(self, wallet_id: int) -> WalletRead:
        try:
            db_wallet = self.db.query(Wallet).filter(Wallet.id == wallet_id).first()
            if db_wallet is None:
                raise HTTPException(status_code=404, detail="Wallet not found")
            return WalletRead(
                id=db_wallet.id,
                user_id=db_wallet.user_id,
                wallet_name=db_wallet.wallet_name,
                wallet_address=db_wallet.wallet_address,
                wallet_currency=db_wallet.wallet_currency,
                created_at=db_wallet.created_at,
                updated_at=db_wallet.updated_at
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def read_wallets(self, page: int = 1, limit: int = 10) -> WalletsResponse:
        try:
            offset = (page - 1) * limit
            wallets = self.db.query(Wallet).offset(offset).limit(limit).all()
            total = self.db.query(Wallet).count()
            wallet_reads = [
                WalletRead(
                    id=wallet.id,
                    user_id=wallet.user_id,
                    wallet_name=wallet.wallet_name,
                    wallet_address=wallet.wallet_address,
                    wallet_currency=wallet.wallet_currency,
                    created_at=wallet.created_at,
                    updated_at=wallet.updated_at
                ) for wallet in wallets
            ]
            return WalletsResponse(wallets=wallet_reads, page=page, limit=limit, total=total, status="success")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_wallet(self, wallet_id: int, wallet: WalletUpdate) -> WalletResponse:
        try:
            db_wallet = self.db.query(Wallet).filter(Wallet.id == wallet_id).first()
            if db_wallet is None:
                raise HTTPException(status_code=404, detail="Wallet not found")
            for key, value in wallet.dict(exclude_unset=True).items():
                setattr(db_wallet, key, value)
            db_wallet.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(db_wallet)
            wallet_read = WalletRead(
                id=db_wallet.id,
                user_id=db_wallet.user_id,
                wallet_name=db_wallet.wallet_name,
                wallet_address=db_wallet.wallet_address,
                wallet_currency=db_wallet.wallet_currency,
                created_at=db_wallet.created_at,
                updated_at=db_wallet.updated_at
            )
            return WalletResponse(wallet=wallet_read, status="success")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def delete_wallet(self, wallet_id: int) -> WalletResponse:
        try:
            db_wallet = self.db.query(Wallet).filter(Wallet.id == wallet_id).first()
            if db_wallet is None:
                raise HTTPException(status_code=404, detail="Wallet not found")
            self.db.delete(db_wallet)
            self.db.commit()
            wallet_read = WalletRead(
                id=db_wallet.id,
                user_id=db_wallet.user_id,
                wallet_name=db_wallet.wallet_name,
                wallet_address=db_wallet.wallet_address,
                wallet_currency=db_wallet.wallet_currency,
                created_at=db_wallet.created_at,
                updated_at=db_wallet.updated_at
            )
            return WalletResponse(wallet=wallet_read, status="success")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
