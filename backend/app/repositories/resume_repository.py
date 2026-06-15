import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume, ResumeCreate, ResumeCreate]):
    """
    Resume repository handling database operations for Resume configurations.
    """

    def __init__(self) -> None:
        super().__init__(Resume)

    def get_resumes_by_user(
        self, db: Session, user_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> List[Resume]:
        """
        Query all resumes matching a specific User ID.
        """
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(query).all())


# Expose repository singleton instance
resume_repository = ResumeRepository()
