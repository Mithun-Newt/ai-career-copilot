import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CareerMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    CareerMessage model representing a single message within a chat session.
    """
    __tablename__ = "career_messages"

    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_chats.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign Key referencing the CareerChat this message belongs to"
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="The role of the message sender (e.g. user, assistant)"
    )
    content: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
        doc="The text content of the message"
    )

    # --- Relationships ---
    chat: Mapped["CareerChat"] = relationship(
        "CareerChat",
        back_populates="messages",
        doc="The CareerChat associated with this message"
    )
