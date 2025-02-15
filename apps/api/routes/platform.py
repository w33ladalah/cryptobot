from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from typing import List
from models.platform import Platform
from utils import get_db
from schema import PlatformCreate, PlatformResponse, PlatformListResponse, PlatformPullDataResponse
from devtools import debug
from celery.result import AsyncResult
from config.celery import celery_app
import traceback
import httpx


router = APIRouter(prefix="/platforms", tags=["Platforms"])


class PlatformAPI:
    def __init__(self, db: Session):
        self.db = db

    def create_platform(self, platform: PlatformCreate):
            try:
                debug(f"Creating platform {platform.name} with address {platform.address}")

                existing_platform = self.db.query(Platform).filter(
                    Platform.name == platform.name,
                    Platform.address == platform.address
                ).first()
                if existing_platform:
                    raise HTTPException(status_code=400, detail="Platform already exists")

                db_platform = Platform(**platform.__dict__)
                self.db.add(db_platform)
                self.db.commit()
                self.db.refresh(db_platform)
                return db_platform
            except HTTPException as e:
                self.db.rollback()
                traceback.print_exc()
                raise HTTPException(status_code=e.status_code, detail=e.detail)

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


@router.post("/", response_model=PlatformResponse)
def create_platform(platform: PlatformCreate, db: Session = Depends(get_db)):
    try:
        return PlatformAPI(db).create_platform(platform)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{platform_id}", response_model=PlatformResponse)
def read_platform(platform_id: int, db: Session = Depends(get_db)):
    return PlatformAPI(db).read_platform(platform_id)


@router.get("/", response_model=PlatformListResponse)
def read_platforms(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    platform_data = PlatformAPI(db).read_platforms(skip, limit)
    return PlatformListResponse(data=platform_data, total=len(platform_data), limit=limit, page=skip)


@router.put("/{platform_id}", response_model=PlatformResponse)
def update_platform(platform_id: int, platform: PlatformCreate, db: Session = Depends(get_db)):
    return PlatformAPI(db).update_platform(platform_id, platform)


@router.delete("/{platform_id}", response_model=PlatformResponse)
def delete_platform(platform_id: int, db: Session = Depends(get_db)):
    return PlatformAPI(db).delete_platform(platform_id)


@router.get("/pull_data/coingecko", response_model=PlatformPullDataResponse, status_code=202)
def pull_data_coingecko():
    try:
        task = celery_app.send_task("pull_coins_from_coingecko")
        return PlatformPullDataResponse(status="success", message="Task started", task_id=task.id)
    except httpx.RequestError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
