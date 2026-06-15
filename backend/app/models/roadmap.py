import uuid
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Roadmap(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Roadmap model representing generated learning and career paths for a user.
    """
    __tablename__ = "roadmaps"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign Key referencing the User this roadmap belongs to"
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Title of the career roadmap (e.g., Python Developer Pathway)"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        doc="Overview of the learning pathway and goals"
    )
    target_role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        doc="Desired career/job role (e.g., AI Research Scientist)"
    )

    # --- Relationships ---
    
    # Many-to-One Back Reference: A roadmap belongs to a single User.
    user: Mapped["User"] = relationship(
        "User",
        back_populates="roadmaps",
        doc="The User who owns this roadmap"
    )

    # One-to-Many: A roadmap is partitioned into individual sequenced tasks/milestones.
    # We apply order_by on the task sequence for consistent fetching.
    tasks: Mapped[List["RoadmapTask"]] = relationship(
        "RoadmapTask",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="RoadmapTask.sequence",
        doc="Sequenced list of tasks within this roadmap"
    )

    @property
    def milestones(self) -> List[dict]:
        """
        Group flat RoadmapTask entities back into structured Milestones based on prefix stored in description.
        """
        from collections import OrderedDict
        milestones_dict = OrderedDict()
        
        for task in self.tasks:
            desc = task.description or ""
            milestone_title = "General Preparation"
            task_desc = desc
            
            if desc.startswith("Milestone: "):
                parts = desc.split("\n\n", 1)
                if len(parts) == 2:
                    milestone_title = parts[0].replace("Milestone: ", "").strip()
                    task_desc = parts[1]
            
            if milestone_title not in milestones_dict:
                milestones_dict[milestone_title] = {
                    "title": milestone_title,
                    "description": f"Target milestone: {milestone_title}",
                    "tasks": []
                }
            
            milestones_dict[milestone_title]["tasks"].append({
                "id": task.id,
                "title": task.title,
                "description": task_desc,
                "sequence": task.sequence,
                "status": task.status
            })
            
        return list(milestones_dict.values())

    @property
    def progress_percentage(self) -> int:
        """
        Calculates the completion percentage of the roadmap based on task statuses.
        """
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return 0
        completed_tasks = sum(1 for task in self.tasks if task.status == "completed")
        return int((completed_tasks / total_tasks) * 100)

