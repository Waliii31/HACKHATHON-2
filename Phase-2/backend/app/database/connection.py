from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# Use the DATABASE_URL from environment or default to a local test database
DATABASE_URL = settings.DATABASE_URL or os.getenv("DATABASE_URL", "")

# Handle SSL query params for asyncpg: remove sslmode from URL and pass connect_args
connect_args = {}
if DATABASE_URL and ("sslmode=" in DATABASE_URL or "ssl=" in DATABASE_URL):
    parts = urlsplit(DATABASE_URL)
    qsl = [(k, v) for k, v in parse_qsl(parts.query) if k.lower() not in ("sslmode", "channel_binding", "ssl")]
    new_query = urlencode(qsl)
    cleaned = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    # For simple cases where ssl is required, pass True to asyncpg via connect_args
    connect_args = {"ssl": True}
    engine = create_async_engine(
        cleaned,
        pool_size=settings.DATABASE_POOL_SIZE,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        echo=False,
        connect_args=connect_args,
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        echo=False,
    )

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()