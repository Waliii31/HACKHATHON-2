# Phase III: Sequential Implementation Guide

## Overview

This document provides a step-by-step implementation guide for Phase III: Todo AI Chatbot. Tasks are organized in sequential order with dependencies clearly marked.

---

## Implementation Phases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE A: Database Setup (Tasks 1-4)                                        │
│  └─ Foundation: Create tables for conversation history                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE B: MCP Server (Tasks 5-12)                                           │
│  └─ Core: Implement MCP server with 5 tools                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE C: AI Agent (Tasks 13-17)                                            │
│  └─ Brain: Configure OpenAI Agents SDK                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE D: Chat API (Tasks 18-23)                                            │
│  └─ Interface: Build stateless POST /api/chat endpoint                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE E: Frontend UI (Tasks 24-32)                                         │
│  └─ Experience: Build chat interface with ChatKit                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE F: Integration (Tasks 33-38)                                         │
│  └─ Connect: Full end-to-end testing and polish                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE A: Database Migration (Tasks 1-4)

### Task 1: Create Conversation Model
**File:** `backend/app/models/conversation.py`  
**Dependencies:** None  
**Estimated Time:** 30 min

**Steps:**
1. Create new file `backend/app/models/conversation.py`
2. Define `Conversation` SQLModel class with fields:
   - `id`: UUID, primary key
   - `user_id`: UUID, foreign key to users
   - `title`: Optional string
   - `created_at`: datetime
   - `updated_at`: datetime
3. Add relationship to messages
4. Export from `__init__.py`

**Acceptance Criteria:**
- [ ] Model class defined with all fields
- [ ] Foreign key relationship to users configured
- [ ] Model importable from models package

---

### Task 2: Create Message Model
**File:** `backend/app/models/message.py`  
**Dependencies:** Task 1  
**Estimated Time:** 30 min

**Steps:**
1. Create new file `backend/app/models/message.py`
2. Define `Message` SQLModel class with fields:
   - `id`: UUID, primary key
   - `conversation_id`: UUID, foreign key to conversations
   - `role`: string (user/assistant/system)
   - `content`: string
   - `tools_used`: Optional JSON string
   - `created_at`: datetime
3. Add relationship to conversation
4. Add helper methods for JSON serialization

**Acceptance Criteria:**
- [ ] Model class defined with all fields
- [ ] Role constraint applied
- [ ] JSON helper methods working

---

### Task 3: Create Database Migration Script
**File:** `backend/migrations/002_conversation_tables.sql`  
**Dependencies:** Tasks 1-2  
**Estimated Time:** 20 min

**Steps:**
1. Create migration SQL file
2. Add `conversations` table CREATE statement
3. Add `messages` table CREATE statement
4. Add indexes for performance
5. Add trigger for `updated_at` auto-update

**Acceptance Criteria:**
- [ ] SQL syntax valid
- [ ] All constraints defined
- [ ] Indexes created

---

### Task 4: Run Database Migration
**File:** `backend/run_migration.py` (update)  
**Dependencies:** Task 3  
**Estimated Time:** 15 min

**Steps:**
1. Update migration runner to execute new SQL
2. Run migration against Neon PostgreSQL
3. Verify tables created successfully
4. Test with sample insert/select

**Acceptance Criteria:**
- [ ] Migration completes without errors
- [ ] Tables visible in database
- [ ] CRUD operations work

---

## PHASE B: MCP Server Implementation (Tasks 5-12)

### Task 5: Install MCP SDK
**File:** `backend/requirements.txt`  
**Dependencies:** None  
**Estimated Time:** 10 min

**Steps:**
1. Add MCP SDK to requirements.txt:
   ```
   mcp-sdk>=1.0.0
   openai-agents>=1.0.0
   ```
2. Install packages: `pip install -r requirements.txt`
3. Verify imports work

**Acceptance Criteria:**
- [ ] Packages installed successfully
- [ ] No import errors

---

