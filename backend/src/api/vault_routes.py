import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
# Supabase client is imported dynamically when needed to avoid import-time errors
# from supabase import create_client, Client  # Commented out to avoid import issues
from dotenv import load_dotenv

from ..database import get_db
from ..services.user_service import UserService
from ..services.vault_service import VaultService
from ..models.user import User
from ..models.encrypted_file import EncryptedFile
from ..config.settings import settings

load_dotenv()


# --- Supabase Configuration ---
from ..config.settings import settings

SUPABASE_URL = settings.supabase_url if settings.supabase_url else os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = settings.supabase_key if settings.supabase_key else os.getenv("SUPABASE_KEY", "")
BUCKET_NAME = settings.bucket_name if settings.bucket_name else os.getenv("BUCKET_NAME", "vaults")
USE_SUPABASE = (settings.use_supabase if settings.use_supabase else os.getenv("USE_SUPABASE", "true")).lower() == "true"

# Initialize Supabase client lazily (only when needed)
from typing import Any
supabase: Optional[Any] = None  # Using Any to avoid import issues with Client type

# --- Temporary directory (always writable on Render Free tier) ---
TEMP_DIR = Path(tempfile.gettempdir())


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
    user = user_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate file size before processing (10MB limit)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

    # Seek to end to get file size, then reset to beginning
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()  # Get size
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Check available disk space before creating temporary files
    import shutil
    total, used, free = shutil.disk_usage(TEMP_DIR)
    # Estimate required space: original file + encrypted file + some buffer
    estimated_required_space = file_size * 3 + (10 * 1024 * 1024)  # 3x file size + 10MB buffer

    if free < estimated_required_space:
        raise HTTPException(
            status_code=507,
            detail="Insufficient disk space for file processing"
        )

    # Initialize file paths to None to ensure they exist in finally block
    local_temp_path = None
    encrypted_temp_path = None

    # Paths for temporary storage using Render-compatible /tmp directory
    local_temp_path = TEMP_DIR / f"raw_{user.id}_{file.filename}"
    encrypted_temp_path = TEMP_DIR / f"enc_{user.id}_{file.filename}"

    try:
        # 1. Save uploaded file temporarily in /tmp (Render free tier writable path)
        with local_temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Encryption Logic
        from ..utils.encryption_utils import generate_salt, derive_key_from_password
        salt = generate_salt()

        # Derive encryption key from password
        key = derive_key_from_password(password, salt)
        from cryptography.fernet import Fernet
        fernet = Fernet(key)

        # Read the original file
        with open(local_temp_path, 'rb') as file_reader:
            file_data = file_reader.read()

        # Encrypt the data
        encrypted_data = fernet.encrypt(file_data)

        # Write encrypted data with salt prepended to our temp location
        with open(encrypted_temp_path, 'wb') as file_writer:
            file_writer.write(salt + encrypted_data)

        # 3. Upload to Supabase (persistent storage) with error handling
        if USE_SUPABASE and SUPABASE_URL and SUPABASE_KEY:
            # Initialize Supabase client only when needed
            supabase = None
            try:
                # Dynamically import the client to avoid import-time errors
                from supabase import create_client
                # Create client with only the required parameters to avoid proxy issues
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            except Exception as init_error:
                # Handle any initialization errors including proxy argument issues
                error_msg = str(init_error)
                if "'proxy'" in error_msg or "unexpected keyword argument" in error_msg:
                    print(f"Supabase client initialization failed due to version incompatibility: {init_error}")
                    print("This is typically caused by httpx/supabase version conflicts.")
                    print("The system will use /tmp storage as fallback.")
                else:
                    print(f"Failed to initialize Supabase client: {init_error}")

                # Continue to fallback logic
                supabase = None

            if supabase:
                try:
                    with encrypted_temp_path.open("rb") as f_enc:
                        file_data = f_enc.read()
                        # Upload to Supabase with a path that includes user ID for organization
                        response = supabase.storage.from_(BUCKET_NAME).upload(
                            path=f"encrypted/{user.id}/{file.filename}",
                            file=file_data,
                            file_options={"content-type": "application/octet-stream"}
                        )

                    # Store metadata in our database
                    from ..models.encrypted_file import EncryptedFile

                    file_size = len(file_data)

                    # Store the path in a format that's easier to parse later
                    encrypted_file_record = EncryptedFile(
                        user_id=user.id,
                        original_filename=file.filename,
                        file_size=file_size,
                        encrypted_path=f"encrypted/{user.id}/{file.filename}",  # Just the path in Supabase bucket
                        storage_location="supabase",  # Indicate where the file is stored
                        algorithm_version="AES-128-Fernet-PBKDF2"
                    )

                    db.add(encrypted_file_record)
                    db.commit()
                    db.refresh(encrypted_file_record)

                    return {
                        "status": "success",
                        "storage": "supabase",
                        "file_id": encrypted_file_record.id,
                        "original_name": encrypted_file_record.original_filename,
                        "size": encrypted_file_record.file_size,
                        "encrypted_at": encrypted_file_record.created_at.isoformat()
                    }

                except Exception as supabase_error:
                    # Log the error and fall back to /tmp storage
                    print(f"Supabase upload failed: {str(supabase_error)}. Falling back to /tmp storage.")

                    # Continue to fallback logic below

        # 4. Fallback to /tmp (ephemeral storage)
        # Move the encrypted file to a final location in temp with user context
        final_path = TEMP_DIR / f"final_{user.id}_{file.filename}"
        shutil.move(str(encrypted_temp_path), str(final_path))

        # Store metadata in our database
        from ..models.encrypted_file import EncryptedFile
        import os

        file_size = os.path.getsize(final_path)

        encrypted_file_record = EncryptedFile(
            user_id=user.id,
            original_filename=file.filename,
            file_size=file_size,
            encrypted_path=str(final_path),  # Local temp path
            storage_location="local",  # Indicate where the file is stored
            algorithm_version="AES-128-Fernet-PBKDF2"
        )

        db.add(encrypted_file_record)
        db.commit()
        db.refresh(encrypted_file_record)

        return {
            "status": "warning",
            "storage": "ephemeral_tmp",
            "message": "File saved to /tmp but will be deleted on next deploy/restart. Supabase upload failed, using fallback storage.",
            "file_id": encrypted_file_record.id,
            "original_name": encrypted_file_record.original_filename,
            "size": encrypted_file_record.file_size,
            "encrypted_at": encrypted_file_record.created_at.isoformat()
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

    finally:
        # Import os module locally to ensure it's available
        import os
        # Cleanup raw file
        if local_temp_path and local_temp_path.exists():
            os.remove(local_temp_path)
        # Only remove encrypted file if it still exists (wasn't moved/uploaded)
        if encrypted_temp_path and encrypted_temp_path.exists():
            os.remove(encrypted_temp_path)


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

    # Check if the encrypted file is stored in Supabase
    if encrypted_file.storage_location == "supabase":
        # The encrypted_path is the path in the Supabase bucket
        actual_path = encrypted_file.encrypted_path

        # Download the file from Supabase
        try:
            from supabase import create_client
            from ..config.settings import settings
            import tempfile
            import os

            SUPABASE_URL = settings.supabase_url if settings.supabase_url else os.getenv("SUPABASE_URL", "")
            SUPABASE_KEY = settings.supabase_key if settings.supabase_key else os.getenv("SUPABASE_KEY", "")

            if not SUPABASE_URL or not SUPABASE_KEY:
                raise HTTPException(status_code=500, detail="Supabase configuration not found")

            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

            # Download the file from Supabase
            response = supabase.storage.from_(settings.bucket_name).download(actual_path)

            # Create a generator to stream the downloaded content
            def iterfile():
                yield response

            # Return the encrypted file as a streaming response with a .enc extension
            encrypted_filename = f"{encrypted_file.original_filename}.enc"

            return StreamingResponse(
                iterfile(),
                media_type='application/octet-stream',
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encrypted_filename}",
                }
            )
        except Exception as e:
            print(f"Error downloading from Supabase: {str(e)}")
            raise HTTPException(status_code=404, detail="Encrypted file does not exist in storage")
    else:
        # Check if the encrypted file exists on disk (local storage)
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