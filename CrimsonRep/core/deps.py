"""Compatibility imports for shared FastAPI dependencies."""
from CrimsonRep.core.dependencies import get_database_session
from CrimsonRep.core.security import get_current_user, oauth2_scheme


get_db = get_database_session

__all__ = ["get_database_session", "get_db", "get_current_user", "oauth2_scheme"]
