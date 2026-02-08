# MCP Server Specification

## Overview

The MCP (Model Context Protocol) Server exposes todo operations as callable tools for the AI agent. Built using the Official MCP SDK, it provides a standardized interface for the OpenAI Agents SDK to interact with the todo database.

## MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Server                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Tool Registry                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │   │
│  │  │add_task  │ │list_tasks│ │complete  │ │delete    │     │   │
│  │  │          │ │          │ │_task     │ │_task     │     │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │   │
│  │       │            │            │            │           │   │
│  │  ┌────┴────────────┴────────────┴────────────┴───────┐   │   │
│  │  │                 update_task                       │   │   │
│  │  └───────────────────────────────────────────────────┘   │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Database Layer                           │   │
│  │              (SQLModel + PostgreSQL)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Tool Specifications

### 1. add_task

**Purpose:** Create a new task in the user's todo list

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | The title of the task (max 200 chars) |
| description | string | No | Optional description (max 1000 chars) |

**Implementation:**
```python
from mcp import Tool, ToolResult

@mcp_server.tool()
async def add_task(
    title: str,
    description: str = "",
    context: ToolContext = None
) -> ToolResult:
    """Add a new task to the user's todo list."""
    user_id = context.user_id
    
    # Validate input
    if not title or len(title) > 200:
        return ToolResult(
            success=False,
            error="Title is required and must be under 200 characters"
        )
    
    # Create task in database
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    async with get_db_session() as session:
        session.add(task)
        await session.commit()
        await session.refresh(task)
    
    return ToolResult(
        success=True,
        data={
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status
        },
        message=f"Task '{title}' created successfully"
    )
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "title": "Buy groceries",
    "description": "Get milk, eggs, bread",
    "status": "pending"
  },
  "message": "Task 'Buy groceries' created successfully"
}
```

---

### 2. list_tasks

**Purpose:** Retrieve tasks from the user's todo list with optional status filtering

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status: "all", "pending", "completed" (default: "all") |

**Implementation:**
```python
@mcp_server.tool()
async def list_tasks(
    status: str = "all",
    context: ToolContext = None
) -> ToolResult:
    """List user's tasks, optionally filtered by status."""
    user_id = context.user_id
    
    # Validate status
    valid_statuses = ["all", "pending", "completed"]
    if status not in valid_statuses:
        return ToolResult(
            success=False,
            error=f"Invalid status. Use one of: {', '.join(valid_statuses)}"
        )
    
    async with get_db_session() as session:
        query = select(Task).where(Task.user_id == user_id)
        
        if status != "all":
            query = query.where(Task.status == status)
        
        query = query.order_by(Task.created_at.desc())
        result = await session.execute(query)
        tasks = result.scalars().all()
    
    task_list = [
        {
            "task_id": str(t.id),
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "created_at": t.created_at.isoformat()
        }
        for t in tasks
    ]
    
    return ToolResult(
        success=True,
        data={"tasks": task_list, "count": len(task_list)},
        message=f"Found {len(task_list)} task(s)"
    )
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "task_id": "uuid-1",
        "title": "Buy groceries",
        "description": "",
        "status": "pending",
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "task_id": "uuid-2",
        "title": "Call mom",
        "description": "Wish happy birthday",
        "status": "completed",
        "created_at": "2024-01-14T08:00:00Z"
      }
    ],
    "count": 2
  },
  "message": "Found 2 task(s)"
}
```

---

### 3. complete_task

**Purpose:** Mark a task as completed

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | Yes | The UUID of the task to complete |

**Implementation:**
```python
@mcp_server.tool()
async def complete_task(
    task_id: str,
    context: ToolContext = None
) -> ToolResult:
    """Mark a task as completed."""
    user_id = context.user_id
    
    # Validate UUID format
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        return ToolResult(
            success=False,
            error="Invalid task ID format"
        )
    
    async with get_db_session() as session:
        # Find task owned by user
        result = await session.execute(
            select(Task).where(
                Task.id == task_uuid,
                Task.user_id == user_id
            )
        )
        task = result.scalar_one_or_none()
        
        if not task:
            return ToolResult(
                success=False,
                error="Task not found or you don't have permission"
            )
        
        if task.status == "completed":
            return ToolResult(
                success=True,
                data={"task_id": task_id, "status": "completed"},
                message=f"Task '{task.title}' was already completed"
            )
        
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        await session.commit()
    
    return ToolResult(
        success=True,
        data={
            "task_id": task_id,
            "title": task.title,
            "status": "completed"
        },
        message=f"Task '{task.title}' marked as completed!"
    )
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "title": "Buy groceries",
    "status": "completed"
  },
  "message": "Task 'Buy groceries' marked as completed!"
}
```

