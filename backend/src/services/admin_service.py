from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.user import User, UserRole, UserStatus
from ..services.user_service import UserService


class AdminService:
    def __init__(self, db_session: Session, user_service: UserService):
        self.db_session = db_session
        self.user_service = user_service

    def get_all_users(self) -> List[User]:
        """
        Get all users in the system.
        
        Returns:
            A list of all User objects
        """
        users = self.db_session.query(User).all()
        return users

    def deactivate_user(self, user_id: str, admin_user_id: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: The ID of the user to deactivate
            admin_user_id: The ID of the admin performing the action
            
        Returns:
            True if the user was deactivated, False otherwise
        """
        # Verify admin privileges
        admin_user = self.db_session.query(User).filter(User.id == admin_user_id).first()
        if not admin_user or admin_user.role != UserRole.ADMIN:
            return False
        
        # Prevent deactivation of other admins
        target_user = self.db_session.query(User).filter(User.id == user_id).first()
        if target_user and target_user.role == UserRole.ADMIN:
            return False  # Admins cannot deactivate other admins
        
        return self.user_service.deactivate_user(user_id)

    def activate_user(self, user_id: str, admin_user_id: str) -> bool:
        """
        Activate a user account.
        
        Args:
            user_id: The ID of the user to activate
            admin_user_id: The ID of the admin performing the action
            
        Returns:
            True if the user was activated, False otherwise
        """
        # Verify admin privileges
        admin_user = self.db_session.query(User).filter(User.id == admin_user_id).first()
        if not admin_user or admin_user.role != UserRole.ADMIN:
            return False
        
        return self.user_service.activate_user(user_id)

    def promote_to_admin(self, user_id: str, admin_user_id: str) -> bool:
        """
        Promote a user to admin role.
        
        Args:
            user_id: The ID of the user to promote
            admin_user_id: The ID of the admin performing the action
            
        Returns:
            True if the user was promoted, False otherwise
        """
        # Verify admin privileges
        admin_user = self.db_session.query(User).filter(User.id == admin_user_id).first()
        if not admin_user or admin_user.role != UserRole.ADMIN:
            return False
        
        # Find the user to promote
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Promote the user
        user.role = UserRole.ADMIN
        self.db_session.commit()
        
        return True

    def demote_from_admin(self, user_id: str, admin_user_id: str) -> bool:
        """
        Demote an admin user to regular user.
        
        Args:
            user_id: The ID of the admin user to demote
            admin_user_id: The ID of the admin performing the action
            
        Returns:
            True if the admin was demoted, False otherwise
        """
        # Verify admin privileges
        admin_user = self.db_session.query(User).filter(User.id == admin_user_id).first()
        if not admin_user or admin_user.role != UserRole.ADMIN:
            return False
        
        # Prevent demotion of oneself
        if admin_user_id == user_id:
            return False  # Admins cannot demote themselves
        
        # Find the admin to demote
        admin_to_demote = self.db_session.query(User).filter(User.id == user_id).first()
        if not admin_to_demote or admin_to_demote.role != UserRole.ADMIN:
            return False
        
        # Demote the admin
        admin_to_demote.role = UserRole.USER
        self.db_session.commit()
        
        return True