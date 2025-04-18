from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from utils import get_db
from schema import UserCreate, UserRead, UserUpdate, UserResponse, UsersResponse, UserLogin, UserLoginResponse
from repositories import UserRepository, AuthenticationRepository
from fastapi.responses import JSONResponse
from utils.jwt import auth_gate
import traceback

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db), _: UserRead = Depends(auth_gate)):
    try:
        user_service = UserRepository(db)
        created_user = user_service.create_user(user)
        return created_user
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        user_service = UserRepository(db)
        created_user = user_service.create_user(user)
        return created_user
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user(user_data: UserRead = Depends(auth_gate)):
    try:
        return UserResponse(user=user_data, status="success")
    except HTTPException as e:
        traceback.print_exc()
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK, name="Read a user by ID")
async def read_user(user_id: int, db: Session = Depends(get_db), _: UserRead = Depends(auth_gate)):
    try:
        user_service = UserRepository(db)
        user_data = user_service.read_user(user_id)
        return UserResponse(user=user_data, status="success")
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})

@router.get("/", response_model=UsersResponse, status_code=status.HTTP_200_OK)
async def read_users(page: int = 1, limit: int = 10, db: Session = Depends(get_db), _: UserRead = Depends(auth_gate)):
    try:
        user_service = UserRepository(db)
        users = user_service.read_users(page, limit)
        return users
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), _: UserRead = Depends(auth_gate)):
    try:
        user_service = UserRepository(db)
        return user_service.update_user(user_id, user)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})

@router.delete("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: Session = Depends(get_db), _: UserRead = Depends(auth_gate)):
    try:
        user_service = UserRepository(db)
        return user_service.delete_user(user_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})

@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        auth_service = AuthenticationRepository(db)
        token = auth_service.authenticate_user(user_credentials.username, user_credentials.password)
        return token
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": str(e)})
