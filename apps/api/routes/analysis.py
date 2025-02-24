from config.celery import celery_app
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm.session import Session
from utils import get_db
from schema import CoingeckoPullDataResponse, AnalysisResultCreate, AnalysisResultResponse, AnalysisResultListResponse, AnalysisResultUpdate
from repositories import AnalysisResultRepository
import traceback
import httpx


routers = APIRouter(prefix="/analysis", tags=["Analysis"])


@routers.get("/perform_analysis", response_model=CoingeckoPullDataResponse, status_code=202)
def perform_analysis(request: Request):
    try:
        task = celery_app.send_task("perform_llm_analysis", args=[request.query_params["token_id"], True])
        return CoingeckoPullDataResponse(status="success", message="Task started", task_id=task.id)
    except httpx.RequestError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@routers.get("/get_analysis_results", response_model=CoingeckoPullDataResponse, status_code=200)
def get_analysis_results(request: Request):
    try:
        task = celery_app.send_task("perform_llm_analysis", args=[request.query_params["token_id"], False])
        return CoingeckoPullDataResponse(status="success", message="Task started", task_id=task.id)
    except httpx.RequestError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@routers.post("/store_analysis_results/{token_pair_id}", response_model=AnalysisResultResponse, status_code=202)
def store_analysis_results(token_pair_id: int, data: AnalysisResultCreate, db: Session = Depends(get_db)):
    try:
        return AnalysisResultRepository(db).create_analysis_result(token_pair_id, data)
    except httpx.RequestError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
