import os
import json
import time
from pathlib import Path
from modules import encryption_manager as em

# Vault and log directories
VAULT_ROOT = Path("vaults")
LOG_DIR = Path("SecureVault_Data/logs")
LOG_FILE = LOG_DIR / "activity_log.txt"


#— Create vault folder for a specific user
def get_user_vault_path(username: str) -> Path:
    path = VAULT_ROOT / username
    for sub in ["encrypted", "decrypted", "backup"]:
        (path / sub).mkdir(parents=True, exist_ok=True)
    return path


#— Maintain secure audit trail
def write_audit_log(username: str, action: str, filename: str, deleted_original: bool, success: bool = True):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "user": username,
        "action": action,
        "file": filename,
        "deleted_original": deleted_original,
        "success": success
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


#— Secure delete (forensically safe)
def secure_delete(file_path: Path) -> bool:
    try:
        if not file_path.exists():
            return False
        length = file_path.stat().st_size
        with open(file_path, "r+b") as f:
            f.seek(0)
            f.write(os.urandom(length))
            f.flush()
            os.fsync(f.fileno())
        file_path.unlink()
        return True
    except Exception:
        try:
            file_path.unlink()
        except Exception:
            pass
        return False


#— Encrypt file for user
def encrypt_user_file(username: str, src_path: Path, password: str, delete_original: bool = False) -> bool:
    try:
        if not src_path.exists() or not src_path.is_file():
            print("[!] Source file not found.")
            return False

        vault_path = get_user_vault_path(username)
        salt = os.urandom(16)
        key = em.derive_key_from_password(password, salt)

        enc_name = src_path.name + ".enc"
        enc_path = vault_path / "encrypted" / enc_name
        meta_path = enc_path.with_suffix(".enc.meta")

        em.encrypt_file_with_key(src_path, enc_path, key)

        meta = {
            "salt": salt.hex(),
            "orig_name": src_path.name,
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        meta_path.write_text(json.dumps(meta))

        deleted = secure_delete(src_path) if delete_original else False
        write_audit_log(username, "encrypt", src_path.name, deleted, success=True)
        return True
    except Exception as e:
        print("[X] Encryption error:", e)
        write_audit_log(username, "encrypt", src_path.name, False, success=False)
        return False


#— Decrypt file for user
def decrypt_user_file(username: str, enc_path: Path, password: str) -> bool:
    try:
        if not enc_path.exists() or not enc_path.is_file():
            print("[!] Encrypted file not found.")
            return False

        meta_path = enc_path.with_suffix(".enc.meta")
        if not meta_path.exists():
            print("[!] Metadata file missing.")
            return False

        meta = json.loads(meta_path.read_text())
        salt = bytes.fromhex(meta.get("salt", ""))
        orig_name = meta.get("orig_name", enc_path.stem)

        key = em.derive_key_from_password(password, salt)
        vault_path = get_user_vault_path(username)

        if "." in orig_name:
            stem, ext = os.path.splitext(orig_name)
            dec_name = f"{stem}_decrypted{ext}"
        else:
            dec_name = f"{orig_name}_decrypted.txt"

        dec_path = vault_path / "decrypted" / dec_name
        ok = em.decrypt_file_with_key(enc_path, dec_path, key)

        write_audit_log(username, "decrypt", enc_path.name, False, success=ok)
        return ok
    except Exception as e:
        print("[X] Decryption error:", e)
        write_audit_log(username, "decrypt", enc_path.name, False, success=False)
        return False


#— List encrypted files
def list_encrypted_files(username: str):
    vault_path = get_user_vault_path(username)
    enc_folder = vault_path / "encrypted"
    files = [f for f in enc_folder.iterdir() if f.is_file() and f.suffix == ".enc"]
    return sorted(files)


#— List decrypted files (extra feature)
def list_decrypted_files(username: str):
    vault_path = get_user_vault_path(username)
    dec_folder = vault_path / "decrypted"
    files = [f for f in dec_folder.iterdir() if f.is_file()]
    return sorted(files)
