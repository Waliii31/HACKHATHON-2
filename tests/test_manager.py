"""Unit tests for TodoManager CRUD operations.

This module contains comprehensive tests for all TodoManager methods including:
- Initialization
- Add task (with validation)
- Get all tasks
- Update task (with validation and error handling)
- Delete task (with error handling)
- Mark task complete/incomplete (with error handling)
- ID uniqueness and persistence
"""

import pytest
from src.manager import TodoManager
from src.models import Task, TaskStatus


class TestTodoManagerInit:
    """Test TodoManager initialization."""
    
    def test_manager_init(self):
        """Test TodoManager initializes with empty task list."""
        manager = TodoManager()
        
        assert manager._tasks == []
        assert manager._next_id == 1
    
    def test_manager_multiple_instances_independent(self):
        """Test multiple TodoManager instances are independent."""
        manager1 = TodoManager()
        manager2 = TodoManager()
        
        manager1.add_task("Task 1")
        
        assert len(manager1.get_all_tasks()) == 1
        assert len(manager2.get_all_tasks()) == 0


class TestAddTask:
    """Test add_task method."""
    
    def test_add_task_with_description(self):
        """Test adding task with title and description."""
        manager = TodoManager()
        
        task = manager.add_task("Buy groceries", "Milk, eggs, bread")
        
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.status == TaskStatus.INCOMPLETE
    
    def test_add_task_without_description(self):
        """Test adding task with title only (no description)."""
        manager = TodoManager()
        
        task = manager.add_task("Call dentist")
        
        assert task.id == 1
        assert task.title == "Call dentist"
        assert task.description is None
        assert task.status == TaskStatus.INCOMPLETE
    
    def test_add_task_generates_unique_sequential_ids(self):
        """Test adding multiple tasks generates unique sequential IDs."""
        manager = TodoManager()
        
        task1 = manager.add_task("Task 1")
        task2 = manager.add_task("Task 2")
        task3 = manager.add_task("Task 3")
        
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3
    
    def test_add_task_with_empty_title_raises_error(self):
        """Test adding task with empty title raises ValueError."""
        manager = TodoManager()
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.add_task("")
    
    def test_add_task_with_whitespace_title_raises_error(self):
        """Test adding task with whitespace-only title raises ValueError."""
        manager = TodoManager()
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.add_task("   ")
    
    def test_add_task_with_none_title_raises_error(self):
        """Test adding task with None title raises ValueError."""
        manager = TodoManager()
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.add_task(None)
    
    def test_add_task_with_long_title(self):
        """Test adding task with very long title succeeds."""
        manager = TodoManager()
        long_title = "A" * 200
        
        task = manager.add_task(long_title)
        
        assert task.title == long_title
        assert len(task.title) == 200


class TestGetAllTasks:
    """Test get_all_tasks method."""
    
    def test_get_all_tasks_empty(self):
        """Test get_all_tasks on empty manager returns empty list."""
        manager = TodoManager()
        
        tasks = manager.get_all_tasks()
        
        assert tasks == []
        assert isinstance(tasks, list)
    
    def test_get_all_tasks_returns_all_tasks(self):
        """Test get_all_tasks returns all added tasks."""
        manager = TodoManager()
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")
        
        tasks = manager.get_all_tasks()
        
        assert len(tasks) == 3
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
        assert tasks[2].title == "Task 3"
    
    def test_get_all_tasks_returns_copy(self):
        """Test get_all_tasks returns copy, not original list."""
        manager = TodoManager()
        manager.add_task("Task 1")
        
        tasks = manager.get_all_tasks()
        tasks.clear()  # Modify returned list
        
        # Original list should be unchanged
        assert len(manager.get_all_tasks()) == 1
    
    def test_get_all_tasks_preserves_insertion_order(self):
        """Test tasks are returned in insertion order (by ID)."""
        manager = TodoManager()
        task1 = manager.add_task("First")
        task2 = manager.add_task("Second")
        task3 = manager.add_task("Third")
        
        tasks = manager.get_all_tasks()
        
        assert tasks[0].id == task1.id
        assert tasks[1].id == task2.id
        assert tasks[2].id == task3.id


