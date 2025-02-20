from sqlalchemy import BigInteger, Column, String, DateTime, func, Text

from models import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(BigInteger, primary_key=True, index=True)
    token_pair_id = Column(BigInteger, ForeignKey("token_pairs.id"), nullable=False)
    historical_data_key = Column(String(100), nullable=False)
    token_pairs_key = Column(String(100), nullable=False)
    real_time_data_key = Column(String(100), nullable=False)
    combined_data_key = Column(String(100), nullable=False)
    buying_decision = Column(String(50), nullable=False)
    trend = Column(String(50), nullable=False)
    sentiment = Column(String(50), nullable=False)
    volatility = Column(String(50), nullable=False)
    reasoning = Column(Text, nullable=False)
    insights = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
