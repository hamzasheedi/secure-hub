@echo off
REM Production startup script for SecureVault backend on Windows

REM Load environment variables from .env file
for /f "tokens=*" %%i in ('type .env ^| findstr /v "^#"') do (
    for /f "tokens=1,* delims==" %%a in ("%%i") do (
        set "%%a=%%b"
    )
)

REM Set default values if environment variables are not set
if "%SERVER_HOST%"=="" set SERVER_HOST=localhost
if "%SERVER_PORT%"=="" set SERVER_PORT=8000

REM Run the application with Gunicorn
gunicorn src.main:app ^
    -k uvicorn.workers.UvicornWorker ^
    --bind %SERVER_HOST%:%SERVER_PORT% ^
    --workers 4 ^
    --worker-class uvicorn.workers.UvicornWorker ^
    --worker-connections 1000 ^
    --max-requests 1000 ^
    --max-requests-jitter 100 ^
    --timeout 30 ^
    --keep-alive 2 ^
    --preload