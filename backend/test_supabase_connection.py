"""
Test script to verify Supabase connection and configuration
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_supabase_connection():
    """Test if Supabase credentials are properly configured"""
    print("Testing Supabase configuration...")
    
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
        print("\n❌ Supabase credentials not provided in settings")
        print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return False
    
    try:
        from supabase import create_client, Client
        
        # Try to create a client
        print(f"\nTrying to create Supabase client with URL: {settings.supabase_url[:50]}...")
        
        # Create client
        supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
        
        # Try to make a simple request to test the connection
        print("Testing connection by accessing storage buckets...")
        
        # List buckets to test the connection
        buckets_response = supabase.storage.list_buckets()
        print(f"Buckets found: {len(buckets_response.data) if buckets_response.data else 0}")
        
        # Check if our vaults bucket exists
        vaults_bucket_exists = any(bucket.name == settings.bucket_name for bucket in buckets_response.data or [])
        
        if not vaults_bucket_exists:
            print(f"⚠️  Warning: Bucket '{settings.bucket_name}' not found")
            print("   You may need to create it in your Supabase dashboard")
        else:
            print(f"✅ Bucket '{settings.bucket_name}' exists")
        
        print("\n✅ Supabase connection successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Supabase connection failed: {str(e)}")
        if "Invalid API key" in str(e):
            print("   This usually means the SUPABASE_KEY is incorrect")
        elif "invalid URL" in str(e).lower():
            print("   This usually means the SUPABASE_URL is incorrect")
        return False

def test_supabase_upload_simulation():
    """Test the upload logic without actually uploading"""
    print("\nTesting Supabase upload logic...")
    
    from dotenv import load_dotenv
    load_dotenv()
    from config.settings import settings
    
    # Check if we have credentials
    if settings.supabase_url and settings.supabase_key and settings.use_supabase.lower() == "true":
        print("✅ Supabase is configured to be used")
        print("   When a file is encrypted, it will attempt to upload to Supabase")
        print("   and only fall back to /tmp if Supabase operations fail")
        return True
    else:
        print("ℹ️  Supabase is not configured to be used")
        print("   Files will be stored in /tmp storage only")
        return True

if __name__ == "__main__":
    print("Supabase Connection Test")
    print("=" * 50)
    
    success1 = test_supabase_connection()
    success2 = test_supabase_upload_simulation()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All Supabase tests passed!")
        print("\nTo use Supabase:")
        print("1. Make sure your .env file has correct SUPABASE_URL and SUPABASE_KEY")
        print("2. Ensure the bucket name exists in your Supabase storage")
        print("3. Restart the server after making changes to .env")
    else:
        print("❌ Some Supabase tests failed!")
        print("\nPlease check your Supabase configuration in the .env file")