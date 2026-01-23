from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, ForeignKey("encrypted_files.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    encryption_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    algorithm_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    encrypted_file = relationship("EncryptedFile", back_populates="file_metadata", lazy="select")