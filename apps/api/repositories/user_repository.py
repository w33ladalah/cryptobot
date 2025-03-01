from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.users import User
from schema import UserCreate, UserRead, UserUpdate, UserResponse, UsersResponse
from datetime import datetime
import traceback


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> UserResponse:
        try:
            existing_user = self.db.query(User).filter(User.username == user.username).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already exists")

            db_user = User(
                username=user.username,
                email=user.email,
                hashed_password=user.password,  # Assume password is already hashed
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)

            user_read = UserRead(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
            return UserResponse(user=user_read, status="success")
        except Exception as e:
            self.db.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    def read_user(self, user_id: int) -> UserRead:
        try:
            db_user = self.db.query(User).filter(User.id == user_id).first()
            if db_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return UserRead(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def read_users(self, page: int = 1, limit: int = 10) -> UsersResponse:
        try:
            offset = (page - 1) * limit
            users = self.db.query(User).offset(offset).limit(limit).all()
            total = self.db.query(User).count()
            user_reads = [
                UserRead(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                ) for user in users
            ]
            return UsersResponse(users=user_reads, page=page, limit=limit, total=total, status="success")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_user(self, user_id: int, user: UserUpdate) -> UserResponse:
        try:
            db_user = self.db.query(User).filter(User.id == user_id).first()
            if db_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            for key, value in user.dict(exclude_unset=True).items():
                setattr(db_user, key, value)
            db_user.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(db_user)
            user_read = UserRead(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
            return UserResponse(user=user_read, status="success")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def delete_user(self, user_id: int) -> UserResponse:
        try:
            db_user = self.db.query(User).filter(User.id == user_id).first()
            if db_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            self.db.delete(db_user)
            self.db.commit()
            user_read = UserRead(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
            return UserResponse(user=user_read, status="success")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
