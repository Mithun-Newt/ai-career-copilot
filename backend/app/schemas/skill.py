from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.base import UUIDBase, TimestampBase


class SkillBase(BaseModel):
    """
    Shared attributes for skill schemas.
    """
    name: str = Field(
        ...,
        max_length=100,
        description="The name of the skill (e.g., Python, Docker)"
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Grouping categorization (e.g. Back-end, Cloud, DevOps)"
    )


class SkillCreate(SkillBase):
    """
    Schema representing a skill registration.
    """
    pass


class SkillResponse(SkillBase, UUIDBase, TimestampBase):
    """
    Schema for skill responses returned to clients.
    """
    model_config = ConfigDict(from_attributes=True)


from typing import List, Dict

class SkillGapResponse(BaseModel):
    """
    Validation schema detailing user skill match percentages and categorical gaps.
    """
    matched_skills: List[str] = Field(..., description="List of matching skills")
    missing_skills: List[str] = Field(..., description="List of missing skills required for the role")
    match_percentage: int = Field(..., description="Calculated match percentage score")
    user_skills_count: int = Field(..., description="Total count of skills possessed by the user")
    target_skills_count: int = Field(..., description="Total count of skills required for the target role")
    focus_areas: Dict[str, List[str]] = Field(
        ...,
        description="Missing skills grouped by their corresponding domain categories"
    )

