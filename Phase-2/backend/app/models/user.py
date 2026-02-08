from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
import enum
from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.task import Task


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)
    name: str = Field(nullable=False, max_length=255)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    # Relationship to tasks (string forward ref to avoid circular import)
    tasks: List["Task"] = Relationship(back_populates="user")

    class Config:
        arbitrary_types_allowed = True