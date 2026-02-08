# Phase III: Todo AI Chatbot - Technical Architecture

## Overview

This document outlines the complete technical architecture for Phase III of the Todo AI Chatbot. The architecture introduces an AI-powered conversational layer on top of the Phase II infrastructure, featuring OpenAI ChatKit for the frontend, OpenAI Agents SDK for the "brain", and an MCP Server that exposes todo operations as callable tools.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        OpenAI ChatKit                                   │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │ │
│  │  │   Chat Input     │  │  Message List    │  │  Domain Allowlist    │  │ │
│  │  │   Component      │  │  Component       │  │  Security Config     │  │ │
│  │  └────────┬─────────┘  └────────▲─────────┘  └──────────────────────┘  │ │
│  └───────────┼──────────────────────┼────────────────────────────────────┘ │
│              │                      │                                       │
│              ▼                      │                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │              POST /api/chat (Stateless Chat Endpoint)                   │ │
│  │  • Receives user message + conversation_id                              │ │
│  │  • Loads history from DB                                                │ │
│  │  • Calls AI Agent                                                       │ │
│  │  • Saves response to DB                                                 │ │
│  │  • Returns AI response                                                  │ │
│  └────────────────────────────────────┬────────────────────────────────────┘ │
└───────────────────────────────────────┼─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                                  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    OpenAI Agents SDK (AI Brain)                         │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  • Intent Recognition                                            │  │ │
│  │  │  • Natural Language Understanding                                │  │ │
│  │  │  • Tool Selection & Orchestration                                │  │ │
│  │  │  • Response Generation                                           │  │ │
│  │  └────────────────────────────────┬─────────────────────────────────┘  │ │
│  └───────────────────────────────────┼─────────────────────────────────────┘ │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    MCP Server (Official MCP SDK)                        │ │
│  │  ┌────────────────┐ ┌────────────────┐ ┌──────────────────────────────┐ │ │
│  │  │  add_task      │ │  list_tasks    │ │  complete_task               │ │ │
│  │  │  (title, desc) │ │  (status)      │ │  (task_id)                   │ │ │
│  │  └────────────────┘ └────────────────┘ └──────────────────────────────┘ │ │
│  │  ┌────────────────┐ ┌────────────────────────────────────────────────┐  │ │
│  │  │  delete_task   │ │  update_task (task_id, title, description)    │  │ │
│  │  │  (task_id)     │ │                                                │  │ │
│  │  └────────────────┘ └────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────┬─────────────────────────────────────┘ │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    Database Layer (SQLModel)                            │ │
│  │  • Task CRUD Operations                                                 │ │
│  │  • Conversation History Storage                                         │ │
│  │  • User Authentication Data                                             │ │
│  └────────────────────────────────────┬────────────────────────────────────┘ │
└───────────────────────────────────────┼─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Neon Serverless PostgreSQL                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────────────┐   │
│  │     users       │  │     tasks       │  │     conversations         │   │
│  │   (from P2)     │  │   (from P2)     │  │     (new for P3)          │   │
│  └─────────────────┘  └─────────────────┘  └────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         messages (new for P3)                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
Phase-3/
├── .spec-kit/
│   └── config.yaml                    # Spec-Kit configuration
├── @specs/                            # Specification documents
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   ├── api/
│   ├── database/
│   └── mcp/
├── frontend/                          # Next.js frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── .env.local
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                   # Landing/redirect
│   │   ├── chat/
│   │   │   └── page.tsx               # Main chat interface
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   └── api/
│   │       └── auth/[...all]/route.ts # Better Auth handler
│   ├── components/
│   │   ├── ChatInterface.tsx          # Main chat component
│   │   ├── MessageList.tsx            # Message display
│   │   ├── ChatInput.tsx              # User input
│   │   └── AuthGuard.tsx              # Route protection
│   ├── lib/
│   │   ├── auth.ts                    # Better Auth config
│   │   ├── auth-client.ts             # Client auth helper
│   │   └── chat-client.ts             # Chat API client
│   └── types/
│       ├── chat.ts                    # Chat types
│       └── user.ts                    # User types
├── backend/
│   ├── requirements.txt
│   ├── .env
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Configuration
│   │   ├── database/
│   │   │   ├── connection.py          # DB connection
│   │   │   └── session.py             # Session management
│   │   ├── models/
│   │   │   ├── user.py                # User model (from P2)
│   │   │   ├── task.py                # Task model (from P2)
│   │   │   ├── conversation.py        # Conversation model (new)
│   │   │   └── message.py             # Message model (new)
│   │   ├── schemas/
│   │   │   ├── chat.py                # Chat request/response schemas
│   │   │   └── task.py                # Task schemas
│   │   ├── api/
│   │   │   ├── chat.py                # POST /api/chat endpoint
│   │   │   ├── auth.py                # Auth endpoints
│   │   │   └── deps.py                # Dependencies
│   │   ├── agent/
│   │   │   ├── brain.py               # OpenAI Agents SDK agent
│   │   │   └── prompts.py             # System prompts
│   │   └── mcp/
│   │       ├── server.py              # MCP Server implementation
│   │       └── tools/
│   │           ├── add_task.py
│   │           ├── list_tasks.py
│   │           ├── complete_task.py
│   │           ├── delete_task.py
│   │           └── update_task.py
└── README.md
```

## Core Components

### 1. Frontend: OpenAI ChatKit Integration

**ChatKit Configuration:**
```typescript
// Domain Allowlist for security
const chatKitConfig = {
  allowedDomains: [
    "localhost:3000",
    "your-production-domain.com"
  ],
  apiEndpoint: "/api/chat"
};
```

**Responsibilities:**
- Render conversational UI with ChatKit components
- Handle user input and message submission
- Display AI responses and message history
- Manage conversation state client-side
- Enforce domain allowlist security

### 2. Stateless Chat API (`POST /api/chat`)

**Endpoint Design:**
```
POST /api/chat
Authorization: Bearer <jwt_token>

