from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class AssessmentBase(BaseModel):
    title: str
    weight_pct: float = Field(ge=0, le=100)
    due_date: date
    score_pct: Optional[float] = Field(default=None, ge=0, le=100)

class AssessmentIn(AssessmentBase): pass

class AssessmentUpdate(BaseModel):
    title: Optional[str] = None
    weight_pct: Optional[float] = Field(default=None, ge=0, le=100)
    due_date: Optional[date] = None
    score_pct: Optional[float] = Field(default=None, ge=0, le=100)

class AssessmentOut(AssessmentBase):
    id: int
    class Config:
        from_attributes = True
