# Phase III Database Schema

## Overview

Phase III extends the Phase II database schema with new tables for conversation history persistence. The existing `users` and `tasks` tables remain unchanged, while new `conversations` and `messages` tables are added.

## Schema Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Neon PostgreSQL Database                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│       users         │       │       tasks         │
│   (from Phase II)   │       │   (from Phase II)   │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │───┐   │ id (PK)             │
│ email               │   │   │ user_id (FK)    ────┼───┐
│ emailVerified       │   │   │ title               │   │
│ name                │   │   │ description         │   │
│ image               │   │   │ status              │   │
│ createdAt           │   │   │ priority            │   │
│ updatedAt           │   │   │ due_date            │   │
└─────────────────────┘   │   │ created_at          │   │
                          │   │ updated_at          │   │
                          │   │ completed_at        │   │
                          │   └─────────────────────┘   │
                          │                             │
                          │   ┌─────────────────────┐   │
                          │   │   conversations     │   │
                          │   │   (NEW for P3)      │   │
                          │   ├─────────────────────┤   │
                          ├──▶│ id (PK)             │   │
                          │   │ user_id (FK)    ────┼───┤
                          │   │ title               │   │
                          │   │ created_at          │   │
                          │   │ updated_at          │   │
                          │   └────────┬────────────┘   │
                          │            │                │
                          │            │ 1:N            │
                          │            ▼                │
                          │   ┌─────────────────────┐   │
                          │   │     messages        │   │
                          │   │   (NEW for P3)      │   │
                          │   ├─────────────────────┤   │
                          │   │ id (PK)             │   │
                          │   │ conversation_id(FK) │   │
                          │   │ role                │   │
                          │   │ content             │   │
                          │   │ tools_used (JSONB)  │   │
                          │   │ created_at          │   │
                          │   └─────────────────────┘   │
                          │                             │
                          └─────────────────────────────┘
```

## Table Definitions

### Existing Tables (From Phase II)

#### users
Unchanged from Phase II. See Phase II schema documentation.

#### tasks
Unchanged from Phase II. Enhanced with MCP tool access patterns.

### New Tables (Phase III)

#### conversations

Stores conversation sessions for each user.

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_conversations_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique conversation identifier |
| user_id | UUID | NOT NULL, FK → users(id) | Owner of the conversation |
| title | TEXT | NULLABLE | Optional conversation title (auto-generated from first message) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

#### messages

Stores individual messages within conversations.

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tools_used JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE,
        
    CONSTRAINT chk_messages_role
        CHECK (role IN ('user', 'assistant', 'system'))
);

-- Indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_created 
    ON messages(conversation_id, created_at);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique message identifier |
| conversation_id | UUID | NOT NULL, FK → conversations(id) | Parent conversation |
| role | TEXT | NOT NULL, CHECK (IN 'user', 'assistant', 'system') | Message author role |
| content | TEXT | NOT NULL | Message content |
| tools_used | JSONB | NULLABLE | Tools used by AI (for assistant messages) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Message timestamp |

**tools_used JSON Schema:**
```json
[
  {
    "name": "add_task",
    "success": true,
    "result": {
      "task_id": "uuid",
      "title": "Buy groceries"
    }
  }
]
```

## SQLModel Definitions

```python
# backend/app/models/conversation.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="conversations")
```

```python
# backend/app/models/message.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Literal
from uuid import UUID, uuid4
from datetime import datetime
import json

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(
        foreign_key="conversations.id", 
        nullable=False, 
        index=True
    )
    role: str = Field(
        sa_column_kwargs={"check": "role IN ('user', 'assistant', 'system')"}
    )
    content: str = Field(nullable=False)
    tools_used: Optional[str] = Field(default=None)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    
    def get_tools_used(self) -> Optional[List[dict]]:
        """Parse tools_used JSON"""
        if self.tools_used:
            return json.loads(self.tools_used)
        return None
    
    def set_tools_used(self, tools: List[dict]) -> None:
        """Serialize tools_used to JSON"""
        self.tools_used = json.dumps(tools)
```

## Migration Script

```sql
-- Migration: 002_add_conversation_tables.sql
-- Phase III: Add conversation history tables

BEGIN;

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tools_used JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
    ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at 
    ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
    ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at 
    ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created 
    ON messages(conversation_id, created_at);

-- Add trigger to update conversations.updated_at
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();

COMMIT;
```

## Query Patterns

### Get User's Conversations
```sql
SELECT 
    c.id,
    c.title,
    c.created_at,
    c.updated_at,
    (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count,
    (SELECT content FROM messages WHERE conversation_id = c.id 
     ORDER BY created_at DESC LIMIT 1) as last_message
FROM conversations c
WHERE c.user_id = :user_id
ORDER BY c.updated_at DESC
LIMIT :limit OFFSET :offset;
```

### Get Conversation Messages
```sql
SELECT id, role, content, tools_used, created_at
FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at ASC
LIMIT :limit;
```

### Get Recent Context (Last N Messages)
```sql
SELECT id, role, content, tools_used, created_at
FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at DESC
LIMIT 10;
```

## Data Retention

### Conversation Cleanup Policy
```sql
-- Delete conversations older than 90 days (optional maintenance)
DELETE FROM conversations 
WHERE updated_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
```

### Storage Estimates

| Table | Avg Row Size | Rows/User/Month | Monthly Growth |
|-------|--------------|-----------------|----------------|
| conversations | 200 bytes | 30 | 6 KB/user |
| messages | 500 bytes | 600 | 300 KB/user |

## Security Considerations

1. **Row-Level Security**: All queries filter by `user_id`
2. **Cascade Deletes**: Messages deleted when conversation deleted
3. **No PII in tools_used**: Only task IDs and titles stored
4. **Encryption**: Database connection uses SSL
5. **Audit Trail**: `created_at` timestamps for all records
