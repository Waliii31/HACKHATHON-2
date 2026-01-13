from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = TaskStatus.ACTIVE
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskStatusUpdate(BaseModel):
    complete: bool


class TaskRead(TaskBase):
    id: UUID
    user_id: UUID
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TaskPagination(BaseModel):
    page: int
    limit: int
    total: int
    has_next: bool
    has_prev: bool


class TaskListResponse(BaseModel):
    tasks: List[TaskRead]
    pagination: TaskPagination