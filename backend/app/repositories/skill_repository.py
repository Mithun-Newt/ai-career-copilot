from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.schemas.skill import SkillCreate
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill, SkillCreate, SkillCreate]):
    """
    Skill repository handling database queries for the master skill directory catalog.
    """

    def __init__(self) -> None:
        super().__init__(Skill)

    def get_by_name(self, db: Session, name: str) -> Optional[Skill]:
        """
        Query a skill item by its matching unique name string (case-insensitive checks can be added here).
        """
        query = select(self.model).where(self.model.name == name)
        return db.scalars(query).first()

    def create_skill(self, db: Session, *, obj_in: SkillCreate) -> Skill:
        """
        Register a new master skill reference tag.
        """
        return self.create(db, obj_in=obj_in)


# Expose repository singleton instance
skill_repository = SkillRepository()
