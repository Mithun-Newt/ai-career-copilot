import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.base import UUIDBase, TimestampBase
from app.schemas.roadmap_task import RoadmapTaskResponse


class RoadmapBase(BaseModel):
    """
    Shared attributes for roadmap schemas.
    """
    title: str = Field(
        ...,
        max_length=255,
        description="The header title of the roadmap pathway"
    )
    description: Optional[str] = Field(
        None,
        description="Overview details of the learning pathway and milestone goal"
    )
    target_role: str = Field(
        ...,
        max_length=150,
        description="The targeted career role for this training track"
    )


class RoadmapCreate(RoadmapBase):
    """
    Schema for creating a roadmap record.
    """
    pass


class MilestoneTaskResponse(BaseModel):
    id: uuid.UUID = Field(description="The unique identifier for the task")
    title: str = Field(description="The task name or study item")
    description: Optional[str] = Field(None, description="Actionable guidelines or details")
    sequence: int = Field(0, description="The execution sequence index")
    status: str = Field("pending", description="Current status of the task")


class MilestoneResponse(BaseModel):
    title: str = Field(description="The title of the milestone")
    description: str = Field(description="Overview of the milestone focus")
    tasks: List[MilestoneTaskResponse] = Field(default=[], description="List of tasks in this milestone")


class RoadmapResponse(RoadmapBase, UUIDBase, TimestampBase):
    """
    Schema representing a roadmap database record.
    Supports resolving nested roadmap tasks automatically.
    """
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(
        description="The ID of the user owning this career roadmap"
    )
    tasks: List[RoadmapTaskResponse] = Field(
        default=[],
        description="List of ordered tasks associated with this career roadmap"
    )
    milestones: List[MilestoneResponse] = Field(
        default=[],
        description="Grouped milestone representation of the tasks"
    )
    progress_percentage: int = Field(
        default=0,
        description="Calculated completion percentage of the roadmap tasks"
    )


class RoadmapGenerateRequest(BaseModel):
    """
    Validation schema requesting career roadmap generation.
    """
    resume_id: uuid.UUID = Field(
        ...,
        description="The ID of the user's uploaded resume PDF to base generation on"
    )
    target_role: str = Field(
        ...,
        max_length=150,
        description="The desired target role (e.g. AI Engineer, Backend Engineer)"
    )


class RoadmapGenerateResponse(BaseModel):
    """
    Response schema returning generated career roadmap outcomes.
    """
    roadmap_id: uuid.UUID = Field(
        ...,
        description="The unique identifier representing the generated Roadmap"
    )
    title: str = Field(
        ...,
        description="The generated title of the roadmap track"
    )
    description: str = Field(
        ...,
        description="Detailed description overview of the roadmap pathway goals"
    )
    tasks: List[RoadmapTaskResponse] = Field(
        ...,
        description="The ordered milestone tasks mapped inside the learning pathway"
    )
    milestones: List[MilestoneResponse] = Field(
        default=[],
        description="Grouped milestone representation of the tasks"
    )
    progress_percentage: int = Field(
        default=0,
        description="Calculated completion percentage of the roadmap tasks"
    )
