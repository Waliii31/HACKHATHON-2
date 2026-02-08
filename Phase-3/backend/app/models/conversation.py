"""
Conversation Model for Phase III AI Chatbot.

Stores chat conversation sessions for each user.
Part of the stateless architecture - all conversation history
is persisted to the database, never stored in memory.
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.message import Message


class ConversationBase(SQLModel):
    """Base schema for Conversation (shared fields)."""
    title: Optional[str] = Field(default=None, max_length=200)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)


class Conversation(ConversationBase, table=True):
    """
    Conversation table - stores chat sessions.
    
    Each conversation belongs to a user and contains multiple messages.
    The stateless API reads/writes to this table for every request.
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to messages (one-to-many)
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        arbitrary_types_allowed = True
