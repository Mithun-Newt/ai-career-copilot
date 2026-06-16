import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.resume import ResumeResponse, ResumeUploadResponse, ResumeListResponse, ResumeParsedResponse
from app.services.resume_service import resume_service
from app.models.user import User
from app.api.deps import get_current_user
from app.utils.exceptions import EntityNotFoundError, ForbiddenError, DomainException

router = APIRouter()


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and store a resume file"
)
def upload_resume(
    file: UploadFile = File(..., description="The PDF or DOCX file to upload"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResumeUploadResponse:
    """
    Accepts resume PDF/DOCX file uploads, writes them to disk storage, and logs metadata.
    """
    try:
        return resume_service.upload_resume(db, user_id=current_user.id, file=file)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/my-resumes",
    response_model=ResumeListResponse,
    status_code=status.HTTP_200_OK,
    summary="List current user's uploaded resumes"
)
def get_my_resumes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResumeListResponse:
    """
    Retrieves all resume files uploaded by the authenticated user.
    """
    try:
        resumes = resume_service.get_user_resumes(
            db, user_id=current_user.id, skip=skip, limit=limit
        )
        return ResumeListResponse(resumes=resumes)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve single resume details"
)
def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResumeResponse:
    """
    Retrieves the details of a single resume file. Enforces ownership verification.
    """
    try:
        return resume_service.get_resume(db, resume_id=resume_id, user_id=current_user.id)
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
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an uploaded resume"
)
def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Deletes the database metadata record and local file storage associated with the given ID.
    Enforces ownership validation.
    """
    try:
        resume_service.delete_resume(db, resume_id=resume_id, user_id=current_user.id)
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


@router.put(
    "/{resume_id}/activate",
    response_model=ResumeResponse,
    status_code=status.HTTP_200_OK,
    summary="Set an uploaded resume as the active resume"
)
def activate_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResumeResponse:
    """
    Sets the specified resume as active, syncing profile parameters and skills dynamically.
    """
    try:
        return resume_service.activate_resume(db, resume_id=resume_id, user_id=current_user.id)
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
    "/{resume_id}/parsed",
    response_model=ResumeParsedResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve parsed resume JSON content"
)
def get_parsed_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResumeParsedResponse:
    """
    Returns the parsed JSON data of the resume. Enforces ownership validation checks.
    """
    try:
        resume = resume_service.get_resume(db, resume_id=resume_id, user_id=current_user.id)
        if resume.parsed_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume parsing content is not available for this record."
            )
        return ResumeParsedResponse(resume_id=resume.id, parsed_data=resume.parsed_data)
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

