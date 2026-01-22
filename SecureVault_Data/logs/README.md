# SecureVault Logs

This directory contains audit logs for the SecureVault application.

## Purpose

- Stores chain-hashed audit logs for tracking user activities
- Maintains integrity through cryptographic hashing
- Enables detection of log tampering

## Log Format

The audit logs use a chain-hashed format where each entry contains:
- Timestamp
- User information
- Action performed
- Target of the action
- Result of the action
- Previous hash (for integrity verification)
- Current hash (for integrity verification)

## Important Notes

- Logs are cryptographically linked to prevent tampering
- The integrity of logs can be verified using the chain-hashed structure
- Regular monitoring of logs is recommended for security purposes
- Log rotation policies may be needed to manage disk space over time