# Tasks: Todo Basic Level Functionality

**Input**: Design documents from `/specs/001-todo-basic-functionality/`  
**Prerequisites**: plan.md ✅, spec.md ✅  
**Constitution**: v1.0.0  
**Date**: 2025-12-17

**Tests**: Tests are REQUIRED for this feature per constitution requirements (>90% coverage).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story following priority order (P1 → P2 → P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] **T-001** Create project directory structure: `src/`, `tests/` at repository root
- [ ] **T-002** [P] Create empty `src/__init__.py` package marker
- [ ] **T-003** [P] Create empty `tests/__init__.py` package marker
- [ ] **T-004** [P] Create `requirements-dev.txt` with pytest dependency
- [ ] **T-005** [P] Create `README.md` with project overview and setup instructions

**Checkpoint**: ✅ Project structure ready for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] **T-006** [P] Create `src/models.py` with TaskStatus enum
  - **File**: `src/models.py`
  - **Requirements**: FR-008 (default status), FR-018 (in-memory storage)
  - **Details**: Define `TaskStatus(Enum)` with INCOMPLETE and COMPLETE values

- [ ] **T-007** Create Task dataclass in `src/models.py`
  - **File**: `src/models.py`
  - **Requirements**: FR-001 (required title, optional description), FR-002 (unique ID), FR-008 (default status)
  - **Details**: Define `@dataclass Task` with: id (int), title (str), description (Optional[str]), status (TaskStatus)
  - **Dependencies**: T-006 (requires TaskStatus enum)

- [ ] **T-008** Add Task validation in `__post_init__` method
  - **File**: `src/models.py` → `Task.__post_init__`
  - **Requirements**: FR-009 (reject empty title), FR-010 (reject empty title on update)
  - **Details**: Raise ValueError if title is empty or only whitespace
  - **Dependencies**: T-007 (requires Task dataclass)

- [ ] **T-009** [P] Write unit tests for TaskStatus enum in `tests/test_models.py`
  - **File**: `tests/test_models.py` → `test_task_status_enum`
  - **Requirements**: SC-008 (code quality), SC-009 (docstrings)
  - **Test Cases**: 
    - Verify INCOMPLETE value is "incomplete"
    - Verify COMPLETE value is "complete"

- [ ] **T-010** [P] Write unit tests for Task creation in `tests/test_models.py`
  - **File**: `tests/test_models.py` → `test_task_creation_valid`, `test_task_creation_invalid`
  - **Requirements**: FR-001, FR-009, SC-002 (error handling)
  - **Test Cases**:
    - Valid task with title and description
    - Valid task with title only (description=None)
    - Invalid task with empty title (should raise ValueError)
    - Invalid task with None title (should raise ValueError)
    - Invalid task with whitespace-only title (should raise ValueError)

**Checkpoint**: ✅ Foundation ready - TodoManager can now be built

---

## Phase 3: User Story 1 - Add New Task (Priority: P1) 🎯 MVP

**Goal**: Implement the ability to add tasks with unique IDs and validation

**Independent Test**: Launch app, add task with title "Test", verify it's created with ID=1 and status="incomplete"

**Requirements**: FR-001, FR-002, FR-003, FR-008, FR-009, FR-018

### Tests for User Story 1 (Write tests FIRST)

- [ ] **T-011** [P] [US1] Write TodoManager init test in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_manager_init`
  - **Requirements**: FR-003 (in-memory storage), FR-018 (data in memory)
  - **Test Cases**:
    - TodoManager initializes with empty task list
    - TodoManager initializes with _next_id = 1

- [ ] **T-012** [P] [US1] Write add_task success tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_add_task_with_description`, `test_add_task_without_description`
  - **Requirements**: FR-001, FR-002, FR-008
  - **Test Cases**:
    - Add task with title and description creates task with id=1, status=INCOMPLETE
    - Add task with title only creates task with id=2, description=None
    - Adding multiple tasks generates unique sequential IDs (1, 2, 3...)

