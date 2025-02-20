from config.celery import celery_app
from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.orm.session import Session
from utils import get_db
from schema import TokenPairCreate, TokenPairsResponse, TokenPairUpdate, CoingeckoPullDataResponse
from repositories import TokenPairRepository
import traceback
import httpx


routers = APIRouter(prefix="/token_pairs", tags=["Token Pairs"])


@routers.get("/perform_analysis", response_model=CoingeckoPullDataResponse, status_code=202)
def perform_analysis(request: Request):
    try:
        task = celery_app.send_task("perform_llm_analysis", args=[request.query_params["token_id"], True])
        return CoingeckoPullDataResponse(status="success", message="Task started", task_id=task.id)
    except httpx.RequestError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


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
