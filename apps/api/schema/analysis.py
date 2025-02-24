from typing import Optional
from click import Option
from pydantic import BaseModel
from datetime import datetime


class AnalysisResultBase(BaseModel):
    token_pair_id: int
    historical_data_key: str
    token_pairs_key: str
    real_time_data_key: str
    combined_data_key: str
    buying_decision: str
    trend: str
    sentiment: str
    volatility: str
    reasoning: str
    insights: str


class AnalysisResult(AnalysisResultBase):
    id: int
    insights: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisResultCreate(AnalysisResultBase):
    insights: Optional[str] = None


class AnalysisResultResponse(AnalysisResult):
    pass


class AnalysisResultUpdate(AnalysisResultBase):
    insights: Optional[str] = None


class AnalysisResultListResponse(BaseModel):
    data: list[AnalysisResultResponse] = []
    total: int
    limit: int
    page: int
