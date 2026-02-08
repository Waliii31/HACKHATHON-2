# Phase III Backend - Todo AI Chatbot API

FastAPI backend for the AI-powered Todo chatbot with MCP tools and OpenAI integration.

## Architecture

```
backend/
├── app/
│   ├── agent/            # AI Agent (OpenAI integration)
│   │   ├── brain.py      # Message processing & tool orchestration
│   │   └── prompts.py    # System prompts for the AI
│   ├── api/              # API Routes
│   │   ├── chat.py       # POST /api/chat & conversation endpoints
│   │   └── deps.py       # Authentication dependencies
│   ├── database/         # Database connection
│   │   └── connection.py # Async SQLAlchemy with Neon
│   ├── mcp/              # MCP Server
│   │   ├── server.py     # Tool registration & execution
│   │   └── tools/        # Individual tool implementations
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── delete_task.py
│   │       └── update_task.py
│   ├── models/           # SQLModel database models
│   │   ├── conversation.py
│   │   └── message.py
│   ├── repositories/     # Database CRUD operations
│   │   ├── conversation.py
│   │   └── message.py
│   ├── schemas/          # Pydantic request/response schemas
│   │   └── chat.py
│   ├── config.py         # Application settings
│   └── main.py           # FastAPI application entrypoint
├── migrations/           # SQL migration scripts
├── requirements.txt
├── run_migration.py
└── .env
```

## Quick Start

### 1. Setup Virtual Environment

```bash
cd Phase-3/backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required environment variables:**
- `DATABASE_URL` - Neon PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `JWT_SECRET_KEY` - Secret for JWT token validation

### 4. Run Database Migrations

```bash
python run_migration.py
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /api/chat
Process a chat message through the AI agent.

**Request:**
```json
{
  "message": "Add buy groceries to my list",
  "conversation_id": null  // Optional - creates new if not provided
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "response": "I've added 'buy groceries' to your list! 📝",
  "tools_used": [
    {"name": "add_task", "success": true, "result": {...}}
  ],
  "timestamp": "2024-02-08T12:00:00Z"
}
```

### GET /api/chat/conversations
List user's conversations with pagination.

### GET /api/chat/conversations/{id}
Get conversation details with messages.

### DELETE /api/chat/conversations/{id}
Delete a conversation and all its messages.

## MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `add_task` | Add a new task | `title`, `description?` |
| `list_tasks` | List user's tasks | `status?` (all/pending/completed) |
| `complete_task` | Mark task as done | `task_id` or `task_title` |
| `delete_task` | Delete a task | `task_id` or `task_title` |
| `update_task` | Update task details | `task_id`/`task_title`, `new_title?`, `new_description?` |

## Stateless Architecture

**IMPORTANT:** This API is completely stateless. Every request:

1. Reads conversation history from the database
2. Stores the user message
3. Processes through the AI agent
4. Stores the AI response
5. Returns the response

No conversation state is kept in memory between requests.

## Authentication

The API expects a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

In development mode (`ENVIRONMENT=development`), requests without tokens are allowed using a test user ID.

## Testing

Test the API with curl:

```bash
# Health check
curl http://localhost:8000/health

# Start a chat (no auth in dev mode)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add buy groceries"}'
```

## OpenAI Integration

The AI agent uses:
- **Model:** gpt-4-turbo-preview (configurable)
- **Temperature:** 0.7 (configurable)
- **Function Calling:** MCP tools are exposed as OpenAI functions

The agent determines which tools to call based on the user's natural language input.
