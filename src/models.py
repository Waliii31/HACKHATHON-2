"""Data models for the Todo application.

This module defines the core data structures used throughout the application:
- TaskStatus: Enumeration for task completion states
- Task: Dataclass representing a single todo item with validation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    """Enumeration for task completion status.
    
    Attributes:
        INCOMPLETE: Task is not yet complete (default state).
        COMPLETE: Task has been completed.
    """
    
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


@dataclass
class Task:
    """Represents a single todo item.
    
    This class uses Python's dataclass decorator to automatically generate
    __init__, __repr__, and __eq__ methods. Post-initialization validation
    ensures data integrity.
    
    Attributes:
        id: Unique integer identifier for the task (assigned by TodoManager).
        title: Required non-empty string describing the task.
        description: Optional string providing additional task details.
        status: TaskStatus enum indicating completion state (defaults to INCOMPLETE).
    
    Raises:
        ValueError: If title is None, empty, or contains only whitespace.
    
    Example:
        >>> task = Task(id=1, title="Buy groceries", description="Milk and eggs")
        >>> task.status
        <TaskStatus.INCOMPLETE: 'incomplete'>
        
        >>> task = Task(id=2, title="")
        Traceback (most recent call last):
            ...
        ValueError: Title cannot be empty
    """
    
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus = field(default=TaskStatus.INCOMPLETE)
    
    def __post_init__(self) -> None:
        """Validate task data after initialization.
        
        Ensures that the title is not None, empty, or whitespace-only.
        This validation runs automatically after __init__ is called.
        
        Raises:
            ValueError: If title is invalid (None, empty, or whitespace-only).
        """
        if self.title is None or not self.title.strip():
            raise ValueError("Title cannot be empty")
