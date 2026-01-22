from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql://username:password@localhost/securevault"
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Encryption settings
    encryption_key: str = "your-encryption-key-change-in-production"
    pbkdf2_iterations: int = 390000
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB in bytes
    allowed_file_types: str = "image/jpeg,image/png,application/pdf,application/zip"
    
    # Storage settings
    storage_path: str = "./secure_storage"
    
    class Config:
        env_file = ".env"


settings = Settings()