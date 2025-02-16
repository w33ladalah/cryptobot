from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
from utils import get_db
from schema import TokenCreate, TokenRead, TokenResponse
from repositories import TokenRepository


router = APIRouter(prefix="/tokens", tags=["Tokens"])


from fastapi.responses import JSONResponse

@router.post("/", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def create_token(token: TokenCreate, db: Session = Depends(get_db)):
    try:
        token_service = TokenRepository(db)
        created_token = token_service.create_token(token)
        return created_token
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})


@router.get("/{token_id}", response_model=TokenRead, status_code=status.HTTP_200_OK)
def read_token(token_id: int, db: Session = Depends(get_db)):
    try:
        token_service = TokenRepository(db)
        return token_service.read_token(token_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})


@router.get("/", response_model=List[TokenRead], status_code=status.HTTP_200_OK)
def read_tokens(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        token_service = TokenRepository(db)
        return token_service.read_tokens(skip, limit)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})


@router.put("/{token_id}", response_model=TokenRead, status_code=status.HTTP_200_OK)
def update_token(token_id: int, token: TokenCreate, db: Session = Depends(get_db)):
    try:
        token_service = TokenRepository(db)
        return token_service.update_token(token_id, token)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})


@router.delete("/{token_id}", response_model=TokenRead, status_code=status.HTTP_200_OK)
def delete_token(token_id: int, db: Session = Depends(get_db)):
    try:
        token_service = TokenRepository(db)
        return token_service.delete_token(token_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})
