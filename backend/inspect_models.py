from src.models.user import User
from src.models.encrypted_file import EncryptedFile
from src.models.file_metadata import FileMetadata
from src.models.vault import Vault
from src.models.audit_log_entry import AuditLogEntry
from src.database import Base

print("Inspecting model table names:")
for table in Base.metadata.sorted_tables:
    print(f"Table: {table.name}, Full name: {table.fullname}")

# Also check the __tablename__ attribute of each model
print("\nModel __tablename__ attributes:")
print(f"User.__tablename__: {User.__tablename__}")
print(f"EncryptedFile.__tablename__: {EncryptedFile.__tablename__}")
print(f"FileMetadata.__tablename__: {FileMetadata.__tablename__}")
print(f"Vault.__tablename__: {Vault.__tablename__}")
print(f"AuditLogEntry.__tablename__: {AuditLogEntry.__tablename__}")