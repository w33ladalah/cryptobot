from fastapi import APIRouter, HTTPException, Depends
from repositories import PlatformRepository as PlatformAPI
from schema import PlatformCreate, PlatformResponse, PlatformListResponse
from sqlalchemy.orm import Session
from utils import get_db


router = APIRouter(prefix="/platforms", tags=["Platforms"])


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
