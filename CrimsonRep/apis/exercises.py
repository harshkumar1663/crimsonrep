from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from CrimsonRep.core.database import SessionLocal
from CrimsonRep.models.muscle_group import MuscleGroup, Exercise
from CrimsonRep.models.user import User 
from CrimsonRep.schemas.exercise import ExerciseBase, ExerciseResponse, ExerciseCreate, ExerciseUpdate


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db)):
    return None

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
def list_default_exercises(db: Session= Depends(get_db)):
    exercises= db.query(Exercise).filter(
        Exercise.is_default == True, 
        Exercise.user_id == None
    ).all()

    return [exercise_to_response(ex, db) for ex in exercises]

@router.post("/exercises/custom", response_model= ExerciseResponse)
def create_custom_exercise(exercise_data: ExerciseCreate, db: Session= Depends(get_db)):
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
        user_id= get_current_user #TODO
    )

    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)

    return exercise_to_response(db_exercise, db)

@router.get("/exercises/my", response_model= List[ExerciseResponse])
def get_my_exercises(db: Session= Depends(get_db)):
    user_id= None

    exercises= db.query(Exercise).filter(
        Exercise.is_default == False,
        Exercise.user_id == user_id
    ).all()

    return [exercise_to_response(ex, db) for ex in exercises]

@router.get("/exercises/{exercise_id}", response_model= ExerciseResponse)
def get_exercise(exercise_id: int, db: Session= Depends(get_db)):
    exercise= db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not exercise:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"Exercise with id {exercise_id} not found"
        )
    return exercise_to_response(exercise, db)

@router.put("/exercises/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: int,
    exercise_update: ExerciseUpdate,
    db: Session = Depends(get_db)
    # Add: current_user: User = Depends(get_current_user)
):
    db_exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found"
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

@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db)
    # Add: current_user: User = Depends(get_current_user)
):
    db_exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found"
        )

    db.delete(db_exercise)
    db.commit()

    return None