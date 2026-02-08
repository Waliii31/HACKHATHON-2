"""
Chat API Endpoints for Phase III.

Implements the stateless chat API following the specification:
- POST /api/chat - Process a chat message
- GET /api/chat/conversations - List user's conversations
- GET /api/chat/conversations/{id} - Get conversation details
- DELETE /api/chat/conversations/{id} - Delete a conversation

CRITICAL: All endpoints are STATELESS - conversation history is read from
and written to the database on EVERY request. No in-memory state is stored.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import datetime
import json

from app.database.connection import get_db_session
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ToolUsage,
    ConversationListResponse,
    ConversationSummary,
    ConversationDetailResponse,
    MessageSchema,
)
from app.repositories import (
    create_conversation,
    get_conversation,
    get_user_conversations,
    delete_conversation,
    add_message,
    get_conversation_messages,
    get_conversation_history,
)
from app.agent.brain import process_message
from app.api.deps import get_current_user_id

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Process a chat message through the AI agent.
    
    This endpoint is STATELESS:
    1. Reads conversation history from database
    2. Stores user message in database
    3. Processes through AI agent (which may execute MCP tools)
    4. Stores AI response in database
    5. Returns the response
    
    If conversation_id is not provided, a new conversation is created.
    """
    try:
        # Step 1: Handle conversation (create or verify)
        if request.conversation_id:
            # Verify conversation exists and belongs to user
            conversation = await get_conversation(db, request.conversation_id, user_id)
            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found"
                )
            conversation_id = conversation["id"]
            
            # Load conversation history from DB (STATELESS)
            history = await get_conversation_history(db, conversation_id)
        else:
            # Create new conversation
            conversation_id, _ = await create_conversation(db, user_id)
            history = []
        
        # Step 2: Store user message in database (STATELESS)
        user_message_id = await add_message(
            db,
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        
        # Step 3: Process through AI agent
        response_text, tools_used = await process_message(
            user_message=request.message,
            user_id=user_id,
            history=history
        )
        
        # Step 4: Store AI response in database (STATELESS)
        ai_message_id = await add_message(
            db,
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            tools_used=tools_used if tools_used else None
        )
        
        # Commit all changes
        await db.commit()
        
        # Step 5: Return response
        return ChatResponse(
            conversation_id=conversation_id,
            message_id=ai_message_id,
            response=response_text,
            tools_used=[
                ToolUsage(
                    name=t["name"],
                    success=t["success"],
                    result=t.get("result"),
                    error=t.get("error")
                )
                for t in tools_used
            ],
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List user's conversations with pagination.
    
    Returns conversations sorted by last activity (newest first).
    Includes last message preview and message count.
    """
    conversations, total = await get_user_conversations(
        db, user_id, limit=limit, offset=offset
    )
    
    return ConversationListResponse(
        conversations=[
            ConversationSummary(
                id=c["id"],
                title=c["title"],
                last_message=c["last_message"][:100] if c["last_message"] else None,
                message_count=c["message_count"],
                created_at=c["created_at"],
                updated_at=c["updated_at"]
            )
            for c in conversations
        ],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_detail(
    conversation_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    before: Optional[UUID] = Query(default=None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get conversation details with messages.
    
    Supports pagination via 'before' parameter for loading older messages.
    """
    # Verify conversation exists and belongs to user
    conversation = await get_conversation(db, conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    messages = await get_conversation_messages(
        db, conversation_id, limit=limit + 1, before_id=before
    )
    
    # Check if there are more messages
    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]
    
    return ConversationDetailResponse(
        id=conversation["id"],
        title=conversation["title"],
        created_at=conversation["created_at"],
        messages=[
            MessageSchema(
                id=m["id"],
                role=m["role"],
                content=m["content"],
                tools_used=m["tools_used"],
                created_at=m["created_at"]
            )
            for m in messages
        ],
        has_more=has_more
    )


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation_endpoint(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a conversation and all its messages.
    
    Returns 204 No Content on success.
    """
    # Verify and delete
    deleted = await delete_conversation(db, conversation_id, user_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.commit()
    return None
