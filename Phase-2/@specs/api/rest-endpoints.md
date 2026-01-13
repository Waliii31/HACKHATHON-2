# REST API Endpoints Specification

## Overview
This document defines all REST API endpoints required for Phase II of the Todo application. All endpoints follow RESTful principles and require JWT authentication for access.

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Base Path
All endpoints are prefixed with `/api/v1`

---

## Endpoint: List User Tasks

### GET /api/v1/users/{user_id}/tasks

**Method:** GET

**Path:** `/api/v1/users/{user_id}/tasks`

**Authentication Required:** Yes (JWT)

**Description:** Retrieve a list of tasks for the specified user

**Parameters:**
- `user_id` (path parameter): The unique identifier of the authenticated user (UUID format)
- `limit` (query parameter, optional): Maximum number of tasks to return (default: 50, max: 100)
- `offset` (query parameter, optional): Number of tasks to skip (for pagination, default: 0)
- `status` (query parameter, optional): Filter tasks by status ("active", "completed", or "all")
- `priority` (query parameter, optional): Filter tasks by priority ("low", "medium", "high")
- `sort_by` (query parameter, optional): Sort field ("created_at", "updated_at", "due_date", "priority", default: "created_at")
- `order` (query parameter, optional): Sort order ("asc", "desc", default: "desc")

**Request Schema:** None (only headers and query parameters)

**Success Response:**
- **Status Code:** 200 OK
- **Content-Type:** application/json

**Response Schema:**
```json
{
  "tasks": [
    {
      "id": "string (UUID)",
      "title": "string (max 255)",
      "description": "string (optional, max 1000)",
      "status": "string (active|completed)",
      "priority": "string (low|medium|high)",
      "due_date": "string (ISO 8601 datetime, optional)",
      "created_at": "string (ISO 8601 datetime)",
      "updated_at": "string (ISO 8601 datetime)",
      "user_id": "string (UUID)"
    }
  ],
  "pagination": {
    "page": "integer",
    "limit": "integer",
    "total": "integer",
    "has_next": "boolean",
    "has_prev": "boolean"
  }
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing JWT token
  ```json
  {
    "detail": "Authentication credentials were not provided/are invalid"
  }
  ```
- **403 Forbidden:** User does not have access to the specified user's tasks
  ```json
  {
    "detail": "Access denied to this user's tasks"
  }
  ```
- **404 Not Found:** User with the specified ID does not exist
  ```json
  {
    "detail": "User not found"
  }
  ```

---

## Endpoint: Create New Task

### POST /api/v1/users/{user_id}/tasks

**Method:** POST

**Path:** `/api/v1/users/{user_id}/tasks`

**Authentication Required:** Yes (JWT)

**Description:** Create a new task for the specified user

**Parameters:**
- `user_id` (path parameter): The unique identifier of the authenticated user (UUID format)

**Request Schema:**
```json
{
  "title": "string (1-255 characters)",
  "description": "string (optional, max 1000 characters)",
  "status": "string (optional, default: 'active')",
  "priority": "string (optional, default: 'medium')",
  "due_date": "string (optional, ISO 8601 datetime)"
}
```

**Success Response:**
- **Status Code:** 201 Created
- **Content-Type:** application/json

**Response Schema:**
```json
{
  "id": "string (UUID)",
  "title": "string (max 255)",
  "description": "string (optional, max 1000)",
  "status": "string (active|completed)",
  "priority": "string (low|medium|high)",
  "due_date": "string (ISO 8601 datetime, optional)",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)",
  "user_id": "string (UUID)"
}
```

**Error Responses:**
- **400 Bad Request:** Invalid request body or validation errors
  ```json
  {
    "detail": "Validation error",
    "errors": [
      {
        "field": "string",
        "message": "string"
      }
    ]
  }
  ```
- **401 Unauthorized:** Invalid or missing JWT token
  ```json
  {
    "detail": "Authentication credentials were not provided/are invalid"
  }
  ```
- **403 Forbidden:** User does not have access to create tasks for the specified user
  ```json
  {
    "detail": "Access denied to create tasks for this user"
  }
  ```
- **404 Not Found:** User with the specified ID does not exist
  ```json
  {
    "detail": "User not found"
  }
  ```

---

## Endpoint: Get Single Task

### GET /api/v1/users/{user_id}/tasks/{id}

**Method:** GET

**Path:** `/api/v1/users/{user_id}/tasks/{id}`

**Authentication Required:** Yes (JWT)

**Description:** Retrieve a specific task by ID for the specified user

**Parameters:**
- `user_id` (path parameter): The unique identifier of the authenticated user (UUID format)
- `id` (path parameter): The unique identifier of the task (UUID format)

**Request Schema:** None (only headers)

**Success Response:**
- **Status Code:** 200 OK
- **Content-Type:** application/json

**Response Schema:**
```json
{
  "id": "string (UUID)",
  "title": "string (max 255)",
  "description": "string (optional, max 1000)",
  "status": "string (active|completed)",
  "priority": "string (low|medium|high)",
  "due_date": "string (ISO 8601 datetime, optional)",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)",
  "user_id": "string (UUID)"
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing JWT token
  ```json
  {
    "detail": "Authentication credentials were not provided/are invalid"
  }
  ```
