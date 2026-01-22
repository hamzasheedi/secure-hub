import json
import time
import os
from getpass import getpass
from pathlib import Path
from modules import file_vault_manager as fvm
from modules.password_analyzer import analyze_password
from modules import password_hasher as ph
from modules import encryption_manager as em
from modules.constant_log import write_audit_log   # integrity 0+ 

 
# --- Utility Function to Clear Screen ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Register New User ---
def register():
    clear_screen()
    print("=== SecureVault | User Registration ===\n")

    username = input("Enter username: ").strip()
    if not username:
        input("\n[!] Username cannot be empty. Press Enter...")
        return

    password = getpass("Enter password: ").strip()
    if not password:
        input("\n[!] Password cannot be empty. Press Enter...")
        return

    rating = analyze_password(password)
    clear_screen()
    print(f"Password rating: {rating}\n")

    if rating == "Weak Password":
        input("[!] Weak password detected. Please choose a stronger one. Press Enter...")
        return

    salt = ph.generate_salt()
    hashed_pw = ph.hash_password(password, salt)

    if ph.store_user(username, salt, hashed_pw):
        input(f"[✓] User '{username}' registered successfully. Press Enter...")
    else:
        input("[!] Username already exists. Press Enter...")

# --- Delete Encrypted File ---
def delete_encrypted_file_flow(username: str):
    vault_enc = Path("vaults") / username / "encrypted"
    vault_enc.mkdir(parents=True, exist_ok=True)

    files = sorted([p for p in vault_enc.iterdir() if p.is_file() and p.suffix == ".enc"])
    if not files:
        input("\n[!] No encrypted files found. Press Enter...")
        return

    print("\n=== Encrypted Files ===")
    for i, p in enumerate(files, start=1):
        print(f"{i}. {p.name}")

    sel = input("\nEnter file number to delete (0 to cancel): ").strip()
    if sel == "0":
        return

    try:
        idx = int(sel) - 1
        target = files[idx]
    except Exception:
        input("\n[!] Invalid selection. Press Enter...")
        return

    confirm = input(f"\nAre you sure to permanently delete '{target.name}'? (y/n): ").lower()
    if confirm != "y":
        return

    pwd = getpass("Enter your password to confirm: ").strip()
    if not ph.verify_user(username, pwd):
        input("\n[!] Incorrect password. Press Enter...")
        return

    try:
        if hasattr(fvm, "secure_delete"):
            fvm.secure_delete(target)
        else:
            target.unlink()
        deleted = True
    except:
        deleted = False

    meta = target.with_name(target.name + ".meta")
    if meta.exists():
        try:
            meta.unlink()
        except:
            pass

    write_audit_log(username, "delete_encrypted", target.name, deleted)

    msg = "[✓] File deleted successfully." if deleted else "[!] Failed to delete file."
    input(f"\n{msg} Press Enter...")

# --- User Login ---
def login():
    clear_screen()
    print("=== SecureVault | Login Portal ===\n")
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ").strip()
    clear_screen()

    if ph.verify_user(username, password):
        user_data = ph.get_user(username)
        if user_data and not user_data.get("active", True):
            input("[!] Your account is inactive. Contact admin.\nPress Enter...")
            return

        print(f"=== Login successful. Welcome, {username}! ===")
        write_audit_log(username, "login", "system", True)
        user_vault_session(username)

    else:
        write_audit_log(username, "login", "system", False)
        input("[!] Login failed. Invalid credentials. Press Enter...")

        
