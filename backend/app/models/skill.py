import uuid
from typing import List, Optional
from sqlalchemy import Table, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

# Many-to-Many association table for Users and Skills
user_skills = Table(
    "user_skills",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Foreign Key referencing the User's ID"
    ),
    Column(
        "skill_id",
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Foreign Key referencing the Skill's ID"
    )
)


class Skill(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Skill model representing a master catalog of skill tags (e.g. Python, SQL, Project Management).
    """
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        doc="Unique skill label (e.g., Python)"
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Category grouping (e.g., Programming, Marketing, Soft Skills)"
    )

    # --- Relationships ---
    
    # Many-to-Many Back Reference: Multiple users possess this skill.
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_skills,
        back_populates="skills",
        doc="List of Users who possess this skill"
    )
