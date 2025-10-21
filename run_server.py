"""
Run Prompt-Scribe API Server
"""

import sys
import os
import subprocess

# Get the correct API directory
api_dir = os.path.join(os.path.dirname(__file__), 'src', 'api')

print("Starting Prompt-Scribe API Server...")
print(f"API Directory: {api_dir}")

# Check if main.py exists
main_py = os.path.join(api_dir, 'main.py')
if not os.path.exists(main_py):
    print(f"ERROR: main.py not found at {main_py}")
    sys.exit(1)

print("main.py found, starting server...")
print("Server will be available at: http://127.0.0.1:8000")
print("API Documentation: http://127.0.0.1:8000/docs")
print("Health Check: http://127.0.0.1:8000/health")
print()
print("Press Ctrl+C to stop the server")
print("-" * 50)

# Change to API directory and run uvicorn
os.chdir(api_dir)

# Run uvicorn
subprocess.run([
    sys.executable, '-m', 'uvicorn', 
    'main:app', 
    '--host', '127.0.0.1', 
    '--port', '8000', 
    '--reload',
    '--log-level', 'info'
])
