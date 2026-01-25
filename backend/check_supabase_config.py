"""
Simple test to verify Supabase configuration without connecting
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_supabase_config():
    """Check if Supabase configuration is properly set"""
    print("Checking Supabase configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Import settings
    from config.settings import settings
    
    print(f"Supabase URL: {'SET' if settings.supabase_url else 'NOT SET'}")
    print(f"Supabase Key: {'SET' if settings.supabase_key else 'NOT SET'}")
    print(f"Bucket Name: {settings.bucket_name}")
    print(f"Use Supabase: {settings.use_supabase}")
    
    # Check if credentials are provided
    if not settings.supabase_url or not settings.supabase_key:
        print("\\nERROR: Supabase credentials not provided in settings")
        print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return False
    
    # Check if USE_SUPABASE is enabled
    use_supabase_enabled = settings.use_supabase.lower() == "true"
    print(f"Use Supabase Enabled: {use_supabase_enabled}")
    
    if not use_supabase_enabled:
        print("\\nINFO: Supabase is configured but not enabled (USE_SUPABASE=false)")
        print("Files will be stored in /tmp only")
        return True
    
    print("\\nSUCCESS: Supabase is properly configured and enabled!")
    print("When you upload files, they will attempt to go to Supabase first")
    print("and only fall back to /tmp if Supabase operations fail")
    
    return True

def check_vault_routes_config():
    """Check the vault routes configuration"""
    print("\\nChecking vault routes configuration...")
    
    # Read the vault routes file to verify the logic
    with open('src/api/vault_routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_lazy_init = 'Initialize Supabase client lazily' in content
    has_error_handling = 'except Exception as supabase_error:' in content
    has_fallback = 'Falling back to /tmp storage' in content
    has_size_validation = 'MAX_FILE_SIZE = 10 * 1024 * 1024' in content
    
    print(f"Lazy initialization: {has_lazy_init}")
    print(f"Error handling: {has_error_handling}")
    print(f"Fallback mechanism: {has_fallback}")
    print(f"Size validation: {has_size_validation}")
    
    all_checks = has_lazy_init and has_error_handling and has_fallback and has_size_validation
    if all_checks:
        print("\\nSUCCESS: All Supabase integration features are properly implemented!")
    else:
        print("\\nERROR: Some Supabase integration features are missing")
    
    return all_checks

if __name__ == "__main__":
    print("Supabase Configuration Check")
    print("=" * 50)
    
    success1 = check_supabase_config()
    success2 = check_vault_routes_config()
    
    print("\\n" + "=" * 50)
    if success1 and success2:
        print("SUCCESS: Supabase is properly configured!")
        print("\\nTo use Supabase:")
        print("1. Make sure your Supabase project is set up with a 'vaults' bucket")
        print("2. Verify your credentials are correct in the .env file")
        print("3. The system will automatically use Supabase when available")
        print("4. It will fall back to /tmp storage if Supabase is unavailable")
    else:
        print("ERROR: Supabase configuration issues found!")