- [ ] **T-013** [P] [US1] Write add_task validation tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_add_task_empty_title`, `test_add_task_whitespace_title`
  - **Requirements**: FR-009, SC-002 (error handling), SC-004 (reject invalid inputs)
  - **Test Cases**:
    - Add task with empty title raises ValueError
    - Add task with whitespace-only title raises ValueError
    - Error message contains "Title cannot be empty"

### Implementation for User Story 1

- [ ] **T-014** Create TodoManager class in `src/manager.py`
  - **File**: `src/manager.py` → `class TodoManager`
  - **Requirements**: FR-003 (in-memory storage), FR-018 (in-memory data)
  - **Details**: Define class with `__init__` method, `_tasks: list[Task] = []`, `_next_id: int = 1`

- [ ] **T-015** [US1] Implement add_task method in TodoManager
  - **File**: `src/manager.py` → `TodoManager.add_task`
  - **Requirements**: FR-001, FR-002, FR-008, FR-009
  - **Details**: Create Task with next_id, append to _tasks, increment _next_id, return Task
  - **Signature**: `def add_task(self, title: str, description: Optional[str] = None) -> Task`
  - **Dependencies**: T-014 (requires TodoManager class)

- [ ] **T-016** [US1] Add Google-style docstring to add_task method
  - **File**: `src/manager.py` → `TodoManager.add_task`
  - **Requirements**: SC-008 (PEP 8), SC-009 (Google-style docstrings)
  - **Details**: Document Args, Returns, Raises with type hints
  - **Dependencies**: T-015 (requires add_task implementation)

- [ ] **T-017** [US1] Run tests for User Story 1 and verify they pass
  - **Command**: `pytest tests/test_manager.py::test_add_task* -v`
  - **Requirements**: SC-001 (Add feature functional)
  - **Dependencies**: T-011, T-012, T-013, T-015 (all US1 tests and implementation)

**Checkpoint**: ✅ User Story 1 complete - Can add tasks with unique IDs

---

## Phase 4: User Story 2 - View All Tasks (Priority: P2)

**Goal**: Implement the ability to retrieve all tasks in memory

**Independent Test**: Add 3 tasks, call get_all_tasks(), verify all 3 are returned with ID, Title, Status, Description

**Requirements**: FR-004, FR-018

### Tests for User Story 2 (Write tests FIRST)

- [ ] **T-018** [P] [US2] Write get_all_tasks tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_get_all_tasks_empty`, `test_get_all_tasks_multiple`
  - **Requirements**: FR-004, SC-006 (display required fields)
  - **Test Cases**:
    - get_all_tasks on empty manager returns empty list
    - get_all_tasks after adding 3 tasks returns list of 3 tasks
    - Returned tasks are copies (modifying returned list doesn't affect internal storage)
    - Tasks are ordered by ID (insertion order)

### Implementation for User Story 2

- [ ] **T-019** [US2] Implement get_all_tasks method in TodoManager
  - **File**: `src/manager.py` → `TodoManager.get_all_tasks`
  - **Requirements**: FR-004, SC-006 (display ID, Title, Status, Description)
  - **Details**: Return copy of _tasks list to prevent external modification
  - **Signature**: `def get_all_tasks(self) -> list[Task]`
  - **Dependencies**: T-014 (requires TodoManager class)

- [ ] **T-020** [US2] Add Google-style docstring to get_all_tasks method
  - **File**: `src/manager.py` → `TodoManager.get_all_tasks`
  - **Requirements**: SC-008, SC-009
  - **Details**: Document Returns with type hint
  - **Dependencies**: T-019 (requires get_all_tasks implementation)

- [ ] **T-021** [US2] Run tests for User Story 2 and verify they pass
  - **Command**: `pytest tests/test_manager.py::test_get_all_tasks* -v`
  - **Requirements**: SC-001 (View feature functional)
  - **Dependencies**: T-018, T-019 (all US2 tests and implementation)

**Checkpoint**: ✅ User Story 2 complete - Can view all tasks

---

## Phase 5: User Story 3 - Update Existing Task (Priority: P3)

**Goal**: Implement the ability to update task title and/or description by ID

**Independent Test**: Add task with ID=1, update title to "New Title", verify task.title changed

**Requirements**: FR-005, FR-010, FR-011, FR-014, FR-015

### Tests for User Story 3 (Write tests FIRST)

- [ ] **T-022** [P] [US3] Write _get_task_by_id helper tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_get_task_by_id_found`, `test_get_task_by_id_not_found`
  - **Requirements**: FR-014 (validate ID exists)
  - **Test Cases**:
    - _get_task_by_id returns Task when ID exists
    - _get_task_by_id returns None when ID doesn't exist

- [ ] **T-023** [P] [US3] Write update_task success tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_update_task_title_only`, `test_update_task_description_only`, `test_update_task_both`
  - **Requirements**: FR-005, SC-003 (update workflow)
  - **Test Cases**:
    - Update task title only (description unchanged)
    - Update task description only (title unchanged)
    - Update both title and description
    - Update returns the modified Task instance

- [ ] **T-024** [P] [US3] Write update_task error tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_update_task_not_found`, `test_update_task_empty_title`
  - **Requirements**: FR-010, FR-011, SC-002 (error handling), SC-004 (reject invalid inputs)
  - **Test Cases**:
    - Update non-existent task ID raises ValueError with "Task with ID X not found"
    - Update with empty title raises ValueError with "Title cannot be empty"
    - Update with whitespace-only title raises ValueError

### Implementation for User Story 3

- [ ] **T-025** [US3] Implement _get_task_by_id helper method in TodoManager
  - **File**: `src/manager.py` → `TodoManager._get_task_by_id`
  - **Requirements**: FR-014 (validate ID before operations)
  - **Details**: Private method that searches _tasks by ID, returns Task or None
  - **Signature**: `def _get_task_by_id(self, task_id: int) -> Optional[Task]`
  - **Dependencies**: T-014 (requires TodoManager class)

- [ ] **T-026** [US3] Implement update_task method in TodoManager
  - **File**: `src/manager.py` → `TodoManager.update_task`
  - **Requirements**: FR-005, FR-010, FR-011, FR-014
  - **Details**: Use _get_task_by_id, validate title if provided, update fields, return Task
  - **Signature**: `def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Task`
  - **Dependencies**: T-025 (requires _get_task_by_id helper)

- [ ] **T-027** [US3] Add Google-style docstrings to update methods
  - **File**: `src/manager.py` → `TodoManager._get_task_by_id`, `TodoManager.update_task`
  - **Requirements**: SC-008, SC-009
  - **Details**: Document Args, Returns, Raises with type hints
  - **Dependencies**: T-025, T-026 (requires both methods implemented)

- [ ] **T-028** [US3] Run tests for User Story 3 and verify they pass
  - **Command**: `pytest tests/test_manager.py::test_update_task* tests/test_manager.py::test_get_task_by_id* -v`
  - **Requirements**: SC-001 (Update feature functional), SC-003 (complete workflow)
  - **Dependencies**: T-022, T-023, T-024, T-025, T-026 (all US3 tests and implementation)

**Checkpoint**: ✅ User Story 3 complete - Can update tasks by ID

---

## Phase 6: User Story 4 - Delete Task (Priority: P3)

**Goal**: Implement the ability to delete tasks by ID

**Independent Test**: Add 3 tasks, delete task with ID=2, verify only IDs 1 and 3 remain

**Requirements**: FR-006, FR-012, FR-014, FR-015

### Tests for User Story 4 (Write tests FIRST)

- [ ] **T-029** [P] [US4] Write delete_task success tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_delete_task_success`, `test_delete_task_middle`
  - **Requirements**: FR-006, SC-001 (Delete feature functional)
  - **Test Cases**:
    - Delete task removes it from list
    - Delete task from middle preserves other tasks
    - Delete last task leaves empty list
    - Task count decreases after deletion

- [ ] **T-030** [P] [US4] Write delete_task error tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_delete_task_not_found`, `test_delete_task_invalid_id`
  - **Requirements**: FR-012, SC-002 (error handling), SC-004 (reject invalid inputs)
  - **Test Cases**:
    - Delete non-existent task ID raises ValueError with "Task with ID X not found"
    - Delete from empty list raises ValueError

- [ ] **T-031** [P] [US4] Write ID persistence test in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_id_not_reused_after_deletion`
  - **Requirements**: FR-002 (unique ID), SC-005 (IDs never reused)
  - **Test Cases**:
    - Add task (ID=1), add task (ID=2), delete task 1, add task (ID=3, not 1)
    - Verify _next_id counter only increases, never decreases

### Implementation for User Story 4

- [ ] **T-032** [US4] Implement delete_task method in TodoManager
  - **File**: `src/manager.py` → `TodoManager.delete_task`
  - **Requirements**: FR-006, FR-012, FR-014
  - **Details**: Use _get_task_by_id, raise if not found, remove from _tasks
  - **Signature**: `def delete_task(self, task_id: int) -> None`
  - **Dependencies**: T-025 (requires _get_task_by_id helper)

- [ ] **T-033** [US4] Add Google-style docstring to delete_task method
  - **File**: `src/manager.py` → `TodoManager.delete_task`
  - **Requirements**: SC-008, SC-009
  - **Details**: Document Args, Raises with type hints
  - **Dependencies**: T-032 (requires delete_task implementation)

- [ ] **T-034** [US4] Run tests for User Story 4 and verify they pass
  - **Command**: `pytest tests/test_manager.py::test_delete_task* tests/test_manager.py::test_id_not_reused* -v`
  - **Requirements**: SC-001 (Delete feature functional), SC-005 (ID uniqueness)
  - **Dependencies**: T-029, T-030, T-031, T-032 (all US4 tests and implementation)

**Checkpoint**: ✅ User Story 4 complete - Can delete tasks by ID

---

## Phase 7: User Story 5 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Implement the ability to toggle task status by ID

**Independent Test**: Add task (status=incomplete), mark complete, verify status="complete", mark incomplete, verify status="incomplete"

**Requirements**: FR-007, FR-013, FR-014, FR-015

### Tests for User Story 5 (Write tests FIRST)

- [ ] **T-035** [P] [US5] Write mark_task_complete tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_mark_task_complete_success`, `test_mark_complete_idempotent`
  - **Requirements**: FR-007, SC-001 (Mark feature functional)
  - **Test Cases**:
    - Mark incomplete task as complete changes status to COMPLETE
    - Mark already complete task as complete remains COMPLETE (idempotent)
    - Method returns the modified Task instance

- [ ] **T-036** [P] [US5] Write mark_task_incomplete tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_mark_task_incomplete_success`, `test_mark_incomplete_idempotent`
  - **Requirements**: FR-007, SC-001
  - **Test Cases**:
    - Mark complete task as incomplete changes status to INCOMPLETE
    - Mark already incomplete task as incomplete remains INCOMPLETE (idempotent)
    - Method returns the modified Task instance

- [ ] **T-037** [P] [US5] Write mark status error tests in `tests/test_manager.py`
  - **File**: `tests/test_manager.py` → `test_mark_complete_not_found`, `test_mark_incomplete_not_found`
  - **Requirements**: FR-013, SC-002 (error handling), SC-004 (reject invalid inputs)
  - **Test Cases**:
    - Mark non-existent task complete raises ValueError with "Task with ID X not found"
    - Mark non-existent task incomplete raises ValueError with "Task with ID X not found"

### Implementation for User Story 5

- [ ] **T-038** [US5] Implement mark_task_complete method in TodoManager
  - **File**: `src/manager.py` → `TodoManager.mark_task_complete`
  - **Requirements**: FR-007, FR-013, FR-014
  - **Details**: Use _get_task_by_id, raise if not found, set status to COMPLETE, return Task
  - **Signature**: `def mark_task_complete(self, task_id: int) -> Task`
  - **Dependencies**: T-025 (requires _get_task_by_id helper)

- [ ] **T-039** [US5] Implement mark_task_incomplete method in TodoManager
  - **File**: `src/manager.py` → `TodoManager.mark_task_incomplete`
  - **Requirements**: FR-007, FR-013, FR-014
  - **Details**: Use _get_task_by_id, raise if not found, set status to INCOMPLETE, return Task
  - **Signature**: `def mark_task_incomplete(self, task_id: int) -> Task`
  - **Dependencies**: T-025 (requires _get_task_by_id helper)

- [ ] **T-040** [US5] Add Google-style docstrings to mark status methods
  - **File**: `src/manager.py` → `TodoManager.mark_task_complete`, `TodoManager.mark_task_incomplete`
  - **Requirements**: SC-008, SC-009
  - **Details**: Document Args, Returns, Raises with type hints
  - **Dependencies**: T-038, T-039 (requires both methods implemented)

- [ ] **T-041** [US5] Run tests for User Story 5 and verify they pass
  - **Command**: `pytest tests/test_manager.py::test_mark_task* -v`
  - **Requirements**: SC-001 (Mark feature functional), SC-003 (complete workflow)
  - **Dependencies**: T-035, T-036, T-037, T-038, T-039 (all US5 tests and implementation)

**Checkpoint**: ✅ User Story 5 complete - Can mark tasks complete/incomplete

---

## Phase 8: CLI Interface Implementation

**Purpose**: Build user interface for all implemented features

**Requirements**: FR-016 (CLI application), FR-017 (Python 3.13+), SC-010 (pure console app)

### Tests for CLI (Integration Testing)

- [ ] **T-042** [P] Write integration test for add workflow in `tests/test_integration.py`
  - **File**: `tests/test_integration.py` → `test_add_task_workflow`
  - **Requirements**: SC-003 (complete workflow: add → view)
  - **Test Cases**:
    - Add task, verify it appears in get_all_tasks output
    - Add multiple tasks, verify all appear with correct IDs

- [ ] **T-043** [P] Write integration test for update workflow in `tests/test_integration.py`
  - **File**: `tests/test_integration.py` → `test_update_task_workflow`
  - **Requirements**: SC-003 (complete workflow: add → update → view)
  - **Test Cases**:
    - Add task, update title, verify change persists
    - Add task, update description, verify change persists

- [ ] **T-044** [P] Write integration test for delete workflow in `tests/test_integration.py`
  - **File**: `tests/test_integration.py` → `test_delete_task_workflow`
  - **Requirements**: SC-003 (complete workflow: add → delete → view)
  - **Test Cases**:
    - Add 3 tasks, delete middle task, verify 2 remain
    - Add task, delete it, verify empty list

- [ ] **T-045** [P] Write integration test for complete workflow in `tests/test_integration.py`
  - **File**: `tests/test_integration.py` → `test_complete_workflow`
  - **Requirements**: SC-003 (complete workflow: add → view → update → mark → delete)
  - **Test Cases**:
    - Add task → view → update → mark complete → mark incomplete → delete
    - Verify each operation succeeds and state changes correctly

### CLI Implementation

- [ ] **T-046** Create display_tasks function in `src/main.py`
  - **File**: `src/main.py` → `display_tasks`
  - **Requirements**: FR-004, SC-006 (display ID, Title, Status, Description)
  - **Details**: Format tasks as table with dynamic column widths, handle empty list, truncate long descriptions
  - **Signature**: `def display_tasks(tasks: list[Task]) -> None`

- [ ] **T-047** [P] Create show_menu function in `src/main.py`
  - **File**: `src/main.py` → `show_menu`
  - **Requirements**: FR-016 (CLI application)
  - **Details**: Display numbered menu with 7 options (Add, View, Update, Delete, Mark Complete, Mark Incomplete, Exit)
  - **Signature**: `def show_menu() -> None`

- [ ] **T-048** [P] Create handle_add_task function in `src/main.py`
  - **File**: `src/main.py` → `handle_add_task`
  - **Requirements**: FR-001, FR-009, SC-004 (reject invalid inputs)
  - **Details**: Prompt for title and description, call manager.add_task, display success/error
  - **Signature**: `def handle_add_task(manager: TodoManager) -> None`

- [ ] **T-049** [P] Create handle_view_tasks function in `src/main.py`
  - **File**: `src/main.py` → `handle_view_tasks`
  - **Requirements**: FR-004
  - **Details**: Call manager.get_all_tasks, pass to display_tasks
  - **Signature**: `def handle_view_tasks(manager: TodoManager) -> None`

- [ ] **T-050** [P] Create handle_update_task function in `src/main.py`
  - **File**: `src/main.py` → `handle_update_task`
  - **Requirements**: FR-005, FR-010, FR-011, FR-015
  - **Details**: Prompt for ID, new title, new description, handle ValueError, display success/error
  - **Signature**: `def handle_update_task(manager: TodoManager) -> None`

- [ ] **T-051** [P] Create handle_delete_task function in `src/main.py`
  - **File**: `src/main.py` → `handle_delete_task`
  - **Requirements**: FR-006, FR-012, FR-015
  - **Details**: Prompt for ID, call manager.delete_task, handle ValueError, display success/error
  - **Signature**: `def handle_delete_task(manager: TodoManager) -> None`

- [ ] **T-052** [P] Create handle_mark_complete function in `src/main.py`
  - **File**: `src/main.py` → `handle_mark_complete`
  - **Requirements**: FR-007, FR-013, FR-015
  - **Details**: Prompt for ID, call manager.mark_task_complete, handle ValueError, display success/error
  - **Signature**: `def handle_mark_complete(manager: TodoManager) -> None`

- [ ] **T-053** [P] Create handle_mark_incomplete function in `src/main.py`
  - **File**: `src/main.py` → `handle_mark_incomplete`
  - **Requirements**: FR-007, FR-013, FR-015
  - **Details**: Prompt for ID, call manager.mark_task_incomplete, handle ValueError, display success/error
  - **Signature**: `def handle_mark_incomplete(manager: TodoManager) -> None`

- [ ] **T-054** Create main function with while True loop in `src/main.py`
  - **File**: `src/main.py` → `main`
  - **Requirements**: FR-016, SC-010 (pure console app)
  - **Details**: Initialize TodoManager, loop showing menu and dispatching to handlers, exit on choice 7
  - **Signature**: `def main() -> None`
  - **Dependencies**: T-047, T-048, T-049, T-050, T-051, T-052, T-053 (all handler functions)

- [ ] **T-055** Add if __name__ == "__main__" block in `src/main.py`
  - **File**: `src/main.py`
  - **Requirements**: FR-016
  - **Details**: Call main() when script is executed directly
  - **Dependencies**: T-054 (requires main function)

- [ ] **T-056** Add Google-style docstrings to all CLI functions
  - **File**: `src/main.py` → all functions
  - **Requirements**: SC-008, SC-009
  - **Details**: Document all functions with Args, Returns (if applicable)
  - **Dependencies**: T-046, T-047, T-048, T-049, T-050, T-051, T-052, T-053, T-054 (all CLI functions)

**Checkpoint**: ✅ CLI Interface complete - All features accessible via menu

---

## Phase 9: Integration Testing & Quality Assurance

**Purpose**: Verify all features work together and meet quality standards

- [ ] **T-057** Run full test suite and verify coverage
  - **Command**: `pytest --cov=src --cov-report=term-missing tests/`
  - **Requirements**: SC-002 (error handling), SC-003 (workflows), SC-008 (code quality)
  - **Acceptance**: >90% line coverage for src/models.py and src/manager.py
  - **Dependencies**: All previous test tasks (T-009 through T-045)

- [ ] **T-058** Manual testing: Add task workflow
  - **Requirements**: SC-001, SC-003
  - **Test**: Run app, select "1. Add Task", enter "Buy groceries" / "Milk, eggs", verify success message

- [ ] **T-059** Manual testing: View tasks workflow
  - **Requirements**: SC-001, SC-003, SC-006
  - **Test**: Add 3 tasks, select "2. View All Tasks", verify table shows ID, Title, Status, Description for all

- [ ] **T-060** Manual testing: Update task workflow
  - **Requirements**: SC-001, SC-003, SC-004
  - **Test**: Add task, select "3. Update Task", update title and description, verify changes in view

- [ ] **T-061** Manual testing: Delete task workflow
  - **Requirements**: SC-001, SC-003
  - **Test**: Add 3 tasks, select "4. Delete Task" with ID=2, verify only 2 tasks remain

- [ ] **T-062** Manual testing: Mark complete/incomplete workflow
  - **Requirements**: SC-001, SC-003
  - **Test**: Add task, mark complete (status→complete), mark incomplete (status→incomplete)

- [ ] **T-063** Manual testing: Error handling
  - **Requirements**: SC-002, SC-004
  - **Test**: Try update with invalid ID, try add with empty title, verify error messages display

- [ ] **T-064** Run PEP 8 linter on all code
  - **Command**: `python -m pylint src/ --disable=C0103,C0114,C0115,C0116 --max-line-length=100`
  - **Requirements**: SC-008 (PEP 8 compliance)
  - **Acceptance**: No errors, only optional warnings allowed

**Checkpoint**: ✅ All quality checks pass - Ready for delivery

---

## Phase 10: Documentation & Polish

**Purpose**: Complete documentation and final refinements

- [ ] **T-065** Update README.md with usage instructions
  - **File**: `README.md`
  - **Requirements**: SC-008
  - **Details**: Add sections: Features, Requirements, Installation, Usage, Testing
  - **Dependencies**: T-055 (requires working application)

- [ ] **T-066** [P] Verify all requirements are met
  - **Requirements**: FR-001 through FR-018 (all functional requirements)
  - **Details**: Checklist verification against spec.md requirements
  - **Acceptance**: All 18 requirements implemented and tested

- [ ] **T-067** [P] Verify all success criteria are met
  - **Requirements**: SC-001 through SC-010 (all success criteria)
  - **Details**: Checklist verification against spec.md success criteria
  - **Acceptance**: All 10 criteria satisfied

- [ ] **T-068** [P] Final code cleanup and comments
  - **Files**: All src/ files
  - **Requirements**: SC-008, SC-009
  - **Details**: Add clarifying comments where needed, ensure consistent formatting

**Checkpoint**: ✅ Project complete - All deliverables ready

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)**: No dependencies - can start immediately
2. **Foundational (Phase 2)**: Depends on Setup (T-001 to T-005) - BLOCKS all user stories
3. **User Stories (Phases 3-7)**: All depend on Foundational (T-006 to T-010) completion
4. **CLI (Phase 8)**: Depends on all User Stories (T-011 to T-041) being complete
5. **Integration Testing (Phase 9)**: Depends on CLI (T-042 to T-056) completion
6. **Documentation (Phase 10)**: Depends on Integration Testing passing

