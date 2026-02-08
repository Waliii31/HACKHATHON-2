# Chat API Specification

## Overview

This document specifies the stateless Chat API endpoint that serves as the primary interface between the frontend ChatKit and the AI Agent backend.

## Stateless Architecture Principles

The Chat API follows a stateless design:

1. **No Server-Side Sessions**: Each request is independent
2. **Database-Backed Context**: Conversation history retrieved from PostgreSQL
3. **Idempotent Operations**: Same input produces same output (given same DB state)
4. **Horizontal Scalability**: Any server instance can handle any request

## Endpoints

### POST /api/chat

**Description:** Process a user message through the AI agent and return the response.

**Authentication:** Required (Bearer JWT token)

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Add buy groceries to my list",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User's message (1-2000 characters) |
| conversation_id | UUID | No | Existing conversation ID. If not provided, creates new conversation |

**Response (Success - 200):**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "response": "I've added 'buy groceries' to your task list! 🛒 Is there anything else you'd like me to help with?",
  "tools_used": [
    {
      "name": "add_task",
      "success": true,
      "result": {
        "task_id": "770e8400-e29b-41d4-a716-446655440002",
        "title": "buy groceries"
      }
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | UUID | ID of the conversation (new or existing) |
| message_id | UUID | ID of the AI response message |
| response | string | AI-generated response text |
| tools_used | array | List of MCP tools executed during processing |
| timestamp | ISO 8601 | Response timestamp |

**Error Responses:**

*400 Bad Request:*
```json
{
  "error": "Message is required and must be between 1 and 2000 characters",
  "error_code": "VALIDATION_ERROR"
}
```

*401 Unauthorized:*
```json
{
  "error": "Authentication required",
  "error_code": "UNAUTHORIZED"
}
```

*404 Not Found:*
```json
{
  "error": "Conversation not found",
  "error_code": "CONVERSATION_NOT_FOUND"
}
```

*429 Too Many Requests:*
```json
{
  "error": "Rate limit exceeded. Please wait before sending another message.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

*500 Internal Server Error:*
```json
{
  "error": "An unexpected error occurred. Please try again.",
  "error_code": "INTERNAL_ERROR"
}
```

---

### GET /api/chat/conversations

**Description:** List user's conversations

**Authentication:** Required (Bearer JWT token)

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Max conversations to return (default: 20, max: 100) |
| offset | integer | No | Pagination offset (default: 0) |

**Response (Success - 200):**
```json
{
  "conversations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Task Management",
      "last_message": "I've added 'buy groceries' to your list!",
      "message_count": 12,
      "created_at": "2024-01-15T09:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 5,
  "limit": 20,
  "offset": 0
}
```

---

### GET /api/chat/conversations/{conversation_id}

**Description:** Get conversation details with messages

**Authentication:** Required (Bearer JWT token)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| conversation_id | UUID | Conversation ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Max messages to return (default: 50) |
| before | UUID | No | Get messages before this message ID (for pagination) |

**Response (Success - 200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Task Management",
  "created_at": "2024-01-15T09:00:00Z",
  "messages": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "role": "user",
      "content": "Add buy groceries to my list",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "role": "assistant",
      "content": "I've added 'buy groceries' to your task list! 🛒",
      "tools_used": ["add_task"],
      "created_at": "2024-01-15T10:30:01Z"
    }
  ],
  "has_more": false
}
```

---

### DELETE /api/chat/conversations/{conversation_id}

**Description:** Delete a conversation and all its messages

**Authentication:** Required (Bearer JWT token)

**Response (Success - 204):** No Content

---

## Request Processing Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    POST /api/chat                                 │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  1. AUTHENTICATION                                                │
│     ├── Extract JWT from Authorization header                     │
│     ├── Verify JWT signature and expiration                       │
│     ├── Extract user_id from claims                               │
│     └── Reject if invalid (401 Unauthorized)                      │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  2. VALIDATION                                                    │
│     ├── Validate message (1-2000 chars, not empty)                │
│     ├── Validate conversation_id format (if provided)            │
│     └── Reject if invalid (400 Bad Request)                       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  3. RATE LIMITING                                                 │
│     ├── Check user's request count in sliding window              │
│     ├── Limit: 60 requests per minute per user                    │
│     └── Reject if exceeded (429 Too Many Requests)                │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  4. CONVERSATION HANDLING                                         │
│     ├── If conversation_id provided:                              │
│     │   ├── Verify conversation exists and belongs to user        │
│     │   └── Load conversation history from PostgreSQL             │
│     └── If not provided:                                          │
│         └── Create new conversation record                        │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  5. SAVE USER MESSAGE                                             │
│     ├── Create message record in PostgreSQL                       │
│     ├── role: "user"                                              │
│     └── content: user's message                                   │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  6. AI AGENT PROCESSING                                           │
│     ├── Build context from conversation history                   │
│     ├── Send to OpenAI Agents SDK                                 │
│     ├── Agent selects and executes MCP tools                      │
│     └── Generate natural language response                        │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  7. SAVE AI RESPONSE                                              │
│     ├── Create message record in PostgreSQL                       │
│     ├── role: "assistant"                                         │
│     ├── content: AI response                                      │
│     └── tools_used: list of executed tools                        │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  8. RETURN RESPONSE                                               │
│     └── Return JSON with conversation_id, response, tools_used    │
└──────────────────────────────────────────────────────────────────┘
```

## Implementation Example

```python
# backend/app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.deps import get_current_user
from app.agent.brain import process_message
from app.database.session import get_db_session
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db_session)
):
    """
    Stateless chat endpoint.
    
    - Loads conversation history from database
    - Processes message through AI agent
    - Saves messages to database
    - Returns AI response
    """
    user_id = current_user.id
    
    # Handle conversation
    if request.conversation_id:
        conversation = await get_conversation(
            db, request.conversation_id, user_id
        )
        if not conversation:
            raise HTTPException(404, "Conversation not found")
        history = await get_conversation_history(db, conversation.id)
    else:
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        await db.flush()
        history = []
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.flush()
    
    # Process through AI agent
    response_text, tools_used = await process_message(
        user_message=request.message,
        user_id=str(user_id),
        history=history
    )
    
    # Save AI response
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        tools_used=tools_used
    )
    db.add(ai_message)
    await db.commit()
    
    return ChatResponse(
        conversation_id=conversation.id,
        message_id=ai_message.id,
        response=response_text,
        tools_used=tools_used,
        timestamp=ai_message.created_at
    )
