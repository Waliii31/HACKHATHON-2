# Todo Application - Basic Level Functionality

A Python console application for managing personal todo tasks with in-memory storage.

## Features

- ✅ **Add Task**: Create new tasks with title and optional description
- ✅ **View All Tasks**: Display all tasks with ID, Title, Status, and Description
- ✅ **Update Task**: Modify task title and/or description by ID
- ✅ **Delete Task**: Remove tasks by ID
- ✅ **Mark Complete/Incomplete**: Toggle task completion status

## Requirements

- Python 3.13 or higher
- No external dependencies for production code
- pytest for running tests (development only)

## Project Structure

```
Hackathon-Todo-Phase1/
├── src/
│   ├── __init__.py        # Package marker
│   ├── models.py          # Task dataclass and TaskStatus enum
│   ├── manager.py         # TodoManager class (CRUD operations)
│   └── main.py            # CLI interface and entry point
├── tests/
│   ├── __init__.py        # Test package marker
│   ├── test_models.py     # Task model unit tests
│   ├── test_manager.py    # TodoManager unit tests
│   └── test_integration.py # End-to-end workflow tests
├── specs/                 # Feature specifications and plans
├── requirements-dev.txt   # Development dependencies
└── README.md              # This file
```

## Installation

1. **Clone or download this repository**

2. **Navigate to the project directory**:
   ```bash
   cd Hackathon-Todo-Phase1
   ```

3. **Install development dependencies** (optional, for running tests):
   ```bash
   pip install -r requirements-dev.txt
   ```

## Usage

### Running the Application

```bash
python src/main.py
```

### Menu Options

Once the application starts, you'll see a menu with the following options:

```
=== Todo Application ===
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete
6. Mark Task Incomplete
7. Exit
========================
```

### Example Workflow

1. **Add a task**: Select option 1, enter "Buy groceries" as title and "Milk, eggs, bread" as description
2. **View tasks**: Select option 2 to see all your tasks in a formatted table
3. **Mark complete**: Select option 5, enter the task ID to mark it as complete
4. **Update task**: Select option 3, enter task ID and new title/description
5. **Delete task**: Select option 4, enter task ID to remove the task
6. **Exit**: Select option 7 to quit the application

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=term-missing tests/
```

### Run Specific Test Files

```bash
# Test models only
pytest tests/test_models.py -v

# Test manager only
pytest tests/test_manager.py -v

# Test integration workflows
pytest tests/test_integration.py -v
```

## Development

This project follows spec-driven development (SDD) principles:

- **Specification**: `specs/001-todo-basic-functionality/spec.md`
- **Implementation Plan**: `specs/001-todo-basic-functionality/plan.md`
- **Task Breakdown**: `specs/001-todo-basic-functionality/tasks.md`

### Code Standards

- **Python Version**: 3.13+
- **Style Guide**: PEP 8
- **Docstrings**: Google-style with type hints
- **Testing**: >90% code coverage target
- **Architecture**: Clean separation of concerns (Data → Logic → Interface)

### Project Constitution

This project adheres to strict architectural principles:

- ✅ Python 3.13+ only
- ✅ In-memory storage (no databases or file persistence)
- ✅ Pure console application (no web frameworks)
- ✅ Standard library only (no external runtime dependencies)
- ✅ Clean code with proper separation in `/src` directory

## Architecture

### Three-Layer Design

1. **Data Layer** (`src/models.py`)
   - `TaskStatus` enum (INCOMPLETE, COMPLETE)
   - `Task` dataclass with validation

2. **Logic Layer** (`src/manager.py`)
   - `TodoManager` class
   - CRUD operations with error handling
   - Auto-incrementing ID management

3. **Interface Layer** (`src/main.py`)
   - CLI menu system
   - User input handling
   - Formatted task display

## License

This project was created for Hackathon II Phase I.

## Author

Generated using spec-driven development with Claude CLI.