### User Story Dependencies

**After Foundational Phase completes, user stories CAN proceed in parallel:**

- **User Story 1 (P1)**: Ready after T-010 - No dependencies on other stories
- **User Story 2 (P2)**: Ready after T-010 - No dependencies on other stories
- **User Story 3 (P3)**: Ready after T-010 - Uses _get_task_by_id (can be written once)
- **User Story 4 (P3)**: Ready after T-010 - Uses _get_task_by_id (can be written once)
- **User Story 5 (P2)**: Ready after T-010 - Uses _get_task_by_id (can be written once)

**Recommended Sequential Order (for single developer):**
1. US1 (Add) → US2 (View) → US5 (Mark Status) → US3 (Update) → US4 (Delete)
2. Rationale: Add+View gives MVP, Mark Status is P2, Update+Delete are P3

### Within Each User Story

1. ✅ **Tests FIRST**: Write and run tests (they should FAIL)
2. ✅ **Implement**: Write production code to make tests pass
3. ✅ **Document**: Add docstrings and comments
4. ✅ **Verify**: Run tests again (they should PASS)

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks T-002 to T-005 can run in parallel

**Phase 2 (Foundational)**:
- T-006 and T-009 can run in parallel (enum + enum tests)
- T-010 can run after T-007 (Task tests need Task class)