class TestGetTaskById:
    """Test _get_task_by_id helper method."""
    
    def test_get_task_by_id_found(self):
        """Test _get_task_by_id returns task when ID exists."""
        manager = TodoManager()
        added_task = manager.add_task("Test task")
        
        found_task = manager._get_task_by_id(1)
        
        assert found_task is not None
        assert found_task.id == added_task.id
        assert found_task.title == "Test task"
    
    def test_get_task_by_id_not_found(self):
        """Test _get_task_by_id returns None when ID doesn't exist."""
        manager = TodoManager()
        manager.add_task("Task 1")
        
        found_task = manager._get_task_by_id(999)
        
        assert found_task is None
    
    def test_get_task_by_id_after_multiple_adds(self):
        """Test _get_task_by_id finds correct task among multiple."""
        manager = TodoManager()
        manager.add_task("Task 1")
        task2 = manager.add_task("Task 2")
        manager.add_task("Task 3")
        
        found_task = manager._get_task_by_id(2)
        
        assert found_task.id == task2.id
        assert found_task.title == "Task 2"


class TestUpdateTask:
    """Test update_task method."""
    
    def test_update_task_title_only(self):
        """Test updating task title only (description unchanged)."""
        manager = TodoManager()
        task = manager.add_task("Old title", "Original description")
        
        updated = manager.update_task(1, title="New title")
        
        assert updated.title == "New title"
        assert updated.description == "Original description"
    
    def test_update_task_description_only(self):
        """Test updating task description only (title unchanged)."""
        manager = TodoManager()
        task = manager.add_task("Original title", "Old description")
        
        updated = manager.update_task(1, description="New description")
        
        assert updated.title == "Original title"
        assert updated.description == "New description"
    
    def test_update_task_both_fields(self):
        """Test updating both title and description."""
        manager = TodoManager()
        task = manager.add_task("Old title", "Old description")
        
        updated = manager.update_task(1, title="New title", description="New description")
        
        assert updated.title == "New title"
        assert updated.description == "New description"
    
    def test_update_task_returns_same_instance(self):
        """Test update_task returns the same Task instance."""
        manager = TodoManager()
        original = manager.add_task("Test")
        
        updated = manager.update_task(1, title="Updated")
        
        assert updated is original  # Same object
    
    def test_update_task_not_found_raises_error(self):
        """Test updating non-existent task raises ValueError."""
        manager = TodoManager()
        manager.add_task("Task 1")
        
        with pytest.raises(ValueError, match="Task with ID 999 not found"):
            manager.update_task(999, title="Test")
    
    def test_update_task_with_empty_title_raises_error(self):
        """Test updating with empty title raises ValueError."""
        manager = TodoManager()
        manager.add_task("Original title")
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.update_task(1, title="")
    
    def test_update_task_with_whitespace_title_raises_error(self):
        """Test updating with whitespace-only title raises ValueError."""
        manager = TodoManager()
        manager.add_task("Original title")
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.update_task(1, title="   ")
    
    def test_update_task_id_and_status_unchanged(self):
        """Test update doesn't change task ID or status."""
        manager = TodoManager()
        task = manager.add_task("Test")
        manager.mark_task_complete(1)
        
        updated = manager.update_task(1, title="Updated")
        
        assert updated.id == 1  # ID unchanged
        assert updated.status == TaskStatus.COMPLETE  # Status unchanged