### Task 6: Create MCP Server Skeleton
**File:** `backend/app/mcp/server.py`  
**Dependencies:** Task 5  
**Estimated Time:** 30 min

**Steps:**
1. Create `backend/app/mcp/` directory
2. Create `__init__.py` and `server.py`
3. Initialize MCP Server with config
4. Create tool registration method
5. Export singleton instance

**Acceptance Criteria:**
- [ ] Server initializes without errors
- [ ] Tool registration method works

---

### Task 7: Create Tool Context
**File:** `backend/app/mcp/context.py`  
**Dependencies:** Task 6  
**Estimated Time:** 15 min

**Steps:**
1. Create `ToolContext` dataclass
2. Add `user_id` field for user isolation
3. Add database session getter
4. Add any utility methods

**Acceptance Criteria:**
- [ ] Context properly passes user_id
- [ ] Database access works through context

---

### Task 8: Implement add_task Tool
**File:** `backend/app/mcp/tools/add_task.py`  
**Dependencies:** Tasks 6-7  
**Estimated Time:** 45 min

**Steps:**
1. Create `backend/app/mcp/tools/` directory
2. Define tool schema (name, description, parameters)
3. Implement execute function:
   - Validate title (required, max 200 chars)
   - Create Task record with user_id from context
   - Return success with task_id and title
4. Register tool with server
5. Write unit test

**Acceptance Criteria:**
- [ ] Tool creates tasks in database
- [ ] User isolation enforced
- [ ] Proper error handling
- [ ] Unit test passes

---

### Task 9: Implement list_tasks Tool
**File:** `backend/app/mcp/tools/list_tasks.py`  
**Dependencies:** Tasks 6-7  
**Estimated Time:** 45 min

**Steps:**
1. Define tool schema with optional status parameter
2. Implement execute function:
   - Query tasks filtered by user_id
   - Apply status filter if provided
   - Format tasks as list of dicts
   - Return with count
3. Register tool with server
4. Write unit test

**Acceptance Criteria:**
- [ ] Lists only user's tasks
- [ ] Status filter works (all/pending/completed)
- [ ] Empty list handled gracefully

---

### Task 10: Implement complete_task Tool
**File:** `backend/app/mcp/tools/complete_task.py`  
**Dependencies:** Tasks 6-7  
**Estimated Time:** 45 min

**Steps:**
1. Define tool schema with task_id parameter
2. Implement execute function:
   - Validate UUID format
   - Find task by ID and user_id
   - Update status to "completed"
   - Set completed_at timestamp
   - Return confirmation
3. Handle task not found error
4. Write unit test

**Acceptance Criteria:**
- [ ] Task status updated correctly
- [ ] Ownership validated
- [ ] Proper error for not found

---

### Task 11: Implement delete_task Tool
**File:** `backend/app/mcp/tools/delete_task.py`  
**Dependencies:** Tasks 6-7  
**Estimated Time:** 30 min

**Steps:**
1. Define tool schema with task_id parameter
2. Implement execute function:
   - Validate UUID format
   - Find task by ID and user_id
   - Delete task record
   - Return confirmation
3. Handle task not found error
4. Write unit test

**Acceptance Criteria:**
- [ ] Task deleted from database
- [ ] Ownership validated
- [ ] Proper error for not found

---

### Task 12: Implement update_task Tool
**File:** `backend/app/mcp/tools/update_task.py`  
**Dependencies:** Tasks 6-7  
**Estimated Time:** 45 min

**Steps:**
1. Define tool schema with task_id, title, description parameters
2. Implement execute function:
   - Validate at least one update field provided
   - Find task by ID and user_id
   - Update provided fields only
   - Return updated task details
3. Handle task not found error
4. Write unit test

**Acceptance Criteria:**
- [ ] Partial updates work
- [ ] Ownership validated
- [ ] Old and new values in response

---

## PHASE C: AI Agent Setup (Tasks 13-17)

### Task 13: Create System Prompt
**File:** `backend/app/agent/prompts.py`  
**Dependencies:** None  
**Estimated Time:** 30 min

