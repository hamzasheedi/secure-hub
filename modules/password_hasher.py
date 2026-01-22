import hashlib
import secrets
import json
from pathlib import Path

DATA_FILE = Path("SecureVault_Data/secure_data.json")

def generate_salt():
    return secrets.token_hex(16)

def hash_password(password, salt):
    combined = (password + salt).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()

def load_users():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_users(users):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def store_user(username, salt, password_hash, role="user"):
    users = load_users()
    for u in users:
        if u.get("username") == username:
            return False
    users.append({
        "username": username,
        "salt": salt,
        "hash": password_hash,
        "active": True,
        "role": role   # default user; can be "admin" only via promote
    })
    save_users(users)
    return True

def get_user(username):
    users = load_users()
    for u in users:
        if u.get("username") == username:
            return u
    return None

def get_all_users():
    return load_users()

def promote_user(username, new_role="admin"):
    users = load_users()
    changed = False
    for u in users:
        if u.get("username") == username:
            u["role"] = new_role
            changed = True
            break
    if changed:
        save_users(users)
    return changed


def verify_user(username, password):
    users = load_users()
    for u in users:
        if u.get("username") == username:
            salt = u.get("salt", "")
            stored = u.get("hash", "")
            return hash_password(password, salt) == stored
    return False

# add these helper functions to password_hasher.py

def get_all_users():
    """Return list of user dicts from secure_data.json"""
    return load_users()

def toggle_user_status(username: str) -> bool:
    """
    Toggle active status for a username.
    Returns True if toggled (success), False if user not found.
    """
    users = load_users()
    changed = False
    for u in users:
        if u.get("username") == username:
            current = u.get("active", True)
            u["active"] = not current
            changed = True
            break
    if changed:
        save_users(users)
    return changed
