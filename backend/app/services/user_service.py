import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import user_repository
from app.utils.exceptions import EntityNotFoundError, EntityAlreadyExistsError


from app.core.security import verify_password


class UserService:
    """
    Business service coordinating operations for the User entity.
    """

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user by verifying their email and password credentials.
        Returns the User object if successful, else None.
        """
        user = user_repository.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


    def register_user(self, db: Session, *, user_in: UserCreate) -> User:
        """
        Register a new user account.
        Checks if the email is already registered, raising an error if so.
        """
        existing_user = user_repository.get_by_email(db, email=user_in.email)
        if existing_user:
            raise EntityAlreadyExistsError("User", "email", user_in.email)
        
        return user_repository.create_user(db, obj_in=user_in)

    def get_user(self, db: Session, *, user_id: uuid.UUID) -> User:
        """
        Retrieve a user record by ID. Raises EntityNotFoundError if missing.
        """
        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        return user

    def update_user(self, db: Session, *, user_id: uuid.UUID, user_in: UserUpdate) -> User:
        """
        Update user account settings.
        """
        db_user = self.get_user(db, user_id=user_id)
        
        # Check if updating email leads to a conflict
        if user_in.email and user_in.email != db_user.email:
            existing_user = user_repository.get_by_email(db, email=user_in.email)
            if existing_user:
                raise EntityAlreadyExistsError("User", "email", user_in.email)

        return user_repository.update_user(db, db_obj=db_user, obj_in=user_in)


# Expose service singleton
user_service = UserService()
