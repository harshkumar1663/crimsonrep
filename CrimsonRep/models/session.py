from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from CrimsonRep.core.database import Base

class Session(Base):
    """A workout session"""

    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
        )
    exercise_id = Column(
        Integer,
        ForeignKey("exercises.id"),
        nullable= False
        )
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, 
                        default= lambda: datetime.now(timezone.utc))

    # relations
    user = relationship("User", foreign_keys=[user_id])
    exercise = relationship("Exercise", foreign_keys= [exercise_id])
    sets = relationship(
        "Set",
        back_populates= "session",
        cascade= "all,delete-orphan"
    )

class Set(Base):
    """A single set within a session"""

    __tablename__ = "sets"
    id = Column(
        Integer, 
        primary_key= True,
    )
    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable= False
    )
    exercise_id = Column(
        Integer,
        ForeignKey("exercises.id"),
        nullable= False
    )
    reps = Column(Integer, nullable= False)
    weight = Column(Float, nullable= False)

    order = Column(Integer, nullable= False)
    created_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc)
    )

    # relationships
    session = relationship(
        "Session",
        back_populates="sets"
    )
    exercise = relationship(
        "Exercise", 
        foreign_keys=[exercise_id]
    )
    