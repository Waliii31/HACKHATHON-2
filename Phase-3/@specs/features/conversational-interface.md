# Conversational Interface Feature Specification

## Overview

The Conversational Interface enables users to manage their todos through natural language interactions instead of traditional UI forms. Built with OpenAI ChatKit, it provides a modern chat experience similar to ChatGPT.

## Feature Requirements

### FR-001: Chat Message Input

**Description:** Users can type natural language messages to interact with their todos.

**Acceptance Criteria:**
- [ ] Text input field at bottom of chat interface
- [ ] Support for messages up to 2000 characters
- [ ] Send button and Enter key submission
- [ ] Input disabled while waiting for response
- [ ] Clear input after successful submission
- [ ] Visual feedback for character limit

**UI Specifications:**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                     Message History                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ ┌─┐ │
│ │ Type a message...                                   │ │➤│ │
│ └─────────────────────────────────────────────────────┘ └─┘ │
└─────────────────────────────────────────────────────────────┘
```

### FR-002: Message Display

**Description:** Chat messages are displayed in a scrollable conversation view.

**Acceptance Criteria:**
- [ ] User messages aligned to right with distinct styling
- [ ] AI responses aligned to left with bot avatar
- [ ] Timestamps for each message
- [ ] Auto-scroll to newest message
- [ ] Support for markdown formatting in AI responses
- [ ] Loading indicator while AI is processing

**Message Styling:**
| Element | User Messages | AI Messages |
|---------|---------------|-------------|
| Alignment | Right | Left |
| Background | Primary color | Gray/Neutral |
| Avatar | User initials/photo | Bot icon |
| Border | Rounded | Rounded |

### FR-003: Conversation History

**Description:** Users can view and continue previous conversations.

**Acceptance Criteria:**
- [ ] Sidebar with conversation list
- [ ] Conversations sorted by last activity
- [ ] Conversation title (auto-generated from first message)
- [ ] Click to load conversation
- [ ] New conversation button
- [ ] Delete conversation option

### FR-004: Real-time Response

**Description:** AI responses appear with minimal delay and visual feedback.

**Acceptance Criteria:**
- [ ] Typing indicator while waiting for response
- [ ] Response appears within 3 seconds for simple commands
- [ ] Error messages displayed inline on failure
- [ ] Retry option for failed requests

### FR-005: Tool Execution Feedback

**Description:** Users see feedback when AI executes tools.

**Acceptance Criteria:**
- [ ] Visual indicator when tool is being executed
- [ ] Success/failure status for tool execution
- [ ] Tool name displayed (e.g., "Adding task...")
- [ ] Result summary in natural language

**Example Display:**
```
┌──────────────────────────────────────────┐
│ 🔧 Adding task...                        │
│ ✅ Task "Buy groceries" added!           │
│                                          │
│ I've added 'Buy groceries' to your list! │
│ Is there anything else you need?         │
└──────────────────────────────────────────┘
```

## ChatKit Integration

### Configuration

```typescript
// frontend/lib/chatkit-config.ts
import { ChatKit } from '@openai/chatkit';

export const chatKitConfig = {
  // Domain allowlist for security
  allowedDomains: [
    'localhost:3000',
    'your-production-domain.com'
  ],
  
  // API configuration
  apiEndpoint: '/api/chat',
  
  // UI customization
  theme: {
    primaryColor: '#3B82F6',
    backgroundColor: '#FFFFFF',
    userMessageBg: '#3B82F6',
    botMessageBg: '#F3F4F6',
    fontFamily: 'Inter, system-ui, sans-serif'
  },
  
  // Behavior settings
  showTimestamps: true,
  showAvatars: true,
  enableMarkdown: true,
  maxMessageLength: 2000
};
```

### Component Structure

```typescript
// frontend/components/ChatInterface.tsx
'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ConversationSidebar } from './ConversationSidebar';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolsUsed?: string[];
}

