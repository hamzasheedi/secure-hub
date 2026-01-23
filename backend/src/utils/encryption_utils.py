import os
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Tuple, Optional
import base64


def generate_salt() -> bytes:
    """Generate a random salt for password hashing."""
    return secrets.token_bytes(32)


def hash_password(password: str, salt: bytes) -> str:
    """Hash a password using SHA-256 with salt."""
    pwdhash = hashlib.sha256(salt + password.encode('utf-8')).hexdigest()
    return pwdhash


def derive_key_from_password(password: str, salt: bytes, iterations: int = 390000) -> bytes:
    """Derive a key from a password using PBKDF2 with SHA-256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(password.encode('utf-8'))
    return base64.urlsafe_b64encode(key)


def encrypt_file(file_path: str, password: str) -> Tuple[str, str]:
    """
    Encrypt a file using Fernet (AES) with a key derived from the password.
    
    Args:
        file_path: Path to the file to encrypt
        password: Password to derive the encryption key from
        
    Returns:
        Tuple of (encrypted_file_path, algorithm_version)
    """
    # Generate salt for key derivation
    salt = generate_salt()
    
    # Derive encryption key from password
    key = derive_key_from_password(password, salt)
    fernet = Fernet(key)
    
    # Read the original file
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    # Encrypt the data
    encrypted_data = fernet.encrypt(file_data)
    
    # Create encrypted file path
    encrypted_file_path = file_path + '.encrypted'
    
    # Write encrypted data with salt prepended
    with open(encrypted_file_path, 'wb') as file:
        file.write(salt + encrypted_data)
    
    return encrypted_file_path, "AES-128-Fernet-PBKDF2"


def decrypt_file(encrypted_file_path: str, password: str) -> str:
    """
    Decrypt a file using Fernet (AES) with a key derived from the password.

    Args:
        encrypted_file_path: Path to the encrypted file
        password: Password to derive the decryption key from

    Returns:
        Path to the decrypted file
    """
    # Read the encrypted file
    with open(encrypted_file_path, 'rb') as file:
        file_data = file.read()

    # Extract salt (first 32 bytes) and encrypted data
    salt = file_data[:32]
    encrypted_data = file_data[32:]

    # Derive decryption key from password
    key = derive_key_from_password(password, salt)
    fernet = Fernet(key)

    # Decrypt the data
    decrypted_data = fernet.decrypt(encrypted_data)

    # Create decrypted file path
    decrypted_file_path = encrypted_file_path.replace('.encrypted', '.decrypted')

    # Write decrypted data
    with open(decrypted_file_path, 'wb') as file:
        file.write(decrypted_data)

    return decrypted_file_path


def decrypt_file_to_bytes(encrypted_file_path: str, password: str) -> Optional[bytes]:
    """
    Decrypt a file and return the decrypted data as bytes.

    Args:
        encrypted_file_path: Path to the encrypted file
        password: Password to derive the decryption key from

    Returns:
        Decrypted data as bytes, or None if decryption failed
    """
    try:
        # Read the encrypted file
        with open(encrypted_file_path, 'rb') as file:
            file_data = file.read()

        # Check if file is large enough to contain salt
        if len(file_data) < 32:
            print(f"Encrypted file is too small to contain salt: {len(file_data)} bytes")
            return None

        # Extract salt (first 32 bytes) and encrypted data
        salt = file_data[:32]
        encrypted_data = file_data[32:]

        # Derive decryption key from password
        key = derive_key_from_password(password, salt)
        fernet = Fernet(key)

        # Decrypt the data
        decrypted_data = fernet.decrypt(encrypted_data)

        return decrypted_data
    except Exception as e:
        # Print the exception for debugging
        print(f"Decryption failed with error: {str(e)}")
        return None