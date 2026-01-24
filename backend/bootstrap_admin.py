"""
SecureVault Initial Admin Bootstrap Script

This script creates the first admin user if no admin exists in the database.
It should be run once during initial system setup.
"""

import sys
import os
import hashlib
import secrets
from datetime import datetime
import uuid

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user import User, UserRole
from src.config.settings import settings
from src.utils.password_utils import normalize_password


def create_initial_admin():
    """Create the initial admin user if no admin exists."""

    # Create database engine and session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if any admin user already exists
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if existing_admin:
            print("An admin user already exists. Skipping initial admin creation.")
            print(f"Existing admin: {existing_admin.username}")
            return False
        
        # Define the initial admin credentials
        username = "admin123"
        password = "admin123"
        
        # Use the same password hashing method as the rest of the application
        # Import the pwd_context from the user_service module
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Normalize password to comply with bcrypt 72-byte limit
        normalized_password = normalize_password(password)

        # Hash the password using the same method as the application
        password_hash = pwd_context.hash(normalized_password)

        # For bcrypt, we don't need a separate salt field as it's included in the hash
        salt = ""  # Empty since passlib handles salting internally
        
        # Create the new admin user
        admin_user = User(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=password_hash_hex,
            salt=salt,
            role=UserRole.ADMIN,
            status="active"
        )
        
        # Add to database
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Initial admin user created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password} (please change after first login)")
        print(f"User ID: {admin_user.id}")
        
        return True
        
    except Exception as e:
        print(f"Error creating initial admin: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("SecureVault Initial Admin Bootstrap")
    print("=" * 40)
    
    success = create_initial_admin()
    
    if success:
        print("\nBootstrap completed successfully.")
        print("You can now start the application and log in with:")
        print("  Username: admin123")
        print("  Password: admin123")
    else:
        print("\nBootstrap process completed (skipped or failed).")
        print("Check if an admin user already exists.")
    
    print("=" * 40)