#!/usr/bin/env python3
"""快速測試 Inspire API (gpt-5-mini)"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("  Inspire API Quick Test (gpt-5-mini)")
print("=" * 60)

# Test start
print("\nTesting /api/inspire/start...")
payload = {
    "message": "我想要一個孤獨的少女",
    "user_access_level": "all-ages"
}

try:
    print(f"Sending request (timeout: 60s)...")
    r = requests.post(
        f"{BASE_URL}/api/inspire/start",
        json=payload,
        timeout=60
    )
    
    print(f"\nStatus: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"Success!")
        print(f"Session ID: {data.get('session_id')}")
        print(f"Phase: {data.get('phase')}")
        print(f"Message: {data.get('message')[:200]}...")
        print(f"Tool calls: {data.get('metadata', {}).get('total_tool_calls')}")
    else:
        print(f"Failed: {r.text[:500]}")
        
except requests.exceptions.Timeout:
    print("TIMEOUT - GPT-5-mini took more than 60s")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
