# Import all models FIRST to ensure they are registered with SQLAlchemy before creating tables/mappers
# This forces the execution of each model module, registering the classes with SQLAlchemy
from .models.user import User
from .models.encrypted_file import EncryptedFile
from .models.file_metadata import FileMetadata
from .models.vault import Vault
from .models.audit_log_entry import AuditLogEntry

# Explicitly configure mappers to ensure all relationships are resolved
from sqlalchemy.orm import configure_mappers
configure_mappers()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.auth_routes import router as auth_router
from .api.vault_routes import router as vault_router
from .api.admin_routes import router as admin_router

# Import settings to get dynamic configuration
from .config.settings import settings

# Print vaults path for debugging - remove after verification
print(f"VAULTS_PATH = {settings.vaults_path}")
print(f"SECURE_DATA_PATH = {settings.secure_data_path}")

app = FastAPI(title="SecureVault API", version="1.0.0")

# Add CORS middleware to allow requests from the frontend
# Allow both the configured frontend URL and localhost for development
allowed_origins = [settings.frontend_url]
if settings.debug:
    # In debug mode, also allow localhost for local development
    allowed_origins.extend([
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://securevault-ixu4.onrender.com"  # Also allow the frontend domain
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Multiple origins for flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(vault_router, prefix="/vault", tags=["vault"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SecureVault API"}