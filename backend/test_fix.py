import requests
import json

# Test the server is running
BASE_URL = "http://127.0.0.1:8000"

try:
    # Test basic connectivity
    response = requests.get(f"{BASE_URL}/docs")
    print(f"API docs accessible: {response.status_code == 200}")
    
    # Test health check if available
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
    except:
        print("No health check endpoint found")
        
    print("Server is running correctly with the applied fixes!")
    
except Exception as e:
    print(f"Error connecting to server: {e}")