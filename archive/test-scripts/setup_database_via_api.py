#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Database using Supabase API
Execute SQL scripts to create database structure
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv("specs/001-sqlite-ags-db/.env")

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def read_sql_file(filename):
    """Read SQL file content"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def execute_sql_script(supabase: Client, script_name, sql_content):
    """Execute SQL script"""
    print(f"\n{'='*60}")
    print(f"[INFO] Executing: {script_name}")
    print(f"{'='*60}")
    
    try:
        # Execute SQL using Supabase RPC
        result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
        print(f"[SUCCESS] {script_name} executed successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to execute {script_name}")
        print(f"Error: {e}")
        return False

def main():
    """Main function to setup database"""
    
    print("="*60)
    print("[INFO] Starting Database Setup")
    print("="*60)
    print(f"URL: {SUPABASE_URL}")
    
    # Create Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # List of SQL scripts to execute
    scripts = [
        ("01_enable_extensions.sql", "Enable pgvector extension"),
        ("02_create_tables.sql", "Create tables"),
        ("03_create_indexes.sql", "Create indexes"),
        ("04_create_rls_policies.sql", "Setup RLS policies"),
        ("05_create_rpc_functions.sql", "Create RPC functions (part 1)"),
        ("06_create_search_functions.sql", "Create RPC functions (part 2)"),
    ]
    
    success_count = 0
    
    for script_file, description in scripts:
        script_path = f"scripts/{script_file}"
        
        if not os.path.exists(script_path):
            print(f"[WARN] Script not found: {script_path}")
            continue
        
        print(f"\n[{success_count + 1}/{len(scripts)}] {description}")
        sql_content = read_sql_file(script_path)
        
        if execute_sql_script(supabase, script_file, sql_content):
            success_count += 1
        else:
            print(f"[WARN] Continuing to next script...")
    
    print("\n" + "="*60)
    print(f"[INFO] Database Setup Complete")
    print(f"[INFO] Successfully executed: {success_count}/{len(scripts)} scripts")
    print("="*60)

if __name__ == "__main__":
    main()

