from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.user_service import UserService
from ..services.admin_service import AdminService
from ..models.user import User, UserRole
import jwt


router = APIRouter()
security = HTTPBearer()


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    status: str
    created_at: str


def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user_service = UserService(db)
    
    user = user_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges required"
        )
    
    return user


@router.get("/users", response_model=List[UserResponse])
def get_all_users(current_user: User = Depends(verify_admin), db: Session = Depends(get_db)):
    from ..services.audit_log_service import AuditLogService
    audit_service = AuditLogService(db)
    admin_service = AdminService(db, UserService(db), audit_service)

    users = admin_service.get_all_users()

    response = []
    for user in users:
        response.append({
            "id": user.id,
            "username": user.username,
            "role": user.role.value,
            "status": user.status.value,
            "created_at": user.created_at.isoformat() if user.created_at else ""
        })

    return response


@router.post("/user/{user_id}/deactivate")
def deactivate_user(
    user_id: str,
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    from ..services.audit_log_service import AuditLogService
    audit_service = AuditLogService(db)
    admin_service = AdminService(db, UserService(db), audit_service)

    success = admin_service.deactivate_user(user_id, current_user.id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to deactivate user")

    return {"message": "User deactivated successfully"}


@router.post("/user/{user_id}/activate")
def activate_user(
    user_id: str,
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    from ..services.audit_log_service import AuditLogService
    audit_service = AuditLogService(db)
    admin_service = AdminService(db, UserService(db), audit_service)

    success = admin_service.activate_user(user_id, current_user.id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to activate user")

    return {"message": "User activated successfully"}


@router.post("/user/{user_id}/promote")
def promote_user(
    user_id: str,
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    from ..services.audit_log_service import AuditLogService
    audit_service = AuditLogService(db)
    admin_service = AdminService(db, UserService(db), audit_service)

    # Prevent self-promotion
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot promote yourself")

    success = admin_service.promote_to_admin(user_id, current_user.id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to promote user - user may not exist or already be an admin")

    return {"message": "User promoted to admin successfully"}


@router.post("/user/{user_id}/demote")
def demote_user(
    user_id: str,
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    from ..services.audit_log_service import AuditLogService
    audit_service = AuditLogService(db)
    admin_service = AdminService(db, UserService(db), audit_service)

    success = admin_service.demote_from_admin(user_id, current_user.id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to demote admin - may be trying to demote yourself or user is not an admin")

    return {"message": "Admin demoted to user successfully"}