- **403 Forbidden:** User does not have access to the specified user's tasks
  ```json
  {
    "detail": "Access denied to this user's tasks"
  }
  ```
- **404 Not Found:** Task or user with the specified ID does not exist
  ```json
  {
    "detail": "Task not found"
  }
  ```

---

## Endpoint: Update Task

### PUT /api/v1/users/{user_id}/tasks/{id}

**Method:** PUT

**Path:** `/api/v1/users/{user_id}/tasks/{id}`

**Authentication Required:** Yes (JWT)

**Description:** Update a specific task by ID for the specified user (full update)

**Parameters:**
- `user_id` (path parameter): The unique identifier of the authenticated user (UUID format)
- `id` (path parameter): The unique identifier of the task (UUID format)

**Request Schema:**
```json
{
  "title": "string (1-255 characters)",
  "description": "string (optional, max 1000 characters)",
  "status": "string (active|completed)",
  "priority": "string (low|medium|high)",
  "due_date": "string (optional, ISO 8601 datetime)"
}
```

**Success Response:**
- **Status Code:** 200 OK
- **Content-Type:** application/json

**Response Schema:**
```json
{
  "id": "string (UUID)",
  "title": "string (max 255)",
  "description": "string (optional, max 1000)",
  "status": "string (active|completed)",
  "priority": "string (low|medium|high)",
  "due_date": "string (ISO 8601 datetime, optional)",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)",
  "user_id": "string (UUID)"
}
```

**Error Responses:**
- **400 Bad Request:** Invalid request body or validation errors
  ```json
  {
    "detail": "Validation error",
    "errors": [
      {
        "field": "string",
        "message": "string"
      }
    ]
  }
  ```
- **401 Unauthorized:** Invalid or missing JWT token
  ```json
  {
    "detail": "Authentication credentials were not provided/are invalid"
  }
  ```
- **403 Forbidden:** User does not have access to update the specified user's task
  ```json
  {
    "detail": "Access denied to update this user's task"
  }
  ```
- **404 Not Found:** Task or user with the specified ID does not exist
  ```json
  {
    "detail": "Task not found"
  }
  ```

---

## Endpoint: Delete Task

### DELETE /api/v1/users/{user_id}/tasks/{id}

**Method:** DELETE

**Path:** `/api/v1/users/{user_id}/tasks/{id}`

**Authentication Required:** Yes (JWT)

**Description:** Delete a specific task by ID for the specified user

**Parameters:**
- `user_id` (path parameter): The unique identifier of the authenticated user (UUID format)
- `id` (path parameter): The unique identifier of the task (UUID format)

**Request Schema:** None (only headers)

**Success Response:**
- **Status Code:** 204 No Content
- **Content-Type:** application/json

**Response Schema:** Empty response body

**Error Responses:**
- **401 Unauthorized:** Invalid or missing JWT token
  ```json
  {
    "detail": "Authentication credentials were not provided/are invalid"
  }
  ```
- **403 Forbidden:** User does not have access to delete the specified user's task
  ```json
  {
    "detail": "Access denied to delete this user's task"
  }
  ```
- **404 Not Found:** Task or user with the specified ID does not exist
  ```json
  {
    "detail": "Task not found"
  }
  ```

---

## Endpoint: Toggle Task Completion

### PATCH /api/v1/users/{user_id}/tasks/{id}/complete

**Method:** PATCH

**Path:** `/api/v1/users/{user_id}/tasks/{id}/complete`

**Authentication Required:** Yes (JWT)

**Description:** Toggle the completion status of a specific task for the specified user

**Parameters:**
- `user_id` (path parameter): The unique identifier of the authenticated user (UUID format)
- `id` (path parameter): The unique identifier of the task (UUID format)

**Request Schema:**
```json
{
  "complete": "boolean (true to mark complete, false to mark incomplete)"
}
```

**Success Response:**
- **Status Code:** 200 OK
- **Content-Type:** application/json

**Response Schema:**
```json
{
  "id": "string (UUID)",
  "title": "string (max 255)",
  "description": "string (optional, max 1000)",
  "status": "string (active|completed)",
  "priority": "string (low|medium|high)",
  "due_date": "string (ISO 8601 datetime, optional)",
  "completed_at": "string (ISO 8601 datetime, optional)",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)",
  "user_id": "string (UUID)"
}
```

**Error Responses:**
- **400 Bad Request:** Invalid request body or validation errors
  ```json
  {
    "detail": "Validation error",
    "errors": [
      {
        "field": "string",
        "message": "string"
      }
    ]
  }
  ```
- **401 Unauthorized:** Invalid or missing JWT token
  ```json
  {
    "detail": "Authentication credentials were not provided/are invalid"
  }
  ```
- **403 Forbidden:** User does not have access to update the specified user's task
  ```json
  {
    "detail": "Access denied to update this user's task"
  }
  ```
- **404 Not Found:** Task or user with the specified ID does not exist
  ```json
  {
    "detail": "Task not found"
  }
  ```