class TestDeleteTask:
    """Test delete_task method."""
    
    def test_delete_task_removes_from_list(self):
        """Test delete_task removes task from list."""
        manager = TodoManager()
        manager.add_task("Task 1")
        
        manager.delete_task(1)
        
        assert len(manager.get_all_tasks()) == 0
    
    def test_delete_task_from_middle(self):
        """Test deleting task from middle preserves other tasks."""
        manager = TodoManager()
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")
        
        manager.delete_task(2)
        
        tasks = manager.get_all_tasks()
        assert len(tasks) == 2
        assert tasks[0].id == 1
        assert tasks[1].id == 3
    
    def test_delete_last_task(self):
        """Test deleting last task leaves empty list."""
        manager = TodoManager()
        manager.add_task("Only task")
        
        manager.delete_task(1)
        
        assert len(manager.get_all_tasks()) == 0
    
    def test_delete_task_not_found_raises_error(self):
        """Test deleting non-existent task raises ValueError."""
        manager = TodoManager()
        manager.add_task("Task 1")
        
        with pytest.raises(ValueError, match="Task with ID 999 not found"):
            manager.delete_task(999)
    
    def test_delete_from_empty_list_raises_error(self):
        """Test deleting from empty list raises ValueError."""
        manager = TodoManager()
        
        with pytest.raises(ValueError, match="Task with ID 1 not found"):
            manager.delete_task(1)
    
    def test_delete_task_decreases_count(self):
        """Test task count decreases after deletion."""
        manager = TodoManager()
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        
        initial_count = len(manager.get_all_tasks())
        manager.delete_task(1)
        final_count = len(manager.get_all_tasks())
        
        assert final_count == initial_count - 1


class TestMarkTaskComplete:
    """Test mark_task_complete method."""
    
    def test_mark_task_complete_changes_status(self):
        """Test marking incomplete task as complete changes status."""
        manager = TodoManager()
        task = manager.add_task("Test task")
        
        assert task.status == TaskStatus.INCOMPLETE
        
        completed = manager.mark_task_complete(1)
        
        assert completed.status == TaskStatus.COMPLETE
    
    def test_mark_task_complete_returns_task(self):
        """Test mark_task_complete returns the Task instance."""
        manager = TodoManager()
        original = manager.add_task("Test task")
        
        completed = manager.mark_task_complete(1)
        
        assert completed is original  # Same object
    
    def test_mark_complete_idempotent(self):
        """Test marking already complete task as complete is idempotent."""
        manager = TodoManager()
        manager.add_task("Test task")
        manager.mark_task_complete(1)
        
        # Mark complete again
        completed = manager.mark_task_complete(1)
        
        assert completed.status == TaskStatus.COMPLETE  # Still complete
    
    def test_mark_complete_not_found_raises_error(self):
        """Test marking non-existent task complete raises ValueError."""
        manager = TodoManager()
        manager.add_task("Task 1")
        
        with pytest.raises(ValueError, match="Task with ID 999 not found"):
            manager.mark_task_complete(999)


class TestMarkTaskIncomplete:
    """Test mark_task_incomplete method."""
    
    def test_mark_task_incomplete_changes_status(self):
        """Test marking complete task as incomplete changes status."""
        manager = TodoManager()
        task = manager.add_task("Test task")
        manager.mark_task_complete(1)
        
        assert task.status == TaskStatus.COMPLETE
        
        incomplete = manager.mark_task_incomplete(1)
        
        assert incomplete.status == TaskStatus.INCOMPLETE
    
    def test_mark_task_incomplete_returns_task(self):
        """Test mark_task_incomplete returns the Task instance."""
        manager = TodoManager()
        original = manager.add_task("Test task")
        manager.mark_task_complete(1)
        
        incomplete = manager.mark_task_incomplete(1)
        
        assert incomplete is original  # Same object
    
    def test_mark_incomplete_idempotent(self):
        """Test marking already incomplete task as incomplete is idempotent."""
        manager = TodoManager()
        manager.add_task("Test task")
        
        # Mark incomplete (already is incomplete)
        incomplete = manager.mark_task_incomplete(1)
        
        assert incomplete.status == TaskStatus.INCOMPLETE
    
    def test_mark_incomplete_not_found_raises_error(self):
        """Test marking non-existent task incomplete raises ValueError."""
        manager = TodoManager()
        manager.add_task("Task 1")
        
        with pytest.raises(ValueError, match="Task with ID 999 not found"):
            manager.mark_task_incomplete(999)


