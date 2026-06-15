import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.roadmap_task import RoadmapTask
from app.schemas.roadmap_task import RoadmapTaskCreate, RoadmapTaskUpdate
from app.repositories.base import BaseRepository


class RoadmapTaskRepository(
    BaseRepository[RoadmapTask, RoadmapTaskCreate, RoadmapTaskUpdate]
):
    """
    RoadmapTask repository handling database query actions for individual roadmap milestones.
    """

    def __init__(self) -> None:
        super().__init__(RoadmapTask)

    def get_tasks_by_roadmap(
        self, db: Session, roadmap_id: uuid.UUID
    ) -> List[RoadmapTask]:
        """
        Query all individual roadmap task/milestone records linked to a Roadmap ID.
        Sorts the output automatically by their execution sequence sequence parameter.
        """
        query = (
            select(self.model)
            .where(self.model.roadmap_id == roadmap_id)
            .order_by(self.model.sequence.asc())
        )
        return list(db.scalars(query).all())


# Expose repository singleton instance
roadmap_task_repository = RoadmapTaskRepository()
