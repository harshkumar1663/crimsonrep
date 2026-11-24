from CrimsonRep.core.database import SessionLocal
from CrimsonRep.models.muscle_group import MuscleGroup, Exercise

def seed_muscle_groups(db):
    # Seed default muscle groups and some dummy data
    muscle_groups = [
        "Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps", "Abs"
    ]

    # Store created objects in a dict, to link exercises later

    seeded_groups = {}

    for name in muscle_groups:
        # check if already exists in DB to aboid duplicates
        existing = db.query(MuscleGroup).filter(
            MuscleGroup.name == name).first()

        if not existing :
            mg = MuscleGroup(name = name)
            db.add(mg)
            db.flush() # flush and give mg.id before committing transaction

            seeded_groups[name] = mg

            print(f"   + Added Muscle Group: {name}")
        else:
            seeded_groups[name] = existing
            print(f"  = Muscle Group already exists : {name}")

    return seeded_groups


def seed_exercises(db, groups):
    # Seed initial default exercises
    # (Exercise name, Targeted Muscle Group)
    default_exercises = [
        ("Bench Press", "Chest"),
        ("Incline Dumbbell Press", "Chest"),
        ("Pull Ups", "Back"),
        ("Deadlift", "Back"),
        ("Barbell Back Squat", "Legs"),
        ("Overhead Press", "Shoulders"),
        ("Barbell Curl", "Biceps"),
        ("Tricep Dips", "Triceps"),
        ("Crunches", "Abs")
    ]

    for ex_name, group_name in default_exercises:
        existing = db.query(Exercise).filter(
            Exercise.name == ex_name, Exercise.is_default == True
            ).first()
        if not existing:
            mg  = groups.get(group_name)
            if mg: 
                exercise = Exercise(name = ex_name,
                                    muscle_group_id = mg.id,
                                    is_default = True,
                                    user_id = None)
                db.add(exercise)
                print(f"  + Added exercise : {ex_name} for {group_name}")
            else:
                print(f"   = Exercise already exists {ex_name}")


def main():
    db = SessionLocal()

    try:
        print("Seeding Muscle Groups...")
        groups = seed_muscle_groups(db)
        print("\nSeeding Default Exercises...")
        seed_exercises(db, groups)

        # save everything to SQL in one atomic trxn
        db.commit() 
        print("\nDB Seeding Complete\n")
    except Exception as e:
        # Revert changes if anything fails
        # To prevent half-seeded data
        db.rollback()
        print(f"\nERROR during seeding {e}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
