import uuid
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.base import UUIDBase, TimestampBase


class RoadmapTaskBase(BaseModel):
    """
    Shared attributes for roadmap task schemas.
    """
    title: str = Field(
        ...,
        max_length=255,
        description="The milestone task name or study item"
    )
    description: Optional[str] = Field(
        None,
        description="Actionable description or study links for the task"
    )
    sequence: int = Field(
        0,
        ge=0,
        description="The execution sequence index"
    )
    status: str = Field(
        "pending",
        max_length=50,
        description="The current completion state of the task (e.g. pending, in_progress, completed)"
    )


class RoadmapTaskCreate(RoadmapTaskBase):
    """
    Schema for creating a roadmap task.
    """
    roadmap_id: uuid.UUID = Field(
        ...,
        description="The ID of the parent career roadmap"
    )


class RoadmapTaskUpdate(BaseModel):
    """
    Schema for updating roadmap tasks.
    """
    title: Optional[str] = Field(
        None,
        max_length=255,
        description="Update task title"
    )
    description: Optional[str] = Field(
        None,
        description="Update task description text"
    )
    sequence: Optional[int] = Field(
        None,
        ge=0,
        description="Update execution order index"
    )
    status: Optional[str] = Field(
        None,
        max_length=50,
        description="Update completion status state"
    )


class RoadmapTaskResponse(RoadmapTaskBase, UUIDBase, TimestampBase):
    """
    Schema representing a roadmap task database response.
    """
    model_config = ConfigDict(from_attributes=True)

    roadmap_id: uuid.UUID = Field(
        description="The ID of the parent career roadmap"
    )
# Break import cycles by putting this down if needed
