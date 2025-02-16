from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.token import Token
from models.platform import Platform
from repositories.platform_repository import PlatformRepository
from schema import TokenCreate, TokenResponse, PlatformCreate, TokenRead
from devtools import debug
import traceback


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_token(self, token: TokenCreate) -> TokenResponse:
        try:
            existing_token = self.db.query(Token).filter(Token.alias_id == token.alias_id).first()
            debug(existing_token)
            if existing_token:
                raise HTTPException(status_code=400, detail="Token already exists")

            db_token = Token(
                alias_id=token.alias_id,
                symbol=token.symbol,
                name=token.name,
            )
            self.db.add(db_token)
            self.db.commit()
            self.db.refresh(db_token)

            platforms = []
            for platform_data in token.platforms:
                try:
                    platform_create = PlatformCreate(
                        name=platform_data.name,
                        address=platform_data.address,
                        token_id=db_token.id
                    )

                    platform_repo = PlatformRepository(self.db)
                    platform_response = platform_repo.create_platform(platform_create)
                    platforms.append(platform_response.__dict__)  # Ensure it is a dictionary
                except HTTPException as e:
                    self.db.rollback()

            self.db.commit()
            token_read = TokenRead(
                id=db_token.id,
                alias_id=db_token.alias_id,
                symbol=db_token.symbol,
                name=db_token.name,
                created_at=db_token.created_at,
                updated_at=db_token.updated_at,
                platforms=platforms
            )
            return TokenResponse(token=token_read, status="success")
        except Exception as e:
            self.db.rollback()
            traceback.print_exc()

            raise HTTPException(status_code=500, detail=str(e))

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

    def pull_data(self, token_data: TokenCreate):
        try:
            token = Token(name=token_data['name'], symbol=token_data['symbol'], alias_id=token_data['id'])
            self.db.add(token)
            self.db.commit()

            for platform_name, address in token_data.get("platforms", {}).items():
                if platform_name and address:
                    platform = Platform(name=platform_name, address=address)
                    self.db.add(platform)
                    self.db.commit()

                    platform = self.db.execute(
                        token_platform_relationship.insert().values(token_id=token.id, platform_id=platform.id)
                    )

            return token
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
