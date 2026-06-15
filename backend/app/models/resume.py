import uuid
from typing import Optional, Any
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Resume(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Resume model storing parsed metadata, structured data, and file locations.
    """
    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign Key referencing the User who uploaded the resume"
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Original uploaded file name"
    )
    file_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Storage system location or key of the stored file (e.g. S3 key)"
    )
    file_size: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        doc="File size in bytes"
    )
    raw_text: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        doc="Raw text parsed directly from the PDF or document"
    )
    # JSONB is highly optimized in PostgreSQL for querying structured JSON documents
    parsed_data: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Structured JSON payload representing parsed experience, education, etc."
    )

    # --- Relationships ---
    
    # Many-to-One Back Reference: A resume is owned by exactly one User.
    user: Mapped["User"] = relationship(
        "User",
        back_populates="resumes",
        doc="The User who owns this resume"
    )
