"""
Simple server debug
"""

import sys
import os

# Add path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'api'))

print("Debug server startup...")
print(f"Python: {sys.executable}")
print(f"Working dir: {os.getcwd()}")
print()

try:
    print("1. Testing config import...")
    from config import settings
    print("SUCCESS: config imported")
    print(f"   API prefix: {settings.api_prefix}")
except Exception as e:
    print(f"ERROR: config import failed: {e}")

try:
    print("\n2. Testing FastAPI import...")
    from fastapi import FastAPI
    print("SUCCESS: FastAPI imported")
except Exception as e:
    print(f"ERROR: FastAPI import failed: {e}")

try:
    print("\n3. Testing router import...")
    from routers.v1 import tags
    print("SUCCESS: routers imported")
except Exception as e:
    print(f"ERROR: router import failed: {e}")

print("\nDebug complete")
