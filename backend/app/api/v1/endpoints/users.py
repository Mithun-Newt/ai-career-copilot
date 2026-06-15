import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import user_service
from app.utils.exceptions import EntityNotFoundError, EntityAlreadyExistsError

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Registers a new account. Ensures the email address is unique.
    """
    try:
        return user_service.register_user(db, user_in=user_in)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve user details by ID"
)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Retrieves user account metadata.
    """
    try:
        return user_service.get_user(db, user_id=user_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user settings"
)
def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Modifies account configurations such as email address or password.
    """
    try:
        return user_service.update_user(db, user_id=user_id, user_in=user_in)
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
