from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./secure_data.db").strip("'\"")  # Default to SQLite for development, strip quotes if present

    # JWT settings
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-fallback-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Encryption settings
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "fallback-encryption-key-for-development")
    pbkdf2_iterations: int = int(os.getenv("PBKDF2_ITERATIONS", "390000"))

    # File upload settings
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB in bytes
    allowed_file_types: str = os.getenv("ALLOWED_FILE_TYPES", "image/jpeg,image/png,application/pdf,application/zip")

    # Storage settings
    storage_path: str = os.getenv("STORAGE_PATH", "./secure_storage")

    # Additional settings from .env
    vaults_path: str = os.getenv("VAULTS_PATH", "./vaults")
    secure_data_path: str = os.getenv("SECURE_DATA_PATH", "./SecureVault_Data")
    server_host: str = os.getenv("SERVER_HOST", "localhost")
    server_port: int = int(os.getenv("SERVER_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Frontend URL for CORS
    frontend_url: str = os.getenv("FRONTEND_URL", "https://securevault-ixu4.onrender.com")

    # Supabase settings
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    bucket_name: str = os.getenv("BUCKET_NAME", "vaults")
    use_supabase: str = os.getenv("USE_SUPABASE", "true")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()