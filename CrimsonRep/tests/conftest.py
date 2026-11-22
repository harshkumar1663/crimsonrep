import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import CrimsonRep.models.user  

from CrimsonRep.core.test_database import engine, TestingSessionLocal, setup_test_db
from CrimsonRep.core.database import Base
from CrimsonRep.app.main import app
from CrimsonRep.apis.auth import get_db

setup_test_db()

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Debug: check what the override looks like
print("DEBUG: get_db function:", get_db)
print("DEBUG: override function:", override_get_db)

app.dependency_overrides[get_db] = override_get_db
print("DEBUG: overrides after setting:", app.dependency_overrides)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()