"""
Test script to verify that all models are properly registered with SQLAlchemy.
This should be run before starting the FastAPI application.
"""

def test_model_registration():
    print("Testing model registration...")

    try:
        # Import the database module which should register all models
        from src.database import SessionLocal, Base
        from src.models.user import User
        from src.models.encrypted_file import EncryptedFile

        print("[SUCCESS] Successfully imported User and EncryptedFile models")

        # Create a session and try to query - this will trigger mapper configuration
        db = SessionLocal()

        # This will trigger SQLAlchemy to configure the mappers
        # If there are any missing models in the registry, this will fail
        try:
            # Just check if we can access the table without triggering a full query
            user_table = User.__table__
            encrypted_file_table = EncryptedFile.__table__
            print("[SUCCESS] Successfully accessed User and EncryptedFile tables")

            # Try to access the mapper to trigger configuration without querying the database
            # This will cause SQLAlchemy to configure the mappers and validate relationships
            from sqlalchemy.orm import class_mapper
            mapper = class_mapper(User)
            print("[SUCCESS] Successfully configured mappers - no missing model errors")

        except Exception as e:
            print(f"[ERROR] Error during mapper configuration: {e}")
            raise
        finally:
            db.close()

        print("\n[SUCCESS] All models are properly registered with SQLAlchemy!")
        print("The backend should now work without the 'EncryptedFile' not found error.")

    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("This means one of the model modules is not being imported properly.")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        print("This indicates the model registration is still not working properly.")
        return False

    return True

if __name__ == "__main__":
    success = test_model_registration()
    if success:
        print("\n[SUCCESS] Model registration test PASSED!")
    else:
        print("\n[ERROR] Model registration test FAILED!")
        exit(1)