from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.analysis import AnalysisResult
from schema import AnalysisResultCreate, AnalysisResultResponse
import traceback

class AnalysisResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_analysis_result(self, token_pair_id, analysis_result: AnalysisResultCreate) -> AnalysisResultResponse:
        try:
            db_analysis_result = AnalysisResult(
                token_pair_id=token_pair_id,
                historical_data_key=analysis_result.historical_data_key,
                token_pairs_key=analysis_result.token_pairs_key,
                real_time_data_key=analysis_result.real_time_data_key,
                combined_data_key=analysis_result.combined_data_key,
                buying_decision=analysis_result.buying_decision,
                trend=analysis_result.trend,
                sentiment=analysis_result.sentiment,
                volatility=analysis_result.volatility,
                reasoning=analysis_result.reasoning,
                insights=analysis_result.insights
            )
            self.db.add(db_analysis_result)
            self.db.commit()
            self.db.refresh(db_analysis_result)

            return AnalysisResultResponse(
                id=db_analysis_result.id,
                token_pair_id=db_analysis_result.token_pair_id,
                historical_data_key=db_analysis_result.historical_data_key,
                token_pairs_key=db_analysis_result.token_pairs_key,
                real_time_data_key=db_analysis_result.real_time_data_key,
                combined_data_key=db_analysis_result.combined_data_key,
                buying_decision=db_analysis_result.buying_decision,
                trend=db_analysis_result.trend,
                sentiment=db_analysis_result.sentiment,
                volatility=db_analysis_result.volatility,
                reasoning=db_analysis_result.reasoning,
                insights=db_analysis_result.insights,
                created_at=db_analysis_result.created_at,
                updated_at=db_analysis_result.updated_at
            )
        except Exception as e:
            self.db.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    def read_analysis_result(self, analysis_result_id: int):
        try:
            db_analysis_result = self.db.query(AnalysisResult).filter(AnalysisResult.id == analysis_result_id).first()
            if db_analysis_result is None:
                raise HTTPException(status_code=404, detail="Analysis result not found")
            return db_analysis_result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def read_analysis_results(self, skip: int = 0, limit: int = 10):
        try:
            analysis_results = self.db.query(AnalysisResult).offset(skip).limit(limit).all()
            return analysis_results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_analysis_result(self, analysis_result_id: int, analysis_result: AnalysisResultCreate):
        try:
            db_analysis_result = self.db.query(AnalysisResult).filter(AnalysisResult.id == analysis_result_id).first()
            if db_analysis_result is None:
                raise HTTPException(status_code=404, detail="Analysis result not found")
            for key, value in analysis_result.model_dump().items():
                setattr(db_analysis_result, key, value)
            self.db.commit()
            self.db.refresh(db_analysis_result)
            return db_analysis_result
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def delete_analysis_result(self, analysis_result_id: int):
        try:
            db_analysis_result = self.db.query(AnalysisResult).filter(AnalysisResult.id == analysis_result_id).first()
            if db_analysis_result is None:
                raise HTTPException(status_code=404, detail="Analysis result not found")
            self.db.delete(db_analysis_result)
            self.db.commit()
            return db_analysis_result
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
