# SecureVault Modules

This directory contains the core modules that power the SecureVault application.

## Modules

### `constant_log.py`
Implements chain-hashed audit logging to ensure log integrity and detect tampering.

### `encryption_manager.py`
Handles all cryptographic operations including key derivation, file encryption, and decryption.

### `file_vault_manager.py`
Manages user vaults, file encryption/decryption operations, and secure file deletion.

### `password_analyzer.py`
Provides password strength analysis to ensure users create secure passwords.

### `password_hasher.py`
Manages user authentication, password hashing, and user account storage.

## Usage

These modules are imported and used by the main application (`main.py`) to provide the core functionality of SecureVault.

Each module follows the single-responsibility principle and can be tested and maintained independently.