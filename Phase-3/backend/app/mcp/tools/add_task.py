"""
MCP Tool: add_task

Adds a new task to the user's todo list.
Part of the stateless architecture - directly writes to database.
"""
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mcp.server import tool, ToolResult, ToolContext
from app.database.connection import AsyncSessionLocal


# Tool parameter schema (OpenAI function calling format)
ADD_TASK_PARAMETERS = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "The title of the task (required, max 255 characters)"
        },
        "description": {
            "type": "string",
            "description": "Optional description of the task (max 1000 characters)"
        }
    },
    "required": ["title"]
}


@tool(
    name="add_task",
    description="Add a new task to the user's todo list. Use this when the user wants to create, add, or remember a new task.",
    parameters=ADD_TASK_PARAMETERS
)
async def add_task(
    title: str,
    description: str = "",
    context: ToolContext = None
) -> ToolResult:
    """
    Add a new task to the database.
    
    Args:
        title: Task title (required)
        description: Optional task description
        context: Tool context with user_id
        
    Returns:
        ToolResult with created task info
    """
    # Validate context
    if not context or not context.user_id:
        return ToolResult(
            success=False,
            error="User context is required"
        )
    
    # Validate title
    if not title or not title.strip():
        return ToolResult(
            success=False,
            error="Title is required"
        )
    
    title = title.strip()
    if len(title) > 255:
        return ToolResult(
            success=False,
            error="Title must be 255 characters or less"
        )
    
    # Validate description
    if description and len(description) > 1000:
        return ToolResult(
            success=False,
            error="Description must be 1000 characters or less"
        )
    
    try:
        # Import here to avoid circular imports
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            # Insert task using raw SQL (compatible with existing Phase II schema)
            query = text("""
                INSERT INTO tasks (id, user_id, title, description, status, priority, created_at, updated_at)
                VALUES (gen_random_uuid(), :user_id, :title, :description, 'active', 'medium', NOW(), NOW())
                RETURNING id, title, status
            """)
            
            result = await session.execute(query, {
                "user_id": context.user_id,
                "title": title,
                "description": description or ""
            })
            
            row = result.fetchone()
            await session.commit()
            
            if row:
                return ToolResult(
                    success=True,
                    data={
                        "task_id": str(row[0]),
                        "title": row[1],
                        "status": row[2]
                    },
                    message=f"Task '{title}' created successfully"
                )
            else:
                return ToolResult(
                    success=False,
                    error="Failed to create task"
                )
                
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Database error: {str(e)}"
        )