**Phase 3-7 (User Stories)**: Different user stories can be worked on in parallel by different developers

**Phase 8 (CLI)**: All handler functions (T-048 to T-053) can be written in parallel

**Phase 9 (Testing)**: Manual tests (T-058 to T-063) can run in parallel

**Phase 10 (Documentation)**: T-066, T-067, T-068 can run in parallel

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

**Goal**: Get basic functionality working as quickly as possible

1. ✅ Phase 1: Setup (30 min)
2. ✅ Phase 2: Foundational - Task model (1.5 hours)
3. ✅ Phase 3: User Story 1 - Add Task (1.5 hours)
4. ✅ Phase 4: User Story 2 - View Tasks (1 hour)
5. ✅ Phase 8: Basic CLI (just Add + View handlers) (1 hour)
6. **STOP and VALIDATE**: Test manually (5 min)

**At this point you have a working MVP**: Can add and view tasks!

### Incremental Delivery

Continue building features incrementally:

7. ✅ Phase 7: User Story 5 - Mark Status (1 hour)
8. ✅ Update CLI with Mark handlers (30 min)
9. **VALIDATE**: Test Add + View + Mark complete workflow

10. ✅ Phase 5: User Story 3 - Update Task (1.5 hours)
11. ✅ Update CLI with Update handler (30 min)
12. **VALIDATE**: Test full edit workflow

