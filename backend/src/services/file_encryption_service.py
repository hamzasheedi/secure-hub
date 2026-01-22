import os
import uuid
from typing import Optional
from ..utils.encryption_utils import encrypt_file, decrypt_file
from ..config.settings import settings


class FileEncryptionService:
    def __init__(self):
        # Initialize any required resources
        pass

    def encrypt_file(self, file_path: str, password: str) -> tuple[str, str]:
        """
        Encrypt a file using the provided password.
        
        Args:
            file_path: Path to the file to encrypt
            password: Password to use for encryption
            
        Returns:
            A tuple containing the encrypted file path and algorithm version
        """
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > settings.max_file_size:
            raise ValueError(f"File exceeds maximum size of {settings.max_file_size} bytes")
        
        # Encrypt the file
        encrypted_file_path, algorithm_version = encrypt_file(file_path, password)
        
        return encrypted_file_path, algorithm_version

    def decrypt_file(self, encrypted_file_path: str, password: str) -> Optional[str]:
        """
        Decrypt a file using the provided password.
        
        Args:
            encrypted_file_path: Path to the encrypted file
            password: Password to use for decryption
            
        Returns:
            Path to the decrypted file, or None if decryption failed
        """
        # Validate file exists
        if not os.path.exists(encrypted_file_path):
            raise FileNotFoundError(f"Encrypted file does not exist: {encrypted_file_path}")
        
        # Decrypt the file
        try:
            decrypted_file_path = decrypt_file(encrypted_file_path, password)
            return decrypted_file_path
        except Exception as e:
            # Log the error in a real implementation
            print(f"Decryption failed: {str(e)}")
            return None

    def validate_file_type(self, file_path: str) -> bool:
        """
        Validate that the file type is allowed for encryption.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if the file type is allowed, False otherwise
        """
        # In a real implementation, we would check the file extension or MIME type
        # against the allowed types in settings
        _, ext = os.path.splitext(file_path)
        # This is a simplified check - in reality, we'd need to check against settings.allowed_file_types
        return True  # For now, allow all files

    def get_file_size(self, file_path: str) -> int:
        """
        Get the size of a file in bytes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Size of the file in bytes
        """
        return os.path.getsize(file_path)

    def is_file_size_allowed(self, file_path: str) -> bool:
        """
        Check if the file size is within the allowed limit.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file size is allowed, False otherwise
        """
        file_size = self.get_file_size(file_path)
        return file_size <= settings.max_file_size