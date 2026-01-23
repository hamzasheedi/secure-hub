from src.config.settings import settings
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Create engine with null pool to avoid connection issues
engine = create_engine(settings.database_url, poolclass=NullPool)

print(f"Connecting to database: {settings.database_url}")

try:
    with engine.connect() as conn:
        # Try to create a simple test table
        print("Creating test_table...")
        conn.execute(text("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR(50));"))
        conn.commit()  # Explicitly commit
        
        # Check if the table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'test_table'
            );
        """))
        table_exists = result.fetchone()[0]
        print(f"Test table exists: {table_exists}")
        
        # Insert a test record
        if table_exists:
            conn.execute(text("INSERT INTO test_table (name) VALUES ('test_record');"))
            conn.commit()
            
            # Query the record back
            result = conn.execute(text("SELECT * FROM test_table;"))
            rows = result.fetchall()
            print(f"Records in test_table: {rows}")
        
        # Clean up - drop the test table
        conn.execute(text("DROP TABLE IF EXISTS test_table;"))
        conn.commit()
        
        print("Direct SQL operations completed successfully.")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()