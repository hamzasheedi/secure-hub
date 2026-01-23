"""
SecureVault Admin Password Fix Script

This script updates the existing admin user's password hash to use the correct bcrypt format.
"""

import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from src.models.user import User
from src.config.settings import settings


def fix_admin_password():
    """Fix the admin user's password hash to use the correct bcrypt format."""
    
    # Create database engine and session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find the admin user
        admin_user = db.query(User).filter(User.username == "admin123").first()
        
        if not admin_user:
            print("Admin user 'admin123' not found in the database.")
            return False
        
        # Use the same password hashing method as the rest of the application
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Hash the password using the same method as the application
        password = "admin123"  # The password we want to set
        new_password_hash = pwd_context.hash(password)
        
        # Update the admin user's password hash
        admin_user.password_hash = new_password_hash
        admin_user.salt = ""  # Bcrypt handles salting internally
        
        # Commit the changes
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user password updated successfully!")
        print(f"Username: {admin_user.username}")
        print(f"New password hash format: {new_password_hash[:20]}...")  # Show partial hash
        
        return True
        
    except Exception as e:
        print(f"Error updating admin password: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("SecureVault Admin Password Fix")
    print("=" * 40)
    
    success = fix_admin_password()
    
    if success:
        print("\nAdmin password fix completed successfully.")
        print("The admin user should now be able to log in with:")
        print("  Username: admin123")
        print("  Password: admin123")
    else:
        print("\nAdmin password fix failed.")
    
    print("=" * 40)