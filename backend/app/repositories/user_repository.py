from typing import Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository


from app.core.security import get_password_hash


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    User repository handling database operations for the User entity.
    """

    def __init__(self) -> None:
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Retrieve a user record matching a specific email address.
        """
        query = select(self.model).where(self.model.email == email)
        return db.scalars(query).first()

    def create_user(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new User.
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            is_active=True,
            is_superuser=False,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_user(
        self, db: Session, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        """
        Update User attributes.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        return self.update(db, db_obj=db_obj, obj_in=update_data)


    def delete_user(self, db: Session, *, id: Any) -> Optional[User]:
        """
        Remove a user from the database.
        """
        return self.delete(db, id=id)


# Expose repository singleton instance
user_repository = UserRepository()
