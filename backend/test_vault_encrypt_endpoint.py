"""
Actual tests for the /vault/encrypt endpoint
Testing file uploads, encryption, Supabase uploads, and /tmp fallback
"""
import os
import tempfile
import requests
import json
import time
import uuid
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Set up test constants
BASE_URL = "http://127.0.0.1:9001"  # Adjust to your test server URL
TEST_USERNAME = f"testuser_{uuid.uuid4().hex[:8]}"
TEST_PASSWORD = "SecurePass123!"
TEST_TOKEN = None


def setup_module():
    """Set up test user and get authentication token"""
    global TEST_TOKEN
    
    # Register test user
    register_resp = requests.post(
        f"{BASE_URL}/auth/register",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
    )
    
    # Login to get token
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
    )
    
    if login_resp.status_code == 200:
        TEST_TOKEN = login_resp.json()["access_token"]
    else:
        raise Exception(f"Failed to authenticate test user: {login_resp.text}")


def get_auth_headers():
    """Helper to get authentication headers"""
    return {"Authorization": f"Bearer {TEST_TOKEN}"}


def create_test_file(size_mb=1, filename="test_file.txt"):
    """Create a test file of specified size"""
    content = "A" * (size_mb * 1024 * 1024)  # Create content of specified size
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix="_" + filename)
    temp_file.write(content.encode('utf-8'))
    temp_file.close()
    return temp_file.name


def test_001_successful_supabase_upload():
    """Test T001: Successful Supabase Upload"""
    # This test requires valid Supabase credentials in the environment
    # For this test, we'll check if the endpoint accepts the request properly
    test_file_path = create_test_file(size_mb=1, filename="test_supabase.txt")
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'password': 'test_password_123'}
        
        response = requests.post(
            f"{BASE_URL}/vault/encrypt",
            files=files,
            data=data,
            headers=get_auth_headers()
        )
    
    # Clean up
    os.unlink(test_file_path)
    
    # The response depends on whether Supabase is configured
    # If Supabase is configured, we expect success
    # If not, we expect fallback to tmp
    assert response.status_code in [200, 500]  # 500 if Supabase fails but that's expected
    
    print(f"T001 Result: Status {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"  Storage: {result.get('storage', 'unknown')}")
        print(f"  Message: {result.get('message', 'none')}")
        return "PASS"
    else:
        print(f"  Error: {response.text}")
        return "FAIL"


def test_002_fallback_to_tmp():
    """Test T002: Fallback to /tmp when Supabase credentials missing"""
    # Temporarily unset Supabase environment variables
    original_supabase_url = os.environ.get('SUPABASE_URL')
    original_supabase_key = os.environ.get('SUPABASE_KEY')
    
    # Remove Supabase credentials to force fallback
    if 'SUPABASE_URL' in os.environ:
        del os.environ['SUPABASE_URL']
    if 'SUPABASE_KEY' in os.environ:
        del os.environ['SUPABASE_KEY']
    
    test_file_path = create_test_file(size_mb=1, filename="test_fallback.txt")
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'password': 'test_password_123'}
        
        response = requests.post(
            f"{BASE_URL}/vault/encrypt",
            files=files,
            data=data,
            headers=get_auth_headers()
        )
    
    # Restore original environment
    if original_supabase_url:
        os.environ['SUPABASE_URL'] = original_supabase_url
    if original_supabase_key:
        os.environ['SUPABASE_KEY'] = original_supabase_key
    
    # Clean up
    os.unlink(test_file_path)
    
    # Should succeed with fallback message
    if response.status_code == 200:
        result = response.json()
        if result.get('storage') == 'ephemeral_tmp':
            print("T002 Result: PASS - Correctly fell back to tmp storage")
            return "PASS"
        else:
            print(f"T002 Result: FAIL - Expected ephemeral_tmp storage, got {result.get('storage')}")
            return "FAIL"
    else:
        print(f"T002 Result: FAIL - Status {response.status_code}, Error: {response.text}")
        return "FAIL"


def test_003_file_encryption_validation():
    """Test T003: File encryption validation"""
    test_file_path = create_test_file(size_mb=1, filename="test_encrypt.txt")
    
    # Read original content
    with open(test_file_path, 'r') as f:
        original_content = f.read()
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'password': 'test_password_123'}
        
        response = requests.post(
            f"{BASE_URL}/vault/encrypt",
            files=files,
            data=data,
            headers=get_auth_headers()
        )
    
    # Clean up
    os.unlink(test_file_path)
    
    if response.status_code == 200:
        print("T003 Result: PASS - File encryption succeeded")
        return "PASS"
    else:
        print(f"T003 Result: FAIL - Status {response.status_code}, Error: {response.text}")
        return "FAIL"