export function ChatInterface() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;
    
    // Add user message immediately
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getToken()}`
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId
        })
      });
      
      const data = await response.json();
      
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }
      
      // Add AI response
      const aiMessage: Message = {
        id: data.message_id,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(data.timestamp),
        toolsUsed: data.tools_used?.map(t => t.name)
      };
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      // Add error message
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <ConversationSidebar
        onSelectConversation={loadConversation}
        onNewConversation={startNewConversation}
      />
      <div className="chat-main">
        <MessageList messages={messages} isLoading={isLoading} />
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
```

## Natural Language Intent Recognition

### Supported Intent Patterns

#### Task Creation
| Pattern | Example | Extracted Data |
|---------|---------|----------------|
| "Add [task]" | "Add buy groceries" | title: "buy groceries" |
| "Create [task]" | "Create a meeting reminder" | title: "a meeting reminder" |
| "New task [task]" | "New task call mom" | title: "call mom" |
| "Remember to [task]" | "Remember to submit report" | title: "submit report" |
| "[task] to my list" | "Buy milk to my list" | title: "Buy milk" |

#### Task Listing
| Pattern | Example | Extracted Data |
|---------|---------|----------------|
| "Show my tasks" | "Show my tasks" | status: "all" |
| "What are my pending tasks?" | - | status: "pending" |
| "List completed tasks" | - | status: "completed" |
| "What do I need to do?" | - | status: "pending" |

#### Task Completion
| Pattern | Example | Extracted Data |
|---------|---------|----------------|
| "Mark [task] as done" | "Mark buy groceries as done" | task identifier |
| "Complete [task]" | "Complete task 3" | task identifier |
| "I finished [task]" | "I finished the report" | task identifier |
| "Done with [task]" | "Done with grocery shopping" | task identifier |

#### Task Deletion
| Pattern | Example | Extracted Data |
|---------|---------|----------------|
| "Delete [task]" | "Delete buy groceries" | task identifier |
| "Remove [task]" | "Remove task 5" | task identifier |
| "Cancel [task]" | "Cancel my meeting reminder" | task identifier |

#### Task Update
| Pattern | Example | Extracted Data |
|---------|---------|----------------|
| "Change [old] to [new]" | "Change buy groceries to buy organic groceries" | old, new |
| "Update [task] to [new]" | "Update task 3 to urgent meeting" | task, new value |
| "Rename [task]" | "Rename groceries to shopping" | task, new name |

## Confirmation Responses

The AI always confirms actions with friendly responses:

### Add Task
```
"I've added '[task title]' to your task list! 📝 Anything else you'd like to add?"
```

### List Tasks
```
"Here are your [status] tasks:

1. 📌 Buy groceries
2. 📌 Call mom
3. ✅ Submit report (completed)

You have 2 pending and 1 completed task. What would you like to do next?"
```

### Complete Task
```
"Great job! ✅ I've marked '[task title]' as complete. Keep up the good work!"
```

### Delete Task
```
"Done! 🗑️ I've removed '[task title]' from your list."
```

### Update Task
```
"Got it! ✏️ I've updated the task. It's now called '[new title]'."
```

## Error Handling

### User-Friendly Error Messages

| Error Type | Message |
|------------|---------|
| Task Not Found | "I couldn't find that task. Could you try describing it differently or say 'show my tasks' to see your list?" |
| Authentication | "It looks like your session has expired. Please log in again to continue." |
| Network Error | "I'm having trouble connecting. Please check your internet and try again." |
| Rate Limit | "You're sending messages too quickly! Please wait a moment and try again." |
| Unknown Intent | "I'm not sure what you'd like to do. Try saying something like 'add buy groceries' or 'show my tasks'." |

## Accessibility

- [ ] Keyboard navigation support (Tab, Enter, Escape)
- [ ] Screen reader compatible with ARIA labels
- [ ] High contrast mode support
- [ ] Reduced motion option for animations
- [ ] Focus indicators for all interactive elements
