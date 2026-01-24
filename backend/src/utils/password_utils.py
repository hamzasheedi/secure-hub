"""
Password utilities for SecureVault backend
Handles password normalization to comply with bcrypt 72-byte limit
"""

def normalize_password(password: str) -> str:
    """
    Normalize a password to comply with bcrypt's 72-byte limit.
    
    Args:
        password: The password string to normalize
        
    Returns:
        A normalized password string that is at most 72 bytes when encoded as UTF-8
    """
    return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")