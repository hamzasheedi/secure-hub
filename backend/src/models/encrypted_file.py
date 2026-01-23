from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid


class EncryptedFile(Base):
    __tablename__ = "encrypted_files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    encrypted_path = Column(String, nullable=False)
    encryption_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    algorithm_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="encrypted_files", lazy="select")
    file_metadata = relationship("FileMetadata", uselist=False, back_populates="encrypted_file", lazy="select")