---

### 4. delete_task

**Purpose:** Delete a task from the todo list

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | Yes | The UUID of the task to delete |

**Implementation:**
```python
@mcp_server.tool()
async def delete_task(
    task_id: str,
    context: ToolContext = None
) -> ToolResult:
    """Delete a task from the todo list."""
    user_id = context.user_id
    
    # Validate UUID format
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        return ToolResult(
            success=False,
            error="Invalid task ID format"
        )
    
    async with get_db_session() as session:
        # Find task owned by user
        result = await session.execute(
            select(Task).where(
                Task.id == task_uuid,
                Task.user_id == user_id
            )
        )
        task = result.scalar_one_or_none()
        
        if not task:
            return ToolResult(
                success=False,
                error="Task not found or you don't have permission"
            )
        
        task_title = task.title
        await session.delete(task)
        await session.commit()
    
    return ToolResult(
        success=True,
        data={"task_id": task_id, "deleted": True},
        message=f"Task '{task_title}' has been deleted"
    )
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "deleted": true
  },
  "message": "Task 'Buy groceries' has been deleted"
}
```

---

### 5. update_task

**Purpose:** Update an existing task's title or description

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | Yes | The UUID of the task to update |
| title | string | No | New title for the task |
| description | string | No | New description for the task |

**Implementation:**
```python
@mcp_server.tool()
async def update_task(
    task_id: str,
    title: str = None,
    description: str = None,
    context: ToolContext = None
) -> ToolResult:
    """Update an existing task's title or description."""
    user_id = context.user_id
    
    # Validate at least one field is provided
    if not title and description is None:
        return ToolResult(
            success=False,
            error="At least one of 'title' or 'description' must be provided"
        )
    
    # Validate UUID format
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        return ToolResult(
            success=False,
            error="Invalid task ID format"
        )
    
    async with get_db_session() as session:
        # Find task owned by user
        result = await session.execute(
            select(Task).where(
                Task.id == task_uuid,
                Task.user_id == user_id
            )
        )
        task = result.scalar_one_or_none()
        
        if not task:
            return ToolResult(
                success=False,
                error="Task not found or you don't have permission"
            )
        
        # Update fields
        old_title = task.title
        if title:
            task.title = title
        if description is not None:
            task.description = description
        
        task.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(task)
    
    return ToolResult(
        success=True,
        data={
            "task_id": task_id,
            "title": task.title,
            "description": task.description,
            "status": task.status
        },
        message=f"Task updated successfully (was: '{old_title}')"
    )
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "title": "Buy organic groceries",
    "description": "From the farmers market",
    "status": "pending"
  },
  "message": "Task updated successfully (was: 'Buy groceries')"
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "error_code": "TASK_NOT_FOUND"
}
```

### Error Codes
| Code | Description |
|------|-------------|
| VALIDATION_ERROR | Input validation failed |
| TASK_NOT_FOUND | Task doesn't exist or user lacks permission |
| INVALID_UUID | Task ID is not a valid UUID |
| DATABASE_ERROR | Database operation failed |
| UNAUTHORIZED | User not authenticated |

## Security Considerations

1. **User Isolation**: All tools filter by `user_id` from JWT context
2. **Input Validation**: All parameters are validated before database operations
3. **SQL Injection Prevention**: Using SQLModel with parameterized queries
4. **Rate Limiting**: Applied at API gateway level
5. **Audit Logging**: All tool invocations are logged

## MCP Server Configuration

```python
# backend/app/mcp/server.py
from mcp import Server, ServerConfig

mcp_server = Server(
    config=ServerConfig(
        name="TodoMCPServer",
        version="1.0.0",
        description="MCP server for todo task management"
    )
)

# Register all tools
mcp_server.register_tools([
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task
])
```

## Integration with AI Agent

```python
# backend/app/agent/brain.py
from openai import OpenAI
from agents import Agent, Runner
from app.mcp.server import mcp_server

# Convert MCP tools to OpenAI Agents format
agent = Agent(
    name="TodoAssistant",
    model="gpt-4",
    instructions=SYSTEM_PROMPT,
    tools=mcp_server.get_tools_for_agent()
)

async def process_message(user_message: str, user_id: str, history: list):
    """Process a user message and return AI response."""
    context = ToolContext(user_id=user_id)
    
    runner = Runner(agent=agent)
    result = await runner.run(
        messages=history + [{"role": "user", "content": user_message}],
        tool_context=context
    )
    
    return result.response, result.tools_used
```
