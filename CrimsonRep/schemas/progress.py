from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ProgressSet(BaseModel):
    """A set of data for either last or best progression"""

    session_id: int
    session_date: datetime
    reps: int
    weight: float
    e1rm: float

    model_config= ConfigDict(from_attributes=True)


class ExerciseProgressResponse(BaseModel):
    """Response for GET /exercises/{id}/progress"""

    exercise_id: int
    last: ProgressSet
    best: ProgressSet

    model_config= ConfigDict(from_attributes=True)