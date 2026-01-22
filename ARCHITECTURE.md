# SecureVault Architecture Reference

## System Architecture Overview

This document provides a detailed reference for the SecureVault system architecture, expanding on the information in QWEN.md with focus on the upcoming FastAPI-based architecture.

## Current Architecture (CLI-based)

### Components
- **main.py**: Main application entry point with menu-driven interface
- **create_admin.py**: Admin account creation script
- **modules/**: Core functionality modules
  - encryption_manager.py: Cryptographic operations
  - file_vault_manager.py: File vault operations
  - password_hasher.py: Authentication
  - constant_log.py: Audit logging
  - password_analyzer.py: Password strength checking

### Data Flow
1. User interacts via CLI
2. Authentication via password_hasher
3. File encryption/decryption via encryption_manager
4. Secure storage in user-specific vaults
5. Audit logging via constant_log

## Planned Architecture (FastAPI-based)

### Backend Components
- **FastAPI Application**: REST API server
- **Authentication Service**: JWT-based auth
- **Vault Service**: File encryption/decryption operations
- **User Service**: User management
- **Audit Service**: Chain-hashed logging

### API Endpoints
- **/auth/**: Registration, login, logout
- **/vault/**: File encryption, decryption, listing
- **/admin/**: User management (admin only)

### Data Storage
- **PostgreSQL**: User accounts, metadata, audit logs
- **File System**: Encrypted files only

## Security Model

### Trust Boundaries
- Frontend: Trusted but limited access
- Backend: Full trust for encryption operations
- Storage: Untrusted (encrypted data only)

### Encryption Flow
1. User authenticates via JWT
2. File uploaded to /vault/encrypt endpoint
3. Backend derives key from user password using PBKDF2
4. File encrypted using Fernet (AES-128)
5. Encrypted file stored on file system
6. Metadata stored in database
7. Audit log entry created

## Deployment Models

### Local Mode
- Single-user setup
- All data stored locally
- Minimal configuration required

### Server Mode
- Multi-user support
- Centralized backend
- Isolated user vaults
- Admin controls

## Development Guidelines

### Coding Standards
- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Write docstrings for all public functions
- Implement proper error handling

### Security Practices
- Never expose encryption keys to frontend
- Validate all user inputs
- Implement rate limiting for auth endpoints
- Use secure random generators for salts

## Future Enhancements

### Planned Features
- Web-based frontend using modern frameworks
- Enhanced audit logging with integrity verification
- Multi-factor authentication
- File sharing capabilities
- Mobile application support

### Scalability Considerations
- Database connection pooling
- File upload size limits
- Asynchronous processing for large files
- Load balancing support