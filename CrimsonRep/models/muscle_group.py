from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

# Base is defined in database.py
from CrimsonRep.core.database import Base

class MuscleGroup(Base):
    __tablename__ = "muscle_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    muscle_group_id = Column(Integer, ForeignKey("muscle_groups.id"))
    muscle_group = relationship("MuscleGroup")

    # Relationship to User (you may need this)
    user = relationship("User", foreign_keys=[user_id])