from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from CrimsonRep.core.database import SessionLocal
from CrimsonRep.models.session import Session, Set
from CrimsonRep.models.user import User
from CrimsonRep.models.muscle_group import Exercise
from CrimsonRep.schemas.session import SessionCreate, SessionResponse, SetResponse
from CrimsonRep.core.security import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sessions",response_model=SessionResponse)
def log_workout(
    session_data: SessionCreate,
    db: Session= Depends(get_db),
    current_user: User= Depends(get_current_user)
):
    """Log a completed workout session with nested sets.
    Request body example:
    {
        "exercise_id": 5,
        "sets": [
            {"reps": 10, "weight": 50},
            {"reps": 8, "weight": 60},
            {"reps": 12, "weight": 45}
        ]
    }"""

    # verify exercise exists
    exercise = db.query(Exercise).filter(
        Exercise.id == session_data.exercise_id
    ).first()

    if not exercise:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Exercise not found"
        )

    # create the session
    db_session= Session(
        user_id= current_user.id,
        exercise_id= session_data.exercise_id
    )

    db.add(db_session)
    db.flush() #Get session ID without committing

    # create all sets with validation
    for idx, set_data in enumerate(session_data.sets):
        # Validate: reps > 0 and weight >= 0
        if set_data.reps <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reps must be > 0 for set {idx + 1}"
            )
        if set_data.weight < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Weight must be >= 0 for set {idx + 1}"
            )

        set_order = set_data.order if set_data.order is not None else idx + 1

        db_set = Set(
            session_id=db_session.id,
            exercise_id=db_session.exercise_id,
            reps=set_data.reps,
            weight=set_data.weight,
            order=set_order
        )
        db.add(db_set)

    # commit everything atomically
    db.commit()
    db.refresh(db_session)

    # fetch sets for response
    for s in db_session.sets:
        db.refresh(s)

    return SessionResponse(
        id= db_session.id,
        exercise_id= db_session.exercise_id,
        sets=[
            SetResponse(
                id=s.id,
                exercise_id=s.exercise_id,
                reps=s.reps,
                weight=s.weight,
                order=s.order
            )
            for s in db_session.sets
        ]
    )