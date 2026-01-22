import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.audit_log_entry import AuditLogEntry
from ..models.user import User


class AuditLogService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def log_action(
        self,
        user_id: Optional[str],
        action_type: str,
        result: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLogEntry:
        """
        Log an action with chain-hashed integrity.
        
        Args:
            user_id: ID of the user performing the action (None for system events)
            action_type: Type of action being performed
            result: Result of the action ('success' or 'failure')
            details: Additional details about the action
            
        Returns:
            The created AuditLogEntry
        """
        # Get the previous hash for chaining
        previous_hash = self._get_latest_hash()
        
        # Create the log entry
        log_entry = AuditLogEntry(
            user_id=user_id,
            action_type=action_type,
            result=result,
            details=details,
            previous_hash=previous_hash
        )
        
        # Add to session and commit
        self.db_session.add(log_entry)
        self.db_session.commit()
        self.db_session.refresh(log_entry)
        
        return log_entry
    
    def _get_latest_hash(self) -> Optional[str]:
        """
        Get the hash of the most recent audit log entry.
        
        Returns:
            The hash of the latest entry, or None if no entries exist
        """
        latest_entry = (
            self.db_session.query(AuditLogEntry)
            .order_by(AuditLogEntry.timestamp.desc())
            .first()
        )
        
        if latest_entry:
            return self._calculate_hash(latest_entry)
        
        return None
    
    def _calculate_hash(self, log_entry: AuditLogEntry) -> str:
        """
        Calculate the hash for an audit log entry.
        
        Args:
            log_entry: The audit log entry to hash
            
        Returns:
            The calculated hash
        """
        # Create a string representation of the log entry
        entry_str = (
            f"{log_entry.id}|"
            f"{log_entry.user_id}|"
            f"{log_entry.action_type}|"
            f"{log_entry.result}|"
            f"{log_entry.timestamp}|"
            f"{json.dumps(log_entry.details, sort_keys=True) if log_entry.details else ''}|"
            f"{log_entry.previous_hash or ''}"
        )
        
        # Calculate SHA-256 hash
        return hashlib.sha256(entry_str.encode('utf-8')).hexdigest()
    
    def verify_integrity(self) -> bool:
        """
        Verify the integrity of the audit log chain.
        
        Returns:
            True if the chain is intact, False otherwise
        """
        # Get all entries ordered by timestamp
        entries = (
            self.db_session.query(AuditLogEntry)
            .order_by(AuditLogEntry.timestamp.asc())
            .all()
        )
        
        # Verify each entry's previous_hash matches the calculated hash of the previous entry
        for i, entry in enumerate(entries):
            if i == 0:
                # First entry should have no previous hash or have a valid initial state
                if entry.previous_hash is not None:
                    # If there's a previous hash for the first entry, it should be empty or a known initial value
                    if entry.previous_hash != "":
                        return False
            else:
                # Calculate the hash of the previous entry
                expected_previous_hash = self._calculate_hash(entries[i-1])
                
                # Compare with the stored previous_hash
                if entry.previous_hash != expected_previous_hash:
                    return False
        
        return True