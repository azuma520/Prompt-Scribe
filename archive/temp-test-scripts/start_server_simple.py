"""
Start Prompt-Scribe API Server
"""

import sys
import os
import uvicorn

# Change to correct directory
api_dir = os.path.join(os.path.dirname(__file__), 'src', 'api')
os.chdir(api_dir)
sys.path.insert(0, api_dir)

print("=" * 60)
print("Starting Prompt-Scribe API Server")
print("=" * 60)
print(f"Working directory: {os.getcwd()}")
print(f"Python version: {sys.version}")
print()

# Check required files
if not os.path.exists('main.py'):
    print("ERROR: main.py not found")
    sys.exit(1)

if not os.path.exists('config.py'):
    print("ERROR: config.py not found")
    sys.exit(1)

print("Required files check passed")
print()

# Test imports
try:
    print("Testing module imports...")
    from config import settings
    print("SUCCESS: config imported")
    
    from fastapi import FastAPI
    print("SUCCESS: FastAPI imported")
    
    from routers.v1 import tags
    print("SUCCESS: routers imported")
    
except Exception as e:
    print(f"ERROR: Import failed: {e}")
    sys.exit(1)

print()
print("Starting server...")
print("URL: http://127.0.0.1:8000")
print("Docs: http://127.0.0.1:8000/docs")
print("Health: http://127.0.0.1:8000/health")
print()
print("Press Ctrl+C to stop")
print("=" * 60)

# Start server
uvicorn.run(
    "main:app",
    host="127.0.0.1",
    port=8000,
    reload=True,
    log_level="info"
)
