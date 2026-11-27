from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class SetCreate(BaseModel):
    """Data for creating a single set"""
    reps: int = Field(gt=0)
    weight: float = Field(ge=0)  # Allow zero weight
    order: Optional[int] = None

class SessionCreate(BaseModel):
    """Data for creating a workout session"""
    exercise_id: int
    sets: List[SetCreate] 
    notes: Optional[str] = None

    @field_validator('sets')
    @classmethod
    def validate_sets_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError("At least one set is required")
        return v

class SetResponse(BaseModel):
    id: int
    exercise_id: int
    reps: int
    weight: float
    order: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes= True

class SessionResponse(BaseModel):
    id: int
    exercise_id: int
    sets: List[SetResponse]
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes= True
    
    