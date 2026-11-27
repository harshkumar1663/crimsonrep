"""Database dependencies for FastAPI routes."""
from CrimsonRep.core.database import SessionLocal


def get_database_session():
    """Get a database session for FastAPI dependency injection.

    This function is intentionally named to avoid conflicts with
    SQLAlchemy's Session class and any user-defined model classes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()