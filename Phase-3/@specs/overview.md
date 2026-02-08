# Phase III: Todo AI Chatbot - Specifications Overview

## Purpose of Phase III

Phase III transforms the Phase II full-stack Todo Web Application into an AI-powered conversational chatbot. Users will manage their todos through natural language interactions instead of traditional UI forms. The core innovation is the integration of OpenAI ChatKit for the frontend, OpenAI Agents SDK for the AI "brain", and an MCP (Model Context Protocol) server that exposes todo operations as tools. This phase demonstrates proficiency in AI agent development, MCP server architecture, and conversational interface design.

## Scope

### Included in Phase III
- Conversational interface for todo management using OpenAI ChatKit
- AI Agent "Brain" using OpenAI Agents SDK for intent recognition and tool orchestration
- MCP Server with Official MCP SDK exposing todo operations as tools
- Stateless chat API endpoint (`POST /api/chat`)
- Conversation history persistence in Neon PostgreSQL database
- Natural language to tool mapping (e.g., "Buy milk" → `add_task`)
- Domain Allowlist security configuration for ChatKit
- Integration with existing Neon PostgreSQL database from Phase II
- Friendly confirmation responses for all actions

### Excluded from Phase III
- Voice interface or speech recognition
- Multi-language support beyond English
- Advanced analytics or reporting features
- Real-time collaboration or shared todos
- Offline capabilities
- Third-party calendar integrations
- Mobile native application

## Current Phase: Phase III

This is the third phase of the Hackathon II project, evolving from the Phase II web application. Phase III introduces AI-driven interactions, agent-based architecture, and the MCP protocol for tool orchestration.

## High-Level Feature List

1. **Conversational Interface**
   - Natural language input for todo management
   - OpenAI ChatKit-powered frontend
   - Real-time chat responses
   - Message history display

2. **AI Agent Brain**
   - Intent recognition from natural language
   - Tool selection and orchestration
   - Context-aware responses
   - Friendly action confirmations

3. **MCP Server Tools**
   - `add_task(title, description)` - Create new tasks
   - `list_tasks(status)` - Retrieve tasks by status
   - `complete_task(task_id)` - Mark tasks as complete
   - `delete_task(task_id)` - Remove tasks
   - `update_task(task_id, title, description)` - Modify existing tasks

4. **Stateless API Architecture**
   - Stateless `POST /api/chat` endpoint
   - Conversation history in PostgreSQL
   - Session-based context management

5. **Security Features**
   - Domain Allowlist for ChatKit
   - JWT-based user authentication
   - Secure API endpoints
   - User data isolation

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend Chat | OpenAI ChatKit | Conversational UI component library |
| AI Agent | OpenAI Agents SDK | Agent orchestration and tool calling |
| MCP Server | Official MCP SDK | Expose todo operations as AI tools |
| Chat API | FastAPI | Stateless chat endpoint |
| Database | Neon Serverless PostgreSQL | Task storage and conversation history |
| Database ORM | SQLModel | SQL database modeling |
| Authentication | Better Auth + JWT | User authentication and verification |
| Backend Framework | FastAPI + Python | Server-side application logic |
| Frontend Framework | Next.js (App Router) | React framework with TypeScript |

## User Stories

### US-001: Natural Language Task Creation
**As a** user  
**I want to** create tasks by typing natural language commands like "Add buy groceries to my list"  
**So that** I can quickly add tasks without navigating complex forms

**Acceptance Criteria:**
- User can type natural language in chat input
- AI agent recognizes task creation intent
- MCP `add_task` tool is called with extracted title/description
- User receives friendly confirmation: "I've added 'buy groceries' to your list!"

### US-002: Task Listing via Conversation
**As a** user  
**I want to** ask "What are my pending tasks?" or "Show my completed tasks"  
**So that** I can view my tasks conversationally

**Acceptance Criteria:**
- User can ask about tasks in natural language
- AI agent recognizes list intent and status filter
- MCP `list_tasks` tool is called with appropriate status
- Tasks are displayed in readable chat format

### US-003: Task Completion via Chat
**As a** user  
**I want to** say "Mark buy groceries as done" or "Complete task 3"  
**So that** I can update task status conversationally

**Acceptance Criteria:**
- User can request task completion in natural language
- AI agent identifies the task and calls `complete_task`
- User sees confirmation: "Done! 'Buy groceries' is now marked as complete."

### US-004: Task Deletion via Chat
**As a** user  
**I want to** say "Delete the grocery task" or "Remove task 5"  
**So that** I can remove tasks without UI navigation

**Acceptance Criteria:**
- User can request task deletion in natural language
- AI agent confirms task to delete
- MCP `delete_task` tool is called
- User receives confirmation message

### US-005: Task Update via Chat
**As a** user  
**I want to** say "Change buy groceries to buy organic groceries"  
**So that** I can update task details conversationally

**Acceptance Criteria:**
- User can request task updates in natural language
- AI agent extracts task ID and new values
- MCP `update_task` tool is called
- User receives confirmation with updated details

### US-006: Conversation History Persistence
**As a** user  
**I want my** conversation history to persist across sessions  
**So that** I can continue where I left off

**Acceptance Criteria:**
- Chat messages are stored in PostgreSQL
- User sees previous messages when returning
- Context is maintained for follow-up questions

### US-007: Secure Chat Access
**As a** user  
**I want to** only access my own tasks and conversations  
**So that** my data remains private

**Acceptance Criteria:**
- Authentication required for chat access
- Tasks are filtered by authenticated user
- Conversation history is user-specific
- Domain allowlist prevents unauthorized access

## Success Criteria for Phase III Submission

### Functional Requirements
- [ ] Conversational interface using OpenAI ChatKit
- [ ] AI agent brain with OpenAI Agents SDK
- [ ] MCP server with all 5 required tools implemented
- [ ] Stateless `POST /api/chat` endpoint
- [ ] Conversation history stored in PostgreSQL
- [ ] Natural language intent mapping to MCP tools
- [ ] Friendly confirmation responses for all actions

### Technical Requirements
- [ ] MCP server using Official MCP SDK
- [ ] Domain Allowlist security configuration
- [ ] Integration with existing Neon PostgreSQL
- [ ] JWT authentication for chat endpoint
- [ ] Proper error handling and validation

### Quality Requirements
- [ ] Accurate intent recognition (>90% success rate)
- [ ] Response time < 3 seconds for tool execution
- [ ] Clear and friendly bot responses
- [ ] Proper conversation context management
- [ ] Comprehensive error messages

### Compliance Requirements
- [ ] Full adherence to project Constitution
- [ ] Implementation following approved specifications
- [ ] Security best practices
- [ ] Documentation completeness
