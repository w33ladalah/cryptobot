import traceback
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm.session import Session
from devtools import debug
from utils import get_db
from models.token_pair import TokenPair
from schema import TokenPairCreate, TokenPairResponse, TokenPairsResponse, TokenPairUpdate

routers = APIRouter(prefix="/token_pairs", tags=["Token Pairs"])


@routers.get("/", status_code=status.HTTP_200_OK, response_model=TokenPairsResponse)
def get_token_pairs(db: Session = Depends(get_db)):
    try:
        token_pairs = db.query(TokenPair).all()

        return {"token_pairs": [token_pair.__dict__ for token_pair in token_pairs]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@routers.get("/{pair_address}", status_code=status.HTTP_200_OK)
def get_token_pair(pair_address: str, db: Session = Depends(get_db)):
    try:
        token_pair = db.query(TokenPair).filter(TokenPair.pair_address == pair_address).first()
        if token_pair is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token pair not found")
        return token_pair
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@routers.post("/", status_code=status.HTTP_201_CREATED)
def create_token_pair(token_pair: TokenPairCreate, db: Session = Depends(get_db)):
    try:
        db.add(token_pair)
        db.commit()
        db.refresh(token_pair)

        return {"status": "Token pair created successfully"}
    except Exception as e:
        debug(e)
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@routers.put("/{pair_address}", status_code=status.HTTP_200_OK)
def update_token_pair(pair_address: str, token_pair: TokenPairUpdate, db: Session = Depends(get_db)):
    try:
        token_pair_db = db.query(TokenPair).filter(TokenPair.pair_address == pair_address).first()

        if token_pair_db is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token pair not found")

        token_pair_db.pair_address = token_pair.pair_address
        token_pair_db.updated_at = token_pair.updated_at
        db.commit()
        return {
            "status": "Token pair updated successfully",
        }
    except Exception as e:
        debug(e)
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
