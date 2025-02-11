from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.token import Token
from utils import get_db
from schema import TokenCreate, TokenRead
from config.settings import config
import httpx
import traceback


router = APIRouter(prefix="/tokens", tags=["Tokens"])

@router.post("/", response_model=TokenRead)
def create_token(token: TokenCreate, db: Session = Depends(get_db)):
    try:
        db_token = Token(**token.__dict__)
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to create token!")


@router.get("/{token_id}", response_model=TokenRead)
def read_token(token_id: int, db: Session = Depends(get_db)):
    try:
        db_token = db.query(Token).filter(Token.id == token_id).first()
        if db_token is None:
            raise HTTPException(status_code=404, detail="Token not found")
        return db_token
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TokenRead])
def read_tokens(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        tokens = db.query(Token).offset(skip).limit(limit).all()
        return tokens
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{token_id}", response_model=TokenRead)
def update_token(token_id: int, token: TokenCreate, db: Session = Depends(get_db)):
    try:
        db_token = db.query(Token).filter(Token.id == token_id).first()
        if db_token is None:
            raise HTTPException(status_code=404, detail="Token not found")
        for key, value in token.__dict__.items():
            setattr(db_token, key, value)
        db.commit()
        db.refresh(db_token)
        return db_token
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{token_id}", response_model=TokenRead)
def delete_token(token_id: int, db: Session = Depends(get_db)):
    try:
        db_token = db.query(Token).filter(Token.id == token_id).first()
        if db_token is None:
            raise HTTPException(status_code=404, detail="Token not found")
        db.delete(db_token)
        db.commit()
        return db_token
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pull-data", response_model=List[TokenRead])
def pull_data(db: Session = Depends(get_db)):
    try:
        response = httpx.get(f"{config.COINGECKO_API}/coins/list")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch data from CoinGecko")

        coin_data = response.json()
        tokens = []
        for coin in coin_data:
            token = Token(name=coin['name'], symbol=coin['symbol'], id=coin['id'])
            db.add(token)
            tokens.append(token)

        db.commit()
        return tokens
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
