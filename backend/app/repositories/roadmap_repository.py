import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.roadmap import Roadmap
from app.schemas.roadmap import RoadmapCreate
from app.repositories.base import BaseRepository


class RoadmapRepository(BaseRepository[Roadmap, RoadmapCreate, RoadmapCreate]):
    """
    Roadmap repository handling database operations for Generated Career Roadmaps.
    """

    def __init__(self) -> None:
        super().__init__(Roadmap)

    def get_roadmaps_by_user(
        self, db: Session, user_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> List[Roadmap]:
        """
        Query all career roadmap records associated with a specific User ID.
        """
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(query).all())


# Expose repository singleton instance
roadmap_repository = RoadmapRepository()
