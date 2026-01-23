from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    database_url: str = "sqlite:///./secure_data.db"  # Default to SQLite for development

    # JWT settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Encryption settings
    encryption_key: str
    pbkdf2_iterations: int = 390000

    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB in bytes
    allowed_file_types: str = "image/jpeg,image/png,application/pdf,application/zip"

    # Storage settings
    storage_path: str = "./secure_storage"

    # Additional settings from .env
    vaults_path: str = "./vaults"
    secure_data_path: str = "./SecureVault_Data"
    server_host: str = "localhost"
    server_port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()