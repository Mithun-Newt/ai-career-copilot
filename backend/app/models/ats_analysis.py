import uuid
from sqlalchemy import Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ATSAnalysis(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    ATSAnalysis model representing the AI-generated ATS compatibility metrics
    and resume enhancement suggestions for a target job description.
    """
    __tablename__ = "ats_analyses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign Key referencing the User this analysis belongs to"
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign Key referencing the Resume used for this analysis"
    )
    ats_score: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=0,
        doc="Calculated ATS compatibility score (0-100)"
    )
    match_percentage: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=0,
        doc="Calculated job match percentage index (0-100)"
    )
    missing_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="List of missing skills required by the job description"
    )
    missing_keywords: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="List of missing key terms or keywords from the job description"
    )
    strengths: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Strong matching skills or points in the candidate's resume"
    )
    weaknesses: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Areas where the resume falls short of the job expectations"
    )
    recommendations: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Actionable suggestions, recommended projects, and interview topics"
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(
        "User",
        back_populates="ats_analyses",
        doc="The User who owns this analysis"
    )
    resume: Mapped["Resume"] = relationship(
        "Resume",
        doc="The Resume evaluated in this analysis"
    )
