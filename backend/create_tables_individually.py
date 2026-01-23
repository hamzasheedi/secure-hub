from src.config.settings import settings
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Create engine with null pool to avoid connection issues
engine = create_engine(settings.database_url, poolclass=NullPool)

print(f"Connecting to database: {settings.database_url}")

# Import models to register them with Base
from src.models.user import User
from src.models.encrypted_file import EncryptedFile
from src.models.file_metadata import FileMetadata
from src.models.vault import Vault
from src.models.audit_log_entry import AuditLogEntry
from src.database import Base

try:
    with engine.connect() as conn:
        # Create all tables using metadata
        print("Creating all tables from Base.metadata...")
        Base.metadata.create_all(conn)
        conn.commit()  # Explicitly commit
        
        # Check what tables were created
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables after Base.metadata.create_all(): {tables}")
        
        # Check specifically for our expected tables
        expected_tables = ['users', 'encrypted_files', 'file_metadata', 'vaults', 'audit_logs']
        for table in expected_tables:
            exists = table in tables
            print(f"Table '{table}' exists: {exists}")
            
        if not any(table in tables for table in expected_tables):
            print("None of the expected tables were created!")
            print("Let's try creating them individually...")
            
            # Create each table individually
            for table_obj in Base.metadata.sorted_tables:
                print(f"Creating table: {table_obj.name}")
                table_obj.create(conn, checkfirst=True)
                
            # Check again
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"Tables after individual creation: {tables}")
            
        conn.commit()  # Commit any remaining changes
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()