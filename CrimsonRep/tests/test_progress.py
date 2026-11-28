from fastapi.testclient import TestClient
from fastapi import status
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from CrimsonRep.core.database import Base
from CrimsonRep.models.user import User
from CrimsonRep.models.muscle_group import MuscleGroup, Exercise
from CrimsonRep.models.session import Session as WorkoutSession, Set
from CrimsonRep.app.main import app
from CrimsonRep.apis.auth import get_db


# Create test engine and session
TEST_ENGINE = create_engine(
    "sqlite:////tmp/test_crimson.db",
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def setup_test_data():
    """Seed test database with required data"""
    db = TestingSessionLocal()
    try:
        # Create user
        from CrimsonRep.core.security import get_password_hash
        user = User(email="test@example.com", hashed_password=get_password_hash("password123"))
        db.add(user)
        db.commit()
        db.refresh(user)

        user_id = user.id

        # Create muscle groups
        for name in ["Chest", "Legs", "Back", "Shoulders"]:
            mg = MuscleGroup(name=name)
            db.add(mg)
        db.commit()

        # Create default exercises
        from sqlalchemy import text
        db.execute(text("""
            INSERT INTO exercises (name, muscle_group_id, is_default, user_id, created_at)
            SELECT 'Bench Press', m.id, true, null, datetime('now')
            FROM muscle_groups m WHERE m.name = 'Chest'
        """))
        db.commit()

    finally:
        db.close()


def get_auth_headers():
    """Helper to get auth headers"""
    client = TestClient(app)
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    if response.status_code != 200:
        client.post("/auth/signup", json={"email": "test@example.com", "password": "password123"})
        response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=TEST_ENGINE)
    Base.metadata.create_all(bind=TEST_ENGINE)
    setup_test_data()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override


def test_progress_returns_last_and_best(client):
    """Test that progress endpoint returns last and best session"""
    headers = get_auth_headers()

    # Create custom exercise
    response = client.post("/exercises/custom", json={"name": "Bench Press", "muscle_group": "Chest"}, headers=headers)
    assert response.status_code == 200, f"Failed to create exercise: {response.json()}"
    exercise_id = response.json()["id"]

    # Create first session (older)
    response = client.post("/sessions", json={
        "exercise_id": exercise_id,
        "sets": [{"reps": 5, "weight": 100}]
    }, headers=headers)
    assert response.status_code == 200

    # Create second session (newer, but lower e1RM)
    response = client.post("/sessions", json={
        "exercise_id": exercise_id,
        "sets": [{"reps": 8, "weight": 90}]
    }, headers=headers)
    assert response.status_code == 200

    # Get progress
    response = client.get(f"/exercises/{exercise_id}/progress", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Verify last session (most recent)
    assert data["last"]["weight"] == 90
    assert data["last"]["reps"] == 8

    # Verify best session (highest e1RM: 100×(1+5/30) = 116.7 > 90×(1+8/30) = 114)
    assert data["best"]["weight"] == 100
    assert data["best"]["reps"] == 5


def test_progress_404_on_missing_session(client):
    """Test that progress returns 404 when no sessions"""
    headers = get_auth_headers()

    # Create a custom exercise
    response = client.post("/exercises/custom", json={"name": "Squats", "muscle_group": "Legs"}, headers=headers)
    assert response.status_code == 200
    exercise_id = response.json()["id"]

    response = client.get(f"/exercises/{exercise_id}/progress", headers=headers)
    assert response.status_code == 404
