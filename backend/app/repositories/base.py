from typing import Any, Generic, List, Optional, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic Base Repository implementing shared CRUD queries using SQLAlchemy 2.0 conventions.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def get_by_id(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Query a single database record by primary key ID.
        """
        return db.get(self.model, id)

    def get_all(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Query list records with pagination options.
        """
        query = select(self.model).offset(skip).limit(limit)
        return list(db.scalars(query).all())

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Persist a new database entry using Pydantic schema validation.
        """
        # Convert schema fields to dictionary
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        Update an existing database entry.
        """
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """
        Delete a database record by primary key ID.
        """
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
