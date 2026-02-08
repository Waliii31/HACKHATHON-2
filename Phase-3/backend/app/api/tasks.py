from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database.session import get_db_session
from app.models.task import Task
from app.api.deps import get_current_user_id

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/", response_model=List[Task])
async def list_tasks(
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by task priority"),
    search: Optional[str] = Query(None, description="Search tasks by title or description"),
    limit: int = Query(50, le=100),
    offset: int = 0,
):
    """
    List all tasks for the current user.
    """
    statement = select(Task).where(Task.user_id == user_id)
    
    if status:
        statement = statement.where(Task.status == status)
    if priority:
        statement = statement.where(Task.priority == priority)
    if search:
        search_term = f"%{search}%"
        # ilike is safer across DBs if supported, else like for SQLite
        # Postgres supports ilike
        statement = statement.where((Task.title.ilike(search_term)) | (Task.description.ilike(search_term)))
        
    statement = statement.offset(offset).limit(limit)
    result = await session.execute(statement)
    tasks = result.scalars().all()
    return tasks

@router.post("/", response_model=Task)
async def create_task(
    task_in: Task,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new task.
    """
    task_in.user_id = user_id
    session.add(task_in)
    await session.commit()
    await session.refresh(task_in)
    return task_in

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: UUID,
    task_update: Task,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update an existing task.
    """
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    task_data = task_update.dict(exclude_unset=True)
    task_data["updated_at"] = datetime.utcnow()
    
    for key, value in task_data.items():
        setattr(task, key, value)
        
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.delete("/{task_id}", response_model=Task)
async def delete_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a task.
    """
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
        
    await session.delete(task)
    await session.commit()
    return task
