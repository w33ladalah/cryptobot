import traceback
from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session
from devtools import debug
from models.token_pair import TokenPair
from schema import TokenPairCreate, TokenPairUpdate


class TokenPairRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_token_pairs(self):
        try:
            token_pairs = self.db.query(TokenPair).all()
            return {"token_pairs": [token_pair.__dict__ for token_pair in token_pairs]}
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_token_pair(self, pair_address: str):
        try:
            token_pair = self.db.query(TokenPair).filter(TokenPair.pair_address == pair_address).first()
            if token_pair is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token pair not found")
            return token_pair
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def create_token_pair(self, token_pair: TokenPairCreate):
        try:
            self.db.add(token_pair)
            self.db.commit()
            self.db.refresh(token_pair)
            return {"status": "Token pair created successfully"}
        except Exception as e:
            debug(e)
            traceback.print_exc()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def update_token_pair(self, pair_address: str, token_pair: TokenPairUpdate):
        try:
            token_pair_db = self.db.query(TokenPair).filter(TokenPair.pair_address == pair_address).first()
            if token_pair_db is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token pair not found")
            token_pair_db.pair_address = token_pair.pair_address
            token_pair_db.updated_at = token_pair.updated_at
            self.db.commit()
            return {"status": "Token pair updated successfully"}
        except Exception as e:
            debug(e)
            traceback.print_exc()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
