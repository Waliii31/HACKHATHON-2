# Phase III: Implementation Plan

## Overview

This document provides the technical implementation plan for transforming the Phase II Todo Web Application into an AI-powered Chatbot. It covers database schema, API layer, MCP server architecture, and frontend integration.

---

## 1. Database Schema

### 1.1 New Tables

#### Conversation Table

Stores chat conversation sessions for each user.

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
```

**SQLModel Definition:**
```python
# backend/app/models/conversation.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

#### Message Table

Stores individual messages within conversations.

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tools_used JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

**SQLModel Definition:**
```python
# backend/app/models/message.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import json

if TYPE_CHECKING:
    from .conversation import Conversation

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: str = Field(nullable=False)  # 'user', 'assistant', 'system'
    content: str = Field(nullable=False)
    tools_used: Optional[str] = Field(default=None)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    
    def get_tools_list(self) -> list:
        if self.tools_used:
            return json.loads(self.tools_used)
        return []
```

### 1.2 Entity Relationship Diagram

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│      user       │         │  conversations  │         │    messages     │
│  (from P2)      │         │    (NEW P3)     │         │    (NEW P3)     │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ id (PK)         │◄───┐    │ id (PK)         │◄───┐    │ id (PK)         │
│ email           │    │    │ user_id (FK)────┼────┘    │ conversation_id │
│ name            │    │    │ title           │         │   (FK)──────────┼───┘
│ ...             │    │    │ created_at      │         │ role            │
└─────────────────┘    │    │ updated_at      │         │ content         │
                       │    └─────────────────┘         │ tools_used      │
┌─────────────────┐    │                                │ created_at      │
│     tasks       │    │                                └─────────────────┘
│  (from P2)      │    │
├─────────────────┤    │
│ id (PK)         │    │
│ user_id (FK)────┼────┘
│ title           │
│ status          │
│ ...             │
└─────────────────┘
```

---

## 2. API Layer

### 2.1 POST /api/chat - Stateless Chat Endpoint

**Purpose:** Process user messages through the AI agent and return responses.

**Request/Response:**
```
POST /api/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
  "message": "Add buy groceries to my list",
  "conversation_id": "uuid-v4"  // optional
}

