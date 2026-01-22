import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from ..models.user import User, UserRole, UserStatus
from ..utils.password_validator import validate_password_strength, validate_username
from ..config.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_user(self, username: str, password: str) -> Optional[User]:
        """
        Create a new user with the given username and password.
        
        Args:
            username: The username for the new user
            password: The password for the new user
            
        Returns:
            The created User object, or None if creation failed
        """
        # Validate username
        is_valid_username, username_msg = validate_username(username)
        if not is_valid_username:
            raise ValueError(f"Invalid username: {username_msg}")
        
        # Validate password strength
        is_valid_password, password_msg = validate_password_strength(password)
        if not is_valid_password:
            raise ValueError(f"Invalid password: {password_msg}")
        
        # Check if user already exists
        existing_user = self.db_session.query(User).filter(User.username == username).first()
        if existing_user:
            raise ValueError("Username already exists")
        
        # Hash the password
        hashed_password = pwd_context.hash(password)
        
        # Create the user
        user = User(
            username=username,
            password_hash=hashed_password,
            salt="",  # We're using bcrypt which handles salting internally
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        # Add to session and commit
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with the given username and password.
        
        Args:
            username: The username to authenticate
            password: The password to authenticate
            
        Returns:
            The authenticated User object, or None if authentication failed
        """
        user = self.db_session.query(User).filter(User.username == username).first()
        
        if not user or not pwd_context.verify(password, user.password_hash):
            return None
        
        if user.status != UserStatus.ACTIVE:
            return None
        
        return user

    def generate_access_token(self, user_id: str) -> str:
        """
        Generate an access token for the given user.
        
        Args:
            user_id: The ID of the user to generate a token for
            
        Returns:
            The generated access token
        """
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "role": self.get_user_role(user_id)
        }
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    def get_current_user(self, token: str) -> Optional[User]:
        """
        Get the current user from the given token.
        
        Args:
            token: The access token to decode
            
        Returns:
            The current User object, or None if token is invalid
        """
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                return None
                
            user = self.db_session.query(User).filter(User.id == user_id).first()
            
            if user is None or user.status != UserStatus.ACTIVE:
                return None
                
            return user
        except JWTError:
            return None

    def get_user_role(self, user_id: str) -> Optional[str]:
        """
        Get the role of the user with the given ID.
        
        Args:
            user_id: The ID of the user to get the role for
            
        Returns:
            The role of the user, or None if user doesn't exist
        """
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if user:
            return user.role.value
        return None

    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate the user with the given ID.
        
        Args:
            user_id: The ID of the user to deactivate
            
        Returns:
            True if the user was deactivated, False otherwise
        """
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if user:
            user.status = UserStatus.INACTIVE
            self.db_session.commit()
            return True
        return False

    def activate_user(self, user_id: str) -> bool:
        """
        Activate the user with the given ID.
        
        Args:
            user_id: The ID of the user to activate
            
        Returns:
            True if the user was activated, False otherwise
        """
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if user:
            user.status = UserStatus.ACTIVE
            self.db_session.commit()
            return True
        return False

    def delete_user(self, user_id: str) -> bool:
        """
        Delete the user with the given ID.
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            True if the user was deleted, False otherwise
        """
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if user:
            self.db_session.delete(user)
            self.db_session.commit()
            return True
        return False