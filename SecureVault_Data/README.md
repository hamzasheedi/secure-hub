# SecureVault Data Directory

This directory stores all application data including user credentials, logs, and backups.

## Structure

- `secure_data.json` - Contains user account information (username, salt, password hash, role)
- `backup/` - Stores backup files
- `encrypted/` - Stores encrypted files (though typically files are in user-specific vaults)
- `logs/` - Contains audit logs for tracking user activities

## Important Notes

- The `secure_data.json` file contains sensitive information and should be protected
- Audit logs in the `logs/` directory use chain-hashing for integrity verification
- This directory should have restricted access permissions in production environments

## Security Considerations

- Regularly backup this directory to prevent data loss
- Monitor access to this directory for security purposes
- Ensure proper encryption of this data at rest in production deployments