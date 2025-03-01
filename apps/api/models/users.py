from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from models import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc), nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc),
                        onupdate=lambda: datetime.now(datetime.timezone.utc), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
