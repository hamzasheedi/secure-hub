"""
SecureVault Server Startup Script
This script allows starting the server in different modes:
- Development: Using uvicorn directly
- Production: Using gunicorn (when called with production flag)
"""

import os
import sys
from src.config.settings import settings

def run_development():
    """Run the server in development mode using uvicorn"""
    import uvicorn
    
    print(f"Starting SecureVault API in development mode...")
    print(f"Server will run on {settings.server_host}:{settings.server_port}")
    print(f"CORS enabled for: {settings.frontend_url}")
    
    uvicorn.run(
        "src.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,  # Enable auto-reload in development
        debug=settings.debug
    )

def run_production():
    """Run the server in production mode using gunicorn"""
    import subprocess
    import multiprocessing
    
    # Determine the number of workers (usually 2 * number of CPU cores + 1)
    workers = (multiprocessing.cpu_count() * 2) + 1
    
    cmd = [
        "gunicorn",
        "src.main:app",
        "-k", "uvicorn.workers.UvicornWorker",
        f"--bind={settings.server_host}:{settings.server_port}",
        f"--workers={workers}",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--worker-connections=1000",
        "--max-requests=1000",
        "--max-requests-jitter=100",
        "--timeout=30",
        "--keep-alive=2",
        "--preload"
    ]
    
    print(f"Starting SecureVault API in production mode...")
    print(f"Server will run on {settings.server_host}:{settings.server_port}")
    print(f"Using {workers} worker processes")
    print(f"CORS enabled for: {settings.frontend_url}")
    
    subprocess.run(cmd)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "production":
        run_production()
    else:
        run_development()