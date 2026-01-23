#!/bin/bash
# Production startup script for SecureVault backend

# Load environment variables from .env file
set -a
source .env
set +a

# Run the application with Gunicorn
exec gunicorn src.main:app \
    -k uvicorn.workers.UvicornWorker \
    --bind "$SERVER_HOST:$SERVER_PORT" \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --preload