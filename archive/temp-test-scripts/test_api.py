"""
Test API endpoints
"""

import requests
import json
import sys
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://127.0.0.1:8000"

print("Testing Prompt-Scribe API...")
print("=" * 50)

# Test health
print("1. Testing health endpoint...")
try:
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Health check passed")
except Exception as e:
    print(f"❌ Health check failed: {e}")

print()

# Test OpenAI config
print("2. Testing OpenAI config...")
try:
    response = requests.get(f"{base_url}/api/llm/test-openai-config")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Available: {result.get('available', False)}")
    print(f"Error: {result.get('error', 'None')}")
    if result.get('validation_stats'):
        stats = result['validation_stats']
        print(f"Validation stats: {stats['total_validations']} total, {stats['success_rate']}% success")
except Exception as e:
    print(f"❌ OpenAI config test failed: {e}")

print()

# Test tag recommendation
print("3. Testing tag recommendation...")
try:
    payload = {"description": "一個長髮藍眼的動漫女孩"}
    response = requests.post(f"{base_url}/api/llm/recommend-tags", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Tags: {result.get('tags', [])}")
    print(f"Confidence: {result.get('confidence', 0)}")
    print(f"Fallback: {result.get('fallback', False)}")
    print("✅ Tag recommendation test passed")
except Exception as e:
    print(f"❌ Tag recommendation test failed: {e}")

print()
print("=" * 50)
print("API testing completed!")