```

## Schemas

```python
# backend/app/schemas/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None

class ToolUsage(BaseModel):
    name: str
    success: bool
    result: Optional[dict] = None

class ChatResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    response: str
    tools_used: List[ToolUsage]
    timestamp: datetime

class ConversationSummary(BaseModel):
    id: UUID
    title: Optional[str]
    last_message: Optional[str]
    message_count: int
    created_at: datetime
    updated_at: datetime

class MessageSchema(BaseModel):
    id: UUID
    role: str  # "user" | "assistant" | "system"
    content: str
    tools_used: Optional[List[str]] = None
    created_at: datetime
```

## Rate Limiting Configuration

```python
# Rate limiting settings
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 60,
    "requests_per_hour": 500,
    "burst_limit": 10  # Max requests in 10-second window
}
```

## Context Window Management

To keep API costs manageable and ensure relevant context:

```python
# Maximum messages to include in context
MAX_CONTEXT_MESSAGES = 10

# Maximum tokens for context
MAX_CONTEXT_TOKENS = 4000

def build_context(history: List[Message]) -> List[dict]:
    """Build context from conversation history."""
    # Take last N messages
    recent_messages = history[-MAX_CONTEXT_MESSAGES:]
    
    # Format for AI agent
    return [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in recent_messages
    ]
```
