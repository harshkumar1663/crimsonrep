from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text

from CrimsonRep.models.muscle_group import MuscleGroup, Exercise
from CrimsonRep.models.user import User
from CrimsonRep.schemas.exercise import ExerciseResponse, ExerciseCreate, ExerciseUpdate
from CrimsonRep.core.dependencies import get_database_session
from CrimsonRep.core.security import get_current_user
from CrimsonRep.schemas.progress import ExerciseProgressResponse, ProgressSet

router = APIRouter()


def get_muscle_group_by_name(db: Session, name: str) -> MuscleGroup:
    return db.query(MuscleGroup).filter(MuscleGroup.name == name).first()

def exercise_to_response(exercise: Exercise, db: Session) -> ExerciseResponse:
    muscle_group_name = ""
    if exercise.muscle_group:
        muscle_group_name = exercise.muscle_group.name

    return ExerciseResponse(
        id= exercise.id,
        name= exercise.name,
        muscle_group= muscle_group_name,
        muscle_group_id= exercise.muscle_group_id,
        is_default= exercise.is_default,
        user_id= exercise.user_id,
        created_at= exercise.created_at
    )

@router.get("/exercises", response_model= List[ExerciseResponse])
def list_default_exercises(db: Session = Depends(get_database_session)):
    exercises= db.query(Exercise).filter(
        Exercise.is_default == True, 
        Exercise.user_id == None
    ).all()

    return [exercise_to_response(ex, db) for ex in exercises]

@router.post("/exercises/custom", response_model= ExerciseResponse)
def create_custom_exercise(
    exercise_data: ExerciseCreate, 
    db: Session = Depends(get_database_session),
    current_user: User= Depends(get_current_user)    
):
    muscle_group= get_muscle_group_by_name(db, exercise_data.muscle_group)
    if not muscle_group:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"Muscle group '{exercise_data.muscle_group}' not found"
        )

    db_exercise= Exercise(
        name= exercise_data.name,
        muscle_group_id= muscle_group.id,
        is_default= False,
        user_id= current_user.id
    )

    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)

    return exercise_to_response(db_exercise, db)

@router.get("/exercises/my", response_model= List[ExerciseResponse])
def get_my_exercises(db: Session = Depends(get_database_session), current_user: User = Depends(get_current_user)):
    user_id = current_user.id

    exercises= db.query(Exercise).filter(
        Exercise.is_default == False,
        Exercise.user_id == user_id
    ).all()

    return [exercise_to_response(ex, db) for ex in exercises]

@router.get("/exercises/{exercise_id}", response_model= ExerciseResponse)
def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    exercise= db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not exercise:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"Exercise with id {exercise_id} not found"
        )
    if not exercise.is_default and exercise.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found"
        )
    return exercise_to_response(exercise, db)

@router.put("/exercises/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: int,
    exercise_update: ExerciseUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    db_exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found"
        )

    # Prevent from updating someone else's exercise
    if db_exercise.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your exercise to update"
        )

    if exercise_update.name is not None:
        db_exercise.name = exercise_update.name

    if exercise_update.muscle_group is not None:
        muscle_group = get_muscle_group_by_name(db, exercise_update.muscle_group)
        if not muscle_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Muscle group '{exercise_update.muscle_group}' not found"
            )
        db_exercise.muscle_group_id = muscle_group.id

    db.commit()
    db.refresh(db_exercise)

    return exercise_to_response(db_exercise, db)

# Delete exercise
@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    db_exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found"
        )
    if db_exercise.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your exercise to delete"
        )

    db.delete(db_exercise)
    db.commit()

    return None

# Last and best progress
@router.get("/exercises/{exercise_id}/progress",
            response_model=ExerciseProgressResponse)
def get_exercise_progress(
    exercise_id: int,
    db: Session= Depends(get_database_session),
    current_user: User= Depends(get_current_user)
):
    """Get the last and best session progression for an exercise.

    Best is defined as the session with the highest estimated 1RM (Epley formula).
    Last is the most recent session.
    """

    # Verify exercise exists and THIS user has access to it

    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id
    ).first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    if not exercise.is_default and exercise.user_id != current_user.id:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized"
        )

    sql = text("""
        WITH ranked_sets AS (
            SELECT
                s.id AS session_id,
                s.created_at AS session_date,
                se.reps,
                se.weight,
                se.weight * (1 + se.reps / 30.0) AS e1rm,
                ROW_NUMBER() OVER (ORDER BY s.created_at DESC) AS rn_last,
                ROW_NUMBER() OVER (ORDER BY se.weight * (1 + se.reps / 30.0) DESC, s.created_at DESC) AS rn_best
            FROM sessions s
            JOIN sets se ON se.session_id = s.id
            WHERE s.exercise_id = :exercise_id
              AND s.user_id = :user_id
        )
        SELECT
            MAX(CASE WHEN rn_last = 1 THEN session_id END) AS last_session_id,
            MAX(CASE WHEN rn_last = 1 THEN session_date END) AS last_session_date,
            MAX(CASE WHEN rn_last = 1 THEN reps END) AS last_reps,
            MAX(CASE WHEN rn_last = 1 THEN weight END) AS last_weight,
            MAX(CASE WHEN rn_last = 1 THEN e1rm END) AS last_e1rm,
            MAX(CASE WHEN rn_best = 1 THEN session_id END) AS best_session_id,
            MAX(CASE WHEN rn_best = 1 THEN session_date END) AS best_session_date,
            MAX(CASE WHEN rn_best = 1 THEN reps END) AS best_reps,
            MAX(CASE WHEN rn_best = 1 THEN weight END) AS best_weight,
            MAX(CASE WHEN rn_best = 1 THEN e1rm END) AS best_e1rm
        FROM ranked_sets
""")

    row = db.execute(sql, {"exercise_id": exercise_id, "user_id": current_user.id}).fetchone()

    if not row or row.last_session_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sessions found for this exercise"
        )

    return ExerciseProgressResponse(
        exercise_id=exercise_id,
        last=ProgressSet(
            session_id=row.last_session_id,
            session_date=row.last_session_date,
            reps=row.last_reps,
            weight=row.last_weight,
            e1rm=row.last_e1rm,
        ),
        best=ProgressSet(
            session_id=row.best_session_id,
            session_date=row.best_session_date,
            reps=row.best_reps,
            weight=row.best_weight,
            e1rm=row.best_e1rm,
        ),
    )