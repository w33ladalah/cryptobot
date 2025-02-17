from pydantic import BaseModel
from typing import Optional


class CoingeckoPullDataResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None