13. ✅ Phase 6: User Story 4 - Delete Task (1 hour)
14. ✅ Update CLI with Delete handler (30 min)
15. **VALIDATE**: Test full CRUD workflow

16. ✅ Phase 9: Integration Testing (2 hours)
17. ✅ Phase 10: Documentation & Polish (1 hour)

**Total Time**: ~12 hours (as planned)

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

- **Developer A**: User Stories 1 + 2 (Add + View) + CLI handlers
- **Developer B**: User Stories 3 + 4 (Update + Delete) + CLI handlers
- **Developer C**: User Story 5 (Mark Status) + display_tasks + integration tests

All converge for Phase 9 (Testing) and Phase 10 (Documentation).

---

## Task Summary

| Phase | Tasks | Focus | Duration |
|-------|-------|-------|----------|
| Phase 1: Setup | T-001 to T-005 | Project structure | 30 min |
| Phase 2: Foundational | T-006 to T-010 | Task model | 1.5 hours |
| Phase 3: US1 (Add) | T-011 to T-017 | Add task feature | 1.5 hours |
| Phase 4: US2 (View) | T-018 to T-021 | View tasks feature | 1 hour |
| Phase 5: US3 (Update) | T-022 to T-028 | Update task feature | 1.5 hours |
| Phase 6: US4 (Delete) | T-029 to T-034 | Delete task feature | 1 hour |
| Phase 7: US5 (Mark) | T-035 to T-041 | Mark status feature | 1 hour |
| Phase 8: CLI | T-042 to T-056 | User interface | 3 hours |
| Phase 9: Integration | T-057 to T-064 | Testing & QA | 2 hours |
| Phase 10: Documentation | T-065 to T-068 | Final polish | 1 hour |
| **TOTAL** | **68 tasks** | **Complete app** | **~12 hours** |

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability (US1-US5)
- **TDD approach**: Write tests FIRST (they fail), then implement (tests pass)
- **Incremental validation**: Test after each user story completion
- **Constitution compliance**: All tasks adhere to Python 3.13+, PEP 8, in-memory storage, CLI-only
- **Requirement traceability**: Every task links back to FR-XXX or SC-XXX from spec.md
- **Commit frequency**: Commit after completing each task or logical group
- **Stop at checkpoints**: Validate independently before proceeding

