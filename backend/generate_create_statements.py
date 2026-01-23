from src.models.user import User
from src.models.encrypted_file import EncryptedFile
from src.models.file_metadata import FileMetadata
from src.models.vault import Vault
from src.models.audit_log_entry import AuditLogEntry
from src.database import Base
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable

# Create a temporary engine to generate SQL
engine = create_engine("sqlite:///:memory:")

# Print the CREATE statements for each table
for table in Base.metadata.sorted_tables:
    print(f"CREATE statement for {table.name}:")
    print(CreateTable(table).compile(engine))
    print("-" * 50)

# Also print the total number of tables
print(f"\nTotal number of tables in metadata: {len(Base.metadata.sorted_tables)}")