Request Body:
{
  "message": "Add buy groceries to my list",
  "conversation_id": "uuid-v4" // optional, creates new if not provided
}

Response:
{
  "conversation_id": "uuid-v4",
  "response": "I've added 'buy groceries' to your task list!",
  "tools_used": ["add_task"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Stateless Design Principles:**
1. No server-side session state
2. All conversation context from database
3. Each request is independent
4. Conversation ID links requests to history

**Request Flow:**
1. Authenticate user via JWT
2. Load conversation history from PostgreSQL (if conversation_id provided)
3. Build context for AI agent
4. Send to OpenAI Agents SDK
5. Execute MCP tools as needed
6. Store user message and AI response in database
7. Return response to client

### 3. AI Agent Brain (OpenAI Agents SDK)

**Agent Configuration:**
```python
from openai import OpenAI
from agents import Agent, Runner

agent = Agent(
    name="TodoAssistant",
    instructions="""You are a friendly todo list assistant. 
    Help users manage their tasks through natural conversation.
    Always confirm actions with friendly responses.
    When users want to add tasks, extract the title and optional description.
    When users ask about their tasks, determine the status filter.
    Be conversational and helpful.""",
    tools=[
        add_task_tool,
        list_tasks_tool,
        complete_task_tool,
        delete_task_tool,
        update_task_tool
    ]
)
```

**Intent Mapping:**

| User Intent | Example Phrases | MCP Tool |
|-------------|-----------------|----------|
| Add Task | "Add...", "Create...", "New task...", "Remember to..." | `add_task` |
| List Tasks | "Show my tasks", "What's pending?", "My todos" | `list_tasks` |
| Complete Task | "Mark as done", "Complete...", "Finish..." | `complete_task` |
| Delete Task | "Delete...", "Remove...", "Get rid of..." | `delete_task` |
| Update Task | "Change...", "Update...", "Rename..." | `update_task` |

### 4. MCP Server (Official MCP SDK)

**Tool Definitions:**

```python
# MCP Server Tools Schema
tools = [
    {
        "name": "add_task",
        "description": "Add a new task to the user's todo list",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the task"
                },
                "description": {
                    "type": "string", 
                    "description": "Optional description of the task"
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "list_tasks",
        "description": "List user's tasks, optionally filtered by status",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter tasks by status"
                }
            }
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID of the task to complete"
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "delete_task",
        "description": "Delete a task from the todo list",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID of the task to delete"
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "update_task",
        "description": "Update an existing task's title or description",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID of the task to update"
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
    }
]
```

## Conversation Flow

### Complete Request Lifecycle

```
1. USER types: "Add buy milk to my list"
   │
   ▼
2. CHATKIT sends POST /api/chat
   {
     "message": "Add buy milk to my list",
     "conversation_id": "abc-123"
   }
   │
   ▼
3. CHAT ENDPOINT (Stateless):
   ├── Verify JWT token
   ├── Load conversation history from PostgreSQL
   ├── Build context array for agent
   │
   ▼
4. AI AGENT (OpenAI Agents SDK):
   ├── Analyze user intent: "add task"
   ├── Extract parameters: title="buy milk"
   ├── Select tool: add_task
   │
   ▼
5. MCP SERVER executes add_task:
   ├── Validate parameters
   ├── Insert task into PostgreSQL
   ├── Return success with task details
   │
   ▼
6. AI AGENT generates response:
   "I've added 'buy milk' to your task list! 🛒"
   │
   ▼
7. CHAT ENDPOINT:
   ├── Save user message to DB
   ├── Save AI response to DB
   ├── Return response to client
   │
   ▼
8. CHATKIT displays response to user
```

## Database Schema Extensions

### New Tables for Phase III

```sql
-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tools_used JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

## Security Architecture

### Domain Allowlist (ChatKit)

```typescript
// frontend/lib/chatkit-config.ts
export const chatKitSecurityConfig = {
  allowedDomains: [
    process.env.NEXT_PUBLIC_APP_URL,
    // Add production domains here
  ],
  enableCSRF: true,
  maxMessageLength: 2000
};
```

### Authentication Flow

1. User authenticates via Better Auth (from Phase II)
2. JWT token stored in secure cookie
3. Chat requests include JWT in Authorization header
4. Backend verifies JWT before processing
5. User ID extracted for task/conversation isolation

### API Security

- All chat endpoints require authentication
- Rate limiting: 60 requests/minute per user
- Input sanitization for all user messages
- SQL injection prevention via SQLModel
- XSS prevention in response rendering

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_CHATKIT_DOMAIN_ALLOWLIST=localhost:3000
DATABASE_URL=postgresql://...
```

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql+asyncpg://...

# OpenAI
OPENAI_API_KEY=sk-...

# JWT
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# MCP
MCP_SERVER_PORT=8001

# Security
ALLOWED_ORIGINS=http://localhost:3000
```

## Error Handling

### Chat Error Responses

| Error Type | HTTP Status | Response |
|------------|-------------|----------|
| Unauthorized | 401 | `{"error": "Authentication required"}` |
| Invalid Message | 400 | `{"error": "Message cannot be empty"}` |
| Rate Limited | 429 | `{"error": "Too many requests", "retry_after": 60}` |
| Agent Error | 500 | `{"error": "Sorry, I'm having trouble. Please try again."}` |
| Tool Failed | 500 | `{"error": "I couldn't complete that action. Details: ..."}` |

## Performance Considerations

- **Response Time Target**: < 3 seconds for tool execution
- **Context Window**: Last 10 messages for context
- **Database Pooling**: 5 connections for chat operations
- **Caching**: Cache conversation metadata in memory
- **Streaming**: Consider streaming responses for long outputs
