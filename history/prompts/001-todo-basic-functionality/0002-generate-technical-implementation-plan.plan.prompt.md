# yaml-language-server: $schema=
---
id: '0002'
title: 'Generate Technical Implementation Plan'
stage: 'plan'
date: '2025-12-17'
surface: 'agent'
model: 'gemini-2.0-flash-exp'
feature: '001-todo-basic-functionality'
branch: 'main'
user: 'USER'
command: '/sp.plan'
labels: ['architecture', 'technical-design', 'module-structure', 'implementation-plan']
links:
  spec: 'specs/001-todo-basic-functionality/spec.md'
  ticket: null
  adr: null
  pr: null
files:
  - 'specs/001-todo-basic-functionality/plan.md'
tests: []
---

## Prompt

/sp.plan Based on the feature specification in /specs/001-todo-basic-functionality/spec.md and the project constitution, generate a detailed technical implementation plan. 

The plan must include:
1. Module Structure: Define a separate `models.py` for data structures and `manager.py` for logic.
2. Data Model: A `Task` class using Python's `dataclasses` or a standard class.
3. Logic Layer: A `TodoManager` class that performs CRUD operations on an in-memory list.
4. Interface: A `cli.py` or `main.py` using a simple `while True` loop to handle user input.
5. ID Management: A strategy for generating unique, incrementing integer IDs for each task.

Plzz act as claude cli and complete this task and it should look like claude cli completed this task

## Response snapshot

Generated comprehensive technical implementation plan (plan.md) with complete architecture design:

**Architecture Layers**:
- **Data Model Layer** (models.py): TaskStatus enum + Task dataclass with post_init validation
- **Logic Layer** (manager.py): TodoManager class with auto-incrementing ID counter and CRUD methods
- **Interface Layer** (main.py): CLI menu system with while True loop and command handlers

**Module Structure**:
```
src/
├── models.py    - Task dataclass, TaskStatus enum, validation
├── manager.py   - TodoManager class, CRUD operations, error handling
└── main.py      - CLI interface, menu system, display utilities

tests/
├── test_models.py       - Task model unit tests
├── test_manager.py      - TodoManager unit tests
└── test_integration.py  - End-to-end workflow tests
```

**ID Management Strategy**:
- Auto-incrementing counter starting at 1
- Never reuses IDs even after deletion
- Thread-safe for single-user CLI usage
- Simple and guaranteed unique

**Key Design Decisions**:
1. **Dataclass for Task**: Automatic __init__, __repr__, __eq__ methods, reduces boilerplate
2. **Enum for Status**: Type safety, prevents invalid status values
3. **Post-init validation**: Catches empty titles at Task creation time
4. **Separate handler functions**: One per command for clarity and testability
5. **Try-except in CLI**: Catches ValueError from manager, displays user-friendly messages
6. **Dynamic table formatting**: Adapts column widths to content
7. **Description truncation**: Shows first 80 chars in list view to prevent line wrapping

**Error Handling**:
- Empty title: ValueError in Task.__post_init__ and TodoManager.update_task
- Not found: ValueError with "Task with ID X not found" message
- Invalid ID format: Caught by int() conversion in CLI handlers
- Edge cases: Empty list, long descriptions, special characters

**Testing Strategy**:
- Unit tests for models (validation, equality)
- Unit tests for manager (all CRUD operations, error paths)
- Integration tests (complete workflows, ID persistence)
- Coverage goals: >90% line coverage, >80% branch coverage

**Development Phases** (12 hours total):
1. Data Model (2h) - Task dataclass + tests
2. Logic Layer (4h) - TodoManager + comprehensive tests
3. CLI Interface (3h) - Menu system + handlers
4. Integration Testing (2h) - Full test suite
5. Documentation (1h) - README + polish

**Constitution Compliance**:
✅ Python 3.13+ only
✅ In-memory storage (list[Task])
✅ Pure console application (no web frameworks)
✅ PEP 8 + Google-style docstrings
✅ All 5 features covered

**Risks Identified**:
- ID collision after deletion (mitigated: never-decreasing counter)
- Long description display (mitigated: truncation in table view)
- Input validation edge cases (mitigated: comprehensive tests)
- Python version compatibility (mitigated: explicit 3.13+ requirement)

## Outcome

- ✅ Impact: Complete technical implementation plan created with detailed architecture, code structure, and development roadmap
- 🧪 Tests: No tests run (planning phase); testing strategy defined with >90% coverage target
- 📁 Files: Created 1 file (specs/001-todo-basic-functionality/plan.md)
- 🔁 Next prompts: /sp.tasks (generate task breakdown), implement Phase 1 (data model)
- 🧠 Reflection: Plan provides concrete code examples for all three layers; ID management strategy is simple and robust; error handling approach is consistent across all operations; development phases are realistic and incremental

## Evaluation notes (flywheel)

- Failure modes observed: None; plan aligns with spec and constitution requirements
- Graders run and results (PASS/FAIL): Manual review PASS - all architectural requirements addressed, code examples provided, risks identified
- Prompt variant (if applicable): Standard /sp.plan workflow with specific module structure requirements
- Next experiment (smallest change to try): Proceed with /sp.tasks to generate detailed task breakdown, then implement data model layer
