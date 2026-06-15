import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.career_chat import ChatMessageCreate, ChatMessageResponse, ChatSessionDetail
from app.services.career_coach_service import career_coach_service
from app.models.user import User
from app.api.deps import get_current_user
from app.utils.exceptions import EntityNotFoundError, ForbiddenError

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Interact with AI Career Coach"
)
def chat_with_coach(
    req: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ChatMessageResponse:
    """
    Submits a message to the Career Coach AI. Analyzes candidate's dynamic profile
    context and saved roadmaps to generate customized suggestions.
    """
    try:
        res = career_coach_service.chat_with_coach(
            db, user_id=current_user.id, message=req.message, chat_id=req.chat_id
        )
        return ChatMessageResponse(
            response=res["response"],
            chat_id=res["chat_id"]
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
    "/chat",
    response_model=List[ChatSessionDetail],
    status_code=status.HTTP_200_OK,
    summary="List saved career coaching sessions"
)
def list_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ChatSessionDetail]:
    """
    List all saved coaching sessions of the authenticated user.
    """
    return career_coach_service.get_user_chats(db, user_id=current_user.id)


@router.get(
    "/chat/{chat_id}",
    response_model=ChatSessionDetail,
    status_code=status.HTTP_200_OK,
    summary="Retrieve session history details"
)
def get_chat(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ChatSessionDetail:
    """
    Query historical conversational details for a specific coaching thread.
    """
    try:
        return career_coach_service.get_chat_session(db, user_id=current_user.id, chat_id=chat_id)
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
    "/chat/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a coaching chat session"
)
def delete_chat(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a career coaching session and all associated messages.
    """
    try:
        career_coach_service.delete_chat_session(db, user_id=current_user.id, chat_id=chat_id)
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
    "/debug",
    status_code=status.HTTP_200_OK,
    summary="Retrieve diagnostic status for AI Career Coach"
)
def debug_career_coach(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Exposes diagnostics concerning LLM credentials setup and database context viability.
    """
    from app.core.config import settings
    import os
    from app.ai.roadmap_generator import get_llm
    from app.models.resume import Resume
    from app.models.roadmap import Roadmap
    from app.models.career_chat import CareerChat
    
    # 1. Resolve LLM provider
    provider = "none"
    if settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        provider = "google"
    elif settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"):
        provider = "openai"
    elif settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY"):
        provider = "groq"
        
    llm_available = get_llm() is not None
    
    # 2. Database checks
    resume_loaded = db.query(Resume).filter(Resume.user_id == current_user.id).first() is not None
    roadmap_loaded = db.query(Roadmap).filter(Roadmap.user_id == current_user.id).first() is not None
    memory_loaded = db.query(CareerChat).filter(CareerChat.user_id == current_user.id).first() is not None
    
    return {
        "llm_available": llm_available,
        "provider": provider,
        "resume_loaded": resume_loaded,
        "roadmap_loaded": roadmap_loaded,
        "memory_loaded": memory_loaded
    }
