import pytest
from fastapi.testclient import TestClient

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

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
