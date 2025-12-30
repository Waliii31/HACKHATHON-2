"""Business logic layer for managing todo tasks.

This module provides the TodoManager class which handles all CRUD operations
on tasks stored in memory. It maintains an auto-incrementing ID counter and
provides methods for creating, reading, updating, deleting, and changing task status.
"""

from typing import Optional
from src.models import Task, TaskStatus


class TodoManager:
    """Manages in-memory task storage and CRUD operations.
    
    This class maintains a list of tasks and provides methods for adding,
    retrieving, updating, deleting, and changing task status. It handles
    automatic ID generation using an auto-incrementing counter.
    
    The ID counter starts at 1 and never decreases, ensuring that IDs are
    never reused even after tasks are deleted. This guarantees uniqueness
    for the lifetime of the TodoManager instance.
    
    Attributes:
        _tasks: Private list storing all Task instances.
        _next_id: Private counter for generating unique task IDs.
    
    Example:
        >>> manager = TodoManager()
        >>> task = manager.add_task("Buy groceries", "Milk and eggs")
        >>> task.id
        1
        >>> task.status
        <TaskStatus.INCOMPLETE: 'incomplete'>
        >>> len(manager.get_all_tasks())
        1
    """
    
    def __init__(self) -> None:
        """Initialize the todo manager with empty task list.
        
        Creates an empty list for storing tasks and initializes the ID
        counter to 1. The counter will auto-increment with each task added.
        """
        self._tasks: list[Task] = []
        self._next_id: int = 1
    
    def add_task(self, title: str, description: Optional[str] = None) -> Task:
        """Add a new task to the todo list.
        
        Creates a new Task instance with a unique auto-generated ID and
        default status of INCOMPLETE. The task is appended to the internal
        task list and the ID counter is incremented.
        
        Args:
            title: Required task title (must be non-empty after stripping whitespace).
            description: Optional task description (can be None or empty string).
        
        Returns:
            The newly created Task instance with assigned ID and default status.
        
        Raises:
            ValueError: If title is None, empty, or contains only whitespace.
                This exception is raised by the Task.__post_init__ validation.
        
        Example:
            >>> manager = TodoManager()
            >>> task1 = manager.add_task("Buy groceries", "Milk, eggs, bread")
            >>> task1.id
            1
            >>> task1.title
            'Buy groceries'
            >>> task1.status
            <TaskStatus.INCOMPLETE: 'incomplete'>
            
            >>> task2 = manager.add_task("Call dentist")
            >>> task2.id
            2
            >>> task2.description is None
            True
            
            >>> manager.add_task("")  # Raises ValueError
            Traceback (most recent call last):
                ...
            ValueError: Title cannot be empty
        """
        # Create task with auto-generated ID
        # Task.__post_init__ will validate the title
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            status=TaskStatus.INCOMPLETE
        )
        
        # Add to task list
        self._tasks.append(task)
        
        # Increment ID counter (never decreases, ensuring uniqueness)
        self._next_id += 1
        
        return task
    
    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks.
        
        Returns a copy of the internal task list to prevent external
        modification. Tasks are ordered by ID (insertion order).
        
        Returns:
            List of all Task instances. Returns empty list if no tasks exist.
        
        Example:
            >>> manager = TodoManager()
            >>> manager.get_all_tasks()
            []
            
            >>> manager.add_task("Buy groceries")
            >>> manager.add_task("Call dentist")
            >>> tasks = manager.get_all_tasks()
            >>> len(tasks)
            2
            >>> tasks[0].id
            1
            >>> tasks[1].id
            2
        """
        # Return copy to maintain encapsulation and prevent external modification
        return self._tasks.copy()
    
    def _get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Find a task by its ID (private helper method).
        
        Searches the internal task list for a task with the specified ID.
        This is a private helper method used by update, delete, and mark
        status methods to avoid code duplication.
        
        Args:
            task_id: The ID of the task to find.
        
        Returns:
            The Task instance if found, None otherwise.
        
        Note:
            This method performs a linear search (O(n)). For the expected
            scale of this application (hundreds of tasks), this is acceptable.
        
        Example:
            >>> manager = TodoManager()
            >>> task = manager.add_task("Buy groceries")
            >>> found = manager._get_task_by_id(1)
            >>> found.title
            'Buy groceries'
            >>> manager._get_task_by_id(999) is None
            True
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None
    
    def delete_task(self, task_id: int) -> None:
        """Delete a task by its ID.
        
        Removes the task with the specified ID from the task list.
        The ID counter is not affected by deletion - IDs are never reused.
        
        Args:
            task_id: ID of the task to delete.
        
        Raises:
            ValueError: If no task with the specified ID exists.
        
        Example:
            >>> manager = TodoManager()
            >>> task1 = manager.add_task("Buy groceries")
            >>> task2 = manager.add_task("Call dentist")
            >>> task3 = manager.add_task("Clean house")
            
            >>> manager.delete_task(2)  # Delete middle task
            >>> tasks = manager.get_all_tasks()
            >>> len(tasks)
            2
            >>> [t.id for t in tasks]
            [1, 3]
            
            >>> manager.delete_task(999)  # Non-existent ID
            Traceback (most recent call last):
                ...
            ValueError: Task with ID 999 not found
            
            >>> # ID counter doesn't reuse deleted IDs
            >>> task4 = manager.add_task("New task")
            >>> task4.id
            4
        """
        task = self._get_task_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found")
        
        self._tasks.remove(task)
    
    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Task:
        """Update an existing task's title and/or description.
        
        Allows updating the title only, description only, or both fields.
        If a parameter is None, that field is not updated. The task's ID
        and status are never modified by this method.
        
        Args:
            task_id: ID of the task to update.
            title: New title (if provided, must be non-empty). None means no change.
            description: New description (can be None to keep current, or empty string).
        
        Returns:
            The updated Task instance.
        
        Raises:
            ValueError: If task_id not found, or if title is provided but empty/whitespace.
        
        Example:
            >>> manager = TodoManager()
            >>> task = manager.add_task("Buy groceries", "Milk")
            
            >>> # Update title only
            >>> updated = manager.update_task(1, title="Buy groceries today")
            >>> updated.title
            'Buy groceries today'
            >>> updated.description
            'Milk'
            
            >>> # Update description only
            >>> updated = manager.update_task(1, description="Milk, eggs, bread")
            >>> updated.title
            'Buy groceries today'
            >>> updated.description
            'Milk, eggs, bread'
            
            >>> # Update both
            >>> updated = manager.update_task(1, title="Shop", description="Food items")
            >>> updated.title
            'Shop'
            
            >>> # Error: Non-existent ID
            >>> manager.update_task(999, title="Test")
            Traceback (most recent call last):
                ...
            ValueError: Task with ID 999 not found
            
            >>> # Error: Empty title
            >>> manager.update_task(1, title="")
            Traceback (most recent call last):
                ...
            ValueError: Title cannot be empty
        """
        task = self._get_task_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Validate and update title if provided
        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            task.title = title
        
        # Update description if provided (including None or empty string)
        if description is not None:
            task.description = description
        
        return task
    
    def mark_task_complete(self, task_id: int) -> Task:
        """Mark a task as complete.
        
        Changes the task's status to COMPLETE. This operation is idempotent -
        marking an already complete task as complete has no effect.
        
        Args:
            task_id: ID of the task to mark complete.
        
        Returns:
            The updated Task instance with status set to COMPLETE.
        
        Raises:
            ValueError: If no task with the specified ID exists.
        
        Example:
            >>> manager = TodoManager()
            >>> task = manager.add_task("Buy groceries")
            >>> task.status
            <TaskStatus.INCOMPLETE: 'incomplete'>
            
            >>> completed = manager.mark_task_complete(1)
            >>> completed.status
            <TaskStatus.COMPLETE: 'complete'>
            
            >>> # Idempotent - no error if already complete
            >>> completed = manager.mark_task_complete(1)
            >>> completed.status
            <TaskStatus.COMPLETE: 'complete'>
            
            >>> # Error: Non-existent ID
            >>> manager.mark_task_complete(999)
            Traceback (most recent call last):
                ...
            ValueError: Task with ID 999 not found
        """
        task = self._get_task_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found")
        
        task.status = TaskStatus.COMPLETE
        return task
    
    def mark_task_incomplete(self, task_id: int) -> Task:
        """Mark a task as incomplete.
        
        Changes the task's status to INCOMPLETE. This operation is idempotent -
        marking an already incomplete task as incomplete has no effect.
        
        Args:
            task_id: ID of the task to mark incomplete.
        
        Returns:
            The updated Task instance with status set to INCOMPLETE.
        
        Raises:
            ValueError: If no task with the specified ID exists.
        
        Example:
            >>> manager = TodoManager()
            >>> task = manager.add_task("Buy groceries")
            >>> completed = manager.mark_task_complete(1)
            >>> completed.status
            <TaskStatus.COMPLETE: 'complete'>
            
            >>> # Mark back to incomplete
            >>> incomplete = manager.mark_task_incomplete(1)
            >>> incomplete.status
            <TaskStatus.INCOMPLETE: 'incomplete'>
            
            >>> # Idempotent - no error if already incomplete
            >>> incomplete = manager.mark_task_incomplete(1)
            >>> incomplete.status
            <TaskStatus.INCOMPLETE: 'incomplete'>
            
            >>> # Error: Non-existent ID
            >>> manager.mark_task_incomplete(999)
            Traceback (most recent call last):
                ...
            ValueError: Task with ID 999 not found
        """
        task = self._get_task_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found")
        
        task.status = TaskStatus.INCOMPLETE
        return task
