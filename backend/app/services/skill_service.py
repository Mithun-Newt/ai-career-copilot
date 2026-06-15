import uuid
from typing import List
from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.schemas.skill import SkillCreate
from app.repositories.skill_repository import skill_repository
from app.repositories.user_repository import user_repository
from app.utils.exceptions import EntityNotFoundError, EntityAlreadyExistsError


class SkillService:
    """
    Business service coordinating actions on skills and user capabilities.
    """

    def create_skill(self, db: Session, *, skill_in: SkillCreate) -> Skill:
        """
        Create a new master skill label.
        Ensures name uniqueness to prevent duplicates.
        """
        existing_skill = skill_repository.get_by_name(db, name=skill_in.name)
        if existing_skill:
            raise EntityAlreadyExistsError("Skill", "name", skill_in.name)
        
        return skill_repository.create_skill(db, obj_in=skill_in)

    def assign_skill_to_user(
        self, db: Session, *, user_id: uuid.UUID, skill_id: uuid.UUID
    ) -> Skill:
        """
        Assign a skill capability tag to a User's profile page.
        """
        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        skill = skill_repository.get_by_id(db, id=skill_id)
        if not skill:
            raise EntityNotFoundError("Skill", skill_id)

        # Handle many-to-many relationship assignment
        if skill not in user.skills:
            user.skills.append(skill)
            db.add(user)
            db.commit()
            db.refresh(skill)

        return skill

    def get_user_skills(self, db: Session, *, user_id: uuid.UUID) -> List[Skill]:
        """
        Fetch all skills possessed by a user.
        """
        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        return user.skills

    def sync_user_skills_from_resume(
        self, db: Session, *, user_id: uuid.UUID, resume_skills: List[str]
    ) -> None:
        """
        Takes list of extracted skills, normalizes names, registers missing skills
        in catalog, and links them to user.
        """
        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        for skill_name in resume_skills:
            # 1. Normalize skill name representation (trim whitespace & title case)
            normalized_name = skill_name.strip()
            if not normalized_name:
                continue

            # 2. Query master skill directory catalog check
            skill = skill_repository.get_by_name(db, name=normalized_name)
            if not skill:
                # Add to master skill catalog list
                skill_in = SkillCreate(name=normalized_name, category="Extracted")
                skill = skill_repository.create(db, obj_in=skill_in)

            # 3. Associate the skill dynamically with user (many-to-many relationship mapping)
            if skill not in user.skills:
                user.skills.append(skill)
                
        db.commit()

    def remove_skill_from_user(
        self, db: Session, *, user_id: uuid.UUID, skill_id: uuid.UUID
    ) -> None:
        """
        Unassign/remove a skill capability from a User's profile.
        """
        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        skill = skill_repository.get_by_id(db, id=skill_id)
        if not skill:
            raise EntityNotFoundError("Skill", skill_id)

        if skill in user.skills:
            user.skills.remove(skill)
            db.add(user)
            db.commit()


# Expose service singleton
skill_service = SkillService()

