"""
Conversation Repository for Phase III.

Handles database operations for conversations.
Part of the stateless architecture - all operations read/write to DB.
"""
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_conversation(
    session: AsyncSession,
    user_id: str,
    title: Optional[str] = None
) -> Tuple[UUID, datetime]:
    """
    Create a new conversation.
    
    Args:
        session: Database session
        user_id: UUID of the user
        title: Optional conversation title
        
    Returns:
        Tuple of (conversation_id, created_at)
    """
    query = text("""
        INSERT INTO conversations (user_id, title, created_at, updated_at)
        VALUES (:user_id, :title, NOW(), NOW())
        RETURNING id, created_at
    """)
    
    result = await session.execute(query, {
        "user_id": user_id,
        "title": title
    })
    
    row = result.fetchone()
    return row[0], row[1]


async def get_conversation(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str
) -> Optional[dict]:
    """
    Get a conversation by ID, verifying user ownership.
    
    Args:
        session: Database session
        conversation_id: UUID of the conversation
        user_id: UUID of the user (for ownership check)
        
    Returns:
        Conversation dict or None if not found
    """
    query = text("""
        SELECT id, user_id, title, created_at, updated_at
        FROM conversations
        WHERE id = :conversation_id AND user_id = :user_id
    """)
    
    result = await session.execute(query, {
        "conversation_id": str(conversation_id),
        "user_id": user_id
    })
    
    row = result.fetchone()
    if row:
        return {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "created_at": row[3],
            "updated_at": row[4]
        }
    return None


async def get_user_conversations(
    session: AsyncSession,
    user_id: str,
    limit: int = 20,
    offset: int = 0
) -> Tuple[List[dict], int]:
    """
    Get user's conversations with pagination.
    
    Args:
        session: Database session
        user_id: UUID of the user
        limit: Max conversations to return
        offset: Pagination offset
        
    Returns:
        Tuple of (conversations list, total count)
    """
    # Get conversations with last message and count
    query = text("""
        SELECT 
            c.id,
            c.title,
            c.created_at,
            c.updated_at,
            (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message,
            (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
        FROM conversations c
        WHERE c.user_id = :user_id
        ORDER BY c.updated_at DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await session.execute(query, {
        "user_id": user_id,
        "limit": limit,
        "offset": offset
    })
    
    rows = result.fetchall()
    conversations = []
    for row in rows:
        conversations.append({
            "id": row[0],
            "title": row[1],
            "created_at": row[2],
            "updated_at": row[3],
            "last_message": row[4],
            "message_count": row[5] or 0
        })
    
    # Get total count
    count_query = text("""
        SELECT COUNT(*) FROM conversations WHERE user_id = :user_id
    """)
    count_result = await session.execute(count_query, {"user_id": user_id})
    total = count_result.scalar() or 0
    
    return conversations, total


async def update_conversation_title(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str,
    title: str
) -> bool:
    """
    Update a conversation's title.
    
    Args:
        session: Database session
        conversation_id: UUID of the conversation
        user_id: UUID of the user (for ownership check)
        title: New title
        
    Returns:
        True if updated, False otherwise
    """
    query = text("""
        UPDATE conversations
        SET title = :title, updated_at = NOW()
        WHERE id = :conversation_id AND user_id = :user_id
        RETURNING id
    """)
    
    result = await session.execute(query, {
        "conversation_id": str(conversation_id),
        "user_id": user_id,
        "title": title
    })
    
    return result.fetchone() is not None


async def delete_conversation(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str
) -> bool:
    """
    Delete a conversation and all its messages.
    
    Args:
        session: Database session
        conversation_id: UUID of the conversation
        user_id: UUID of the user (for ownership check)
        
    Returns:
        True if deleted, False otherwise
    """
    # Messages are deleted via cascade
    query = text("""
        DELETE FROM conversations
        WHERE id = :conversation_id AND user_id = :user_id
        RETURNING id
    """)
    
    result = await session.execute(query, {
        "conversation_id": str(conversation_id),
        "user_id": user_id
    })
    
    return result.fetchone() is not None
