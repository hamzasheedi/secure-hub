from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.user_service import UserService
from ..services.vault_service import VaultService
from ..models.user import User
import os


router = APIRouter()
security = HTTPBearer()


class FileMetadataResponse(BaseModel):
    file_id: str
    original_name: str
    size: int
    encrypted_at: str


@router.post("/encrypt")
def encrypt_file(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    vault_service = VaultService(db)
    
    user = user_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Save uploaded file temporarily
    temp_file_path = f"temp_{user.id}_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    try:
        # For demonstration, we'll use a dummy password
        # In a real implementation, this would come from the user securely
        dummy_password = "TempPassword123!"
        
        encrypted_file = vault_service.encrypt_and_store_file(
            user.id, temp_file_path, dummy_password
        )
        
        if not encrypted_file:
            raise HTTPException(status_code=400, detail="File encryption failed")
        
        # Clean up temporary file
        os.remove(temp_file_path)
        
        return {
            "file_id": encrypted_file.id,
            "original_name": encrypted_file.original_filename,
            "size": encrypted_file.file_size,
            "encrypted_at": encrypted_file.created_at.isoformat()
        }
    except ValueError as e:
        # Clean up temporary file in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Clean up temporary file in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/decrypt/{file_id}")
def decrypt_file(
    file_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    vault_service = VaultService(db)
    
    user = user_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For demonstration, we'll use a dummy password
    # In a real implementation, this would come from the user securely
    dummy_password = "TempPassword123!"
    
    decrypted_file_path = vault_service.decrypt_file(file_id, user.id, dummy_password)
    
    if not decrypted_file_path:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    
    # In a real implementation, we would return the file for download
    # For now, we'll just return a success message
    return {"message": "File decrypted successfully", "file_path": decrypted_file_path}


@router.get("/files", response_model=List[FileMetadataResponse])
def list_files(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    vault_service = VaultService(db)
    
    user = user_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    files = vault_service.list_user_files(user.id)
    
    response = []
    for file in files:
        response.append({
            "file_id": file.id,
            "original_name": file.original_filename,
            "size": file.file_size,
            "encrypted_at": file.created_at.isoformat()
        })
    
    return response


@router.delete("/file/{file_id}")
def delete_file(
    file_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    vault_service = VaultService(db)
    
    user = user_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    success = vault_service.delete_file(file_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    
    return {"message": "File deleted successfully"}