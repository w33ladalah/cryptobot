from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.token import Token, token_platform_relationship
from schema import TokenCreate
from config.settings import config
import httpx
import traceback


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_token(self, token: TokenCreate):
        try:
            db_token = Token(**token.__dict__)
            self.db.add(db_token)
            self.db.commit()
            self.db.refresh(db_token)

            for platform_id in token.platform_ids:
                self.db.execute(
                    token_platform_relationship.insert().values(token_id=db_token.id, platform_id=platform_id)
                )
            self.db.commit()
            return db_token
        except Exception:
            self.db.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Failed to create token!")

    def read_token(self, token_id: int):
        try:
            db_token = self.db.query(Token).filter(Token.id == token_id).first()
            if db_token is None:
                raise HTTPException(status_code=404, detail="Token not found")
            return db_token
        except Exception:
            raise HTTPException(status_code=500, detail="Internal Server Error")

    def read_tokens(self, skip: int = 0, limit: int = 10):
        try:
            tokens = self.db.query(Token).offset(skip).limit(limit).all()
            return tokens
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_token(self, token_id: int, token: TokenCreate):
        try:
            db_token = self.db.query(Token).filter(Token.id == token_id).first()
            if db_token is None:
                raise HTTPException(status_code=404, detail="Token not found")
            for key, value in token.__dict__.items():
                setattr(db_token, key, value)
            self.db.commit()
            self.db.refresh(db_token)
            return db_token
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

    def delete_token(self, token_id: int):
        try:
            db_token = self.db.query(Token).filter(Token.id == token_id).first()
            if db_token is None:
                raise HTTPException(status_code=404, detail="Token not found")
            self.db.delete(db_token)
            self.db.commit()
            return db_token
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def pull_data(self):
        try:
            response = httpx.get(f"{config.COINGECKO_API}/coins/list")
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch data from CoinGecko")

            coin_data = response.json()
            tokens = []
            for coin in coin_data:
                token = Token(name=coin['name'], symbol=coin['symbol'], alias_id=coin['id'])
                self.db.add(token)
                tokens.append(token)

            self.db.commit()
            return tokens
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
