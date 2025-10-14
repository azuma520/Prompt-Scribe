#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test different API key formats and methods
"""

import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv("specs/001-sqlite-ags-db/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("=" * 60)
print("[DEBUG] Testing API Key Formats")
print("=" * 60)

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_ANON_KEY: {SUPABASE_ANON_KEY[:20]}...")
print(f"SUPABASE_SERVICE_ROLE_KEY: {SUPABASE_SERVICE_ROLE_KEY[:20]}...")

# Test 1: Direct REST API call with new format keys
print("\n[TEST 1] Direct REST API call with new format keys")
try:
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "name": "rest_api_test",
        "danbooru_cat": 0,
        "post_count": 999,
        "main_category": "REST_TEST",
        "sub_category": "REST_SUB",
        "confidence": 0.95,
        "classification_source": "rest_api_test"
    }
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/tags_final",
        headers=headers,
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print(f"[SUCCESS] REST API call successful!")
        print(f"Response: {response.json()}")
    else:
        print(f"[ERROR] REST API call failed: {response.text}")
        
except Exception as e:
    print(f"[ERROR] REST API call exception: {e}")

# Test 2: Try with old format JWT keys
print("\n[TEST 2] Try with old format JWT keys")
try:
    from supabase import create_client, Client
    
    # Try with anon key as service role (this might work for testing)
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    record = {
        "name": "jwt_test",
        "danbooru_cat": 0,
        "post_count": 888,
        "main_category": "JWT_TEST",
        "sub_category": "JWT_SUB",
        "confidence": 0.85,
        "classification_source": "jwt_test"
    }
    
    response = supabase.table("tags_final").insert(record).execute()
    print(f"[SUCCESS] JWT client call successful!")
    print(f"Response: {response}")
    
except Exception as e:
    print(f"[ERROR] JWT client call failed: {e}")
