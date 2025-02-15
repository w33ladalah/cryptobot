from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from utils import get_db
from schema import TokenCreate, TokenRead
from repositories import TokenRepository


router = APIRouter(prefix="/tokens", tags=["Tokens"])


@router.post("/", response_model=TokenRead)
def create_token(token: TokenCreate, db: Session = Depends(get_db)):
    token_service = TokenRepository(db)
    return token_service.create_token(token)


@router.get("/{token_id}", response_model=TokenRead)
def read_token(token_id: int, db: Session = Depends(get_db)):
    token_service = TokenRepository(db)
    return token_service.read_token(token_id)


@router.get("/", response_model=List[TokenRead])
def read_tokens(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    token_service = TokenRepository(db)
    return token_service.read_tokens(skip, limit)


@router.put("/{token_id}", response_model=TokenRead)
def update_token(token_id: int, token: TokenCreate, db: Session = Depends(get_db)):
    token_service = TokenRepository(db)
    return token_service.update_token(token_id, token)


@router.delete("/{token_id}", response_model=TokenRead)
def delete_token(token_id: int, db: Session = Depends(get_db)):
    token_service = TokenRepository(db)
    return token_service.delete_token(token_id)


@router.get("/pull-data", response_model=List[TokenRead])
def pull_data(db: Session = Depends(get_db)):
    token_service = TokenRepository(db)
    return token_service.pull_data()
