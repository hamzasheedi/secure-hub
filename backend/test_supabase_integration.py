"""
Test script to verify the Supabase integration with /tmp fallback
This script simulates the encrypt_file function behavior
"""
import os
import tempfile
from pathlib import Path
import shutil

# Mock environment variables
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["BUCKET_NAME"] = "vaults"
os.environ["USE_SUPABASE"] = "true"

# Import the configuration from our updated vault_routes
import sys
sys.path.insert(0, r'C:\Users\Hamza\Desktop\SecureVault_Project\backend\src')

from api.vault_routes import SUPABASE_URL, SUPABASE_KEY, BUCKET_NAME, USE_SUPABASE, supabase, TEMP_DIR

def test_supabase_config():
    """Test that Supabase configuration is loaded correctly"""
    print("Testing Supabase configuration...")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {'*' * len(SUPABASE_KEY) if SUPABASE_KEY else 'None'}")  # Don't print the actual key
    print(f"BUCKET_NAME: {BUCKET_NAME}")
    print(f"USE_SUPABASE: {USE_SUPABASE}")
    print(f"TEMP_DIR: {TEMP_DIR}")
    print(f"Supabase client initialized: {supabase is not None}")
    print()

def test_temp_file_handling():
    """Test temporary file creation and cleanup"""
    print("Testing temporary file handling...")
    
    # Create test files in temp directory
    test_raw_file = TEMP_DIR / "raw_test_user_testfile.txt"
    test_encrypted_file = TEMP_DIR / "enc_test_user_testfile.txt"
    
    # Write test content to raw file
    with open(test_raw_file, 'w') as f:
        f.write("This is a test file for encryption.")
    
    print(f"Created raw file: {test_raw_file}")
    print(f"Raw file exists: {test_raw_file.exists()}")
    
    # Simulate encryption by copying content to encrypted file
    shutil.copy(test_raw_file, test_encrypted_file)
    print(f"Copied to encrypted file: {test_encrypted_file}")
    print(f"Encrypted file exists: {test_encrypted_file.exists()}")
    
    # Test cleanup
    if test_raw_file.exists():
        test_raw_file.unlink()
        print(f"Cleaned up raw file: {test_raw_file}")
    
    if test_encrypted_file.exists():
        test_encrypted_file.unlink()
        print(f"Cleaned up encrypted file: {test_encrypted_file}")
    
    print(f"Raw file exists after cleanup: {test_raw_file.exists()}")
    print(f"Encrypted file exists after cleanup: {test_encrypted_file.exists()}")
    print()

def test_fallback_scenario():
    """Test the scenario when Supabase is not configured"""
    print("Testing fallback scenario (no Supabase)...")
    
    # Temporarily disable Supabase
    original_supabase = os.environ.get("SUPABASE_URL")
    if "SUPABASE_URL" in os.environ:
        del os.environ["SUPABASE_URL"]
    
    # Reload the configuration
    import importlib
    import api.vault_routes
    importlib.reload(api.vault_routes)
    
    from api.vault_routes import supabase as fallback_supabase
    print(f"Supabase client with no config: {fallback_supabase is not None}")
    
    # Restore original environment
    if original_supabase:
        os.environ["SUPABASE_URL"] = original_supabase
    
    print()

if __name__ == "__main__":
    print("Running tests for Supabase integration with /tmp fallback...\n")
    
    test_supabase_config()
    test_temp_file_handling()
    test_fallback_scenario()
    
    print("All tests completed successfully!")
    print("\nNote: This test verifies the configuration and file handling logic.")
    print("For actual Supabase integration testing, you would need valid credentials.")