**Steps:**
1. Create `backend/app/agent/` directory
2. Write SYSTEM_PROMPT constant with:
   - Agent personality (friendly, helpful)
   - Available tools documentation
   - Intent recognition patterns
   - Response templates
   - Error handling guidelines
3. Export constant

**Acceptance Criteria:**
- [ ] Prompt covers all tools
- [ ] Clear intent patterns defined
- [ ] Response style documented

---

### Task 14: Configure Agent
**File:** `backend/app/agent/brain.py`  
**Dependencies:** Tasks 6-12, 13  
**Estimated Time:** 45 min

**Steps:**
1. Import OpenAI Agents SDK
2. Import MCP server tools
3. Create Agent instance with:
   - name: "TodoBot"
   - model: "gpt-4-turbo-preview"
   - instructions: SYSTEM_PROMPT
   - tools: MCP tools
   - tool_choice: "auto"
   - temperature: 0.7
4. Export agent instance

**Acceptance Criteria:**
- [ ] Agent instantiates without errors
- [ ] Tools properly connected
- [ ] Configuration matches spec

---

### Task 15: Implement process_message Function
**File:** `backend/app/agent/brain.py`  
**Dependencies:** Task 14  
**Estimated Time:** 60 min

**Steps:**
1. Create `process_message` async function
2. Parameters: user_message, user_id, history
3. Implementation:
   - Create ToolContext with user_id
   - Build messages array from history
   - Add user message
   - Run agent with Runner
   - Extract response content
   - Extract tools_used list
4. Return (response_text, tools_used)
5. Write integration test

**Acceptance Criteria:**
- [ ] Function executes tools correctly
- [ ] Response generated properly
- [ ] Tools tracked in tools_used

---

### Task 16: Implement Context Window Management
**File:** `backend/app/agent/brain.py`  
**Dependencies:** Task 15  
**Estimated Time:** 30 min

**Steps:**
1. Add context optimization function
2. Limit to last 10 messages
3. Estimate token count
4. Truncate if exceeding limit
5. Test with long conversations

**Acceptance Criteria:**
- [ ] Context properly limited
- [ ] Recent messages prioritized
- [ ] No token limit errors

---

### Task 17: Add Error Handling
**File:** `backend/app/agent/brain.py`  
**Dependencies:** Task 15  
**Estimated Time:** 30 min

**Steps:**
1. Wrap agent execution in try/except
2. Handle API errors (rate limit, timeout)
3. Handle tool execution failures
4. Generate user-friendly error messages
5. Log errors for debugging

**Acceptance Criteria:**
- [ ] Errors caught and logged
- [ ] User sees friendly messages
- [ ] No stack traces exposed

---

## PHASE D: Chat API Endpoint (Tasks 18-23)

### Task 18: Create Chat Schemas
**File:** `backend/app/schemas/chat.py`  
**Dependencies:** None  
**Estimated Time:** 20 min

**Steps:**
1. Create Pydantic schemas:
   - `ChatRequest`: message (str), conversation_id (Optional[UUID])
   - `ToolUsage`: name, success, result
   - `ChatResponse`: conversation_id, message_id, response, tools_used, timestamp
2. Add validation rules (message length 1-2000)

**Acceptance Criteria:**
- [ ] Schemas validate correctly
- [ ] Proper error messages for invalid input

---

### Task 19: Create Conversation Repository
**File:** `backend/app/repositories/conversation.py`  
**Dependencies:** Tasks 1-4  
**Estimated Time:** 30 min

**Steps:**
1. Create `get_conversation` function (by ID and user_id)
2. Create `create_conversation` function
3. Create `get_user_conversations` function (with pagination)
4. Create `delete_conversation` function

**Acceptance Criteria:**
- [ ] All CRUD operations work
- [ ] User isolation enforced

---

### Task 20: Create Message Repository
**File:** `backend/app/repositories/message.py`  
**Dependencies:** Tasks 1-4  
**Estimated Time:** 30 min

