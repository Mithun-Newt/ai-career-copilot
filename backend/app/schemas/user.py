from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.schemas.base import UUIDBase, TimestampBase


class UserBase(BaseModel):
    """
    Shared attributes for user schemas.
    """
    email: EmailStr = Field(
        ...,
        description="The primary email address of the user",
        examples=["user@example.com"]
    )


class UserCreate(UserBase):
    """
    Schema representing user registration payload.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="The raw password for the user account (minimum 8 characters)"
    )


class UserLogin(UserBase):
    """
    Schema representing login credentials payload.
    """
    password: str = Field(
        ...,
        description="The raw password credentials"
    )


class UserUpdate(BaseModel):
    """
    Schema representing attributes that can be updated on a user account.
    """
    email: Optional[EmailStr] = Field(
        None,
        description="Update the email address"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="Update/reset the user password"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Enable or disable the user account status"
    )


class UserResponse(UserBase, UUIDBase, TimestampBase):
    """
    Response schema returning safe user metadata to clients.
    Excludes sensitive attributes such as hashed_password.
    """
    model_config = ConfigDict(from_attributes=True)

    is_active: bool = Field(
        description="Flag indicating if the user account is active"
    )
    is_superuser: bool = Field(
        description="Flag indicating if the user is a superuser"
    )


class LoginRequest(UserBase):
    """
    Schema representing user login credentials payload.
    """
    password: str = Field(
        ...,
        description="The raw password credentials"
    )


class Token(BaseModel):
    """
    Schema representing a generated access token response.
    """
    access_token: str = Field(
        ...,
        description="The encoded JWT access token"
    )
    token_type: str = Field(
        "bearer",
        description="The token authorization scheme type"
    )


class TokenPayload(BaseModel):
    """
    Schema representing validated JWT access token claims.
    """
    sub: Optional[str] = Field(
        None,
        description="Subject of the access token (User ID)"
    )

