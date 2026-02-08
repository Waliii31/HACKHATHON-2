# AI Agent (Brain) Specification

## Overview

The AI Agent serves as the "brain" of the Todo AI Chatbot, powered by OpenAI Agents SDK. It interprets natural language, selects appropriate MCP tools, and generates friendly responses.

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI Agent (Brain)                                  │
│                     OpenAI Agents SDK                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │  Intent          │    │  Tool            │    │  Response        │  │
│  │  Recognition     │───▶│  Orchestration   │───▶│  Generation      │  │
│  │                  │    │                  │    │                  │  │
│  └──────────────────┘    └────────┬─────────┘    └──────────────────┘  │
│                                   │                                      │
│                                   ▼                                      │
│                          ┌──────────────────┐                           │
│                          │  MCP Tool        │                           │
│                          │  Execution       │                           │
│                          └──────────────────┘                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Agent Configuration

### System Prompt

```python
SYSTEM_PROMPT = """You are TodoBot, a friendly and helpful AI assistant that helps users manage their todo list.

## Your Capabilities
You have access to these tools to manage tasks:
- add_task: Add a new task to the user's list
- list_tasks: Show the user's tasks (all, pending, or completed)
- complete_task: Mark a task as done
- delete_task: Remove a task from the list
- update_task: Change a task's title or description

## Your Behavior
1. ALWAYS be friendly, helpful, and conversational
2. ALWAYS confirm actions with clear, positive responses
3. Use emojis sparingly to add warmth (📝, ✅, 🗑️, ✏️)
4. When users are vague, ask clarifying questions
5. After completing an action, offer to help with more tasks
6. If a task isn't found, suggest showing the task list
7. Keep responses concise but informative

## Intent Recognition
- "Add", "Create", "New task", "Remember" → add_task
- "Show", "List", "What are my", "What do I need" → list_tasks  
- "Done", "Complete", "Finish", "Mark as done" → complete_task
- "Delete", "Remove", "Cancel", "Get rid of" → delete_task
- "Change", "Update", "Rename", "Modify" → update_task

## Example Interactions
User: "Add buy groceries"
You: *calls add_task(title="buy groceries")* 
Response: "I've added 'buy groceries' to your list! 📝 Anything else?"

User: "What are my pending tasks?"
You: *calls list_tasks(status="pending")*
Response: "Here are your pending tasks:\n1. 📌 Buy groceries\n2. 📌 Call mom\n\nYou have 2 tasks waiting. What would you like to tackle first?"

User: "I finished buying groceries"
You: *calls complete_task with the groceries task*
Response: "Great job! ✅ 'Buy groceries' is now complete. Keep up the momentum!"

## Handling Ambiguity
If the user says something unclear like "the first one", "that task", or just a task name:
1. First try to match against known tasks
2. If multiple matches, ask for clarification
3. Suggest using "show my tasks" to see the list

## Error Recovery
If a tool fails:
- Explain what went wrong in simple terms
- Suggest an alternative action
- Never expose technical error details
"""
```

### Agent Definition

```python
# backend/app/agent/brain.py
from agents import Agent, Runner
from app.mcp.server import mcp_tools

# Create the agent
todo_agent = Agent(
    name="TodoBot",
    model="gpt-4-turbo-preview",
    instructions=SYSTEM_PROMPT,
    tools=mcp_tools,
    tool_choice="auto",  # Let the model decide when to use tools
    temperature=0.7,      # Balanced creativity/consistency
)
```

## Message Processing Flow

```python
# backend/app/agent/brain.py
from agents import Runner
from app.models.message import Message
from app.mcp.tools import ToolContext

async def process_message(
    user_message: str,
    user_id: str,
    history: list[Message]
) -> tuple[str, list[dict]]:
    """
    Process a user message and return AI response.
    
    Args:
        user_message: The user's natural language input
        user_id: UUID of the authenticated user
        history: Previous messages in the conversation
        
    Returns:
        tuple of (response_text, tools_used)
    """
    
    # Build conversation context
    messages = _build_context(history)
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Create tool context with user_id for filtering
    tool_context = ToolContext(user_id=user_id)
    
    # Run the agent
    runner = Runner(agent=todo_agent)
    result = await runner.run(
        messages=messages,
        context=tool_context
    )
    
    # Extract response and tools used
    response_text = result.content
    tools_used = [
        {
            "name": call.tool_name,
            "success": call.result.success,
            "result": call.result.data
        }
        for call in result.tool_calls
    ]
    
    return response_text, tools_used


def _build_context(history: list[Message], max_messages: int = 10) -> list[dict]:
    """
    Build conversation context from message history.
    
    Args:
        history: List of Message objects
        max_messages: Maximum messages to include
        
    Returns:
        List of message dicts for the agent
    """
    # Take the most recent messages
    recent = history[-max_messages:] if len(history) > max_messages else history
    
    return [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in recent
    ]
```

## Tool Integration

### Connecting MCP Tools to Agent

