from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.user_service import UserService
from ..services.vault_service import VaultService
from ..models.user import User
from ..models.encrypted_file import EncryptedFile
import os


router = APIRouter()
security = HTTPBearer()


class EncryptRequest(BaseModel):
    password: str


class FileMetadataResponse(BaseModel):
    file_id: str
    original_name: str
    size: int
    encrypted_at: str


@router.post("/encrypt")
async def encrypt_file(
    file: UploadFile = File(...),
    password: str = Form(...),
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

    # Create a temporary directory for uploads using the vault path
    temp_dir = os.path.join(settings.vaults_path, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Save uploaded file temporarily
    temp_file_path = os.path.join(temp_dir, f"temp_{user.id}_{file.filename}")
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        encrypted_file = vault_service.encrypt_and_store_file(
            user.id, temp_file_path, password
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


class DecryptRequest(BaseModel):
    password: str


@router.post("/decrypt/{file_id}")
def decrypt_file(
    file_id: str,
    request: DecryptRequest,
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

    result = vault_service.decrypt_file(file_id, user.id, request.password)

    if not result:
        raise HTTPException(status_code=404, detail="File not found, access denied, or decryption failed")

    decrypted_data, original_filename = result

    # Determine the media type based on file extension
    file_extension = original_filename.lower().split('.')[-1]
    media_types = {
        'txt': 'text/plain',
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'zip': 'application/zip'
    }

    media_type = media_types.get(file_extension, 'application/octet-stream')

    # Create a generator to stream the file content
    def iterfile():
        yield decrypted_data

    # Return the file as a streaming response with the original filename
    return StreamingResponse(
        iterfile(),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{original_filename}",
        }
    )


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


@router.post("/decrypt-local")
async def decrypt_local_file(
    file: UploadFile = File(...),
    password: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)

    user = user_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a temporary directory for uploads using the vault path
    temp_dir = os.path.join(settings.vaults_path, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Save uploaded encrypted file temporarily
    temp_file_path = os.path.join(temp_dir, f"temp_decrypt_{user.id}_{file.filename}")
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Attempt to decrypt the file using the provided password
        from ..utils.encryption_utils import decrypt_file_to_bytes

        # Decrypt the file and get the data
        decrypted_data = decrypt_file_to_bytes(temp_file_path, password)

        if decrypted_data is None:
            raise HTTPException(status_code=400, detail="Failed to decrypt file. Incorrect password or corrupted file.")

        # Extract original filename from the temp file name (remove user ID and "temp_decrypt_" prefix)
        original_filename = file.filename.replace('.enc', '') if file.filename.endswith('.enc') else file.filename

        # Determine the media type based on file extension
        file_extension = original_filename.lower().split('.')[-1]
        media_types = {
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'zip': 'application/zip'
        }

        media_type = media_types.get(file_extension, 'application/octet-stream')

        # Create a generator to stream the decrypted content
        def iterfile():
            yield decrypted_data

        # Clean up temporary file
        os.remove(temp_file_path)

        # Return the decrypted file as a streaming response with the original filename
        return StreamingResponse(
            iterfile(),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{original_filename}",
            }
        )
    except Exception as e:
        # Clean up temporary file in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/download-encrypted/{file_id}")
def download_encrypted_file(
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

    # Verify the file belongs to the user
    encrypted_file = (
        db.query(EncryptedFile)
        .filter(EncryptedFile.id == file_id, EncryptedFile.user_id == user.id)
        .first()
    )

    if not encrypted_file:
        raise HTTPException(status_code=404, detail="File not found or access denied")

    # Check if the encrypted file exists on disk
    if not os.path.exists(encrypted_file.encrypted_path):
        raise HTTPException(status_code=404, detail="Encrypted file does not exist on disk")

    # Create a generator to stream the encrypted file content
    def iterfile():
        with open(encrypted_file.encrypted_path, 'rb') as file:
            yield from file

    # Return the encrypted file as a streaming response with a .enc extension
    encrypted_filename = f"{encrypted_file.original_filename}.enc"

    return StreamingResponse(
        iterfile(),
        media_type='application/octet-stream',
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encrypted_filename}",
        }
    )


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