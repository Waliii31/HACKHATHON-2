"""
MCP Tool: list_tasks

Lists the user's tasks, optionally filtered by status.
Part of the stateless architecture - directly reads from database.
"""
from sqlalchemy import text

from app.mcp.server import tool, ToolResult, ToolContext
from app.database.connection import AsyncSessionLocal


# Tool parameter schema
LIST_TASKS_PARAMETERS = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["all", "pending", "completed", "active"],
            "description": "Filter tasks by status. 'all' returns all tasks, 'pending' or 'active' returns incomplete tasks, 'completed' returns done tasks."
        }
    }
}


@tool(
    name="list_tasks",
    description="List the user's tasks. Use this when the user wants to see their tasks, view their todo list, or check what they need to do.",
    parameters=LIST_TASKS_PARAMETERS
)
async def list_tasks(
    status: str = "all",
    context: ToolContext = None
) -> ToolResult:
    """
    List user's tasks from the database.
    
    Args:
        status: Filter by status (all, pending/active, completed)
        context: Tool context with user_id
        
    Returns:
        ToolResult with list of tasks
    """
    # Validate context
    if not context or not context.user_id:
        return ToolResult(
            success=False,
            error="User context is required"
        )
    
    # Normalize status
    status = (status or "all").lower().strip()
    if status == "pending":
        status = "active"  # Map pending to active (Phase II schema uses 'active')
    
    try:
        async with AsyncSessionLocal() as session:
            # Build query based on status filter
            if status == "all":
                query = text("""
                    SELECT id, title, description, status, priority, due_date, created_at, completed_at
                    FROM tasks
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
            elif status == "completed":
                query = text("""
                    SELECT id, title, description, status, priority, due_date, created_at, completed_at
                    FROM tasks
                    WHERE user_id = :user_id AND status = 'completed'
                    ORDER BY completed_at DESC
                    LIMIT 50
                """)
            else:  # active/pending
                query = text("""
                    SELECT id, title, description, status, priority, due_date, created_at, completed_at
                    FROM tasks
                    WHERE user_id = :user_id AND status = 'active'
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
            
            result = await session.execute(query, {"user_id": context.user_id})
            rows = result.fetchall()
            
            # Format tasks for response
            tasks = []
            for row in rows:
                task = {
                    "task_id": str(row[0]),
                    "title": row[1],
                    "description": row[2] or "",
                    "status": row[3],
                    "priority": row[4],
                    "due_date": str(row[5]) if row[5] else None,
                    "created_at": str(row[6]) if row[6] else None
                }
                tasks.append(task)
            
            # Count by status
            pending_count = sum(1 for t in tasks if t["status"] == "active")
            completed_count = sum(1 for t in tasks if t["status"] == "completed")
            
            return ToolResult(
                success=True,
                data={
                    "tasks": tasks,
                    "count": len(tasks),
                    "pending_count": pending_count,
                    "completed_count": completed_count,
                    "filter": status
                },
                message=f"Found {len(tasks)} task(s)"
            )
            
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Database error: {str(e)}"
        )
