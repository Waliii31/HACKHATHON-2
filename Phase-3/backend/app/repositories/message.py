"""
Message Repository for Phase III.

Handles database operations for messages.
Part of the stateless architecture - all operations read/write to DB.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import json


async def add_message(
    session: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str,
    tools_used: Optional[List[dict]] = None
) -> UUID:
    """
    Add a message to a conversation.
    
    Args:
        session: Database session
        conversation_id: UUID of the conversation
        role: Message role ('user', 'assistant', 'system')
        content: Message content
        tools_used: Optional list of tools used (for assistant messages)
        
    Returns:
        UUID of the created message
    """
    tools_json = json.dumps(tools_used) if tools_used else None
    
    query = text("""
        INSERT INTO messages (conversation_id, role, content, tools_used, created_at)
        VALUES (:conversation_id, :role, :content, :tools_used::jsonb, NOW())
        RETURNING id
    """)
    
    result = await session.execute(query, {
        "conversation_id": str(conversation_id),
        "role": role,
        "content": content,
        "tools_used": tools_json
    })
    
    row = result.fetchone()
    return row[0]


async def get_conversation_messages(
    session: AsyncSession,
    conversation_id: UUID,
    limit: int = 50,
    before_id: Optional[UUID] = None
) -> List[dict]:
    """
    Get messages for a conversation.
    
    Args:
        session: Database session
        conversation_id: UUID of the conversation
        limit: Max messages to return
        before_id: Get messages before this ID (for pagination)
        
    Returns:
        List of message dicts ordered by created_at ASC
    """
    if before_id:
        query = text("""
            SELECT id, role, content, tools_used, created_at
            FROM messages
            WHERE conversation_id = :conversation_id
              AND created_at < (SELECT created_at FROM messages WHERE id = :before_id)
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        params = {
            "conversation_id": str(conversation_id),
            "before_id": str(before_id),
            "limit": limit
        }
    else:
        query = text("""
            SELECT id, role, content, tools_used, created_at
            FROM messages
            WHERE conversation_id = :conversation_id
            ORDER BY created_at ASC
            LIMIT :limit
        """)
        params = {
            "conversation_id": str(conversation_id),
            "limit": limit
        }
    
    result = await session.execute(query, params)
    rows = result.fetchall()
    
    messages = []
    for row in rows:
        # Parse tools_used JSON
        tools_used = None
        if row[3]:
            try:
                tools_data = row[3] if isinstance(row[3], list) else json.loads(row[3])
                tools_used = [t for t in tools_data if isinstance(t, dict)]
            except (json.JSONDecodeError, TypeError):
                pass
        
        messages.append({
            "id": row[0],
            "role": row[1],
            "content": row[2],
            "tools_used": tools_used,
            "created_at": row[4]
        })
    
    return messages


async def get_conversation_history(
    session: AsyncSession,
    conversation_id: UUID,
    limit: int = 10
) -> List[dict]:
    """
    Get recent conversation history for AI context.
    
    Returns messages in chronological order (oldest first).
    
    Args:
        session: Database session
        conversation_id: UUID of the conversation
        limit: Max messages to include in context
        
    Returns:
        List of message dicts for AI context
    """
    query = text("""
        SELECT role, content
        FROM (
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = :conversation_id
            ORDER BY created_at DESC
            LIMIT :limit
        ) sub
        ORDER BY created_at ASC
    """)
    
    result = await session.execute(query, {
        "conversation_id": str(conversation_id),
        "limit": limit
    })
    
    rows = result.fetchall()
    return [{"role": row[0], "content": row[1]} for row in rows]


async def get_message_count(
    session: AsyncSession,
    conversation_id: UUID
) -> int:
    """
    Get the number of messages in a conversation.
    
    Args:
        session: Database session
        conversation_id: UUID of the conversation
        
    Returns:
        Message count
    """
    query = text("""
        SELECT COUNT(*) FROM messages WHERE conversation_id = :conversation_id
    """)
    
    result = await session.execute(query, {
        "conversation_id": str(conversation_id)
    })
    
    return result.scalar() or 0
