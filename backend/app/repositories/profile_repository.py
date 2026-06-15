import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[Profile, ProfileCreate, ProfileUpdate]):
    """
    Profile repository handling database operations for the User Profile entity.
    """

    def __init__(self) -> None:
        super().__init__(Profile)

    def get_profile_by_user_id(self, db: Session, user_id: uuid.UUID) -> Optional[Profile]:
        """
        Retrieve a profile record associated with a specific User ID.
        """
        query = select(self.model).where(self.model.user_id == user_id)
        return db.scalars(query).first()


# Expose repository singleton instance
profile_repository = ProfileRepository()
