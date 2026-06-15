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
from app.ai.role_skill_mapper import role_skill_mapper
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
    summary="List all master skill tags"
)
def get_skills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[SkillResponse]:
    """
    Queries catalog skills list with pagination limit settings.
    """
    # Direct repository delegation for simple reads is standard or we can wrap inside a service read helper.
    # In this phase, query the repository.
    return skill_repository.get_all(db, skip=skip, limit=limit)


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
    # 1. Fetch user skills (or resume-specific skills)
    if resume_id:
        from app.services.resume_service import resume_service
        try:
            resume = resume_service.get_resume(db, resume_id=resume_id, user_id=current_user.id)
            user_skill_names = resume.parsed_data.get("skills", []) if resume.parsed_data else []
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or access denied."
            )
    else:
        user_skills = skill_service.get_user_skills(db, user_id=current_user.id)
        user_skill_names = [skill.name for skill in user_skills]
    
    # 2. Map target role to skills list
    target_skills = role_skill_mapper.get_skills_for_role(target_role)
    
    # 3. Perform gap analysis
    analysis_results = skill_gap_analyzer.analyze_gap(user_skill_names, target_skills)
    
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

