import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ChatMessageCreate(BaseModel):
    message: str = Field(..., description="The user's chat message content")
    chat_id: Optional[uuid.UUID] = Field(None, description="The ID of the existing chat session, if continuing")


class ChatMessageResponse(BaseModel):
    response: str = Field(..., description="The AI Career Coach response message")
    chat_id: uuid.UUID = Field(..., description="The ID of the chat session")


class ChatMessageDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    created_at: datetime


class ChatSessionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime
    messages: List[ChatMessageDetail] = []