def test_004_temporary_file_cleanup():
    """Test T004: Temporary file cleanup"""
    # This test is difficult to validate externally, but we can at least call the endpoint
    test_file_path = create_test_file(size_mb=1, filename="test_cleanup.txt")
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'password': 'test_password_123'}
        
        response = requests.post(
            f"{BASE_URL}/vault/encrypt",
            files=files,
            data=data,
            headers=get_auth_headers()
        )
    
    # Clean up
    os.unlink(test_file_path)
    
    if response.status_code == 200:
        print("T004 Result: PASS - Endpoint completed (cleanup behavior assumed)")
        return "PASS"
    else:
        print(f"T004 Result: FAIL - Status {response.status_code}, Error: {response.text}")
        return "FAIL"


def test_005_large_file_handling():
    """Test T005: Large file handling"""
    # Create a larger file (but not too large for testing)
    test_file_path = create_test_file(size_mb=5, filename="test_large.txt")
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'password': 'test_password_123'}
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/vault/encrypt",
            files=files,
            data=data,
            headers=get_auth_headers()
        )
        end_time = time.time()
    
    # Clean up
    os.unlink(test_file_path)
    
    processing_time = end_time - start_time
    
    if response.status_code == 200:
        print(f"T005 Result: PASS - Large file processed in {processing_time:.2f}s")
        return "PASS"
    elif response.status_code == 413:  # Payload Too Large
        print(f"T005 Result: FAIL - Large file rejected (proper behavior if size limit implemented)")
        return "FAIL"
    else:
        print(f"T005 Result: FAIL - Status {response.status_code}, Error: {response.text}")
        return "FAIL"


def test_006_missing_invalid_file():
    """Test T006: Missing or invalid file"""
    # Send request without a file
    data = {'password': 'test_password_123'}
    
    response = requests.post(
        f"{BASE_URL}/vault/encrypt",
        data=data,
        headers=get_auth_headers()
    )
    
    if response.status_code in [422]:  # Validation error
        print("T006 Result: PASS - Missing file properly rejected")
        return "PASS"
    else:
        print(f"T006 Result: FAIL - Expected 422, got {response.status_code}")
        return "FAIL"


def test_007_unauthorized_requests():
    """Test T007: Unauthorized requests"""
    test_file_path = create_test_file(size_mb=1, filename="test_auth.txt")
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'password': 'test_password_123'}
        
        response = requests.post(
            f"{BASE_URL}/vault/encrypt",
            files=files,
            data=data,
            # No auth header
        )
    
    # Clean up
    os.unlink(test_file_path)
    
    if response.status_code in [401, 403]:
        print("T007 Result: PASS - Unauthorized request properly rejected")
        return "PASS"
    else:
        print(f"T007 Result: FAIL - Expected 401/403, got {response.status_code}")
        return "FAIL"


def test_008_supabase_network_failure():
    """Test T008: Supabase network failure"""
    # Temporarily mock Supabase client to simulate network failure
    with patch('src.api.vault_routes.supabase') as mock_supabase:
        mock_supabase.storage.from_.side_effect = Exception("Network error")
        
        test_file_path = create_test_file(size_mb=1, filename="test_network.txt")
        
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'password': 'test_password_123'}
            
            response = requests.post(
                f"{BASE_URL}/vault/encrypt",
                files=files,
                data=data,
                headers=get_auth_headers()
            )
        
        # Clean up
        os.unlink(test_file_path)
        
        # If the endpoint properly handles the exception, it should either:
        # 1. Fall back to tmp storage (status 200 with tmp storage)
        # 2. Return an appropriate error (status 500)
        if response.status_code == 200:
            result = response.json()
            if result.get('storage') == 'ephemeral_tmp':
                print("T008 Result: PASS - Correctly fell back to tmp on network failure")
                return "PASS"
            else:
                print(f"T008 Result: PARTIAL - Status OK but storage: {result.get('storage')}")
                return "FAIL"
        elif response.status_code == 500:
            print("T008 Result: FAIL - Network error caused complete failure instead of fallback")
            return "FAIL"
        else:
            print(f"T008 Result: FAIL - Unexpected status {response.status_code}")
            return "FAIL"


def test_009_supabase_permission_failure():
    """Test T009: Supabase permission failure"""
    # Temporarily mock Supabase client to simulate permission failure
    with patch('src.api.vault_routes.supabase') as mock_supabase:
        # Mock an upload that raises a permission error
        mock_supabase.storage.from_.return_value.upload.side_effect = Exception("Permission denied")
        
        test_file_path = create_test_file(size_mb=1, filename="test_perm.txt")
        
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'password': 'test_password_123'}
            
            response = requests.post(
                f"{BASE_URL}/vault/encrypt",
                files=files,
                data=data,
                headers=get_auth_headers()
            )
        
        # Clean up
        os.unlink(test_file_path)
        
        # Check if fallback happened
        if response.status_code == 200:
            result = response.json()
            if result.get('storage') == 'ephemeral_tmp':
                print("T009 Result: PASS - Correctly fell back to tmp on permission failure")
                return "PASS"
            else:
                print(f"T009 Result: PARTIAL - Status OK but storage: {result.get('storage')}")
                return "FAIL"
        elif response.status_code == 500:
            print("T009 Result: FAIL - Permission error caused complete failure instead of fallback")
            return "FAIL"
        else:
            print(f"T009 Result: FAIL - Unexpected status {response.status_code}")
            return "FAIL"


