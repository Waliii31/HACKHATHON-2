# Implementation Plan: Todo Basic Level Functionality

**Branch**: `001-todo-basic-functionality` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-todo-basic-functionality/spec.md`

## Summary

Build a pure Python console application for managing todo tasks with five core operations: Add, View, Update, Delete, and Mark Complete/Incomplete. The application uses in-memory storage (no database) and operates entirely via command-line interface. All data is stored in a Python list of Task objects during runtime.

**Technical Approach**: Implement a three-layer architecture separating concerns:
1. **Data Layer** (`models.py`): Task data structure using Python dataclasses
2. **Logic Layer** (`manager.py`): TodoManager class handling CRUD operations and validation
3. **Interface Layer** (`main.py`): CLI loop processing user commands and displaying output

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: Standard library only (dataclasses, typing, enum)  
**Storage**: In-memory list of Task instances (no persistence)  
**Testing**: pytest with standard assertions  
**Target Platform**: Cross-platform console (Windows/Linux/macOS)  
**Project Type**: Single console application  
**Performance Goals**: < 100ms response for all operations with up to 10,000 tasks  
**Constraints**: 
- No external dependencies beyond Python stdlib
- No web frameworks (FastAPI, Flask, etc.)
- No database or file persistence
- Must follow PEP 8 with Google-style docstrings  

**Scale/Scope**: 
- 5 core features (CRUD + Status toggle)
- ~300-500 lines of production code
- ~15-20 functions/methods total
- Single-user, single-session usage

## Constitution Check

✅ **Python 3.13+ only** - Using Python 3.13 with modern type hints  
✅ **In-memory storage** - Using `list[Task]` as data store  
✅ **Pure Console Application** - No web frameworks, CLI-only interface  
✅ **PEP 8 compliance** - All code follows PEP 8 guidelines  
✅ **Google-style docstrings** - All functions include type hints and docstrings  
✅ **Clean separation** - Code organized in `/src` directory with clear module boundaries  
✅ **All 5 features** - Implementation plan covers Add, Delete, Update, View, Mark Complete

**No constitution violations detected**. This plan adheres to all requirements.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-basic-functionality/
├── spec.md             # Feature specification (COMPLETE)
└── plan.md             # This implementation plan
```

### Source Code (repository root)

```text
src/
├── __init__.py         # Package marker (empty)
├── models.py           # Task data class and Status enum
├── manager.py          # TodoManager class (CRUD logic)
└── main.py             # CLI interface and entry point

tests/
├── __init__.py         # Test package marker
├── test_models.py      # Task model unit tests
├── test_manager.py     # TodoManager unit tests
└── test_integration.py # End-to-end workflow tests

README.md               # Project overview and usage instructions
requirements-dev.txt    # Development dependencies (pytest)
```

**Structure Decision**: Single project structure is appropriate for this console application. All business logic resides in `/src`, tests in `/tests`. No need for web/mobile patterns since this is a pure CLI tool.

## Architecture Design

### 1. Data Model Layer (`src/models.py`)

**Purpose**: Define the Task entity and related enums with validation.

**Components**:

#### 1.1 TaskStatus Enum
```python
from enum import Enum

class TaskStatus(Enum):
    """Enumeration for task completion status."""
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"
```

**Rationale**: Using Enum ensures type safety and prevents invalid status values. Provides clear contract for valid states.