**Steps:**
1. Create `get_conversation_messages` function (with limit)
2. Create `add_message` function
3. Create `get_message_count` function

**Acceptance Criteria:**
- [ ] Messages retrieved in order
- [ ] Limit parameter works

---

### Task 21: Implement POST /api/chat Endpoint
**File:** `backend/app/api/chat.py`  
**Dependencies:** Tasks 13-20  
**Estimated Time:** 90 min

**Steps:**
1. Create chat router
2. Add authentication dependency
3. Implement endpoint following flow:
   ```
   1. Verify JWT → get user_id
   2. Get/create conversation
   3. Store user message in DB
   4. Call process_message (agent)
   5. Store AI response in DB
   6. Return ChatResponse
   ```
4. Add proper error handling
5. Register router in main app

**Acceptance Criteria:**
- [ ] Full flow works end-to-end
- [ ] Messages persisted correctly
- [ ] Authentication enforced

---

### Task 22: Implement Conversation List Endpoint
**File:** `backend/app/api/chat.py`  
**Dependencies:** Tasks 19-21  
**Estimated Time:** 30 min

**Steps:**
1. Add GET /api/chat/conversations endpoint
2. Implement pagination (limit, offset)
3. Include last message preview
4. Include message count

**Acceptance Criteria:**
- [ ] Pagination works
- [ ] Metadata included

---

### Task 23: Implement Conversation Delete Endpoint
**File:** `backend/app/api/chat.py`  
**Dependencies:** Tasks 19-21  
**Estimated Time:** 20 min

**Steps:**
1. Add DELETE /api/chat/conversations/{id} endpoint
2. Verify ownership before delete
3. Cascade delete messages
4. Return 204 No Content

**Acceptance Criteria:**
- [ ] Conversation and messages deleted
- [ ] Ownership validated

---

## PHASE E: Frontend UI (Tasks 24-32)

### Task 24: Create Chat Page Route
**File:** `frontend/app/chat/page.tsx`  
**Dependencies:** None  
**Estimated Time:** 20 min

**Steps:**
1. Create `app/chat/` directory
2. Create `page.tsx` with basic structure
3. Add authentication check (redirect if not logged in)
4. Set up page metadata

**Acceptance Criteria:**
- [ ] Page accessible at /chat
- [ ] Protected by auth

---

### Task 25: Create Chat API Client
**File:** `frontend/lib/chat-client.ts`  
**Dependencies:** None  
**Estimated Time:** 30 min

**Steps:**
1. Create `sendChatMessage` function
2. Create `getConversations` function
3. Create `getConversation` function
4. Create `deleteConversation` function
5. Add JWT token handling

**Acceptance Criteria:**
- [ ] All API calls work
- [ ] Proper error handling

---

### Task 26: Create TypeScript Types
**File:** `frontend/types/chat.ts`  
**Dependencies:** None  
**Estimated Time:** 15 min

**Steps:**
1. Define `Message` interface
2. Define `Conversation` interface
3. Define `ChatRequest` interface
4. Define `ChatResponse` interface
5. Define `ToolUsage` interface

**Acceptance Criteria:**
- [ ] Types match API schemas
- [ ] IntelliSense works

---

### Task 27: Create MessageList Component
**File:** `frontend/components/chat/MessageList.tsx`  
**Dependencies:** Task 26  
**Estimated Time:** 60 min

**Steps:**
1. Create scrollable container
2. Render messages with different styles:
   - User: right-aligned, primary color
   - Assistant: left-aligned, neutral color
3. Add timestamps
4. Implement auto-scroll to bottom
5. Add loading indicator

**Acceptance Criteria:**
- [ ] Messages display correctly
- [ ] Scroll works
- [ ] Loading state shown

---

### Task 28: Create ChatInput Component
**File:** `frontend/components/chat/ChatInput.tsx`  
**Dependencies:** None  
**Estimated Time:** 45 min

**Steps:**
1. Create text input with send button
2. Handle Enter key submission
3. Implement 2000 character limit
4. Add disabled state during loading
5. Clear input after send

