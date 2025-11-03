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

# Stay in project root, use absolute module path
# This ensures proper Python module resolution
project_root = os.path.dirname(__file__)

# Run uvicorn from project root with absolute module path
# Use --reload only if explicitly requested
import_mode = os.getenv('UVICORN_RELOAD', 'false').lower() == 'true'
args = [
    sys.executable, '-m', 'uvicorn', 
    'src.api.main:app',  # Use absolute import path
    '--host', '127.0.0.1', 
    '--port', '8000', 
    '--log-level', 'info'
]
if import_mode:
    args.extend(['--reload', '--reload-dir', 'src/api'])
subprocess.run(args, cwd=project_root)
