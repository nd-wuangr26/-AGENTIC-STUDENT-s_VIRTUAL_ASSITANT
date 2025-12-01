from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.core.schenma.chat_schema import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatHistoryResponse,
    ChatMessage,
    DeleteSessionRequest
)
from app.core.services.mysql_service import get_mysql_service, MySQLService
from app.api.auth import get_current_user
import uuid

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: ChatSessionCreate,
    current_user: dict = Depends(get_current_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Tạo chat session mới"""
    session_id = str(uuid.uuid4())
    user_id = current_user['user_id']
    
    success = await db.create_chat_session(
        session_id=session_id,
        user_id=user_id,
        title=session_data.title
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )
    
    # Get the created session
    sessions = await db.get_user_sessions(user_id)
    created_session = next((s for s in sessions if s['session_id'] == session_id), None)
    
    if not created_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session created but not found"
        )
    
    return ChatSessionResponse(**created_session)

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_sessions(
    current_user: dict = Depends(get_current_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Lấy tất cả chat sessions của user hiện tại"""
    user_id = current_user['user_id']
    sessions = await db.get_user_sessions(user_id)
    return [ChatSessionResponse(**session) for session in sessions]

@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_session_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Lấy lịch sử chat của một session"""
    user_id = current_user['user_id']
    
    # Check ownership
    has_access = await db.check_session_ownership(session_id, user_id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied"
        )
    
    # Get messages
    messages = await db.get_session_messages(session_id, user_id)
    
    # Get session info
    sessions = await db.get_user_sessions(user_id)
    session = next((s for s in sessions if s['session_id'] == session_id), None)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return ChatHistoryResponse(
        session_id=session_id,
        title=session['title'],
        messages=[ChatMessage(**msg) for msg in messages]
    )

@router.post("/messages", status_code=status.HTTP_201_CREATED)
async def save_message(
    message_data: ChatMessageCreate,
    current_user: dict = Depends(get_current_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Lưu một message vào session"""
    user_id = current_user['user_id']
    
    # Check ownership
    has_access = await db.check_session_ownership(message_data.session_id, user_id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied"
        )
    
    success = await db.save_chat_message(
        session_id=message_data.session_id,
        role=message_data.role,
        content=message_data.content
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message"
        )
    
    return {"success": True, "message": "Message saved successfully"}

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Xóa một chat session"""
    user_id = current_user['user_id']
    
    success = await db.delete_chat_session(session_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already deleted"
        )
    
    return {"success": True, "message": "Session deleted successfully"}

@router.delete("/sessions")
async def delete_all_sessions(
    current_user: dict = Depends(get_current_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Xóa tất cả chat sessions của user"""
    user_id = current_user['user_id']
    
    deleted_count = await db.delete_all_user_sessions(user_id)
    
    return {
        "success": True,
        "message": f"Deleted {deleted_count} sessions",
        "deleted_count": deleted_count
    }

@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: str,
    title: str,
    current_user: dict = Depends(get_current_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Cập nhật title của session"""
    user_id = current_user['user_id']
    
    success = await db.update_session_title(session_id, user_id, title)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"success": True, "message": "Title updated successfully"}
