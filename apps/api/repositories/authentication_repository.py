import traceback
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.users import User
from schema import UserRead, UserResponse, UserLoginResponse
from utils.jwt import create_access_token, create_refresh_token, verify_password


class AuthenticationRepository:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> UserLoginResponse:
        try:
            db_user = self.db.query(User).filter(User.username == username).first()
            if db_user is None or not verify_password(password, db_user.hashed_password):
                raise HTTPException(status_code=401, detail="Invalid username or password")

            user_read = UserRead(
                id=db_user.id,
                username=db_user.username,
                fullname=db_user.fullname,
                email=db_user.email,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
            access_token = create_access_token(data={"sub": db_user.username})
            refresh_token = create_refresh_token(data={"sub": db_user.username})

            return UserLoginResponse(user=user_read, status="success", access_token=access_token, refresh_token=refresh_token)
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