#### 1.2 Task Dataclass
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Task:
    """Represents a single todo item.
    
    Attributes:
        id: Unique integer identifier for the task (auto-assigned).
        title: Required non-empty string describing the task.
        description: Optional string providing additional task details.
        status: TaskStatus enum, defaults to INCOMPLETE.
    """
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus = field(default=TaskStatus.INCOMPLETE)
    
    def __post_init__(self) -> None:
        """Validate task data after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
```

**Design Decisions**:
- **Dataclass**: Provides automatic `__init__`, `__repr__`, `__eq__` methods, reducing boilerplate
- **Optional[str] for description**: Explicitly allows None values per spec requirement
- **Field default for status**: Ensures all tasks start as INCOMPLETE per FR-008
- **Post-init validation**: Catches empty titles at creation time (FR-009)
- **Immutable ID**: ID set at creation, never changed

**Attributes**:
- `id: int` - Unique identifier (never reused, even after deletion)
- `title: str` - Required, non-empty after stripping whitespace
- `description: Optional[str]` - Can be None or empty string
- `status: TaskStatus` - Enum value, defaults to INCOMPLETE

---

### 2. Logic Layer (`src/manager.py`)

**Purpose**: Encapsulate all business logic for task management with validation and error handling.

**Components**:

#### 2.1 TodoManager Class
```python
class TodoManager:
    """Manages in-memory task storage and CRUD operations.
    
    This class maintains a list of tasks and provides methods for adding,
    retrieving, updating, deleting, and changing task status. It handles
    ID generation and validation.
    """
    
    def __init__(self) -> None:
        """Initialize the todo manager with empty task list."""
        self._tasks: list[Task] = []
        self._next_id: int = 1  # Auto-incrementing ID counter
```

**ID Management Strategy**:
- **Auto-incrementing counter**: Start at 1, increment on each task creation
- **Never reuse IDs**: Even after deletion, counter only increases
- **Thread-safe for single user**: No locking needed (single-threaded CLI)
- **Guaranteed uniqueness**: Counter-based approach ensures no collisions

**Rationale**: Simple counter is sufficient for in-memory single-session usage. More complex UUID or timestamp-based IDs would be overkill.

#### 2.2 Core Methods

##### Add Task (FR-001, FR-002, FR-009)
```python
def add_task(self, title: str, description: Optional[str] = None) -> Task:
    """Add a new task to the todo list.
    
    Args:
        title: Required task title (must be non-empty).
        description: Optional task description.
    
    Returns:
        The newly created Task instance.
    
    Raises:
        ValueError: If title is empty or None.
    """
    # Validation happens in Task.__post_init__
    task = Task(id=self._next_id, title=title, description=description)
    self._tasks.append(task)
    self._next_id += 1
    return task
```

**Error Handling**: Relies on Task validation, propagates ValueError for empty titles.

##### Get All Tasks (FR-004)
```python
def get_all_tasks(self) -> list[Task]:
    """Retrieve all tasks.
    
    Returns:
        List of all Task instances, ordered by ID (insertion order).
    """
    return self._tasks.copy()  # Return copy to prevent external modification
```

**Rationale**: Returns copy to maintain encapsulation. Tasks ordered by ID naturally.

##### Get Task by ID (Internal utility for FR-011, FR-012, FR-013)
```python
def _get_task_by_id(self, task_id: int) -> Optional[Task]:
    """Find a task by its ID.
    
    Args:
        task_id: The ID of the task to find.
    
    Returns:
        The Task if found, None otherwise.
    """
    for task in self._tasks:
        if task.id == task_id:
            return task
    return None
```

**Rationale**: Private helper method to avoid code duplication. O(n) lookup is acceptable for expected scale.

##### Update Task (FR-005, FR-010, FR-011)
```python
def update_task(
    self, 
    task_id: int, 
    title: Optional[str] = None, 
    description: Optional[str] = None
) -> Task:
    """Update an existing task's title and/or description.
    
    Args:
        task_id: ID of the task to update.
        title: New title (if provided, must be non-empty).
        description: New description (can be None to keep current).
    
    Returns:
        The updated Task instance.
    
    Raises:
        ValueError: If title is provided but empty, or task_id not found.
    """
    task = self._get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"Task with ID {task_id} not found")
    
    if title is not None:
        if not title.strip():
            raise ValueError("Title cannot be empty")
        task.title = title
    
    if description is not None:
        task.description = description
    
    return task
```

**Design Decisions**:
- **Optional parameters**: Allow updating title-only, description-only, or both
- **None vs empty string**: `title=None` means "don't update", `title=""` is invalid
- **Explicit validation**: Check for empty title before assignment (FR-010)
- **Error messages**: Include task ID in error for debugging (FR-011)

##### Delete Task (FR-006, FR-012)
```python
def delete_task(self, task_id: int) -> None:
    """Delete a task by its ID.
    
    Args:
        task_id: ID of the task to delete.
    
    Raises:
        ValueError: If task_id not found.
    """
    task = self._get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"Task with ID {task_id} not found")
    
    self._tasks.remove(task)
```

**Rationale**: Simple removal from list. ID counter never decrements, maintaining uniqueness.

##### Mark Complete/Incomplete (FR-007, FR-013)
```python
def mark_task_complete(self, task_id: int) -> Task:
    """Mark a task as complete.
    
    Args:
        task_id: ID of the task to mark complete.
    
    Returns:
        The updated Task instance.
    
    Raises:
        ValueError: If task_id not found.
    """
    task = self._get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"Task with ID {task_id} not found")
    
    task.status = TaskStatus.COMPLETE
    return task

def mark_task_incomplete(self, task_id: int) -> Task:
    """Mark a task as incomplete.
    
    Args:
        task_id: ID of the task to mark incomplete.
    
    Returns:
        The updated Task instance.
    
    Raises:
        ValueError: If task_id not found.
    """
    task = self._get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"Task with ID {task_id} not found")
    
    task.status = TaskStatus.INCOMPLETE
    return task
```

**Rationale**: Separate methods for clarity. Idempotent operations (safe to call multiple times).

---

### 3. Interface Layer (`src/main.py`)

**Purpose**: Provide command-line interface for user interaction.

**Components**:

#### 3.1 Display Utilities
```python
def display_tasks(tasks: list[Task]) -> None:
    """Display all tasks in a formatted table.
    
    Args:
        tasks: List of Task instances to display.
    """
    if not tasks:
        print("\nNo tasks found.\n")
        return
    
    # Calculate column widths
    id_width = 4
    title_width = max(len(task.title) for task in tasks) + 2
    title_width = max(title_width, 20)  # Minimum width
    status_width = 12
    
    # Header
    print(f"\n{'ID':<{id_width}} | {'Title':<{title_width}} | {'Status':<{status_width}} | Description")
    print("-" * (id_width + title_width + status_width + 50))
    
    # Rows
    for task in tasks:
        desc = task.description or ""
        # Truncate long descriptions for display
        desc_display = desc[:80] + "..." if len(desc) > 80 else desc
        print(f"{task.id:<{id_width}} | {task.title:<{title_width}} | {task.status.value:<{status_width}} | {desc_display}")
    
    print()  # Blank line after table
```

**Design Decisions**:
- **Dynamic column widths**: Adapt to content but enforce minimums for readability
- **Description truncation**: Long descriptions show first 80 chars + "..." in list view
- **Clear formatting**: Uses pipes and dashes for table structure
- **Empty state handling**: Shows "No tasks found" when list is empty

#### 3.2 Menu System
```python
def show_menu() -> None:
    """Display the main menu options."""
    print("\n=== Todo Application ===")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete")
    print("6. Mark Task Incomplete")
    print("7. Exit")
    print("========================\n")
```

#### 3.3 Input Handlers

Each command has a dedicated handler function:

```python
def handle_add_task(manager: TodoManager) -> None:
    """Handle the add task command."""
    title = input("Enter task title: ").strip()
    description = input("Enter task description (optional): ").strip()
    
    # Convert empty description to None
    description = description if description else None
    
    try:
        task = manager.add_task(title, description)
        print(f"\n✓ Task added successfully! (ID: {task.id})")
    except ValueError as e:
        print(f"\n✗ Error: {e}")

def handle_view_tasks(manager: TodoManager) -> None:
    """Handle the view tasks command."""
    tasks = manager.get_all_tasks()
    display_tasks(tasks)

def handle_update_task(manager: TodoManager) -> None:
    """Handle the update task command."""
    try:
        task_id = int(input("Enter task ID to update: "))
        title = input("Enter new title (press Enter to skip): ").strip()
        description = input("Enter new description (press Enter to skip): ").strip()
        
        # None means "don't update", empty string means "update to empty"
        title = title if title else None
        description = description if description else None
        
        if title is None and description is None:
            print("\n! No changes specified.")
            return
        
        task = manager.update_task(task_id, title, description)
        print(f"\n✓ Task {task.id} updated successfully!")
    except ValueError as e:
        print(f"\n✗ Error: {e}")

def handle_delete_task(manager: TodoManager) -> None:
    """Handle the delete task command."""
    try:
        task_id = int(input("Enter task ID to delete: "))
        manager.delete_task(task_id)
        print(f"\n✓ Task {task_id} deleted successfully!")
    except ValueError as e:
        print(f"\n✗ Error: {e}")

def handle_mark_complete(manager: TodoManager) -> None:
    """Handle the mark complete command."""
    try:
        task_id = int(input("Enter task ID to mark complete: "))
        manager.mark_task_complete(task_id)
        print(f"\n✓ Task {task_id} marked as complete!")
    except ValueError as e:
        print(f"\n✗ Error: {e}")

def handle_mark_incomplete(manager: TodoManager) -> None:
    """Handle the mark incomplete command."""
    try:
        task_id = int(input("Enter task ID to mark incomplete: "))
        manager.mark_task_incomplete(task_id)
        print(f"\n✓ Task {task_id} marked as incomplete!")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
```

**Error Handling Strategy**:
- **Try-except blocks**: Catch ValueError from manager methods and invalid input
- **User-friendly messages**: Show ✓/✗ symbols and clear error text
- **Input validation**: Convert to int, handle non-numeric input gracefully
- **Empty input handling**: Distinguish between skip (None) and clear (empty string)

#### 3.4 Main Loop
```python
def main() -> None:
    """Main application entry point."""
    manager = TodoManager()
    
    while True:
        show_menu()
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            handle_add_task(manager)
        elif choice == "2":
            handle_view_tasks(manager)
        elif choice == "3":
            handle_update_task(manager)
        elif choice == "4":
            handle_delete_task(manager)
        elif choice == "5":
            handle_mark_complete(manager)
        elif choice == "6":
            handle_mark_incomplete(manager)
        elif choice == "7":
            print("\nGoodbye!\n")
            break
        else:
            print("\n✗ Invalid choice. Please enter a number between 1 and 7.\n")

if __name__ == "__main__":
    main()
```

**Design Decisions**:
- **Single manager instance**: Created once and passed to handlers
- **Infinite loop**: Runs until user selects Exit (7)
- **String-based menu**: Simple input matching, extensible for future features
- **Graceful exit**: Displays goodbye message before terminating

---

## Error Handling Strategy

### Validation Errors (FR-009, FR-010)
- **Empty title on add**: ValueError raised in `Task.__post_init__`, caught in CLI handler
- **Empty title on update**: ValueError raised in `TodoManager.update_task`, caught in CLI handler
- **User feedback**: Display clear message "Title cannot be empty"

### Not Found Errors (FR-011, FR-012, FR-013)
- **Missing task ID**: ValueError raised with message "Task with ID X not found"
- **Consistent across operations**: Update, Delete, Mark Complete/Incomplete all use same pattern
- **User feedback**: Display error message with task ID for debugging

### Invalid Input Format (FR-015)
- **Non-numeric ID**: Caught by `int()` conversion in CLI handlers
- **ValueError exception**: Handled in try-except block
- **User feedback**: "Invalid task ID format" or prompt retry

### Edge Cases
- **Empty task list**: `display_tasks` shows "No tasks found"
- **Long descriptions**: Truncated to 80 characters in table view (full text preserved in data)
- **Special characters**: Python strings handle Unicode natively, no special processing needed
- **ID overflow**: Python int has unlimited precision, practically impossible to overflow

---

## Testing Strategy

### Unit Tests (`tests/test_models.py`)
- Test Task creation with valid data
- Test Task validation (empty title rejection)
- Test TaskStatus enum values
- Test Task dataclass equality and repr

### Unit Tests (`tests/test_manager.py`)
- Test ID generation (sequential, unique)
- Test add_task success and validation
- Test get_all_tasks (empty, single, multiple)
- Test update_task (title only, description only, both, not found)
- Test delete_task (success, not found)
- Test mark_complete/incomplete (success, not found, idempotent)

### Integration Tests (`tests/test_integration.py`)
- Test complete workflow: add → view → update → mark complete → delete
- Test multiple tasks with different IDs
- Test ID persistence after deletion (no reuse)
- Test error recovery (invalid operations don't corrupt state)

### Test Coverage Goals
- **Line coverage**: > 90% for models.py and manager.py
- **Branch coverage**: > 80% for all error paths
- **Integration coverage**: All 5 features tested end-to-end

---

## Development Phases

### Phase 1: Data Model (2 hours)
1. Create `src/models.py` with TaskStatus enum
2. Implement Task dataclass with validation
3. Write unit tests for Task model
4. **Acceptance**: All model tests pass, empty title rejected

### Phase 2: Logic Layer (4 hours)
1. Create `src/manager.py` with TodoManager class
2. Implement ID generation strategy
3. Implement add_task, get_all_tasks
4. Implement update_task, delete_task
5. Implement mark_complete, mark_incomplete
6. Write comprehensive unit tests
7. **Acceptance**: All manager tests pass, error handling verified

### Phase 3: CLI Interface (3 hours)
1. Create `src/main.py` with menu system
2. Implement display_tasks formatter
3. Implement all command handlers
4. Implement main loop
5. Manual testing of full workflows
6. **Acceptance**: All 5 features accessible and functional

### Phase 4: Integration Testing (2 hours)
1. Write integration tests
2. Run full test suite
3. Fix any bugs discovered
4. **Acceptance**: All tests pass, > 90% coverage

### Phase 5: Documentation & Polish (1 hour)
1. Write README with usage instructions
2. Add code comments where needed
3. Run linter (pylint/flake8) and fix issues
4. **Acceptance**: PEP 8 compliant, README complete

**Total Estimated Time**: 12 hours

---

## Risk Analysis

### Risk 1: ID Collision After Deletion
**Probability**: Low | **Impact**: High  
**Mitigation**: Use auto-incrementing counter that never decreases  
**Verification**: Integration test confirms IDs not reused after deletion

### Risk 2: Long Description Display Issues
**Probability**: Medium | **Impact**: Low  
**Mitigation**: Truncate descriptions in table view, show full text on demand (future feature)  
**Verification**: Manual test with 500-character description

### Risk 3: Input Validation Edge Cases
**Probability**: Medium | **Impact**: Medium  
**Mitigation**: Comprehensive unit tests for all validation paths  
**Verification**: Test empty strings, whitespace-only, special characters, Unicode

### Risk 4: Python Version Compatibility
**Probability**: Low | **Impact**: Medium  
**Mitigation**: Explicitly require Python 3.13+ in README, use type hints correctly  
**Verification**: Test on Python 3.13 interpreter

---

## Non-Goals (Out of Scope)

- ❌ Data persistence (save to file/database) - Phase 2 feature
- ❌ Search or filter functionality - Future enhancement
- ❌ Task priorities or due dates - Future enhancement
- ❌ Multi-user support - Not required
- ❌ Undo/redo functionality - Future enhancement
- ❌ Task categories or tags - Future enhancement
- ❌ Web or GUI interface - Explicitly prohibited by constitution
- ❌ External dependencies - Constitution requires stdlib only

---

## Success Criteria

This implementation plan is complete when:

✅ All 18 functional requirements (FR-001 through FR-018) are implemented  
✅ All 10 success criteria (SC-001 through SC-010) are met  
✅ Unit test coverage > 90% for models and manager  
✅ Integration tests cover all 5 user stories  
✅ Code passes PEP 8 linter with no errors  
✅ All functions have Google-style docstrings with type hints  
✅ README includes installation and usage instructions  
✅ Constitution compliance verified (Python 3.13+, no external deps, CLI-only)

---

## Next Steps

1. ✅ **Review this plan** - Verify alignment with spec and constitution
2. ⏭️ **Run `/sp.tasks`** - Generate detailed task breakdown from this plan
3. ⏭️ **Implement Phase 1** - Start with data model layer
4. ⏭️ **TDD approach** - Write tests first, then implementation
5. ⏭️ **Incremental delivery** - Complete each phase before moving to next