**Acceptance Criteria:**
- [ ] Input sends on Enter
- [ ] Character limit enforced
- [ ] Disabled during processing

---

### Task 29: Create ConversationList Component
**File:** `frontend/components/chat/ConversationList.tsx`  
**Dependencies:** Tasks 25-26  
**Estimated Time:** 45 min

**Steps:**
1. Fetch and display conversations
2. Show title and timestamp
3. Handle conversation selection
4. Add "New Chat" button
5. Add delete option

**Acceptance Criteria:**
- [ ] Conversations listed
- [ ] Selection works
- [ ] Delete works

---

### Task 30: Create TypingIndicator Component
**File:** `frontend/components/chat/TypingIndicator.tsx`  
**Dependencies:** None  
**Estimated Time:** 20 min

**Steps:**
1. Create animated typing dots (CSS)
2. Match assistant message style
3. Export component

**Acceptance Criteria:**
- [ ] Animation smooth
- [ ] Style matches messages

---

### Task 31: Create ChatInterface Component
**File:** `frontend/components/chat/ChatInterface.tsx`  
**Dependencies:** Tasks 27-30  
**Estimated Time:** 90 min

**Steps:**
1. Create main chat container
2. Manage state: messages, conversationId, isLoading
3. Implement handleSendMessage:
   - Add user message to UI
   - Call API
   - Add AI response
4. Implement loadConversation
5. Implement startNewConversation
6. Compose child components

**Acceptance Criteria:**
- [ ] Full chat flow works
- [ ] State managed correctly
- [ ] Error handling in place

---

### Task 32: Style Chat Interface
**File:** `frontend/app/chat/page.tsx` + CSS  
**Dependencies:** Tasks 24-31  
**Estimated Time:** 60 min

**Steps:**
1. Add responsive layout (sidebar + main)
2. Style message bubbles
3. Add empty state with suggestions
4. Add transitions and animations
5. Ensure mobile responsiveness

**Acceptance Criteria:**
- [ ] UI looks polished
- [ ] Mobile layout works
- [ ] Animations smooth

---

## PHASE F: Integration & Testing (Tasks 33-38)

### Task 33: Configure Environment Variables
**Files:** `.env`, `.env.local`  
**Dependencies:** All previous  
**Estimated Time:** 20 min

**Steps:**
1. Update backend .env:
   - OPENAI_API_KEY
   - DATABASE_URL
   - ALLOWED_ORIGINS
2. Update frontend .env.local:
   - NEXT_PUBLIC_API_BASE_URL
   - NEXT_PUBLIC_CHATKIT_DOMAIN_ALLOWLIST
3. Create .env.example files

**Acceptance Criteria:**
- [ ] All vars documented
- [ ] Examples provided

---

### Task 34: Connect Frontend to Backend
**File:** N/A (integration)  
**Dependencies:** All previous  
**Estimated Time:** 60 min

**Steps:**
1. Start backend server
2. Start frontend server
3. Test authentication flow
4. Test sending first message
5. Verify message persistence
6. Test conversation history

**Acceptance Criteria:**
- [ ] Full flow works
- [ ] Messages persisted
- [ ] History loads correctly

---

### Task 35: Test MCP Tool Execution
**File:** N/A (testing)  
**Dependencies:** Task 34  
**Estimated Time:** 90 min

**Steps:**
1. Test: "Add buy groceries" → verify task created
2. Test: "Show my tasks" → verify tasks listed
3. Test: "Complete buy groceries" → verify status updated
4. Test: "Delete buy groceries" → verify task deleted
5. Test: "Update task to buy organic groceries" → verify updated
6. Test error cases (not found, ambiguous)

**Acceptance Criteria:**
- [ ] All 5 tools work via chat
- [ ] Error messages friendly

---

### Task 36: Implement Rate Limiting
**File:** `backend/app/api/deps.py`  
**Dependencies:** Task 21  
**Estimated Time:** 45 min

**Steps:**
1. Add rate limiting dependency
2. Configure: 60/min, 500/hour per user
3. Add rate limit headers
4. Test rate limit behavior
5. Add friendly error messages

