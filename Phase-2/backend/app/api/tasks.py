from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
import uuid

from app.database.session import get_db_session
from app.auth.jwt import get_current_user_id
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskStatusUpdate, TaskRead,
    TaskListResponse, TaskPagination
)
from app.models.task import Task, TaskStatus
from app.models.user import User

router = APIRouter(tags=["tasks"])


@router.get("/users/{user_id}/tasks", response_model=TaskListResponse)
async def list_user_tasks(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("desc")
):
    """
    Retrieve a list of tasks for the specified user.
    Only the authenticated user can access their own tasks.
    """
    # Verify that the requesting user is the same as the user whose tasks are being requested
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user's tasks"
        )

    # Build the query
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if status_filter:
        if status_filter.lower() in ["active", "completed"]:
            query = query.where(Task.status == TaskStatus(status_filter.lower()))

    if priority:
        if priority.lower() in ["low", "medium", "high"]:
            query = query.where(Task.priority == priority.lower())

    # Apply sorting
    if hasattr(Task, sort_by):
        sort_column = getattr(Task, sort_by)
        if order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    # Count total items for pagination
    count_query = select(Task).where(Task.user_id == user_id)
    if status_filter:
        if status_filter.lower() in ["active", "completed"]:
            count_query = count_query.where(Task.status == TaskStatus(status_filter.lower()))
    if priority:
        if priority.lower() in ["low", "medium", "high"]:
            count_query = count_query.where(Task.priority == priority.lower())

    total_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
    total = total_result.scalar()

    # Apply pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    tasks = result.scalars().all()

    # Calculate pagination details
    page = (offset // limit) + 1
    has_next = (offset + limit) < total
    has_prev = offset > 0

    pagination = TaskPagination(
        page=page,
        limit=limit,
        total=total,
        has_next=has_next,
        has_prev=has_prev
    )

    task_dicts = [task.__dict__ for task in tasks]
    task_reads = [TaskRead(**task_dict) for task_dict in task_dicts]

    return TaskListResponse(tasks=task_reads, pagination=pagination)


@router.post("/users/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new task for the specified user.
    Only the authenticated user can create tasks for themselves.
    """
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to create tasks for this user"
        )

    # Verify that the user exists
    user_check = await db.execute(select(User).where(User.id == user_id))
    try:
        user_check.one()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Create the task
    task = Task(
        **task_data.dict(),
        user_id=user_id
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return TaskRead(**task.__dict__)


@router.get("/users/{user_id}/tasks/{id}", response_model=TaskRead)
async def get_task(
    user_id: UUID,
    id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Retrieve a specific task by ID for the specified user.
    Only the authenticated user can access their own tasks.
    """
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user's tasks"
        )

    result = await db.execute(
        select(Task).where(Task.id == id).where(Task.user_id == user_id)
    )

    try:
        task = result.scalar_one()
        return TaskRead(**task.__dict__)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.put("/users/{user_id}/tasks/{id}", response_model=TaskRead)
async def update_task(
    user_id: UUID,
    id: UUID,
    task_data: TaskUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update a specific task by ID for the specified user.
    Only the authenticated user can update their own tasks.
    """
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to update this user's task"
        )

    result = await db.execute(
        select(Task).where(Task.id == id).where(Task.user_id == user_id)
    )

    try:
        task = result.scalar_one()

        # Update task fields based on provided data
        update_data = task_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(task, field, value)

        await db.commit()
        await db.refresh(task)

        return TaskRead(**task.__dict__)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.delete("/users/{user_id}/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: UUID,
    id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a specific task by ID for the specified user.
    Only the authenticated user can delete their own tasks.
    """
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this user's task"
        )

    result = await db.execute(
        select(Task).where(Task.id == id).where(Task.user_id == user_id)
    )

    try:
        task = result.scalar_one()
        await db.delete(task)
        await db.commit()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.patch("/users/{user_id}/tasks/{id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    user_id: UUID,
    id: UUID,
    status_update: TaskStatusUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Toggle the completion status of a specific task for the specified user.
    Only the authenticated user can update their own tasks.
    """
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to update this user's task"
        )

    result = await db.execute(
        select(Task).where(Task.id == id).where(Task.user_id == user_id)
    )

    try:
        task = result.scalar_one()

        # Update status based on the complete flag
        if status_update.complete:
            task.status = TaskStatus.COMPLETED
            from datetime import datetime
            task.completed_at = datetime.utcnow()
        else:
            task.status = TaskStatus.ACTIVE
            task.completed_at = None

        await db.commit()
        await db.refresh(task)

        return TaskRead(**task.__dict__)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )