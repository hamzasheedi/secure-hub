from src.database import SessionLocal
from src.services.user_service import UserService

def test_registration():
    db = SessionLocal()
    try:
        user_service = UserService(db)

        # Try to create a user with a shorter password
        user = user_service.create_user("testuser", "TestPass123!")
        print(f"User created: {user.username}")

        # Try to authenticate
        authenticated_user = user_service.authenticate_user("testuser", "TestPass123!")
        print(f"Authenticated user: {authenticated_user.username if authenticated_user else 'None'}")

    except Exception as e:
        print(f"Error during registration test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_registration()