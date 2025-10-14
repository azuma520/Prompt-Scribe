#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug test for batch upload
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src" / "migration"))

from dotenv import load_dotenv
from supabase import create_client, Client
from sqlite_reader import SQLiteReader

# Load environment
load_dotenv("specs/001-sqlite-ags-db/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("=" * 60)
print("[DEBUG] Testing Single Record Upload")
print("=" * 60)

# Create client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Read one record
with SQLiteReader() as reader:
    batch = reader.read_batch(0, 1)
    record = batch[0] if batch else None

if record:
    print(f"\n[INFO] Test record:")
    print(f"  ID: {record['id']}")
    print(f"  Name: {record['name']}")
    print(f"  Category: {record.get('main_category')}")
    print(f"  Post count: {record.get('post_count')}")
    
    # Remove the id field since Supabase table has auto-increment id
    record_for_insert = record.copy()
    record_for_insert.pop('id', None)
    
    # Try to insert
    print("\n[INFO] Attempting insert...")
    try:
        response = supabase.table("tags_final").insert(record_for_insert).execute()
        print(f"[SUCCESS] Record inserted!")
        print(f"Response: {response}")
        if response.data:
            print(f"Inserted record ID: {response.data[0]['id']}")
    except Exception as e:
        print(f"[ERROR] Insert failed: {e}")
        print(f"\nRecord data for insert:")
        for key, value in record_for_insert.items():
            print(f"  {key}: {value} ({type(value).__name__})")

