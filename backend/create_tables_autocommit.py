from src.config.settings import settings
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Create engine with null pool to avoid connection issues
engine = create_engine(settings.database_url, poolclass=NullPool)

print(f"Connecting to database: {settings.database_url}")

try:
    # Connect and drop tables with autocommit
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        # Drop the alembic_version table if it exists
        print("Dropping alembic_version table...")
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        
        # Drop any existing model tables to start fresh
        tables_to_drop = [
            'audit_log_entries',
            'encrypted_files', 
            'file_metadata',
            'vaults',
            'users'
        ]
        
        for table in tables_to_drop:
            print(f"Dropping table {table} if it exists...")
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            
        print("Tables dropped successfully.")

    # Now recreate all tables using the models
    from src.models.user import User
    from src.models.encrypted_file import EncryptedFile
    from src.models.file_metadata import FileMetadata
    from src.models.vault import Vault
    from src.models.audit_log_entry import AuditLogEntry
    from src.database import Base
    
    print("Creating all tables from models...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Verify tables were created with autocommit
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables after creation: {tables}")
        
        # Check specifically for our expected tables
        expected_tables = ['users', 'encrypted_files', 'file_metadata', 'vaults', 'audit_log_entries']
        for table in expected_tables:
            exists = table in tables
            print(f"Table '{table}' exists: {exists}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()