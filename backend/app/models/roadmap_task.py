import uuid
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class RoadmapTask(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    RoadmapTask model representing specific tasks, learning milestones, or achievements.
    """
    __tablename__ = "roadmap_tasks"

    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign Key referencing the Roadmap this task belongs to"
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Task or milestone title (e.g. Master Basic Python Syntax)"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        doc="Actionable guidelines or resource links to accomplish this task"
    )
    sequence: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=0,
        doc="The order sequence value indicating when this task should be completed relative to others"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        doc="Current status of the task (e.g., pending, in_progress, completed)"
    )

    # --- Relationships ---
    
    # Many-to-One Back Reference: A task belongs to a single Roadmap.
    roadmap: Mapped["Roadmap"] = relationship(
        "Roadmap",
        back_populates="tasks",
        doc="The Roadmap associated with this task"
    )
