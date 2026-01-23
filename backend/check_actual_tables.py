from src.config.settings import settings
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Create engine with null pool to avoid connection issues
engine = create_engine(settings.database_url, poolclass=NullPool)

print(f"Connecting to database: {settings.database_url}")

# Verify tables were created with autocommit
try:
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"All tables in public schema: {tables}")
        
        # Check specifically for our expected tables
        expected_tables = ['users', 'encrypted_files', 'file_metadata', 'vaults', 'audit_logs']
        for table in expected_tables:
            exists = table in tables
            print(f"Table '{table}' exists: {exists}")
            
        # Check if any tables were created at all
        if not tables:
            print("No tables found in the database!")
        else:
            print(f"Found {len(tables)} tables in total.")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()