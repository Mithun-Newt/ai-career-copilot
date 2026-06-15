from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.services.user_service import user_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Log in user to retrieve JWT access token"
)
def login(
    login_in: LoginRequest,
    db: Session = Depends(get_db)
) -> Token:
    
    user = user_service.authenticate(
        db,
        email=login_in.email,
        password=login_in.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(subject=user.id)

    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current authenticated user details"
)
def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Retrieves metadata settings representing the current active session user.
    """
    return current_user