# --- Vault Session ---
def user_vault_session(username: str):
    while True:
        clear_screen()
        print("===============================================")
        print(f"     SecureVault | {username}'s Vault")
        print("===============================================")
        print("1 → Encrypt File")
        print("2 → Decrypt File")
        print("3 → List Encrypted Files")
        print("4 → Delete Encrypted File")
        print("5 → Delete My Account")
        print("6 → Logout")
        print("===============================================")

        choice = input("Select an option (1–6): ").strip()

        if choice == "1":
            clear_screen()
            print("=== File Encryption ===\n")

            raw_path = input("Enter file path: ").strip()

            if raw_path.startswith("& "):
                raw_path = raw_path[2:].strip()
            raw_path = raw_path.strip('"').strip("'")
            raw_path = os.path.expanduser(raw_path)
            src_path = Path(raw_path)

            if not src_path.exists():
                input("\n[!] File Not Found. Press Enter...")
                continue

            pwd = getpass("Enter password: ").strip()
            yn = input("Delete original after encryption? (y/n): ").lower()

            ok = fvm.encrypt_user_file(username, src_path, pwd, yn == "y")
            write_audit_log(username, "encrypt", src_path.name, ok)

            input("\n[✓] Success!" if ok else "\n[!] Encryption failed.")

        elif choice == "2":
            clear_screen()
            print("=== File Decryption ===\n")

            files = fvm.list_encrypted_files(username)
            if not files:
                input("[!] No encrypted files found. Press Enter...")
                continue

            for i, p in enumerate(files, start=1):
                print(f"{i}. {p.name}")

            sel = input("\nSelect file number: ").strip()

            try:
                enc_path = files[int(sel) - 1]
                pwd = getpass("Enter password: ").strip()

                ok = fvm.decrypt_user_file(username, enc_path, pwd)
                write_audit_log(username, "decrypt", enc_path.name, ok)

                input("\n[✓] File decrypted!" if ok else "\n[!] Wrong password or corrupt file.")

            except:
                input("\n[!] Invalid input. Press Enter...")

        elif choice == "3":
            clear_screen()
            print("=== Your Encrypted Files ===\n")
            files = fvm.list_encrypted_files(username)

            if not files:
                print("[!] No files found.")
            else:
                for p in files:
                    print("-", p.name)

            input("\nPress Enter...")

        elif choice == "4":
            try:
                delete_encrypted_file_flow(username)
            except Exception as e:
                input(f"[!] Error deleting file: {e}\nPress Enter...")

        elif choice == "5":
            confirm = input("Are you sure you want to delete your account? (y/n): ").lower()
            if confirm == "y":
                delete_account(username)
                input("\n[✓] Account deleted successfully.")
                break

        elif choice == "6":
            print(f"\nLogging out {username}...")
            time.sleep(1)
            break

        else:
            input("[!] Invalid choice. Press Enter...")

# --- Delete Account ---
def delete_account(username):
    clear_screen()
    print("=== Delete My Account (Permanent) ===\n")

    if username.lower() == "admin":
        input("[!] Admin account cannot be deleted. Press Enter...")
        return

    confirm = input("Are you sure you want to permanently delete your account and all files? (y/n): ").lower()
    if confirm != "y":
        return

    clear_screen()
    print("=== Confirm Deletion ===\n")
    pwd = getpass("Enter your password to confirm deletion: ").strip()

    if not ph.verify_user(username, pwd):
        input("\n[!] Incorrect password. Account not deleted. Press Enter...")
        return

    vault_dir = Path("vaults") / username
    if vault_dir.exists():
        for p in vault_dir.rglob("*"):
            try: p.unlink()
            except: pass
        try: vault_dir.rmdir()
        except: pass

    users = ph.load_users()
    ph.save_users([u for u in users if u.get("username") != username])

    write_audit_log(username, "delete_account", username, True)

    clear_screen()
    print("=======================================")
    print(f"[✓] Account '{username}' deleted successfully.")
    print("All associated vault files and data are now removed.")
    print("=======================================")
    input("\nPress Enter to continue...")


# --- Admin Panel ---
def manage_users():

    clear_screen()
    print("=== Manage Users (Admin) ===\n")
    admin_user = input("Admin username: ").strip()
    admin_pw = getpass("Admin password: ").strip()
    print("=== Manage Users (Admin) ===\n")
    if not ph.verify_user(admin_user, admin_pw):
        input("[!] Invalid admin credentials. Press Enter...")
        return

    user_record = ph.get_user(admin_user)
    if not user_record or user_record.get("role") != "admin":
        input("[!] Only admin accounts can access this. Press Enter...")
        return

    users = ph.get_all_users()
    if not users:
        input("[!] No users found. Press Enter...")
        return

    while True:
        clear_screen()
        print("=== User List ===\n")

        for i, u in enumerate(users, start=1):
            status = "Active" if u.get("active", True) else "Inactive"
            print(f"{i}. {u.get('username')}  [{status}]")

        print("\n0. Return to Main Menu")
        sel = input("\nSelect user number: ").strip().lower()

        if sel == "0":
            break

        try:
            idx = int(sel) - 1
            target = users[idx].get("username")

            if target.lower() == "admin":
                input("\n[!] Admin status cannot be changed. Press Enter...")
                continue

            ok = ph.toggle_user_status(target)
            write_audit_log(admin_user, "toggle_user", target, ok)

            if ok:
                input(f"\n[✓] '{target}' status toggled. Press Enter...")
            else:
                input("\n[!] Failed to toggle user status. Press Enter...")

            users = ph.get_all_users()

        except:
            input("\n[!] Invalid selection. Press Enter...")


# --- Main Menu ---
def main():
    while True:
        clear_screen()
        print("""
=====================================
        SecureVault Main Menu
=====================================
1 → Register New User
2 → Login to Account
3 → Manage Users (Admin)
4 → Exit
==============*___*==================
""")
        choice = input("Select an option (1–4): ").strip()

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            manage_users()
        elif choice == "4":
            clear_screen()
            print("Exiting SecureVault... Stay Safe Online!")
            break
        else:
            input("[!] Invalid option. Press Enter...")

if __name__ == "__main__":
    main()
