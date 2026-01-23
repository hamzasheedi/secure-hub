from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config.settings import settings
from .models.base import Base

# Create the database engine
engine = create_engine(settings.database_url)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def register_models():
    """Function to register all models with SQLAlchemy"""
    # Import all models to register them with SQLAlchemy
    from .models.user import User
    from .models.encrypted_file import EncryptedFile
    from .models.file_metadata import FileMetadata
    from .models.vault import Vault
    from .models.audit_log_entry import AuditLogEntry


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()