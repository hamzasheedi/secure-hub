#!/usr/bin/env bash
# Build script for Render

# Exit on any error
set -e

# Upgrade pip first
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run any necessary database migrations
python create_tables_autocommit.py || echo "Database creation step completed or skipped"