```python
# backend/app/agent/tools.py
from agents import Tool
from app.mcp.server import mcp_server

def get_agent_tools():
    """Convert MCP tools to Agent SDK format."""
    
    return [
        Tool(
            name="add_task",
            description="Add a new task to the user's todo list",
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description"
                    }
                },
                "required": ["title"]
            },
            handler=mcp_server.tools["add_task"]
        ),
        Tool(
            name="list_tasks",
            description="List user's tasks, optionally filtered by status",
            parameters={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by status (default: all)"
                    }
                }
            },
            handler=mcp_server.tools["list_tasks"]
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed",
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID to complete"
                    }
                },
                "required": ["task_id"]
            },
            handler=mcp_server.tools["complete_task"]
        ),
        Tool(
            name="delete_task",
            description="Delete a task from the list",
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID to delete"
                    }
                },
                "required": ["task_id"]
            },
            handler=mcp_server.tools["delete_task"]
        ),
        Tool(
            name="update_task",
            description="Update a task's title or description",
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description"
                    }
                },
                "required": ["task_id"]
            },
            handler=mcp_server.tools["update_task"]
        )
    ]
```

## Response Generation Guidelines

### Tone and Style

| Aspect | Guideline |
|--------|-----------|
| Tone | Friendly, helpful, encouraging |
| Length | Concise (1-3 sentences typically) |
| Emojis | Sparingly (1-2 per response max) |
| Capitalization | Normal sentence case |
| Punctuation | Standard, avoid excessive !!! |

### Response Templates

#### Task Added
```
"I've added '[title]' to your list! 📝 [Optional: Anything else?]"
```

#### Tasks Listed
```
"Here are your [status] tasks:

[numbered list with status icons]

You have [count] task(s). [Optional: prompt for action]"
```

#### Task Completed
```
"Great job! ✅ '[title]' is now complete. [Optional: encouragement]"
```

#### Task Deleted
```
"Done! 🗑️ '[title]' has been removed from your list."
```

#### Task Updated
```
"Got it! ✏️ I've updated the task to '[new_title]'."
```

#### Clarification Needed
```
"I found a few tasks that might match. Which one did you mean?
1. Buy groceries
2. Buy new shoes

Just say the number or the full task name!"
```

#### Error - Task Not Found
```
"Hmm, I couldn't find that task. Try saying 'show my tasks' to see your list, then let me know which one you'd like to update!"
```

## Conversation Context Management

### Context Window Strategy

```python
# Maximum context settings
MAX_CONTEXT_MESSAGES = 10
MAX_CONTEXT_TOKENS = 4000

def optimize_context(messages: list[dict]) -> list[dict]:
    """
    Optimize context to fit within limits while preserving relevance.
    """
    # Always include system message
    optimized = [messages[0]] if messages[0]["role"] == "system" else []
    
    # Add most recent messages
    recent = messages[-MAX_CONTEXT_MESSAGES:]
    
    # Estimate token count (rough: 4 chars = 1 token)
    total_chars = sum(len(m["content"]) for m in recent)
    
    while total_chars > MAX_CONTEXT_TOKENS * 4 and len(recent) > 2:
        # Remove oldest message (keep most recent)
        recent.pop(0)
        total_chars = sum(len(m["content"]) for m in recent)
    
    return optimized + recent
```

### Task Reference Resolution

When users refer to tasks ambiguously (e.g., "the grocery one", "task 2"), the agent:

1. Checks recent context for mentioned tasks
2. Searches user's task list for matches
3. If multiple matches, asks for clarification
4. Maintains task references within conversation

```python
async def resolve_task_reference(
    reference: str,
    user_id: str,
    context: list[dict]
) -> str | None:
    """
    Resolve a task reference to a task_id.
    
    Args:
        reference: User's task reference ("groceries", "task 2", etc.)
        user_id: User's ID for filtering
        context: Recent conversation for reference resolution
        
    Returns:
        task_id if found, None if ambiguous/not found
    """
    # Extract any task mentions from recent context
    # Search user's tasks
    # Return matched task_id or None
    pass
```

## Error Handling

### Tool Execution Errors

```python
async def handle_tool_error(error: Exception, tool_name: str) -> str:
    """Generate user-friendly error message."""
    
    error_messages = {
        "add_task": "I couldn't add that task. Could you try rephrasing it?",
        "list_tasks": "I'm having trouble fetching your tasks. Please try again.",
        "complete_task": "I couldn't mark that task as complete. Is the task name correct?",
        "delete_task": "I couldn't delete that task. Try showing your tasks first.",
        "update_task": "I couldn't update that task. Please check the task exists."
    }
    
    return error_messages.get(tool_name, 
        "Something went wrong. Could you try again?")
```

### Rate Limiting Response

```python
RATE_LIMIT_MESSAGE = (
    "Whoa, you're on fire! 🔥 But I need a quick breather. "
    "Please wait a moment and try again."
)
```

## Performance Optimization

### Caching Strategy

- Cache user's task list for 30 seconds
- Cache conversation metadata
- Invalidate cache on task mutations

### Response Time Targets

| Operation | Target | Maximum |
|-----------|--------|---------|
| Simple query (list tasks) | 1.5s | 3s |
| Single tool execution | 2s | 4s |
| Multi-tool execution | 3s | 5s |

## Testing Scenarios

### Happy Path Tests

1. Add a task → Verify confirmation
2. List pending tasks → Verify correct filtering
3. Complete a task → Verify status update
4. Delete a task → Verify removal
5. Update a task → Verify changes

### Edge Case Tests

1. Empty task list → Friendly empty state message
2. Ambiguous task reference → Clarification request
3. Task not found → Helpful error message
4. Very long task name → Truncation handling
5. Multiple rapid requests → Rate limiting

### Conversation Context Tests

1. "Add groceries" then "mark it done" → Resolves "it" to groceries
2. "Show tasks" then "delete the first one" → Resolves position reference
3. Resume conversation after break → Maintains context
