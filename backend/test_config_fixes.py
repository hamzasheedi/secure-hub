"""
Test to verify configuration issues are fixed
"""
import os
import sys
import tempfile
import subprocess
from pathlib import Path

def test_configuration_loading():
    """Test that the configuration loads without validation errors"""
    print("Testing configuration loading...")
    
    try:
        # Add the src directory to the path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Import settings to check if it loads without validation errors
        from config.settings import settings
        print(f"[OK] Settings loaded successfully")
        print(f"    Database URL: {settings.database_url}")
        print(f"    Server Port: {settings.server_port}")
        print(f"    Debug Mode: {settings.debug}")
        print(f"    Supabase URL: {'SET' if settings.supabase_url else 'NOT SET'}")
        print(f"    Supabase Key: {'SET' if settings.supabase_key else 'NOT SET'}")
        print(f"    Bucket Name: {settings.bucket_name}")
        print(f"    Use Supabase: {settings.use_supabase}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Settings failed to load: {e}")
        return False

def test_vault_routes_import():
    """Test that vault_routes can be imported without configuration errors"""
    print("\nTesting vault_routes import...")

    try:
        # Add the src directory to the path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        sys.path.insert(0, src_path)

        # Add src to Python path for relative imports
        import importlib.util
        spec = importlib.util.spec_from_file_location("vault_routes",
                                                     os.path.join(src_path, "api", "vault_routes.py"))
        vault_routes = importlib.util.module_from_spec(spec)

        # Execute the module to check for configuration errors
        spec.loader.exec_module(vault_routes)

        # Check the variables
        SUPABASE_URL = getattr(vault_routes, 'SUPABASE_URL', None)
        SUPABASE_KEY = getattr(vault_routes, 'SUPABASE_KEY', None)
        BUCKET_NAME = getattr(vault_routes, 'BUCKET_NAME', None)
        USE_SUPABASE = getattr(vault_routes, 'USE_SUPABASE', None)

        print(f"[OK] vault_routes imported successfully")
        print(f"    SUPABASE_URL: {'SET' if SUPABASE_URL else 'NOT SET'}")
        print(f"    SUPABASE_KEY: {'SET' if SUPABASE_KEY else 'NOT SET'}")
        print(f"    BUCKET_NAME: {BUCKET_NAME}")
        print(f"    USE_SUPABASE: {USE_SUPABASE}")

        return True
    except Exception as e:
        print(f"[ERROR] vault_routes failed to import: {e}")
        return False

def test_main_app_import():
    """Test that the main app can be imported without configuration errors"""
    print("\nTesting main app import...")

    try:
        # Add the src directory to the path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        sys.path.insert(0, src_path)

        # Add src to Python path for relative imports
        import importlib.util
        spec = importlib.util.spec_from_file_location("main",
                                                     os.path.join(src_path, "main.py"))
        main_module = importlib.util.module_from_spec(spec)

        # Execute the module to check for configuration errors
        spec.loader.exec_module(main_module)

        # Check the app
        app = getattr(main_module, 'app', None)

        print(f"[OK] Main app imported successfully")
        print(f"    App title: {getattr(app, 'title', 'Unknown')}")

        return True
    except Exception as e:
        print(f"[ERROR] Main app failed to import: {e}")
        return False

def test_environment_variables():
    """Test that environment variables are properly handled"""
    print("\nTesting environment variable handling...")

    # Temporarily set some environment variables to test the logic
    original_env = {}
    test_vars = {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'BUCKET_NAME': 'test-bucket',
        'USE_SUPABASE': 'true'
    }

    # Save original values
    for var in test_vars:
        original_env[var] = os.environ.get(var)

    # Set test values
    for var, value in test_vars.items():
        os.environ[var] = value

    try:
        # Add the src directory to the path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        sys.path.insert(0, src_path)

        # Add src to Python path for relative imports
        import importlib.util
        spec = importlib.util.spec_from_file_location("vault_routes_env_test",
                                                     os.path.join(src_path, "api", "vault_routes.py"))
        vault_routes = importlib.util.module_from_spec(spec)

        # Execute the module to check for configuration errors
        spec.loader.exec_module(vault_routes)

        # Check the variables
        SUPABASE_URL = getattr(vault_routes, 'SUPABASE_URL', None)
        SUPABASE_KEY = getattr(vault_routes, 'SUPABASE_KEY', None)
        BUCKET_NAME = getattr(vault_routes, 'BUCKET_NAME', None)
        USE_SUPABASE = getattr(vault_routes, 'USE_SUPABASE', None)

        print(f"[OK] Environment variables properly handled")
        print(f"    SUPABASE_URL: {SUPABASE_URL}")
        print(f"    SUPABASE_KEY: {SUPABASE_KEY}")
        print(f"    BUCKET_NAME: {BUCKET_NAME}")
        print(f"    USE_SUPABASE: {USE_SUPABASE}")

        # Verify values match
        success = (
            SUPABASE_URL == test_vars['SUPABASE_URL'] and
            SUPABASE_KEY == test_vars['SUPABASE_KEY'] and
            BUCKET_NAME == test_vars['BUCKET_NAME'] and
            USE_SUPABASE == (test_vars['USE_SUPABASE'].lower() == 'true')
        )

        if success:
            print("    [OK] All environment variables correctly loaded")
        else:
            print("    [ERROR] Environment variables not loaded correctly")

        return success
    except Exception as e:
        print(f"[ERROR] Environment variable test failed: {e}")
        return False
    finally:
        # Restore original environment
        for var, original_value in original_env.items():
            if original_value is not None:
                os.environ[var] = original_value
            elif var in os.environ:
                del os.environ[var]

def run_all_tests():
    """Run all configuration tests"""
    print("Testing configuration fixes...")
    print("="*60)
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("Vault Routes Import", test_vault_routes_import),
        ("Main App Import", test_main_app_import),
        ("Environment Variables", test_environment_variables),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*60)
    print("CONFIGURATION TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        icon = "[OK]" if result else "[ERROR]"
        print(f"{icon} {test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\nOverall result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\nConfiguration fixes successfully implemented:")
        print("- Added Supabase settings to Settings class")
        print("- Updated vault_routes to use settings properly")
        print("- Fixed validation errors")
        print("- Maintained backward compatibility with environment variables")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()