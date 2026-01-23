import requests
import json
import uuid

def test_securevault_api():
    BASE_URL = "http://127.0.0.1:9001"
    
    print("[TEST] Starting comprehensive API functionality test...")
    
    # Test 1: Health check
    try:
        response = requests.get(BASE_URL + "/")
        assert response.status_code == 200
        assert "message" in response.json()
        print("[PASS] Health check: PASSED")
    except Exception as e:
        print(f"[FAIL] Health check: FAILED - {e}")
        return False

    # Test 2: User registration
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "username": username,
                "password": "SecurePass123!"
            })
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "User registered successfully"
        print("[PASS] User registration: PASSED")
    except Exception as e:
        print(f"[FAIL] User registration: FAILED - {e}")
        return False

    # Test 3: User login
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "username": username,
                "password": "SecurePass123!"
            })
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        token = response.json()["access_token"]
        print("[PASS] User login: PASSED")
    except Exception as e:
        print(f"[FAIL] User login: FAILED - {e}")
        return False

    # Test 4: Access vault with auth
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/vault/files", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("[PASS] Vault access with auth: PASSED")
    except Exception as e:
        print(f"[FAIL] Vault access with auth: FAILED - {e}")
        return False

    # Test 5: Delete user account
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{BASE_URL}/auth/account", headers=headers)
        assert response.status_code == 200
        assert "message" in response.json()
        print("[PASS] Account deletion: PASSED")
    except Exception as e:
        print(f"[FAIL] Account deletion: FAILED - {e}")
        return False

    print("\n[SUMMARY] All core API functionality tests PASSED!")
    print("[STATUS] SecureVault API is working correctly")
    return True

if __name__ == "__main__":
    success = test_securevault_api()
    if success:
        print("\n[RESULT] Backend is stable and all core functionality verified!")
    else:
        print("\n[ERROR] Backend has issues that need to be addressed!")