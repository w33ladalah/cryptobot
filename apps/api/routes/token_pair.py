from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm.session import Session
from utils import get_db
from schema import TokenPairCreate, TokenPairsResponse, TokenPairUpdate
from repositories import TokenPairRepository

routers = APIRouter(prefix="/token_pairs", tags=["Token Pairs"])


@routers.get("/", status_code=status.HTTP_200_OK, response_model=TokenPairsResponse)
def get_token_pairs(db: Session = Depends(get_db)):
    service = TokenPairRepository(db)
    return service.get_token_pairs()


@routers.get("/{pair_address}", status_code=status.HTTP_200_OK)
def get_token_pair(pair_address: str, db: Session = Depends(get_db)):
    service = TokenPairRepository(db)
    return service.get_token_pair(pair_address)


@routers.post("/", status_code=status.HTTP_201_CREATED)
def create_token_pair(token_pair: TokenPairCreate, db: Session = Depends(get_db)):
    service = TokenPairRepository(db)
    return service.create_token_pair(token_pair)


@routers.put("/{pair_address}", status_code=status.HTTP_200_OK)
def update_token_pair(pair_address: str, token_pair: TokenPairUpdate, db: Session = Depends(get_db)):
    service = TokenPairRepository(db)
    return service.update_token_pair(pair_address, token_pair)


@routers.delete("/{pair_address}", status_code=status.HTTP_204_NO_CONTENT)
def delete_token_pair(pair_address: str, db: Session = Depends(get_db)):
    service = TokenPairRepository(db)
    return service.delete_token_pair(pair_address)
