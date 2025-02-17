from config.celery import celery_app
from fastapi import APIRouter, HTTPException
from schema import CoingeckoPullDataResponse
import traceback
import httpx

router = APIRouter(prefix="/data-sources", tags=["Data Sources"])


@router.get("/pull/coingecko", response_model=CoingeckoPullDataResponse, status_code=202)
def pull_data_coingecko():
    try:
        task = celery_app.send_task("pull_coins_from_coingecko")
        return CoingeckoPullDataResponse(status="success", message="Task started", task_id=task.id)
    except httpx.RequestError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
