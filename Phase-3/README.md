# Phase III: Todo AI Chatbot 🤖

> Transform your Todo app into an AI-powered conversational experience

## 🎯 Overview

Phase III evolves the Phase II Todo Web Application into an AI-powered chatbot where users manage their tasks through natural language conversations instead of traditional UI forms.

**Key Innovation:** Users can simply say "Add buy groceries" or "What are my pending tasks?" and the AI assistant handles everything!

## ✨ Features

- 💬 **Conversational Interface** - OpenAI ChatKit-powered chat UI
- 🧠 **AI Brain** - OpenAI Agents SDK for intent recognition
- 🔧 **MCP Tools** - 5 task management tools exposed via MCP Server
- 📊 **Conversation History** - Persistent chat history in PostgreSQL
- 🔒 **Secure** - Domain allowlist and JWT authentication

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Frontend (Next.js + OpenAI ChatKit)                         │
│  └─→ POST /api/chat (Stateless)                              │
│       └─→ AI Agent (OpenAI Agents SDK)                       │
│            └─→ MCP Server (MCP Tools)                        │
│                 └─→ PostgreSQL (Tasks + Conversations)       │
└──────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend Chat | OpenAI ChatKit |
| AI Agent | OpenAI Agents SDK |
| MCP Server | Official MCP SDK |
| Backend | FastAPI (Python) |
| Database | Neon PostgreSQL |
| Auth | Better Auth + JWT |

## 📁 Project Structure

```
Phase-3/
├── @specs/                    # Specifications
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   ├── api/
│   ├── database/
│   └── mcp/
├── frontend/                  # Next.js + ChatKit
│   ├── app/chat/             # Chat page
│   ├── components/           # Chat components
│   └── lib/                  # API clients
├── backend/                   # FastAPI
│   ├── app/
│   │   ├── agent/            # AI Agent brain
│   │   ├── mcp/              # MCP Server + tools
│   │   └── api/              # Chat endpoint
│   └── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- pnpm
- OpenAI API Key
- Neon PostgreSQL database

### 1. Clone and Setup
```bash
cd Phase-3

# Install frontend dependencies
cd frontend
pnpm install

# Install backend dependencies
cd ../backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

**Frontend (.env.local):**
```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_CHATKIT_DOMAIN_ALLOWLIST=localhost:3000
DATABASE_URL=postgresql://...
```

**Backend (.env):**
```env
DATABASE_URL=postgresql+asyncpg://...
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=your-secret
ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Run Database Migration
```bash
cd backend
python run_migration.py
```

### 4. Start Development Servers
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
pnpm dev
```

### 5. Open Chat
Navigate to http://localhost:3000/chat

## 💬 Usage Examples

```
User: "Add buy groceries to my list"
Bot:  "I've added 'buy groceries' to your list! 📝"

User: "What are my pending tasks?"
Bot:  "Here are your pending tasks:
       1. 📌 Buy groceries
       2. 📌 Call mom
       You have 2 tasks waiting!"

User: "Mark buy groceries as done"
Bot:  "Great job! ✅ 'Buy groceries' is now complete!"

User: "Delete the groceries task"
Bot:  "Done! 🗑️ 'Buy groceries' has been removed."
```

## 🔧 MCP Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_task` | title, description? | Add a new task |
| `list_tasks` | status? | List tasks (all/pending/completed) |
| `complete_task` | task_id | Mark task as done |
| `delete_task` | task_id | Remove a task |
| `update_task` | task_id, title?, description? | Update task details |

## 📚 Documentation

- [Overview Specification](./@specs/overview.md)
- [Architecture](./@specs/architecture.md)
- [MCP Tools](./@specs/mcp/tools.md)
- [Chat API](./@specs/api/chat-endpoint.md)
- [Database Schema](./@specs/database/schema.md)
- [Task Breakdown](./@specs/tasks.md)

## 🔐 Security

- **Domain Allowlist**: ChatKit restricted to allowed domains
- **JWT Authentication**: All chat endpoints require auth
- **User Isolation**: Tasks filtered by authenticated user
- **Rate Limiting**: 60 requests/minute per user

## 📊 Phase II → Phase III Evolution

| Phase II | Phase III |
|----------|-----------|
| Form-based task creation | Natural language commands |
| Click-based navigation | Conversational flow |
| Traditional UI | Chat interface |
| Direct API calls | AI-orchestrated tool execution |

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
pnpm test
```

## 📝 License

MIT License - Hackathon II Project

---

Built with ❤️ for the Evolution of Todo Hackathon
