<!-- Sync Impact Report:
Version change: None → 1.0.0
Modified principles:
  - None
Added sections:
  - Core Principles
Removed sections:
  - None
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ updated
  - .specify/templates/spec-template.md: ✅ updated
  - .specify/templates/tasks-template.md: ✅ updated
  - .specify/templates/commands/*.md: ✅ updated
Follow-up TODOs: None
-->
# Hackathon II Phase I: Todo In-Memory Python Console App Constitution

## Core Principles

### I. Tech Stack
Python 3.13+ only. No external database or persistent storage; data must be stored in a simple in-memory Python data structure (e.g., a list of class instances).

### II. Architecture
Pure Console Application (CLI). No web frameworks (FastAPI, Flask, etc.) are allowed in this phase.

### III. Code Style
Follow Python's PEP 8 guidelines, use clean class/function separation in the `/src` directory, and include Google-style docstrings with type hints.

### IV. Deliverable
All 5 Basic Level features (Add, Delete, Update, View, Mark Complete) must be implemented.

## Governance
This constitution supersedes all other practices. Amendments require documentation, approval, and a migration plan. All pull requests and reviews must verify compliance. Complexity must be justified.

**Version**: 1.0.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
