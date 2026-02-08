"""
MCP Tool: delete_task

Deletes a task from the user's todo list.
Part of the stateless architecture - directly removes from database.
"""
from sqlalchemy import text

from app.mcp.server import tool, ToolResult, ToolContext
from app.database.connection import AsyncSessionLocal


# Tool parameter schema
DELETE_TASK_PARAMETERS = {
    "type": "object",
    "properties": {
        "task_id": {
            "type": "string",
            "description": "The UUID of the task to delete"
        },
        "task_title": {
            "type": "string",
            "description": "Alternatively, the title/name of the task to delete (if task_id not known)"
        }
    }
}


@tool(
    name="delete_task",
    description="Delete a task from the todo list. Use this when the user wants to remove, delete, or cancel a task.",
    parameters=DELETE_TASK_PARAMETERS
)
async def delete_task(
    task_id: str = None,
    task_title: str = None,
    context: ToolContext = None
) -> ToolResult:
    """
    Delete a task from the database.
    
    Args:
        task_id: UUID of the task (preferred)
        task_title: Title to search for (fallback)
        context: Tool context with user_id
        
    Returns:
        ToolResult with deletion confirmation
    """
    # Validate context
    if not context or not context.user_id:
        return ToolResult(
            success=False,
            error="User context is required"
        )
    
    # Need either task_id or task_title
    if not task_id and not task_title:
        return ToolResult(
            success=False,
            error="Either task_id or task_title is required"
        )
    
    try:
        async with AsyncSessionLocal() as session:
            # Find the task first
            if task_id:
                # Direct lookup by ID
                find_query = text("""
                    SELECT id, title
                    FROM tasks
                    WHERE id = :task_id AND user_id = :user_id
                """)
                result = await session.execute(find_query, {
                    "task_id": task_id,
                    "user_id": context.user_id
                })
            else:
                # Search by title (case-insensitive, partial match)
                find_query = text("""
                    SELECT id, title
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
            found_title = row[1]
            
            # Delete the task
            delete_query = text("""
                DELETE FROM tasks
                WHERE id = :task_id AND user_id = :user_id
                RETURNING id
            """)
            
            delete_result = await session.execute(delete_query, {
                "task_id": found_task_id,
                "user_id": context.user_id
            })
            
            deleted_row = delete_result.fetchone()
            await session.commit()
            
            if deleted_row:
                return ToolResult(
                    success=True,
                    data={
                        "task_id": str(found_task_id),
                        "title": found_title,
                        "deleted": True
                    },
                    message=f"Task '{found_title}' has been deleted"
                )
            else:
                return ToolResult(
                    success=False,
                    error="Failed to delete task"
                )
                
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Database error: {str(e)}"
        )
