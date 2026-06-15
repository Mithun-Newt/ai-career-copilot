import uuid
from typing import Optional, Any, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.base import UUIDBase, TimestampBase




class ResumeBase(BaseModel):
    """
    Shared attributes for resume schemas.
    """
    filename: str = Field(
        ...,
        max_length=255,
        description="Name of the uploaded resume file"
    )
    file_path: str = Field(
        ...,
        max_length=512,
        description="Path or URL referencing the file storage location"
    )
    file_size: int = Field(
        ...,
        gt=0,
        description="Size of the uploaded file in bytes"
    )


class ResumeCreate(ResumeBase):
    """
    Schema for creating a resume record.
    """
    raw_text: Optional[str] = Field(
        None,
        description="Extracted raw text from the resume document"
    )
    parsed_data: Optional[Any] = Field(
        None,
        description="Parsed structured experience, education, and skills JSON representation"
    )


class ResumeResponse(ResumeBase, UUIDBase, TimestampBase):
    """
    Schema representing a saved Resume database record.
    """
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(
        description="The ID of the user who uploaded the resume"
    )
    raw_text: Optional[str] = Field(
        None,
        description="Extracted raw text content"
    )
    parsed_data: Optional[Any] = Field(
        None,
        description="Extracted structured JSON representation"
    )


class ResumeUploadResponse(ResumeResponse):
    """
    Schema returned after a successful resume upload.
    """
    pass


class ResumeListResponse(BaseModel):
    """
    Schema wrapping a list of resume records.
    """
    resumes: List[ResumeResponse] = Field(
        ...,
        description="List of user uploaded resume records"
    )


class ResumeParsedData(BaseModel):
    """
    Structured sections extracted from a resume PDF using the parsing engine.
    """
    name: str = Field(..., description="Extracted candidate name")
    email: str = Field(..., description="Extracted email address")
    phone: str = Field(..., description="Extracted contact phone number")
    skills: List[str] = Field(default=[], description="List of recognized skills")
    education: List[str] = Field(default=[], description="Timeline entries of education history")
    experience: List[str] = Field(default=[], description="Timeline entries of professional experience")


class ResumeParsedResponse(BaseModel):
    """
    API Response schema returning structured parsing outputs.
    """
    resume_id: uuid.UUID = Field(..., description="ID of the parsed resume document")
    parsed_data: ResumeParsedData = Field(..., description="Structured parsing results payload")


