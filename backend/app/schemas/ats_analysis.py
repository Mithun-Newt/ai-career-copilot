import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ATSAnalysisCreateRequest(BaseModel):
    resume_id: uuid.UUID = Field(..., description="The ID of the candidate's resume to evaluate")
    job_description: str = Field(..., description="The text content representing the target job description")


class ATSAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    ats_score: int
    match_percentage: int
    missing_skills: List[str]
    missing_keywords: List[str]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: dict
    created_at: datetime
