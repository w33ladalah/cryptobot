import trace
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.platform import Platform
from utils import get_db
from schema import PlatformCreate, Platform, PlatformResponse
from config.settings import config
import traceback
import httpx

router = APIRouter(prefix="/platforms", tags=["Platforms"])

class PlatformAPI:
    def __init__(self, db: Session):
        self.db = db

    def create_platform(self, platform: PlatformCreate):
        try:
            db_platform = Platform(**platform.dict())
            self.db.add(db_platform)
            self.db.commit()
            self.db.refresh(db_platform)
            return db_platform
        except Exception as e:
            self.db.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Failed to create platform!")

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
            for key, value in platform.dict().items():
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

@router.post("/", response_model=Platform)
def create_platform(platform: PlatformCreate, db: Session = Depends(get_db)):
    return PlatformAPI(db).create_platform(platform)

@router.get("/{platform_id}", response_model=Platform)
def read_platform(platform_id: int, db: Session = Depends(get_db)):
    return PlatformAPI(db).read_platform(platform_id)

@router.get("/", response_model=List[Platform])
def read_platforms(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return PlatformAPI(db).read_platforms(skip, limit)

@router.put("/{platform_id}", response_model=Platform)
def update_platform(platform_id: int, platform: PlatformCreate, db: Session = Depends(get_db)):
    return PlatformAPI(db).update_platform(platform_id, platform)

@router.delete("/{platform_id}", response_model=Platform)
def delete_platform(platform_id: int, db: Session = Depends(get_db)):
    return PlatformAPI(db).delete_platform(platform_id)

@router.get("/pull_data", response_model=List[Platform])
def pull_data(db: Session = Depends(get_db)):
    try:
        response = httpx.get(f"{config.COINGECKO_API}/coins/list?include_platform=true")
        response.raise_for_status()
        data = response.json()
        platforms = []
        for item in data:
            for platform_name, address in item.get("platforms", {}).items():
                platform_data = PlatformCreate(
                    name=platform_name,
                    address=address
                )
                platforms.append(PlatformAPI(db).create_platform(platform_data))
        return platforms
    except httpx.RequestError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
