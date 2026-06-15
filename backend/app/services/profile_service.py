import uuid
from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.repositories.profile_repository import profile_repository
from app.repositories.user_repository import user_repository
from app.utils.exceptions import EntityNotFoundError, EntityAlreadyExistsError


class ProfileService:
    """
    Business service coordinating operations for the User Profile entity.
    """

    def create_profile(
        self, db: Session, *, user_id: uuid.UUID, profile_in: ProfileCreate
    ) -> Profile:
        """
        Create and associate a professional Profile with a User ID.
        Raises EntityNotFoundError if user doesn't exist, or EntityAlreadyExistsError if a profile exists.
        """
        # Ensure the owner User exists
        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        # Ensure unique 1-to-1 profile constraint is preserved
        existing_profile = profile_repository.get_profile_by_user_id(db, user_id=user_id)
        if existing_profile:
            raise EntityAlreadyExistsError("Profile", "user_id", user_id)

        # Merge input schema with relationship requirements
        profile_data = profile_in.model_dump()
        profile_data["user_id"] = user_id
        
        # Instantiate raw Profile ORM model via generic repository creation context
        # We manually construct profile parameters
        db_profile = Profile(**profile_data)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile

    def get_profile(self, db: Session, *, user_id: uuid.UUID) -> Profile:
        """
        Get the profile associated with a User ID.
        Raises EntityNotFoundError if profile is missing.
        """
        profile = profile_repository.get_profile_by_user_id(db, user_id=user_id)
        if not profile:
            raise EntityNotFoundError("Profile", f"user_id: {user_id}")
        return profile

    def update_profile(
        self, db: Session, *, user_id: uuid.UUID, profile_in: ProfileUpdate
    ) -> Profile:
        """
        Update profile details for a User ID.
        """
        db_profile = self.get_profile(db, user_id=user_id)
        return profile_repository.update(db, db_obj=db_profile, obj_in=profile_in)


# Expose service singleton
profile_service = ProfileService()
