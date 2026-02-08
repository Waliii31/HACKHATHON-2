"""
Script to initialize better-auth database tables in Neon PostgreSQL
This creates the necessary tables for better-auth authentication
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_Wok19JETtAhe@ep-jolly-fog-aiblc4as-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Better-auth database schema
BETTER_AUTH_SCHEMA = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    "emailVerified" BOOLEAN DEFAULT FALSE,
    name TEXT,
    image TEXT,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    "expiresAt" TIMESTAMP NOT NULL,
    token TEXT NOT NULL UNIQUE,
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "userId" TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table (for password authentication)
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    "userId" TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    "accountId" TEXT NOT NULL,
    "providerId" TEXT NOT NULL,
    "accessToken" TEXT,
    "refreshToken" TEXT,
    "idToken" TEXT,
    "expiresAt" TIMESTAMP,
    password TEXT,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE ("userId", "providerId")
);

-- Verification tokens table
CREATE TABLE IF NOT EXISTS "verificationTokens" (
    id TEXT PRIMARY KEY,
    identifier TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (identifier, token)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS "idx_sessions_userId" ON sessions("userId");
CREATE INDEX IF NOT EXISTS "idx_sessions_token" ON sessions(token);
CREATE INDEX IF NOT EXISTS "idx_accounts_userId" ON accounts("userId");
CREATE INDEX IF NOT EXISTS "idx_verificationTokens_token" ON "verificationTokens"(token);
"""

async def init_better_auth_tables():
    """Initialize better-auth database tables"""
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
        
        print("🔄 Initializing better-auth tables in Neon PostgreSQL...")
        
        # Execute schema creation
        async with engine.begin() as conn:
            # Split and execute each statement
            statements = [s.strip() for s in BETTER_AUTH_SCHEMA.split(';') if s.strip()]
            for statement in statements:
                await conn.execute(text(statement))
            
        print("✓ Successfully created better-auth tables!")
        print("✓ Tables created:")
        print("  - users")
        print("  - sessions")
        print("  - accounts")
        print("  - verificationTokens")
        print("✓ Indexes created for optimal performance")
        return True
            
    except Exception as e:
        print(f"✗ Failed to initialize tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if engine:
            await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(init_better_auth_tables())
    sys.exit(0 if success else 1)
