"""
MCP Tool: update_task

Updates a task's title or description.
Part of the stateless architecture - directly updates database.
"""
from sqlalchemy import text

from app.mcp.server import tool, ToolResult, ToolContext
from app.database.connection import AsyncSessionLocal


# Tool parameter schema
UPDATE_TASK_PARAMETERS = {
    "type": "object",
    "properties": {
        "task_id": {
            "type": "string",
            "description": "The UUID of the task to update"
        },
        "task_title": {
            "type": "string",
            "description": "The current title/name of the task to update (if task_id not known)"
        },
        "new_title": {
            "type": "string",
            "description": "The new title for the task"
        },
        "new_description": {
            "type": "string",
            "description": "The new description for the task"
        }
    }
}


@tool(
    name="update_task",
    description="Update a task's title or description. Use this when the user wants to change, rename, modify, or update a task.",
    parameters=UPDATE_TASK_PARAMETERS
)
async def update_task(
    task_id: str = None,
    task_title: str = None,
    new_title: str = None,
    new_description: str = None,
    context: ToolContext = None
) -> ToolResult:
    """
    Update a task in the database.
    
    Args:
        task_id: UUID of the task (preferred)
        task_title: Current title to search for (fallback)
        new_title: New title to set
        new_description: New description to set
        context: Tool context with user_id
        
    Returns:
        ToolResult with update confirmation
    """
    # Validate context
    if not context or not context.user_id:
        return ToolResult(
            success=False,
            error="User context is required"
        )
    
    # Need either task_id or task_title to find the task
    if not task_id and not task_title:
        return ToolResult(
            success=False,
            error="Either task_id or task_title is required to identify the task"
        )
    
    # Need at least one field to update
    if not new_title and new_description is None:
        return ToolResult(
            success=False,
            error="At least new_title or new_description is required"
        )
    
    # Validate new_title if provided
    if new_title:
        new_title = new_title.strip()
        if len(new_title) > 255:
            return ToolResult(
                success=False,
                error="Title must be 255 characters or less"
            )
        if not new_title:
            return ToolResult(
                success=False,
                error="Title cannot be empty"
            )
    
    # Validate new_description if provided
    if new_description and len(new_description) > 1000:
        return ToolResult(
            success=False,
            error="Description must be 1000 characters or less"
        )
    
    try:
        async with AsyncSessionLocal() as session:
            # Find the task first
            if task_id:
                find_query = text("""
                    SELECT id, title, description
                    FROM tasks
                    WHERE id = :task_id AND user_id = :user_id
                """)
                result = await session.execute(find_query, {
                    "task_id": task_id,
                    "user_id": context.user_id
                })
            else:
                find_query = text("""
                    SELECT id, title, description
                    FROM tasks
                    WHERE user_id = :user_id 
                      AND LOWER(title) LIKE LOWER(:title_pattern)
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                result = await session.execute(find_query, {
                    "user_id": context.user_id,
                    "title_pattern": f"%{task_title}%"
                })
            
            row = result.fetchone()
            
            if not row:
                return ToolResult(
                    success=False,
                    error=f"Task not found. Try saying 'show my tasks' to see your list."
                )
            
            found_task_id = row[0]
            old_title = row[1]
            old_description = row[2]
            
            # Build update query
            updates = []
            params = {
                "task_id": found_task_id,
                "user_id": context.user_id
            }
            
            if new_title:
                updates.append("title = :new_title")
                params["new_title"] = new_title
            
            if new_description is not None:
                updates.append("description = :new_description")
                params["new_description"] = new_description
            
            updates.append("updated_at = NOW()")
            
            update_query = text(f"""
                UPDATE tasks
                SET {', '.join(updates)}
                WHERE id = :task_id AND user_id = :user_id
                RETURNING id, title, description
            """)
            
            update_result = await session.execute(update_query, params)
            updated_row = update_result.fetchone()
            await session.commit()
            
            if updated_row:
                return ToolResult(
                    success=True,
                    data={
                        "task_id": str(updated_row[0]),
                        "title": updated_row[1],
                        "description": updated_row[2] or "",
                        "old_title": old_title,
                        "old_description": old_description or ""
                    },
                    message=f"Task updated: '{old_title}' → '{updated_row[1]}'"
                )
            else:
                return ToolResult(
                    success=False,
                    error="Failed to update task"
                )
                
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Database error: {str(e)}"
        )
