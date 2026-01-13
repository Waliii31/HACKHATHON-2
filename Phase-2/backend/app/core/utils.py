from datetime import datetime
from typing import Optional
from uuid import UUID


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.utcnow()


def validate_uuid(uuid_string: str) -> Optional[UUID]:
    """Validate and return UUID from string."""
    try:
        return UUID(uuid_string)
    except ValueError:
        return None