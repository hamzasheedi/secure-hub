"""
Database Initialization Script

This script creates all database tables based on the defined models.
Use this to initialize your database after setting up the models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.config.settings import settings
from src.database import Base, register_models

def init_db():
    """Initialize the database by creating all tables"""
    # Register all models to ensure they are registered with SQLAlchemy before creating tables
    register_models()

    print(f"Connecting to database: {settings.database_url}")
    engine = create_engine(settings.database_url)

    # Test the connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print(f"Connected to: {result.fetchone()[0]}")

            # Check if users table exists before creation
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'users'
                );
            """))
            table_exists = result.fetchone()[0]
            print(f"Users table exists before creation: {table_exists}")
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Check if users table exists after creation
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'users'
                );
            """))
            table_exists = result.fetchone()[0]
            print(f"Users table exists after creation: {table_exists}")
    except Exception as e:
        print(f"Error checking table after creation: {e}")

    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()