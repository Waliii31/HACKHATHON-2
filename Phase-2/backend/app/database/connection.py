from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Use the DATABASE_URL from environment or default to a local test database
DATABASE_URL = settings.DATABASE_URL or os.getenv("DATABASE_URL", "")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    echo=False  # Set to True for debugging SQL queries
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()