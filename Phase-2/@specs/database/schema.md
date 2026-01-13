# Database Schema Specification

## Overview
This document defines the database schema for the Todo application, compatible with SQLModel and Neon PostgreSQL. The schema includes tables for user management and task storage with proper relationships and constraints.

## Database System
- **Provider**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (compatible with SQLAlchemy and Pydantic)
- **Connection**: Async connection pooling
- **Schema Version**: 1.0

## Users Table (Managed by Better Auth)

### Table Definition
```
Table: users
```

### Fields
| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, UNIQUE | Auto-generated unique identifier for the user |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User's email address (used for authentication) |
| name | VARCHAR(255) | NOT NULL | User's display name |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Timestamp when the user account was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW(), ON UPDATE CURRENT_TIMESTAMP | Timestamp when the user record was last updated |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Flag indicating if the user account is active |

### Notes
- This table is primarily managed by Better Auth
- Additional fields may be added by Better Auth as needed
- The id field serves as the foreign key reference for tasks

### Indexes
- `idx_users_email`: UNIQUE INDEX on email field for fast lookup and uniqueness enforcement
- `idx_users_created_at`: INDEX on created_at for efficient chronological queries

## Tasks Table

### Table Definition
```
Table: tasks
```

### Fields
| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, UNIQUE, DEFAULT gen_random_uuid() | Auto-generated unique identifier for the task |
| title | VARCHAR(255) | NOT NULL | Task title (1-255 characters) |
| description | TEXT | NULL | Optional detailed description of the task (max 1000 characters) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | Task status: 'active' or 'completed' |
| priority | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | Task priority: 'low', 'medium', or 'high' |
| due_date | TIMESTAMP | NULL | Optional due date for the task |
| completed_at | TIMESTAMP | NULL | Timestamp when the task was marked as completed |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Timestamp when the task was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW(), ON UPDATE CURRENT_TIMESTAMP | Timestamp when the task was last updated |
| user_id | UUID | NOT NULL, FOREIGN KEY (users.id) | Reference to the user who owns this task |

### Constraints
- `fk_tasks_user_id`: FOREIGN KEY constraint linking user_id to users.id
- `chk_task_status`: CHECK constraint ensuring status is one of ('active', 'completed')
- `chk_task_priority`: CHECK constraint ensuring priority is one of ('low', 'medium', 'high')
- `chk_due_date_future`: CHECK constraint ensuring due_date (if provided) is not in the past

### Indexes
- `idx_tasks_user_id`: INDEX on user_id for efficient user-specific task retrieval
- `idx_tasks_status`: INDEX on status for filtering by task status
- `idx_tasks_priority`: INDEX on priority for sorting by priority
- `idx_tasks_due_date`: INDEX on due_date for deadline-based queries
- `idx_tasks_created_at`: INDEX on created_at for chronological ordering
- `idx_tasks_user_status`: COMPOSITE INDEX on (user_id, status) for efficient user-task-status queries

## Foreign Key Relationships

### Relationship: tasks.user_id → users.id
- **Parent Table**: users
- **Child Table**: tasks
- **Foreign Key**: tasks.user_id
- **Referenced Key**: users.id
- **On Update**: CASCADE (if user id changes, update all related tasks)
- **On Delete**: CASCADE (if user is deleted, remove all their tasks)
- **Purpose**: Ensures referential integrity between users and their tasks

## SQLModel Compatibility Notes

### Base Model Requirements
- All models should inherit from SQLModel
- Use `Field` for column definitions with appropriate constraints
- Use `Relationship` for foreign key relationships
- Primary keys should use appropriate default generators
- Timestamps should use `datetime.utcnow` for defaults

### Field Type Mapping
- UUID: Use `UUID` type with `gen_random_uuid()` default
- VARCHAR: Use `str` with max length constraints
- TEXT: Use `str` for longer text fields
- TIMESTAMP: Use `datetime` type with timezone-aware storage
- BOOLEAN: Use `bool` type
- FOREIGN KEY: Use appropriate reference to parent table

## Neon PostgreSQL Specifics

### Extensions Required
- `uuid-ossp`: For UUID generation functions
- `pgcrypto`: For cryptographic functions if needed

### Connection Pooling
- Utilize Neon's connection pooling capabilities
- Configure appropriate pool sizes for expected load
- Implement proper connection cleanup and reuse

### Performance Considerations
- Leverage Neon's serverless scaling for variable loads
- Use prepared statements for frequently executed queries
- Implement proper indexing strategies for common query patterns

## Data Integrity Constraints

### Referential Integrity
- Foreign key constraints enforce relationship validity
- Cascade operations maintain data consistency
- No orphaned records allowed in child tables

### Domain Constraints
- Enum-like constraints using CHECK constraints
- Length limits on variable-length fields
- Format validation at database level

## Sample SQL Schema Representation

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (managed by Better Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Indexes for users table
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- Constraints for tasks table
ALTER TABLE tasks ADD CONSTRAINT chk_task_status
    CHECK (status IN ('active', 'completed'));
ALTER TABLE tasks ADD CONSTRAINT chk_task_priority
    CHECK (priority IN ('low', 'medium', 'high'));

-- Indexes for tasks table
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
```

## Future Considerations
- Potential audit trail table for tracking task changes
- Tags or categories table for enhanced task organization
- Sharing capabilities requiring additional relationship tables
- Soft delete capability if needed for data recovery