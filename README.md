# SecureVault

SecureVault is a modular, secure, and user-friendly file encryption and decryption system designed to protect sensitive data while providing a seamless user experience across platforms.

## Features

- **File Encryption/Decryption**: Securely encrypt and decrypt files using AES encryption
- **User Management**: Register, login, and manage user accounts
- **Admin Panel**: Administrative controls for user management
- **Audit Logging**: Chain-hashed audit logs for integrity verification
- **Password Strength Analysis**: Built-in password strength checker
- **Secure File Deletion**: Overwrite files before deletion for security

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 12+
- `cryptography` library

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   uvicorn src.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `https://securevault-ixu4.onrender.com/` (default) or `http://localhost:3000` during local development.

## Usage

The application provides a web-based interface for:

1. **Register New User**: Create a new user account with password validation
2. **Login to Account**: Access your personal vault
3. **Manage Users (Admin)**: Activate/deactivate user accounts (admin only)

Once logged in, users can:
- Encrypt files with password protection
- Decrypt previously encrypted files
- List encrypted files
- Delete encrypted files
- Delete their account

## Deployment Configuration

When both frontend and backend are deployed separately:

- **Frontend** is deployed at: `https://securevault-ixu4.onrender.com/`
- **Backend** is deployed at: `https://securevault-backend.onrender.com/`
- The frontend environment variable `NEXT_PUBLIC_API_BASE_URL` must be set to the backend URL for proper API communication

### CORS Configuration

The backend is configured to allow requests from:
- The configured frontend URL (via `FRONTEND_URL` environment variable)
- Additional development origins when running in debug mode:
  - `http://localhost:3000`
  - `http://localhost:8000`
  - `http://127.0.0.1:3000`
  - `http://127.0.0.1:8000`
  - `https://securevault-ixu4.onrender.com`

## Security Features

- **Encryption**: Uses Fernet (AES 128 in CBC mode) for file encryption
- **Key Derivation**: PBKDF2 with SHA256 and 390,000 iterations
- **Password Hashing**: Salted SHA-256 hashing for stored passwords
- **Audit Logs**: Chain-hashed logs to detect tampering
- **Secure Deletion**: Overwrites files with random data before deletion

## Architecture

SecureVault follows a modern, API-first, layered architecture:

- **Frontend Layer**: Web-based UI using Next.js
- **API & Backend Layer**: FastAPI backend with authentication and business logic
- **Core Security & Vault Services**: Encryption, user management, and audit services
- **Data & Storage Layer**: PostgreSQL for metadata, filesystem for encrypted files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.