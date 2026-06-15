import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.ats_analysis import ATSAnalysisCreateRequest, ATSAnalysisResponse
from app.services.ats_service import ats_service
from app.models.user import User
from app.api.deps import get_current_user
from app.utils.exceptions import EntityNotFoundError, ForbiddenError

router = APIRouter()


@router.post(
    "/analyze",
    response_model=ATSAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze resume compatibility with job description"
)
def analyze_resume(
    req: ATSAnalysisCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ATSAnalysisResponse:
    """
    Evaluates candidate's resume content against a past job description using LLMs,
    returns calculated scores and improvement metrics, and stores the analytics.
    """
    try:
        return ats_service.analyze_resume_compatibility(
            db, user_id=current_user.id, resume_id=req.resume_id, job_description=req.job_description
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[ATSAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="List saved ATS evaluations"
)
def list_evaluations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ATSAnalysisResponse]:
    """
    Retrieve all historical ATS analyses completed by the current active user.
    """
    return ats_service.list_analyses_for_user(db, user_id=current_user.id)


@router.get(
    "/{analysis_id}",
    response_model=ATSAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Get ATS analysis details"
)
def get_evaluation(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ATSAnalysisResponse:
    """
    Query specific scores and metrics from a saved historical analysis.
    """
    try:
        return ats_service.get_analysis(db, user_id=current_user.id, analysis_id=analysis_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete ATS analysis record"
)
def delete_evaluation(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a saved analysis from the system logs.
    """
    try:
        ats_service.delete_analysis(db, user_id=current_user.id, analysis_id=analysis_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
