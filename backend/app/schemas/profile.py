import uuid
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.schemas.base import UUIDBase, TimestampBase


class ProfileBase(BaseModel):
    """
    Shared attributes for profile schemas.
    """
    first_name: Optional[str] = Field(
        None,
        max_length=100,
        description="First name of the user"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Last name of the user"
    )
    title: Optional[str] = Field(
        None,
        max_length=150,
        description="Professional title (e.g., Lead AI Engineer)"
    )
    bio: Optional[str] = Field(
        None,
        description="Professional bio or summary text"
    )
    experience_years: Optional[int] = Field(
        None,
        ge=0,
        le=80,
        description="Years of relevant professional experience"
    )


class ProfileCreate(ProfileBase):
    """
    Schema for creating a profile.
    """
    pass


class ProfileUpdate(ProfileBase):
    """
    Schema for updating professional profile elements.
    """
    pass


class ProfileResponse(ProfileBase, UUIDBase, TimestampBase):
    """
    Profile database response serializer.
    """
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(
        description="The ID of the user owning this profile"
    )
