import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.skill import SkillCreate, SkillResponse, SkillGapResponse
from app.services.skill_service import skill_service
from app.repositories.skill_repository import skill_repository
from app.models.user import User
from app.api.deps import get_current_user
from app.ai.skill_gap_analyzer import skill_gap_analyzer
from app.utils.exceptions import EntityAlreadyExistsError

router = APIRouter()


@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new master skill tag"
)
def create_skill(
    skill_in: SkillCreate,
    db: Session = Depends(get_db)
) -> SkillResponse:
    """
    Registers a new master skill catalog entry.
    """
    try:
        return skill_service.create_skill(db, skill_in=skill_in)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[SkillResponse],
    status_code=status.HTTP_200_OK,
    summary="List current user's skills"
)
def get_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[SkillResponse]:
    """
    Queries current user's skills.
    """
    return skill_service.get_user_skills(db, user_id=current_user.id)


@router.get(
    "/gap-analysis/{target_role}",
    response_model=SkillGapResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze skill gaps against a target role"
)
def analyze_skill_gap(
    target_role: str,
    resume_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SkillGapResponse:
    """
    Computes matches, missing skills, and coverage metrics for the active authenticated user compared to target requirements.
    """
    parsed_resume = None
    raw_resume_text = None
    
    if resume_id:
        from app.services.resume_service import resume_service
        try:
            resume = resume_service.get_resume(db, resume_id=resume_id, user_id=current_user.id)
            user_skill_names = resume.parsed_data.get("skills", []) if resume.parsed_data else []
            parsed_resume = resume.parsed_data
            raw_resume_text = resume.raw_text
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or access denied."
            )
    else:
        # Load user active resume if it exists to get full context
        from app.models.resume import Resume
        active_resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_active == True).first()
        if active_resume:
            user_skill_names = active_resume.parsed_data.get("skills", []) if active_resume.parsed_data else []
            parsed_resume = active_resume.parsed_data
            raw_resume_text = active_resume.raw_text
            resume_id = active_resume.id
        else:
            user_skills = skill_service.get_user_skills(db, user_id=current_user.id)
            user_skill_names = [skill.name for skill in user_skills]
    
    # Perform gap analysis using 100% AI Career Intelligence Engine
    analysis_results = skill_gap_analyzer.analyze_gap(
        user_skills=user_skill_names,
        target_role=target_role,
        user_id=current_user.id,
        resume_id=resume_id,
        parsed_resume=parsed_resume,
        raw_resume_text=raw_resume_text
    )
    
    return SkillGapResponse(**analysis_results)


@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unassign a skill tag from user profile"
)
def delete_skill_from_profile(
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Removes a skill assignment from the authenticated user's profile database relations.
    """
    try:
        skill_service.remove_skill_from_user(db, user_id=current_user.id, skill_id=skill_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

