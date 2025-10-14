#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單驗證 Supabase 表結構
"""

import os
import requests
from dotenv import load_dotenv

def simple_verify():
    """簡單驗證表是否存在"""
    
    load_dotenv("specs/001-sqlite-ags-db/.env")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("簡單驗證表結構...")
    print("=" * 30)
    
    tables = ['tags_final', 'tag_embeddings', 'migration_log']
    
    for table in tables:
        try:
            url = f"{supabase_url}/rest/v1/{table}?select=*&limit=1"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                print(f"SUCCESS: {table} 表存在")
            else:
                print(f"ERROR: {table} 表不存在 (狀態碼: {response.status_code})")
                
        except Exception as e:
            print(f"ERROR: {table} 檢查失敗: {e}")
    
    print("=" * 30)

if __name__ == "__main__":
    simple_verify()
