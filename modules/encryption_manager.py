# modules/encryption_manager.py
import base64
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend

def derive_key_from_password(password: str, salt: bytes, iterations: int = 390000) -> bytes:
    password_bytes = password.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(password_bytes)
    return base64.urlsafe_b64encode(key)

def encrypt_file_with_key(src_path: Path, dest_path: Path, fernet_key: bytes) -> None:
    f = Fernet(fernet_key)
    data = src_path.read_bytes()
    token = f.encrypt(data)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(token)

def decrypt_file_with_key(enc_path: Path, dest_path: Path, fernet_key: bytes) -> bool:
    try:
        f = Fernet(fernet_key)
        token = enc_path.read_bytes()
        data = f.decrypt(token)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(data)
        return True
    except Exception:
        return False
