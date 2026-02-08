"""
Message Model for Phase III AI Chatbot.

Stores individual messages within conversations.
Supports user, assistant, and system roles.
Tracks tools used by the AI for each response.
"""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, TYPE_CHECKING
import json

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class MessageRole:
    """Allowed message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    
    @classmethod
    def all_roles(cls) -> List[str]:
        return [cls.USER, cls.ASSISTANT, cls.SYSTEM]


class MessageBase(SQLModel):
    """Base schema for Message (shared fields)."""
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: str = Field(nullable=False, max_length=20)  # user, assistant, system
    content: str = Field(sa_column=Column(Text, nullable=False))


class Message(MessageBase, table=True):
    """
    Message table - stores individual chat messages.
    
    Each message belongs to a conversation.
    Assistant messages track which MCP tools were executed.
    The stateless API creates new records for every interaction.
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tools_used: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to conversation (many-to-one)
    conversation: "Conversation" = Relationship(back_populates="messages")

    class Config:
        arbitrary_types_allowed = True

    def get_tools_list(self) -> List[dict]:
        """Parse tools_used JSON string to list of dicts."""
        if self.tools_used:
            try:
                return json.loads(self.tools_used)
            except json.JSONDecodeError:
                return []
        return []

    def set_tools_list(self, tools: List[dict]) -> None:
        """Serialize list of tool usage dicts to JSON string."""
        if tools:
            self.tools_used = json.dumps(tools)
        else:
            self.tools_used = None

    @property
    def is_user_message(self) -> bool:
        return self.role == MessageRole.USER

    @property
    def is_assistant_message(self) -> bool:
        return self.role == MessageRole.ASSISTANT
