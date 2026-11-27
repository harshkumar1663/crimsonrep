from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class SetCreate(BaseModel):
    """Data for creating a single set"""
    reps: int = Field(gt=0)
    weight: float = Field(ge=0)  # FIXED: Allow zero weight
    order: Optional[int] = Field(default=None, gt=0)

class SessionCreate(BaseModel):
    """Data for creating a workout session"""
    exercise_id: int = Field(gt=0)
    sets: List[SetCreate] = Field(min_length=1)
    notes: Optional[str] = None

    @field_validator('sets')
    @classmethod
    def validate_sets_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError("At least one set is required")
        orders = [item.order if item.order is not None else index + 1
                  for index, item in enumerate(v)]
        if len(orders) != len(set(orders)):
            raise ValueError("Set order values must be unique")
        return v

class SetResponse(BaseModel):
    id: int
    exercise_id: int
    reps: int
    weight: float
    order: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    id: int
    exercise_id: int
    sets: List[SetResponse]
    notes: Optional[str] = None  # FIXED: Was Optional[int]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