---

## Requirements Coverage

| Requirement | Tasks | Phase |
|-------------|-------|-------|
| FR-001 | T-007, T-012, T-015, T-048 | Phase 2, 3, 8 |
| FR-002 | T-007, T-015, T-031 | Phase 2, 3, 6 |
| FR-003 | T-011, T-014 | Phase 2, 3 |
| FR-004 | T-018, T-019, T-046, T-049 | Phase 4, 8 |
| FR-005 | T-023, T-026, T-050 | Phase 5, 8 |
| FR-006 | T-029, T-032, T-051 | Phase 6, 8 |
| FR-007 | T-035, T-038, T-039, T-052, T-053 | Phase 7, 8 |
| FR-008 | T-007, T-012, T-015 | Phase 2, 3 |
| FR-009 | T-008, T-010, T-013, T-048 | Phase 2, 3, 8 |
| FR-010 | T-023, T-024, T-026, T-050 | Phase 5, 8 |
| FR-011 | T-023, T-024, T-026, T-050 | Phase 5, 8 |
| FR-012 | T-029, T-030, T-032, T-051 | Phase 6, 8 |
| FR-013 | T-035, T-037, T-038, T-039, T-052, T-053 | Phase 7, 8 |
| FR-014 | T-022, T-025, T-026, T-032, T-038, T-039 | Phase 5, 6, 7 |
| FR-015 | T-024, T-030, T-037 | Phase 5, 6, 7 |
| FR-016 | T-047, T-054, T-055 | Phase 8 |
| FR-017 | T-065 (README) | Phase 10 |
| FR-018 | T-011, T-014 | Phase 2, 3 |

All 18 functional requirements are covered across the 68 tasks.
