import re
from typing import Tuple


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validates password strength based on security requirements.
    
    Args:
        password: The password to validate
        
    Returns:
        Tuple of (is_valid, message) indicating if password is strong enough
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:  # Reasonable upper limit
        return False, "Password must be no more than 128 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password meets strength requirements"


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validates username based on requirements.
    
    Args:
        username: The username to validate
        
    Returns:
        Tuple of (is_valid, message) indicating if username is valid
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be no more than 50 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, hyphens, and underscores"
    
    return True, "Username is valid"