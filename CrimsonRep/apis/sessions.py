from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session as DbSession

from CrimsonRep.core.dependencies import get_database_session
from CrimsonRep.models.session import Session as WorkoutSession, Set
from CrimsonRep.models.user import User
from CrimsonRep.models.muscle_group import Exercise
from CrimsonRep.schemas.session import SessionCreate, SessionResponse, SetResponse
from CrimsonRep.core.security import get_current_user

router = APIRouter()

@router.post("/sessions", response_model=SessionResponse)
def log_workout(
    session_data: SessionCreate,
    db: DbSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    if exercise.user_id is not None and exercise.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # create the session
    db_session = WorkoutSession(
        user_id=current_user.id,
        exercise_id=session_data.exercise_id,
        notes=session_data.notes,
    )

    db.add(db_session)
    db.flush()  # Get session ID without committing

    # Persist all sets in the same transaction as their parent session.
    for idx, set_data in enumerate(session_data.sets):
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
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_session)

    # fetch sets for response
    for s in db_session.sets:
        db.refresh(s)

    return SessionResponse(
        id=db_session.id,
        exercise_id=db_session.exercise_id,
        notes=db_session.notes,
        created_at=db_session.created_at,
        sets=[
            SetResponse(
                id=s.id,
                exercise_id=s.exercise_id,
                reps=s.reps,
                weight=s.weight,
                order=s.order,
                created_at=s.created_at,
            )
            for s in sorted(db_session.sets, key=lambda item: item.order)
        ]
    )


@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(
    skip: int = 0,
    limit: int = 20,
    db: DbSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """List the authenticated user's sessions, newest first."""
    if skip < 0:
        raise HTTPException(status_code=400, detail="skip must be non-negative")
    if not 1 <= limit <= 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    sessions = (
        db.query(WorkoutSession)
        .filter(WorkoutSession.user_id == current_user.id)
        .order_by(WorkoutSession.created_at.desc(), WorkoutSession.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        SessionResponse(
            id=session.id,
            exercise_id=session.exercise_id,
            notes=session.notes,
            created_at=session.created_at,
            sets=[
                SetResponse(
                    id=workout_set.id,
                    exercise_id=workout_set.exercise_id,
                    reps=workout_set.reps,
                    weight=workout_set.weight,
                    order=workout_set.order,
                    created_at=workout_set.created_at,
                )
                for workout_set in sorted(session.sets, key=lambda item: item.order)
            ],
        )
        for session in sessions
    ]

@router.get("/sessions/{session_id}",
            response_model=SessionResponse)
def get_single_session(
    session_id: int,
    db: DbSession= Depends(get_database_session),
    current_user: User= Depends(get_current_user)
):
    """Get a specified workout session by ID"""
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Session not found"
        )

    # Auth check
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= "Not authorized to access this session"
        )
    return SessionResponse(
        id = session.id,
        exercise_id= session.exercise_id,
        notes= session.notes,
        created_at= session.created_at,
        sets = [
            SetResponse(
                id= s.id,
                exercise_id= s.exercise_id,
                reps= s.reps,
                weight=s.weight,
                order=s.order,
                created_at=s.created_at
            )
            for s in sorted(session.sets, key=lambda item: item.order)
        ]
    )

@router.delete("/sessions/{session_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: DbSession= Depends(get_database_session),
    current_user: User= Depends(get_current_user)
):
    """Delete a workout session. Sets are cascade-deleted"""
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Auth check 
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this session"
        )
    
    db.delete(session)
    db.commit()

    return None #FastAPI return 204