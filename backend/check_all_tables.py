from src.config.settings import settings
from src.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # Get all tables in the public schema
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"All tables in public schema: {tables}")
        
        # Check specifically for our expected tables
        expected_tables = ['users', 'encrypted_files', 'file_metadata', 'vaults', 'audit_log_entries']
        for table in expected_tables:
            exists = table in tables
            print(f"Table '{table}' exists: {exists}")
        
except Exception as e:
    print(f"Error checking tables: {e}")