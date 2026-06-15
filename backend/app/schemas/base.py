import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class UUIDBase(BaseModel):
    """
    Base schema containing a UUID primary key.
    """
    id: uuid.UUID = Field(
        description="The unique identifier (UUIDv4) for the resource"
    )


class TimestampBase(BaseModel):
    """
    Base schema containing timezone-aware created and updated timestamps.
    """
    created_at: datetime = Field(
        description="The date and time the resource was created (timezone-aware)"
    )
    updated_at: datetime = Field(
        description="The date and time the resource was last updated (timezone-aware)"
    )
