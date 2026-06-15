from app.schemas.base import UUIDBase, TimestampBase
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserResponse, LoginRequest, Token, TokenPayload
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeUploadResponse, ResumeListResponse, ResumeParsedData, ResumeParsedResponse
from app.schemas.skill import SkillCreate, SkillResponse, SkillGapResponse
from app.schemas.roadmap import RoadmapCreate, RoadmapResponse, RoadmapGenerateRequest, RoadmapGenerateResponse
from app.schemas.roadmap_task import RoadmapTaskCreate, RoadmapTaskUpdate, RoadmapTaskResponse
from app.schemas.career_chat import ChatMessageCreate, ChatMessageResponse, ChatMessageDetail, ChatSessionDetail
from app.schemas.ats_analysis import ATSAnalysisCreateRequest, ATSAnalysisResponse

__all__ = [
    "UUIDBase",
    "TimestampBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "Token",
    "TokenPayload",
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "ResumeCreate",
    "ResumeResponse",
    "ResumeUploadResponse",
    "ResumeListResponse",
    "ResumeParsedData",
    "ResumeParsedResponse",
    "SkillCreate",
    "SkillResponse",
    "SkillGapResponse",
    "RoadmapCreate",
    "RoadmapResponse",
    "RoadmapGenerateRequest",
    "RoadmapGenerateResponse",
    "RoadmapTaskCreate",
    "RoadmapTaskUpdate",
    "RoadmapTaskResponse",
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatMessageDetail",
    "ChatSessionDetail",
    "ATSAnalysisCreateRequest",
    "ATSAnalysisResponse",
]
