from src.main import app
import uvicorn
import sys
import traceback

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="127.0.0.1", port=9001, log_level="debug")
    except Exception as e:
        print(f"Error starting server: {e}")
        traceback.print_exc()
        sys.exit(1)