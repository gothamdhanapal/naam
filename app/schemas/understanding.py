from pydantic import BaseModel
from typing import Optional


class UnderstandingResult(BaseModel):
    type: str
    title: str
    due_date: Optional[str] = None
    confidence: float