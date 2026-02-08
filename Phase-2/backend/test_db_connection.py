"""
Script to test Neon database connection
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_Wok19JETtAhe@ep-jolly-fog-aiblc4as-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

async def test_connection():
    """Test database connection"""
    engine = None
    try:
        # Clean SSL parameters from URL
        parts = urlsplit(DATABASE_URL)
        qsl = [(k, v) for k, v in parse_qsl(parts.query) if k.lower() not in ("sslmode", "channel_binding", "ssl")]
        new_query = urlencode(qsl)
        cleaned_url = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
        
        # Create engine with SSL
        engine = create_async_engine(
            cleaned_url,
            pool_size=5,
            pool_timeout=30,
            echo=False,
            connect_args={"ssl": True},
        )
        
        # Test connection
        async with engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("SELECT 1"))
            print("✓ Successfully connected to Neon PostgreSQL database!")
            print(f"✓ Database: neondb")
            print(f"✓ Host: ep-jolly-fog-aiblc4as-pooler.c-4.us-east-1.aws.neon.tech")
            return True
            
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if engine:
            await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
