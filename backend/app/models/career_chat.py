import uuid
from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CareerChat(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    CareerChat model representing a conversation thread with the AI Career Coach.
    """
    __tablename__ = "career_chats"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign Key referencing the User this chat belongs to"
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Career Coaching Session",
        doc="The summary title of this chat session"
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(
        "User",
        back_populates="career_chats",
        doc="The User who owns this chat"
    )
    messages: Mapped[List["CareerMessage"]] = relationship(
        "CareerMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="CareerMessage.created_at",
        doc="The ordered list of messages in this chat"
    )
