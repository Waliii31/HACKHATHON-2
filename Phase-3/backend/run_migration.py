"""
Database Migration Runner for Phase III.

Runs SQL migration scripts against Neon PostgreSQL.
Handles statement-by-statement execution to avoid multi-statement issues.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_url() -> str:
    """Get DATABASE_URL from environment."""
    url = os.getenv("DATABASE_URL", "")
    if not url:
        print("❌ DATABASE_URL not set in environment")
        sys.exit(1)
    return url


def create_engine_with_ssl(database_url: str):
    """Create async engine with SSL handling for Neon."""
    connect_args = {}
    
    if "sslmode=" in database_url or "ssl=" in database_url:
        parts = urlsplit(database_url)
        qsl = [
            (k, v) for k, v in parse_qsl(parts.query)
            if k.lower() not in ("sslmode", "channel_binding", "ssl")
        ]
        new_query = urlencode(qsl)
        cleaned = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
        connect_args = {"ssl": True}
        return create_async_engine(cleaned, connect_args=connect_args)
    
    return create_async_engine(database_url)


def parse_sql_statements(sql_content: str) -> list:
    """
    Parse SQL content into individual statements.
    
    Handles:
    - Single-line comments (--)
    - Multi-statement blocks (BEGIN/COMMIT)
    - Functions with $$ delimiters
    """
    statements = []
    current_statement = []
    in_dollar_block = False
    
    for line in sql_content.split('\n'):
        stripped = line.strip()
        
        # Skip empty lines and comments outside of statements
        if not stripped or (stripped.startswith('--') and not current_statement):
            continue
        
        # Skip inline comments in the middle of parsing
        if stripped.startswith('--'):
            continue
        
        # Track $$ blocks (for functions)
        if '$$' in stripped:
            dollar_count = stripped.count('$$')
            if dollar_count % 2 == 1:
                in_dollar_block = not in_dollar_block
        
        current_statement.append(line)
        
        # Statement ends with ; and we're not in a $$ block
        if stripped.endswith(';') and not in_dollar_block:
            statement = '\n'.join(current_statement).strip()
            if statement:
                statements.append(statement)
            current_statement = []
    
    # Add any remaining statement
    if current_statement:
        statement = '\n'.join(current_statement).strip()
        if statement:
            statements.append(statement)
    
    return statements


async def run_migration(migration_file: str):
    """Run a single migration file."""
    print(f"\n📄 Running migration: {migration_file}")
    
    # Read migration SQL
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Parse into statements
    statements = parse_sql_statements(sql_content)
    print(f"   Found {len(statements)} SQL statements")
    
    # Create engine
    database_url = get_database_url()
    engine = create_engine_with_ssl(database_url)
    
    # Execute statements
    async with engine.begin() as conn:
        for i, statement in enumerate(statements, 1):
            # Skip BEGIN/COMMIT as we use engine.begin()
            if statement.strip().upper() in ('BEGIN', 'BEGIN;', 'COMMIT', 'COMMIT;'):
                continue
            
            try:
                # Show first 50 chars of statement
                preview = statement[:50].replace('\n', ' ')
                print(f"   [{i}/{len(statements)}] {preview}...")
                await conn.execute(text(statement))
            except Exception as e:
                error_msg = str(e)
                # Ignore "already exists" errors (idempotent migrations)
                if "already exists" in error_msg.lower():
                    print(f"   ⚠️  Already exists (skipping)")
                elif "does not exist" in error_msg.lower() and "DROP" in statement.upper():
                    print(f"   ⚠️  Does not exist (skipping)")
                else:
                    print(f"   ❌ Error: {error_msg[:100]}")
                    raise
    
    await engine.dispose()
    print(f"✅ Migration completed: {migration_file}")


async def run_all_migrations():
    """Run all migrations in order."""
    migrations_dir = Path(__file__).parent / "migrations"
    
    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        return
    
    # Get all SQL files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("ℹ️  No migration files found")
        return
    
    print(f"🔄 Found {len(migration_files)} migration file(s)")
    
    for migration_file in migration_files:
        await run_migration(str(migration_file))
    
    print("\n✅ All migrations completed successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase III Database Migration Runner")
    print("=" * 60)
    
    asyncio.run(run_all_migrations())
