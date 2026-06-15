import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.ats_analysis import ATSAnalysis
from app.schemas.ats_analysis import ATSAnalysisCreateRequest
from app.repositories.base import BaseRepository


class ATSAnalysisRepository(BaseRepository[ATSAnalysis, ATSAnalysisCreateRequest, ATSAnalysisCreateRequest]):
    """
    ATSAnalysis repository handling database operations for AI-generated resume ATS evaluations.
    """

    def __init__(self) -> None:
        super().__init__(ATSAnalysis)

    def get_analyses_by_user(
        self, db: Session, user_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> List[ATSAnalysis]:
        """
        Query all saved ATS analyses matching a specific User ID.
        """
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(query).all())


# Expose repository singleton
ats_analysis_repository = ATSAnalysisRepository()
