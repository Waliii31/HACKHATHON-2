"""
Chat API Schemas for Phase III.

Defines Pydantic models for request/response validation.
These schemas enforce the stateless API contract.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Request body for POST /api/chat
    
    The stateless chat endpoint receives a message and optional conversation_id.
    If conversation_id is not provided, a new conversation is created.
    """
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="The user's message (1-2000 characters)"
    )
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID. If not provided, creates new conversation"
    )
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ToolUsage(BaseModel):
    """Details of a tool that was executed."""
    name: str = Field(..., description="Name of the MCP tool")
    success: bool = Field(..., description="Whether the tool execution succeeded")
    result: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Tool result data (if successful)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message (if failed)"
    )


class ChatResponse(BaseModel):
    """
    Response body for POST /api/chat
    
    Contains the AI's response along with metadata about the conversation
    and any tools that were executed.
    """
    conversation_id: UUID = Field(
        ..., 
        description="ID of the conversation (new or existing)"
    )
    message_id: UUID = Field(
        ..., 
        description="ID of the AI response message"
    )
    response: str = Field(
        ..., 
        description="AI-generated response text"
    )
    tools_used: List[ToolUsage] = Field(
        default=[],
        description="List of MCP tools executed during processing"
    )
    timestamp: datetime = Field(
        ..., 
        description="Response timestamp"
    )


# ============================================================================
# Conversation List Schemas
# ============================================================================

class ConversationSummary(BaseModel):
    """Summary of a conversation for listing."""
    id: UUID
    title: Optional[str] = None
    last_message: Optional[str] = None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    """Response for GET /api/chat/conversations"""
    conversations: List[ConversationSummary]
    total: int
    limit: int
    offset: int


# ============================================================================
# Conversation Detail Schemas
# ============================================================================

class MessageSchema(BaseModel):
    """Single message in a conversation."""
    id: UUID
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str
    tools_used: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    """Response for GET /api/chat/conversations/{id}"""
    id: UUID
    title: Optional[str] = None
    created_at: datetime
    messages: List[MessageSchema]
    has_more: bool = False


# ============================================================================
# Error Response Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Human-readable error message")
    error_code: str = Field(..., description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = None


class RateLimitErrorResponse(ErrorResponse):
    """Rate limit exceeded error."""
    retry_after: int = Field(
        ..., 
        description="Seconds to wait before retrying"
    )