Response:
{
  "conversation_id": "uuid-v4",
  "message_id": "uuid-v4",
  "response": "I've added 'buy groceries' to your list! 📝",
  "tools_used": [{"name": "add_task", "success": true}],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2.2 Logic Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         POST /api/chat                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: AUTHENTICATION                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • Extract JWT from Authorization header                            │    │
│  │  • Verify token signature and expiration                            │    │
│  │  • Extract user_id from token claims                                │    │
│  │  • Return 401 if invalid                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: FETCH CONVERSATION HISTORY                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  IF conversation_id provided:                                       │    │
│  │    • Verify conversation belongs to user                            │    │
│  │    • Load last N messages from database                             │    │
│  │  ELSE:                                                              │    │
│  │    • Create new conversation record                                 │    │
│  │    • history = []                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: STORE USER MESSAGE                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • Create Message record:                                           │    │
│  │    - conversation_id = current conversation                         │    │
│  │    - role = "user"                                                  │    │
│  │    - content = request.message                                      │    │
│  │  • Save to database                                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: RUN AI AGENT (MCP)                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • Build context from conversation history                          │    │
│  │  • Call OpenAI Agents SDK with:                                     │    │
│  │    - System prompt                                                  │    │
│  │    - Conversation history                                           │    │
│  │    - User message                                                   │    │
│  │    - Available MCP tools                                            │    │
│  │  • Agent selects and executes MCP tools as needed                   │    │
│  │  • Agent generates natural language response                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: STORE AI RESPONSE                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • Create Message record:                                           │    │
│  │    - conversation_id = current conversation                         │    │
│  │    - role = "assistant"                                             │    │
│  │    - content = agent response                                       │    │
│  │    - tools_used = JSON of executed tools                            │    │
│  │  • Save to database                                                 │    │
│  │  • Update conversation.updated_at                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: RETURN RESPONSE                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • Return JSON:                                                     │    │
│  │    - conversation_id                                                │    │
│  │    - message_id (of AI response)                                    │    │
│  │    - response (AI text)                                             │    │
│  │    - tools_used                                                     │    │
│  │    - timestamp                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Implementation Code Structure

```python
# backend/app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.deps import get_current_user, get_db
from app.agent.brain import process_message
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Step 1: Auth handled by dependency
    user_id = current_user.id
    
    # Step 2: Fetch/Create Conversation
    if request.conversation_id:
        conversation = await get_conversation(db, request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(404, "Conversation not found")
        history = await get_messages(db, conversation.id, limit=10)
    else:
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        await db.flush()
        history = []
    
    # Step 3: Store User Message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_msg)
    await db.flush()
    
    # Step 4: Run Agent (MCP)
    response_text, tools_used = await process_message(
        user_message=request.message,
        user_id=str(user_id),
        history=[{"role": m.role, "content": m.content} for m in history]
    )
    
    # Step 5: Store AI Response
    ai_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        tools_used=json.dumps(tools_used) if tools_used else None
    )
    db.add(ai_msg)
    conversation.updated_at = datetime.utcnow()
    await db.commit()
    
    # Step 6: Return Response
    return ChatResponse(
        conversation_id=conversation.id,
        message_id=ai_msg.id,
        response=response_text,
        tools_used=tools_used,
        timestamp=ai_msg.created_at
    )
```

---

## 3. MCP Server Architecture

### 3.1 MCP Server Structure

```
backend/app/mcp/
├── __init__.py
├── server.py           # MCP Server initialization
├── context.py          # Tool execution context
└── tools/
    ├── __init__.py
    ├── add_task.py
    ├── list_tasks.py
    ├── complete_task.py
    ├── delete_task.py
    └── update_task.py
```

### 3.2 MCP Server Implementation

```python
# backend/app/mcp/server.py
from mcp import Server, ServerConfig
from .tools import add_task, list_tasks, complete_task, delete_task, update_task

class TodoMCPServer:
    """MCP Server exposing todo management tools."""
    
    def __init__(self):
        self.server = Server(
            config=ServerConfig(
                name="TodoMCPServer",
                version="1.0.0",
                description="MCP server for AI-powered todo management"
            )
        )
        self._register_tools()
    
    def _register_tools(self):
        """Register all MCP tools."""
        self.server.register_tool(add_task.tool)
        self.server.register_tool(list_tasks.tool)
        self.server.register_tool(complete_task.tool)
        self.server.register_tool(delete_task.tool)
        self.server.register_tool(update_task.tool)
    
    def get_tools(self):
        """Get all registered tools for agent integration."""
        return self.server.tools

# Singleton instance
mcp_server = TodoMCPServer()
```

### 3.3 Tool Definitions

#### Tool 1: add_task

```python
# backend/app/mcp/tools/add_task.py
from mcp import Tool, ToolResult
from app.models.task import Task
from app.database.session import get_db_session

tool = Tool(
    name="add_task",
    description="Add a new task to the user's todo list",
    parameters={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the task (required)"
            },
            "description": {
                "type": "string",
                "description": "Optional description of the task"
            }
        },
        "required": ["title"]
    }
)

async def execute(title: str, description: str = "", context=None) -> ToolResult:
    """Execute add_task tool."""
    user_id = context.user_id
    
    async with get_db_session() as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            status="pending"
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
    
    return ToolResult(
        success=True,
        data={"task_id": str(task.id), "title": task.title},
        message=f"Task '{title}' created successfully"
    )
```

#### Tool 2: list_tasks

```python
# backend/app/mcp/tools/list_tasks.py
tool = Tool(
    name="list_tasks",
    description="List user's tasks, optionally filtered by status",
    parameters={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "description": "Filter by status (default: all)"
            }
        }
    }
)

async def execute(status: str = "all", context=None) -> ToolResult:
    """Execute list_tasks tool."""
    user_id = context.user_id
    
    async with get_db_session() as session:
        query = select(Task).where(Task.user_id == user_id)
        if status != "all":
            query = query.where(Task.status == status)
        result = await session.execute(query.order_by(Task.created_at.desc()))
        tasks = result.scalars().all()
    
    task_list = [
        {"task_id": str(t.id), "title": t.title, "status": t.status}
        for t in tasks
    ]
    
    return ToolResult(
        success=True,
        data={"tasks": task_list, "count": len(task_list)},
        message=f"Found {len(task_list)} task(s)"
    )
```

#### Tool 3: complete_task

```python
# backend/app/mcp/tools/complete_task.py
tool = Tool(
    name="complete_task",
    description="Mark a task as completed",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The UUID of the task to complete"
            }
        },
        "required": ["task_id"]
    }
)

async def execute(task_id: str, context=None) -> ToolResult:
    """Execute complete_task tool."""
    # Implementation: Find task, verify ownership, update status
    pass
```

#### Tool 4: delete_task

```python
# backend/app/mcp/tools/delete_task.py
tool = Tool(
    name="delete_task",
    description="Delete a task from the todo list",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The UUID of the task to delete"
            }
        },
        "required": ["task_id"]
    }
)

async def execute(task_id: str, context=None) -> ToolResult:
    """Execute delete_task tool."""
    # Implementation: Find task, verify ownership, delete
    pass
```

#### Tool 5: update_task

```python
# backend/app/mcp/tools/update_task.py
tool = Tool(
    name="update_task",
    description="Update a task's title or description",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The UUID of the task to update"
            },
            "title": {
                "type": "string",
                "description": "New title for the task"
            },
            "description": {
                "type": "string",
                "description": "New description for the task"
            }
        },
        "required": ["task_id"]
    }
)

async def execute(task_id: str, title: str = None, description: str = None, context=None) -> ToolResult:
    """Execute update_task tool."""
    # Implementation: Find task, verify ownership, update fields
    pass
```

### 3.4 Tool Summary Table

| Tool | Parameters | Required | Returns |
|------|------------|----------|---------|
| `add_task` | title, description | title | task_id, title |
| `list_tasks` | status | none | tasks[], count |
| `complete_task` | task_id | task_id | task_id, status |
| `delete_task` | task_id | task_id | deleted: true |
| `update_task` | task_id, title, description | task_id | task_id, title, description |

---

## 4. Frontend Integration

### 4.1 ChatKit Component Structure

```
frontend/
├── app/
│   └── chat/
│       └── page.tsx           # Main chat page
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx  # Main container
│   │   ├── MessageList.tsx    # Message display
│   │   ├── ChatInput.tsx      # User input
│   │   ├── ConversationList.tsx
│   │   └── TypingIndicator.tsx
│   └── ...
└── lib/
    └── chat-client.ts         # API client
```

### 4.2 ChatKit Integration

```typescript
// frontend/components/chat/ChatInterface.tsx
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { sendChatMessage, getConversation } from '@/lib/chat-client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolsUsed?: string[];
}

export function ChatInterface() {
  const { user, getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;
    
    // Add user message to UI immediately
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      const token = await getToken();
      const response = await sendChatMessage(content, conversationId, token);
      
      // Update conversation ID if new
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }
      
      // Add AI response
      const aiMessage: Message = {
        id: response.message_id,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp),
        toolsUsed: response.tools_used?.map(t => t.name)
      };
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      // Handle error
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-100 p-4">
        <ConversationList onSelect={loadConversation} />
      </aside>
      
      {/* Chat Area */}
      <main className="flex-1 flex flex-col">
        <MessageList messages={messages} isLoading={isLoading} />
        <ChatInput onSend={handleSendMessage} disabled={isLoading} />
      </main>
    </div>
  );
}
```

### 4.3 API Client

```typescript
// frontend/lib/chat-client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface ChatResponse {
  conversation_id: string;
  message_id: string;
  response: string;
  tools_used: { name: string; success: boolean }[];
  timestamp: string;
}

export async function sendChatMessage(
  message: string,
  conversationId: string | null,
  token: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to send message');
  }
  
  return response.json();
}

export async function getConversations(token: string) {
  const response = await fetch(`${API_BASE}/api/chat/conversations`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

export async function getConversation(id: string, token: string) {
  const response = await fetch(`${API_BASE}/api/chat/conversations/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

### 4.4 Domain Allowlist Configuration

```typescript
// frontend/lib/chatkit-config.ts
export const CHATKIT_CONFIG = {
  allowedDomains: [
    process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  ],
  maxMessageLength: 2000,
  enableMarkdown: true
};

// Validate domain on initialization
export function validateDomain(): boolean {
  const currentDomain = window.location.origin;
  return CHATKIT_CONFIG.allowedDomains.some(
    domain => currentDomain.includes(domain.replace(/https?:\/\//, ''))
  );
}
```

---

## 5. Agent Configuration

### 5.1 OpenAI Agents SDK Setup

```python
# backend/app/agent/brain.py
from agents import Agent, Runner
from app.mcp.server import mcp_server
from .prompts import SYSTEM_PROMPT

# Create the AI agent
todo_agent = Agent(
    name="TodoBot",
    model="gpt-4-turbo-preview",
    instructions=SYSTEM_PROMPT,
    tools=mcp_server.get_tools(),
    tool_choice="auto",
    temperature=0.7
)

async def process_message(
    user_message: str,
    user_id: str,
    history: list[dict]
) -> tuple[str, list[dict]]:
    """
    Process a user message through the AI agent.
    
    Args:
        user_message: User's natural language input
        user_id: UUID of authenticated user
        history: Previous conversation messages
        
    Returns:
        (response_text, tools_used)
    """
    from .context import ToolContext
    
    # Create context with user_id for MCP tools
    context = ToolContext(user_id=user_id)
    
    # Build messages array
    messages = history + [{"role": "user", "content": user_message}]
    
    # Run the agent
    runner = Runner(agent=todo_agent)
    result = await runner.run(messages=messages, context=context)
    
    # Extract tools used
    tools_used = [
        {
            "name": call.tool_name,
            "success": call.result.success if call.result else False,
            "result": call.result.data if call.result else None
        }
        for call in result.tool_calls
    ] if result.tool_calls else []
    
    return result.content, tools_used
```

### 5.2 System Prompt

```python
# backend/app/agent/prompts.py
SYSTEM_PROMPT = """You are TodoBot, a friendly AI assistant that helps users manage their todo list through natural conversation.

## Available Tools
- add_task(title, description): Add a new task
- list_tasks(status): Show tasks (all/pending/completed)
- complete_task(task_id): Mark a task as done
- delete_task(task_id): Remove a task
- update_task(task_id, title, description): Update a task

## Behavior Rules
1. Always be friendly and helpful
2. Confirm every action with a clear response
3. Use emojis sparingly: 📝 ✅ 🗑️ ✏️
4. If task not found, suggest "show my tasks"
5. Keep responses concise (1-3 sentences)

## Intent Recognition
- "Add/Create/New/Remember" → add_task
- "Show/List/What are my" → list_tasks
- "Done/Complete/Finish/Mark" → complete_task
- "Delete/Remove/Cancel" → delete_task
- "Change/Update/Rename" → update_task

## Example Responses
- Added: "I've added 'buy groceries' to your list! 📝"
- Listed: "Here are your tasks:\n1. 📌 Task1\n2. ✅ Task2"
- Completed: "Great job! ✅ 'Task' is now complete!"
- Deleted: "Done! 🗑️ 'Task' has been removed."
"""
```

---

## 6. Security Configuration

### 6.1 Domain Allowlist

**Backend CORS:**
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Frontend ChatKit:**
```typescript
// Verify domain before enabling chat
if (!validateDomain()) {
  throw new Error("Domain not allowed");
}
```

### 6.2 Environment Variables

**Backend (.env):**
```env
# Database
DATABASE_URL=postgresql+asyncpg://...

# OpenAI
OPENAI_API_KEY=sk-...

# Security
JWT_SECRET_KEY=your-secret
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_CHATKIT_DOMAIN_ALLOWLIST=localhost:3000
DATABASE_URL=postgresql://...
```

---

## 7. Architecture Summary

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           PHASE III ARCHITECTURE                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  FRONTEND (Next.js + ChatKit)                                       │   │
│  │  • Domain Allowlist Security                                        │   │
│  │  • Chat UI Components                                               │   │
│  │  • JWT Token Management                                             │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                      │
│                          POST /api/chat (Stateless)                         │
│                                      │                                      │
│  ┌───────────────────────────────────▼─────────────────────────────────┐   │
│  │  CHAT API (FastAPI)                                                 │   │
│  │  1. Authenticate (JWT)                                              │   │
│  │  2. Fetch History (DB)                                              │   │
│  │  3. Store User Msg (DB)                                             │   │
│  │  4. Run Agent (MCP)                                                 │   │
│  │  5. Store Response (DB)                                             │   │
│  │  6. Return Response                                                 │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                      │
│  ┌───────────────────────────────────▼─────────────────────────────────┐   │
│  │  AI AGENT (OpenAI Agents SDK)                                       │   │
│  │  • Intent Recognition                                               │   │
│  │  • Tool Selection                                                   │   │
│  │  • Response Generation                                              │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                      │
│  ┌───────────────────────────────────▼─────────────────────────────────┐   │
│  │  MCP SERVER (Official MCP SDK)                                      │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │   │
│  │  │add_task│ │list    │ │complete│ │delete  │ │update  │            │   │
│  │  │        │ │_tasks  │ │_task   │ │_task   │ │_task   │            │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘            │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                      │
│  ┌───────────────────────────────────▼─────────────────────────────────┐   │
│  │  NEON POSTGRESQL                                                    │   │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────────┐ ┌──────────┐             │   │
│  │  │ users   │ │ tasks   │ │conversations │ │ messages │             │   │
│  │  └─────────┘ └─────────┘ └──────────────┘ └──────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```