**Acceptance Criteria:**
- [ ] Limits enforced
- [ ] Headers present
- [ ] User-friendly 429 response

---

### Task 37: Security Audit
**File:** N/A (security)  
**Dependencies:** All previous  
**Estimated Time:** 60 min

**Steps:**
1. Verify domain allowlist works
2. Test unauthorized access attempts
3. Verify user data isolation
4. Check for injection vulnerabilities
5. Review CORS settings
6. Verify JWT validation

**Acceptance Criteria:**
- [ ] No security issues found
- [ ] User isolation confirmed

---

### Task 38: Documentation & Cleanup
**Files:** README.md, code comments  
**Dependencies:** All previous  
**Estimated Time:** 60 min

**Steps:**
1. Update Phase-3 README with setup instructions
2. Add code comments to complex logic
3. Create API documentation
4. Document known issues
5. Clean up unused code
6. Final code review

**Acceptance Criteria:**
- [ ] Setup instructions work
- [ ] API documented
- [ ] Code clean

---

## Task Summary

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| A: Database | 1-4 | 1.5 hours |
| B: MCP Server | 5-12 | 5 hours |
| C: AI Agent | 13-17 | 3.5 hours |
| D: Chat API | 18-23 | 4 hours |
| E: Frontend UI | 24-32 | 7 hours |
| F: Integration | 33-38 | 6 hours |
| **Total** | **38 tasks** | **~27 hours** |

---

## Dependency Graph

```
PHASE A (DB)
│
├── Task 1 (Conversation Model)
│   └── Task 2 (Message Model)
│       └── Task 3 (Migration SQL)
│           └── Task 4 (Run Migration)
│
PHASE B (MCP) ──────────────────────┐
│                                   │
├── Task 5 (Install SDK)            │
│   └── Task 6 (Server Skeleton)    │
│       └── Task 7 (Context)        │
│           ├── Task 8 (add_task)   │
│           ├── Task 9 (list_tasks) │
│           ├── Task 10 (complete)──┼───┐
│           ├── Task 11 (delete)    │   │
│           └── Task 12 (update)    │   │
│                                   │   │
PHASE C (Agent) ◄───────────────────┘   │
│                                       │
├── Task 13 (System Prompt)             │
│   └── Task 14 (Configure Agent) ◄─────┘
│       └── Task 15 (process_message)
│           ├── Task 16 (Context Window)
│           └── Task 17 (Error Handling)
│
PHASE D (API) ◄─────────────────────────┐
│                                       │
├── Task 18 (Schemas)                   │
├── Task 19 (Conversation Repo) ◄───────┤
├── Task 20 (Message Repo) ◄────────────┤
│   └── Task 21 (POST /api/chat) ◄──────┘
│       ├── Task 22 (List Convos)
│       └── Task 23 (Delete Convo)
│
PHASE E (Frontend)
│
├── Task 24 (Chat Page)
├── Task 25 (API Client)
├── Task 26 (Types)
│   └── Task 27 (MessageList) ◄─────┐
│       ├── Task 28 (ChatInput)     │
│       ├── Task 29 (ConvoList)     │
│       └── Task 30 (Typing)        │
│           └── Task 31 (Interface)─┘
│               └── Task 32 (Styling)
│
PHASE F (Integration)
│
├── Task 33 (Env Vars)
│   └── Task 34 (Connect F/B)
│       └── Task 35 (Test MCP)
│           └── Task 36 (Rate Limit)
│               └── Task 37 (Security)
│                   └── Task 38 (Docs)
```

---

## Quick Start Checklist

- [ ] **Phase A Complete**: Database tables created
- [ ] **Phase B Complete**: MCP server with 5 tools working
- [ ] **Phase C Complete**: AI agent processing messages
- [ ] **Phase D Complete**: Chat API accepting requests
- [ ] **Phase E Complete**: Chat UI rendering
- [ ] **Phase F Complete**: Full integration tested
