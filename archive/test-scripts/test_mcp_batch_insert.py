#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test batch insert using MCP approach
"""

import os
import sys
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment
load_dotenv("specs/001-sqlite-ags-db/.env")

sys.path.insert(0, str(Path(__file__).parent / "src" / "migration"))

from sqlite_reader import SQLiteReader

print("=" * 60)
print("[DEBUG] Testing MCP Batch Insert Approach")
print("=" * 60)

# Read a small batch from SQLite
with SQLiteReader() as reader:
    batch = reader.read_batch(0, 3)  # Read 3 records for testing

if batch:
    print(f"Read {len(batch)} records from SQLite")
    
    # Prepare SQL for batch insert
    values_list = []
    for record in batch:
        # Remove id field and prepare values
        record_for_insert = record.copy()
        record_for_insert.pop('id', None)
        
        values = f"""(
            '{record_for_insert["name"]}',
            {record_for_insert["danbooru_cat"]},
            {record_for_insert["post_count"]},
            '{record_for_insert["main_category"]}',
            '{record_for_insert["sub_category"]}',
            {record_for_insert["confidence"]},
            '{record_for_insert["classification_source"]}'
        )"""
        values_list.append(values)
    
    sql = f"""
    INSERT INTO tags_final (name, danbooru_cat, post_count, main_category, sub_category, confidence, classification_source)
    VALUES {', '.join(values_list)}
    RETURNING id, name;
    """
    
    print("Generated SQL:")
    print(sql)
    
    print("\n[INFO] You can now execute this SQL via MCP:")
    print("mcp_supabase_execute_sql")
    print("project_id: fumuvmbhmmzkenizksyq")
    print(f"query: {sql}")
else:
    print("[ERROR] No records read from SQLite")
