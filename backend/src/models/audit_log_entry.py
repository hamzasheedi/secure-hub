from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid


class AuditLogEntry(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Nullable for system events
    action_type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    result = Column(String, nullable=False)  # 'success' or 'failure'
    details = Column(JSON, nullable=True)
    previous_hash = Column(String, nullable=True)  # For chain integrity

    # Relationship
    user = relationship("User", back_populates="audit_logs")