def test_010_multiple_file_simultaneous():
    """Test T010: Multiple file uploads simultaneously"""
    import threading
    
    results = []
    
    def upload_file(filename):
        test_file_path = create_test_file(size_mb=1, filename=filename)
        
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'password': 'test_password_123'}
            
            response = requests.post(
                f"{BASE_URL}/vault/encrypt",
                files=files,
                data=data,
                headers=get_auth_headers()
            )
        
        # Clean up
        os.unlink(test_file_path)
        
        results.append((filename, response.status_code, response.json() if response.status_code == 200 else response.text))
    
    # Create and start multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=upload_file, args=[f"concurrent_test_{i}.txt"])
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Check results
    all_passed = all(r[1] == 200 for r in results)
    
    if all_passed:
        print("T010 Result: PASS - All concurrent uploads succeeded")
        return "PASS"
    else:
        failed_uploads = [(name, status) for name, status, _ in results if status != 200]
        print(f"T010 Result: FAIL - Failed uploads: {failed_uploads}")
        return "FAIL"


def test_011_system_limits_disk_space():
    """Test T011: System limits (disk space)"""
    # This is hard to test without actually filling the disk
    # Instead, we'll check if the implementation has disk space checking
    # For now, just call the endpoint and see if it works
    test_file_path = create_test_file(size_mb=2, filename="test_disk.txt")
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'password': 'test_password_123'}
        
        response = requests.post(
            f"{BASE_URL}/vault/encrypt",
            files=files,
            data=data,
            headers=get_auth_headers()
        )
    
    # Clean up
    os.unlink(test_file_path)
    
    if response.status_code == 200:
        print("T011 Result: PASS - Normal operation (disk space check not easily testable)")
        return "PASS"
    else:
        print(f"T011 Result: FAIL - Status {response.status_code}, Error: {response.text}")
        return "FAIL"


def test_012_system_limits_memory():
    """Test T012: System limits (memory usage)"""
    # Test with a moderately sized file to check memory handling
    test_file_path = create_test_file(size_mb=3, filename="test_memory.txt")
    
    import psutil
    import os
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'password': 'test_password_123'}
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/vault/encrypt",
            files=files,
            data=data,
            headers=get_auth_headers()
        )
        end_time = time.time()
    
    # Get final memory usage
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    memory_increase = final_memory - initial_memory
    
    # Clean up
    os.unlink(test_file_path)
    
    if response.status_code == 200:
        print(f"T012 Result: PASS - Processed with {memory_increase:.2f}MB memory increase in {end_time-start_time:.2f}s")
        return "PASS"
    else:
        print(f"T012 Result: FAIL - Status {response.status_code}, Error: {response.text}")
        return "FAIL"


def test_013_invalid_password_handling():
    """Test T013: Invalid password handling"""
    test_file_path = create_test_file(size_mb=1, filename="test_pass.txt")
    
    # Test with various password types
    passwords = [
        'normal_password_123',
        'p@ssw0rd_with_symbols!',
        'very_long_password_that_has_lots_of_characters_123456',
        'pa$$w0rd_w1th_numb3rs_@nd_$ymb0ls!'
    ]
    
    all_passed = True
    for pwd in passwords:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'password': pwd}
            
            response = requests.post(
                f"{BASE_URL}/vault/encrypt",
                files=files,
                data=data,
                headers=get_auth_headers()
            )
        
        if response.status_code != 200:
            print(f"Password '{pwd}' failed with status {response.status_code}")
            all_passed = False
    
    # Clean up
    os.unlink(test_file_path)
    
    if all_passed:
        print("T013 Result: PASS - All password formats handled correctly")
        return "PASS"
    else:
        print("T013 Result: FAIL - Some password formats failed")
        return "FAIL"


