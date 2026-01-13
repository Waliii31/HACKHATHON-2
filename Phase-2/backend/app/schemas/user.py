from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    email: str
    name: str


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool