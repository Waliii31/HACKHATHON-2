from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import AsyncSessionLocal


async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()