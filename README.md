# SecureVault

SecureVault is a command-line file encryption and decryption system that provides secure file storage with user management and audit logging capabilities.

## Features

- **File Encryption/Decryption**: Securely encrypt and decrypt files using AES encryption
- **User Management**: Register, login, and manage user accounts
- **Admin Panel**: Administrative controls for user management
- **Audit Logging**: Chain-hashed audit logs for integrity verification
- **Password Strength Analysis**: Built-in password strength checker
- **Secure File Deletion**: Overwrite files before deletion for security

## Prerequisites

- Python 3.6+
- `cryptography` library

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Install dependencies:
```bash
pip install cryptography
```

## Setup

1. Create an admin account:
```bash
python create_admin.py
```

2. Run the application:
```bash
python main.py
```

## Usage

The application provides a menu-driven interface:

1. **Register New User**: Create a new user account with password validation
2. **Login to Account**: Access your personal vault
3. **Manage Users (Admin)**: Activate/deactivate user accounts (admin only)

Once logged in, users can:
- Encrypt files with password protection
- Decrypt previously encrypted files
- List encrypted files
- Delete encrypted files
- Delete their account

## Security Features

- **Encryption**: Uses Fernet (AES 128 in CBC mode) for file encryption
- **Key Derivation**: PBKDF2 with SHA256 and 390,000 iterations
- **Password Hashing**: Salted SHA-256 hashing for stored passwords
- **Audit Logs**: Chain-hashed logs to detect tampering
- **Secure Deletion**: Overwrites files with random data before deletion

## Project Structure

```
├── main.py                 # Main application entry point
├── create_admin.py         # Script to create admin accounts
├── secure_data.json        # User credentials storage
├── modules/                # Application modules
│   ├── __init__.py
│   ├── constant_log.py     # Chain-hashed audit logging
│   ├── encryption_manager.py # Cryptographic operations
│   ├── file_vault_manager.py # File vault operations
│   ├── password_analyzer.py # Password strength analysis
│   ├── password_hasher.py  # User authentication
├── SecureVault_Data/       # Application data storage
│   ├── secure_data.json    # User credentials
│   ├── backup/
│   ├── encrypted/
│   └── logs/
└── vaults/                 # Individual user vaults
    └── {username}/
        ├── encrypted/
        ├── decrypted/
        └── backup/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.