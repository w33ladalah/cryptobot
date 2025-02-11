from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.platform import Platform
from utils import get_db
from schema import PlatformCreate, Platform
import traceback

# filepath: /home/hendro/projects/crypto-bot/apps/api/routes/platform.py

router = APIRouter(prefix="/platforms", tags=["Platforms"])

@router.post("/", response_model=Platform)
def create_platform(platform: PlatformCreate, db: Session = Depends(get_db)):
    try:
        db_platform = Platform(**platform.dict())
        db.add(db_platform)
        db.commit()
        db.refresh(db_platform)
        return db_platform
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to create platform!")

@router.get("/{platform_id}", response_model=Platform)
def read_platform(platform_id: int, db: Session = Depends(get_db)):
    try:
        db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if db_platform is None:
            raise HTTPException(status_code=404, detail="Platform not found")
        return db_platform
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Platform])
def read_platforms(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        platforms = db.query(Platform).offset(skip).limit(limit).all()
        return platforms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{platform_id}", response_model=Platform)
def update_platform(platform_id: int, platform: PlatformCreate, db: Session = Depends(get_db)):
    try:
        db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if db_platform is None:
            raise HTTPException(status_code=404, detail="Platform not found")
        for key, value in platform.dict().items():
            setattr(db_platform, key, value)
        db.commit()
        db.refresh(db_platform)
        return db_platform
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{platform_id}", response_model=Platform)
def delete_platform(platform_id: int, db: Session = Depends(get_db)):
    try:
        db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if db_platform is None:
            raise HTTPException(status_code=404, detail="Platform not found")
        db.delete(db_platform)
        db.commit()
        return db_platform
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
