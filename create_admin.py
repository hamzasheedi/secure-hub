from modules import password_hasher as ph
from modules.password_hasher import generate_salt, hash_password

def create_admin(username, password):
    salt = generate_salt()
    h = hash_password(password, salt)
    ok = ph.store_user(username, salt, h, role="admin")
    if ok:
        print(f"Admin '{username}' created.")
    else:
        print("User exists. Use promote_user if needed.")

if __name__ == "__main__":
    uname = input("Admin username (suggest 'admin'): ").strip()
    pwd = input("Admin password: ").strip()
    create_admin(uname, pwd)