class TestIDPersistence:
    """Test ID uniqueness and persistence after deletion."""
    
    def test_id_not_reused_after_deletion(self):
        """Test IDs are never reused even after task deletion."""
        manager = TodoManager()
        
        task1 = manager.add_task("Task 1")  # ID=1
        task2 = manager.add_task("Task 2")  # ID=2
        
        manager.delete_task(1)  # Delete task 1
        
        task3 = manager.add_task("Task 3")  # Should be ID=3, not 1
        
        assert task3.id == 3
        assert task3.id != task1.id
    
    def test_next_id_counter_only_increases(self):
        """Test _next_id counter only increases, never decreases."""
        manager = TodoManager()
        
        manager.add_task("Task 1")
        assert manager._next_id == 2
        
        manager.add_task("Task 2")
        assert manager._next_id == 3
        
        manager.delete_task(1)
        assert manager._next_id == 3  # Unchanged after deletion
        
        manager.add_task("Task 3")
        assert manager._next_id == 4
    
    def test_id_uniqueness_across_many_operations(self):
        """Test ID uniqueness across many add/delete operations."""
        manager = TodoManager()
        
        # Add 5 tasks
        for i in range(1, 6):
            manager.add_task(f"Task {i}")
        
        # Delete tasks 2 and 4
        manager.delete_task(2)
        manager.delete_task(4)
        
        # Add 2 more tasks
        task6 = manager.add_task("Task 6")
        task7 = manager.add_task("Task 7")
        
        # Verify IDs are 6 and 7, not reusing 2 and 4
        assert task6.id == 6
        assert task7.id == 7
        
        # Verify remaining task IDs
        all_ids = [t.id for t in manager.get_all_tasks()]
        assert all_ids == [1, 3, 5, 6, 7]


class TestCompleteWorkflows:
    """Test complete CRUD workflows."""
    
    def test_complete_crud_workflow(self):
        """Test complete workflow: add → view → update → mark → delete."""
        manager = TodoManager()
        
        # Add
        task = manager.add_task("Buy groceries", "Milk, eggs")
        assert task.id == 1
        
        # View
        tasks = manager.get_all_tasks()
        assert len(tasks) == 1
        
        # Update
        updated = manager.update_task(1, title="Buy groceries today")
        assert updated.title == "Buy groceries today"
        
        # Mark complete
        completed = manager.mark_task_complete(1)
        assert completed.status == TaskStatus.COMPLETE
        
        # Mark incomplete
        incomplete = manager.mark_task_incomplete(1)
        assert incomplete.status == TaskStatus.INCOMPLETE
        
        # Delete
        manager.delete_task(1)
        assert len(manager.get_all_tasks()) == 0
    
    def test_multiple_tasks_workflow(self):
        """Test working with multiple tasks simultaneously."""
        manager = TodoManager()
        
        # Add multiple tasks
        manager.add_task("Task 1", "Description 1")
        manager.add_task("Task 2", "Description 2")
        manager.add_task("Task 3", "Description 3")
        
        # Mark some complete
        manager.mark_task_complete(1)
        manager.mark_task_complete(3)
        
        # Update one
        manager.update_task(2, title="Updated Task 2")
        
        # Verify states
        tasks = manager.get_all_tasks()
        assert tasks[0].status == TaskStatus.COMPLETE
        assert tasks[1].status == TaskStatus.INCOMPLETE
        assert tasks[1].title == "Updated Task 2"
        assert tasks[2].status == TaskStatus.COMPLETE
        
        # Delete middle task
        manager.delete_task(2)
        
        # Verify 2 tasks remain
        remaining = manager.get_all_tasks()
        assert len(remaining) == 2
        assert remaining[0].id == 1
        assert remaining[1].id == 3
