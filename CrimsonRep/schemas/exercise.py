from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExerciseBase(BaseModel):
    name: str
    muscle_group: str

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseResponse(BaseModel):
    id: int
    name: str
    muscle_group: str
    muscle_group_id : int
    is_default: bool
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ExerciseUpdate(BaseModel):
    name: Optional[str]= None
    muscle_group: Optional[str]= None

