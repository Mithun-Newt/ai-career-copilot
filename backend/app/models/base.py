import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Mixin adding timezone-aware created_at and updated_at columns using SQLAlchemy 2.0 mapped properties.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timezone-aware timestamp indicating when the record was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timezone-aware timestamp indicating when the record was last updated"
    )


class UUIDPrimaryKeyMixin:
    """
    Mixin adding a UUID primary key using PostgreSQL-specific UUID type or generic UUID.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique identifier for the record (UUIDv4)"
    )
