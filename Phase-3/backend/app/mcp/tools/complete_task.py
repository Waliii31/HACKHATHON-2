"""
MCP Tool: complete_task

Marks a task as completed.
Part of the stateless architecture - directly updates database.
"""
from sqlalchemy import text

from app.mcp.server import tool, ToolResult, ToolContext
from app.database.connection import AsyncSessionLocal


# Tool parameter schema
COMPLETE_TASK_PARAMETERS = {
    "type": "object",
    "properties": {
        "task_id": {
            "type": "string",
            "description": "The UUID of the task to mark as complete"
        },
        "task_title": {
            "type": "string",
            "description": "Alternatively, the title/name of the task to complete (if task_id not known)"
        }
    }
}


@tool(
    name="complete_task",
    description="Mark a task as completed/done. Use this when the user says they finished, completed, or are done with a task.",
    parameters=COMPLETE_TASK_PARAMETERS
)
async def complete_task(
    task_id: str = None,
    task_title: str = None,
    context: ToolContext = None
) -> ToolResult:
    """
    Mark a task as completed in the database.
    
    Args:
        task_id: UUID of the task (preferred)
        task_title: Title to search for (fallback)
        context: Tool context with user_id
        
    Returns:
        ToolResult with completion confirmation
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
            # Find the task
            if task_id:
                # Direct lookup by ID
                find_query = text("""
                    SELECT id, title, status
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
                    SELECT id, title, status
                    FROM tasks
                    WHERE user_id = :user_id 
                      AND LOWER(title) LIKE LOWER(:title_pattern)
                      AND status = 'active'
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
            current_status = row[2]
            
            # Check if already completed
            if current_status == "completed":
                return ToolResult(
                    success=True,
                    data={
                        "task_id": str(found_task_id),
                        "title": found_title,
                        "status": "completed"
                    },
                    message=f"Task '{found_title}' is already completed"
                )
            
            # Update task status
            update_query = text("""
                UPDATE tasks
                SET status = 'completed', completed_at = NOW(), updated_at = NOW()
                WHERE id = :task_id AND user_id = :user_id
                RETURNING id, title, status
            """)
            
            update_result = await session.execute(update_query, {
                "task_id": found_task_id,
                "user_id": context.user_id
            })
            
            updated_row = update_result.fetchone()
            await session.commit()
            
            if updated_row:
                return ToolResult(
                    success=True,
                    data={
                        "task_id": str(updated_row[0]),
                        "title": updated_row[1],
                        "status": updated_row[2]
                    },
                    message=f"Task '{updated_row[1]}' marked as complete"
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
