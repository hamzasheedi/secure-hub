import os
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.encrypted_file import EncryptedFile
from ..models.vault import Vault
from ..models.file_metadata import FileMetadata
from ..utils.encryption_utils import encrypt_file, decrypt_file, decrypt_file_to_bytes
from ..config.settings import settings


class VaultService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_vault(self, user_id: str) -> Optional[Vault]:
        """
        Create a vault for the given user.
        
        Args:
            user_id: The ID of the user to create a vault for
            
        Returns:
            The created Vault object, or None if creation failed
        """
        # Check if vault already exists
        existing_vault = self.db_session.query(Vault).filter(Vault.user_id == user_id).first()
        if existing_vault:
            return existing_vault
        
        # Create the vault
        vault = Vault(user_id=user_id)
        
        # Add to session and commit
        self.db_session.add(vault)
        self.db_session.commit()
        self.db_session.refresh(vault)
        
        return vault

    def encrypt_and_store_file(self, user_id: str, file_path: str, password: str) -> Optional[EncryptedFile]:
        """
        Encrypt a file and store it in the user's vault.
        
        Args:
            user_id: The ID of the user uploading the file
            file_path: Path to the file to encrypt
            password: Password to use for encryption
            
        Returns:
            The created EncryptedFile object, or None if encryption failed
        """
        # Verify user exists
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > settings.max_file_size:
            raise ValueError(f"File exceeds maximum size of {settings.max_file_size} bytes")

        # Create the vault if it doesn't exist
        self.create_vault(user_id)

        # Encrypt the file
        encrypted_file_path, algorithm_version = encrypt_file(file_path, password, user_id)

        # Create encrypted file record
        encrypted_file = EncryptedFile(
            user_id=user_id,
            original_filename=os.path.basename(file_path),
            file_size=file_size,
            encrypted_path=encrypted_file_path,
            algorithm_version=algorithm_version
        )

        # Add to session and commit
        self.db_session.add(encrypted_file)
        self.db_session.commit()
        self.db_session.refresh(encrypted_file)

        # Create file metadata record
        file_metadata = FileMetadata(
            file_id=encrypted_file.id,
            original_filename=encrypted_file.original_filename,
            file_size=encrypted_file.file_size,
            algorithm_version=encrypted_file.algorithm_version
        )

        # Add metadata to session and commit
        self.db_session.add(file_metadata)
        self.db_session.commit()

        return encrypted_file

    def decrypt_file(self, file_id: str, user_id: str, password: str) -> Optional[tuple]:
        """
        Decrypt a file from the user's vault.

        Args:
            file_id: The ID of the file to decrypt
            user_id: The ID of the user requesting decryption
            password: Password to use for decryption

        Returns:
            Tuple of (decrypted_data: bytes, original_filename: str), or None if decryption failed
        """
        # Verify the file belongs to the user
        encrypted_file = (
            self.db_session.query(EncryptedFile)
            .filter(EncryptedFile.id == file_id, EncryptedFile.user_id == user_id)
            .first()
        )

        if not encrypted_file:
            return None

        # Check if the encrypted file is stored in Supabase
        if encrypted_file.storage_location == "supabase":
            # The encrypted_path is the path in the Supabase bucket
            actual_path = encrypted_file.encrypted_path

            # Download the file from Supabase
            try:
                from supabase import create_client
                from ..config.settings import settings
                import tempfile

                SUPABASE_URL = settings.supabase_url if settings.supabase_url else os.getenv("SUPABASE_URL", "")
                SUPABASE_KEY = settings.supabase_key if settings.supabase_key else os.getenv("SUPABASE_KEY", "")

                if not SUPABASE_URL or not SUPABASE_KEY:
                    print("Supabase configuration not found")
                    return None

                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

                # Download the file from Supabase
                response = supabase.storage.from_(settings.bucket_name).download(actual_path)

                # Process the downloaded content
                from ..utils.encryption_utils import decrypt_file_to_bytes
                import os
                import tempfile

                # Create a temporary file to hold the downloaded content
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(response)
                    temp_file_path = temp_file.name

                try:
                    # Decrypt the temporary file
                    decrypted_data = decrypt_file_to_bytes(temp_file_path, password)

                    if decrypted_data is None:
                        print(f"Failed to decrypt file: {encrypted_file.encrypted_path}")
                        return None

                    return decrypted_data, encrypted_file.original_filename
                finally:
                    # Clean up the temporary file
                    os.unlink(temp_file_path)

            except Exception as e:
                print(f"Error downloading from Supabase: {str(e)}")
                return None
        else:
            # Check if the encrypted file exists on disk (local storage)
            if not os.path.exists(encrypted_file.encrypted_path):
                print(f"Encrypted file does not exist at path: {encrypted_file.encrypted_path}")
                return None

            # Decrypt the file and get the data
            decrypted_data = decrypt_file_to_bytes(encrypted_file.encrypted_path, password)

            if decrypted_data is None:
                print(f"Failed to decrypt file: {encrypted_file.encrypted_path}")
                return None

            return decrypted_data, encrypted_file.original_filename

    def list_user_files(self, user_id: str) -> List[EncryptedFile]:
        """
        List all encrypted files in the user's vault.
        
        Args:
            user_id: The ID of the user whose files to list
            
        Returns:
            A list of EncryptedFile objects
        """
        files = (
            self.db_session.query(EncryptedFile)
            .filter(EncryptedFile.user_id == user_id)
            .all()
        )
        
        return files

    def delete_file(self, file_id: str, user_id: str) -> bool:
        """
        Delete a file from the user's vault.

        Args:
            file_id: The ID of the file to delete
            user_id: The ID of the user requesting deletion

        Returns:
            True if the file was deleted, False otherwise
        """
        # Verify the file belongs to the user
        encrypted_file = (
            self.db_session.query(EncryptedFile)
            .filter(EncryptedFile.id == file_id, EncryptedFile.user_id == user_id)
            .first()
        )

        if not encrypted_file:
            return False

        # Check if the encrypted file is stored in Supabase
        if encrypted_file.storage_location == "supabase":
            # The encrypted_path is the path in the Supabase bucket
            actual_path = encrypted_file.encrypted_path

            # Delete the file from Supabase
            try:
                from supabase import create_client
                from ..config.settings import settings

                SUPABASE_URL = settings.supabase_url if settings.supabase_url else os.getenv("SUPABASE_URL", "")
                SUPABASE_KEY = settings.supabase_key if settings.supabase_key else os.getenv("SUPABASE_KEY", "")

                if not SUPABASE_URL or not SUPABASE_KEY:
                    print("Supabase configuration not found")
                    # Continue to delete the database record anyway
                else:
                    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

                    # Delete the file from Supabase storage
                    supabase.storage.from_(settings.bucket_name).remove([actual_path])

            except Exception as e:
                print(f"Error deleting from Supabase: {str(e)}")
                # Continue to delete the database record anyway
        else:
            # Delete the file from the local filesystem
            if os.path.exists(encrypted_file.encrypted_path):
                os.remove(encrypted_file.encrypted_path)

        # Delete the file metadata
        file_metadata = (
            self.db_session.query(FileMetadata)
            .filter(FileMetadata.file_id == file_id)
            .first()
        )
        if file_metadata:
            self.db_session.delete(file_metadata)

        # Delete the encrypted file record
        self.db_session.delete(encrypted_file)
        self.db_session.commit()

        return True