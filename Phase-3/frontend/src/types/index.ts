// @/types/index.ts

export interface ToolUsage {
    name: string;
    success: boolean;
    result?: any;
    error?: string;
}

export interface ChatResponse {
    conversation_id: string; // UUID
    message_id: string; // UUID
    response: string;
    tools_used: ToolUsage[];
    timestamp: string;
}

export interface Conversation {
    id: string;
    title: string | null;
    last_message?: string;
    message_count: number;
    created_at: string;
    updated_at: string;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    tools_used?: ToolUsage[];
    timestamp: string;
    isOptimistic?: boolean; // For UI logic
}

export interface Task {
    id: string;
    title: string;
    description?: string;
    status: 'active' | 'completed';
    priority: 'low' | 'medium' | 'high';
    created_at: string;
    updated_at: string;
}