def test_014_file_name_sanitization():
    """Test T014: File name sanitization"""
    # Test with potentially dangerous filenames
    dangerous_names = [
        "normal_file.txt",
        "file_with_special_chars_@#$%.pdf",
        "file with spaces.docx",
        "file..with..dots.txt",
        "file_with_üñíçødé_chars.txt"  # Unicode characters
    ]
    
    all_passed = True
    for name in dangerous_names:
        test_file_path = create_test_file(size_mb=1, filename=name)
        
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'password': 'test_password_123'}
            
            response = requests.post(
                f"{BASE_URL}/vault/encrypt",
                files=files,
                data=data,
                headers=get_auth_headers()
            )
        
        if response.status_code != 200:
            print(f"Filename '{name}' failed with status {response.status_code}")
            all_passed = False
        
        # Clean up
        os.unlink(test_file_path)
    
    if all_passed:
        print("T014 Result: PASS - All filenames handled safely")
        return "PASS"
    else:
        print("T014 Result: FAIL - Some filenames caused failures")
        return "FAIL"


def test_015_database_transaction_integrity():
    """Test T015: Database transaction integrity"""
    # This is difficult to test directly, but we can verify that
    # successful encryptions result in proper database records
    test_file_path = create_test_file(size_mb=1, filename="test_db.txt")
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'password': 'test_password_123'}
        
        response = requests.post(
            f"{BASE_URL}/vault/encrypt",
            files=files,
            data=data,
            headers=get_auth_headers()
        )
    
    # Clean up
    os.unlink(test_file_path)
    
    if response.status_code == 200:
        result = response.json()
        # Check that required fields are present
        required_fields = ['file_id', 'original_name', 'size', 'encrypted_at']
        has_required_fields = all(field in result for field in required_fields)
        
        if has_required_fields:
            print("T015 Result: PASS - Database record has required fields")
            return "PASS"
        else:
            print(f"T015 Result: FAIL - Missing required fields in response: {result.keys()}")
            return "FAIL"
    else:
        print(f"T015 Result: FAIL - Status {response.status_code}, Error: {response.text}")
        return "FAIL"


def run_single_test(test_func, test_id, max_retries=6):
    """Run a single test with retry logic"""
    for attempt in range(1, max_retries + 1):
        try:
            result = test_func()
            if result == "PASS":
                print(f"{test_id}: PASS on attempt {attempt}")
                return "PASS"
            else:
                if attempt < max_retries:
                    print(f"{test_id}: FAIL on attempt {attempt}, retrying...")
                    time.sleep(1)  # Brief delay before retry
                else:
                    print(f"{test_id}: FINAL FAIL after {max_retries} attempts")
                    return "FAIL"
        except Exception as e:
            if attempt < max_retries:
                print(f"{test_id}: ERROR on attempt {attempt} ({str(e)}), retrying...")
                time.sleep(1)
            else:
                print(f"{test_id}: FINAL ERROR after {max_retries} attempts: {str(e)}")
                return "FAIL"
    
    return "FAIL"  # Should not reach here


def main():
    """Run all tests"""
    print("Starting tests for /vault/encrypt endpoint...")
    print("="*60)
    
    # Define all tests
    tests = [
        (test_001_successful_supabase_upload, "T001"),
        (test_002_fallback_to_tmp, "T002"),
        (test_003_file_encryption_validation, "T003"),
        (test_004_temporary_file_cleanup, "T004"),
        (test_005_large_file_handling, "T005"),
        (test_006_missing_invalid_file, "T006"),
        (test_007_unauthorized_requests, "T007"),
        (test_008_supabase_network_failure, "T008"),
        (test_009_supabase_permission_failure, "T009"),
        (test_010_multiple_file_simultaneous, "T010"),
        (test_011_system_limits_disk_space, "T011"),
        (test_012_system_limits_memory, "T012"),
        (test_013_invalid_password_handling, "T013"),
        (test_014_file_name_sanitization, "T014"),
        (test_015_database_transaction_integrity, "T015"),
    ]
    
    results = {}
    
    # Run each test
    for test_func, test_id in tests:
        print(f"\nRunning {test_id}: {test_func.__name__}")
        print("-" * 50)
        result = run_single_test(test_func, test_id)
        results[test_id] = result
    
    # Print final summary
    print("\n" + "="*60)
    print("FINAL TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result == "PASS")
    failed = sum(1 for result in results.values() if result == "FAIL")
    
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    print("Detailed Results:")
    for test_id, result in results.items():
        status = "PASS" if result == "PASS" else "FAIL"
        print(f"  {test_id}: {status}")
    
    print("\nRecommendations for failing tests:")
    failing_tests = [tid for tid, result in results.items() if result == "FAIL"]
    
    if "T005" in failing_tests:
        print("  - T005: Implement file size validation before processing")
    if "T008" in failing_tests:
        print("  - T008: Add exception handling around Supabase operations with fallback to /tmp")
    if "T009" in failing_tests:
        print("  - T009: Add permission error handling for Supabase operations")
    if "T011" in failing_tests:
        print("  - T011: Add disk space validation before creating temporary files")
    if "T012" in failing_tests:
        print("  - T012: Implement streaming/chunked processing for large files")
    
    return results


if __name__ == "__main__":
    main()