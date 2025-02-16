import token
from turtle import st
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.platform import Platform
from schema import PlatformCreate, PlatformResponse
from devtools import debug
import traceback


class PlatformRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_platform(self, platform: PlatformCreate) -> PlatformResponse:
        try:
            db_platform = Platform(
                name=platform.name,
                address=platform.address,
                token_id=platform.token_id
            )
            self.db.add(db_platform)
            self.db.commit()
            self.db.refresh(db_platform)

            return PlatformResponse(
                name=db_platform.name,
                address=db_platform.address,
                id=db_platform.id,
                created_at=db_platform.created_at,
                updated_at=db_platform.updated_at
            )
        except Exception as e:
            self.db.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    def read_platform(self, platform_id: int):
        try:
            db_platform = self.db.query(Platform).filter(Platform.id == platform_id).first()
            if db_platform is None:
                raise HTTPException(status_code=404, detail="Platform not found")
            return db_platform
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def read_platforms(self, skip: int = 0, limit: int = 10):
        try:
            platforms = self.db.query(Platform).offset(skip).limit(limit).all()
            return platforms
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_platform(self, platform_id: int, platform: PlatformCreate):
        try:
            db_platform = self.db.query(Platform).filter(Platform.id == platform_id).first()
            if db_platform is None:
                raise HTTPException(status_code=404, detail="Platform not found")
            for key, value in platform.model_dump().items():
                setattr(db_platform, key, value)
            self.db.commit()
            self.db.refresh(db_platform)
            return db_platform
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def delete_platform(self, platform_id: int):
        try:
            db_platform = self.db.query(Platform).filter(Platform.id == platform_id).first()
            if db_platform is None:
                raise HTTPException(status_code=404, detail="Platform not found")
            self.db.delete(db_platform)
            self.db.commit()
            return db_platform
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
