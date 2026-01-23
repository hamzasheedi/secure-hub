from src.config.settings import settings
from src.database import engine

print(f"Database URL from settings: {settings.database_url}")
print(f"Engine URL: {engine.url}")

# Also test the actual connection
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print(f"Connected to PostgreSQL: {result.fetchone()[0]}")
        
        # Check if users table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """))
        table_exists = result.fetchone()[0]
        print(f"Users table exists: {table_exists}")
        
except Exception as e:
    print(f"Connection error: {e}")