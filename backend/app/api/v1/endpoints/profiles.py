import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.services.profile_service import profile_service
from app.utils.exceptions import EntityNotFoundError, EntityAlreadyExistsError

router = APIRouter()


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user profile"
)
def create_profile(
    user_id: uuid.UUID,
    profile_in: ProfileCreate,
    db: Session = Depends(get_db)
) -> ProfileResponse:
    """
    Creates a professional profile page linked to the specified User ID.
    Enforces the unique one-to-one constraint.
    """
    try:
        return profile_service.create_profile(db, user_id=user_id, profile_in=profile_in)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(
    "/{user_id}",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve user profile by User ID"
)
def get_profile(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> ProfileResponse:
    """
    Retrieves the profile details of the user matching the given ID.
    """
    try:
        return profile_service.get_profile(db, user_id=user_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{user_id}",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile"
)
def update_profile(
    user_id: uuid.UUID,
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db)
) -> ProfileResponse:
    """
    Updates details on a user's professional profile.
    """
    try:
        return profile_service.update_profile(db, user_id=user_id, profile_in=profile_in)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
