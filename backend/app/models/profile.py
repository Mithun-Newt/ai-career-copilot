import uuid
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Profile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Profile model containing detailed career metadata linked to a User account.
    """
    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Foreign Key referencing the owning User's ID"
    )
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="User's first name"
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="User's last name"
    )
    title: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        doc="Professional title (e.g. Senior Software Engineer)"
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        doc="Brief professional biography or summary statement"
    )
    experience_years: Mapped[Optional[int]] = mapped_column(
        Integer(),
        nullable=True,
        doc="Total years of professional experience"
    )

    # --- Relationships ---
    
    # One-to-One Back Reference: A profile links back to exactly one User.
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
        doc="The User account associated with this profile"
    )
