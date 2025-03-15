import jwt
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from numpy import full
from models.users import User
from schema.users import UserRead
from sqlalchemy.orm import Session
from utils import get_db
import base64
import os
import traceback

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_data = payload.get("sub")
        if user_data is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        return user_data
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

def auth_gate(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserRead:
    try:
        user_sub = get_current_user(token)
        user_data = db.query(User).filter(User.username == user_sub).first()
        if user_data is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        return UserRead(
            id=user_data.id,
            username=user_data.username,
            fullname=user_data.fullname,
            email=user_data.email,
            created_at=user_data.created_at,
            updated_at=user_data.updated_at
        )
    except jwt.PyJWTError:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

def auth_required(func):
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        token = await oauth2_scheme(request)
        user_data = get_current_user(token)
        kwargs["user_data"] = user_data
        return await func(*args, **kwargs)
    return wrapper

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    hashed_password = base64.urlsafe_b64encode(salt + key)

    return hashed_password.decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    decoded = base64.urlsafe_b64decode(hashed_password.encode())
    salt = decoded[:16]
    key = decoded[16:]
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    try:
        kdf.verify(plain_password.encode(), key)
        return True
    except Exception:
        return False
