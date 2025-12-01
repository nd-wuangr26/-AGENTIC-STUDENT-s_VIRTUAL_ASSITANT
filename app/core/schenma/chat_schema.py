from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

class ChatMessage(BaseModel):
    """Schema cho một tin nhắn chat"""
    role: Literal['user', 'assistant']
    content: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    """Schema để tạo session mới"""
    title: Optional[str] = "New Chat"

class ChatSessionResponse(BaseModel):
    """Schema cho response session"""
    session_id: str
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    """Schema để tạo message mới"""
    session_id: str
    role: Literal['user', 'assistant']
    content: str

class ChatHistoryResponse(BaseModel):
    """Schema cho lịch sử chat của một session"""
    session_id: str
    title: str
    messages: List[ChatMessage]

class DeleteSessionRequest(BaseModel):
    """Schema để xóa session"""
    session_id: str
