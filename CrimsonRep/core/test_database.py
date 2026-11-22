from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from CrimsonRep.core.database import Base

# Use a file-based SQLite for tests (persists across connections)
import tempfile
import os

# Create a temporary file for the test database
TEST_DB_FILE = tempfile.mktemp(suffix='.db')
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_test_db():
    """Create all tables in the test database."""
    Base.metadata.create_all(bind=engine)
    print(f"DEBUG: Test database created at: {TEST_DB_FILE}")


def cleanup_test_db():
    """Remove the test database file."""
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)