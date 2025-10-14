#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細驗證 Supabase 資料庫結構的腳本
"""

import os
import requests
from dotenv import load_dotenv

def verify_database_structure():
    """詳細驗證資料庫結構"""
    
    # 載入環境變數
    load_dotenv("specs/001-sqlite-ags-db/.env")
    
    # 取得環境變數
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERROR: 找不到環境變數")
        return False
    
    # 準備請求標頭
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("開始驗證資料庫結構...")
    print("=" * 50)
    
    # 1. 檢查表是否存在
    tables_to_check = ['tags_final', 'tag_embeddings', 'migration_log']
    
    print("\n1. 檢查表是否存在:")
    for table_name in tables_to_check:
        try:
            # 嘗試查詢表結構
            table_url = f"{supabase_url}/rest/v1/{table_name}?select=*&limit=1"
            response = requests.get(table_url, headers=headers)
            
            if response.status_code == 200:
                print(f"  SUCCESS: {table_name} 表存在")
            elif response.status_code == 404:
                print(f"  NOT_FOUND: {table_name} 表不存在")
            else:
                print(f"  ERROR: {table_name} 表檢查失敗 (狀態碼: {response.status_code})")
                print(f"    錯誤訊息: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ERROR: {table_name} 表檢查異常: {e}")
    
    # 2. 檢查 pgvector 擴展
    print("\n2. 檢查 pgvector 擴展:")
    try:
        # 使用 SQL 查詢檢查擴展
        sql_query = "SELECT * FROM pg_extension WHERE extname = 'vector';"
        sql_endpoint = f"{supabase_url}/rest/v1/rpc/exec_sql"
        
        data = {'sql': sql_query}
        response = requests.post(sql_endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result:
                print("  SUCCESS: pgvector 擴展已安裝")
            else:
                print("  WARNING: pgvector 擴展未安裝")
        else:
            print(f"  ERROR: 無法檢查 pgvector 擴展 (狀態碼: {response.status_code})")
            
    except Exception as e:
        print(f"  ERROR: pgvector 檢查異常: {e}")
    
    # 3. 檢查索引
    print("\n3. 檢查索引:")
    try:
        sql_query = """
        SELECT indexname, tablename 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND indexname LIKE 'idx_%';
        """
        
        data = {'sql': sql_query}
        response = requests.post(sql_endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result:
                print(f"  SUCCESS: 找到 {len(result)} 個索引")
                for idx in result[:5]:  # 只顯示前5個
                    print(f"    - {idx.get('indexname')} on {idx.get('tablename')}")
                if len(result) > 5:
                    print(f"    ... 還有 {len(result) - 5} 個索引")
            else:
                print("  WARNING: 沒有找到索引")
        else:
            print(f"  ERROR: 無法檢查索引 (狀態碼: {response.status_code})")
            
    except Exception as e:
        print(f"  ERROR: 索引檢查異常: {e}")
    
    # 4. 嘗試直接 SQL 查詢
    print("\n4. 嘗試直接 SQL 查詢:")
    try:
        # 嘗試查詢 information_schema.tables
        sql_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('tags_final', 'tag_embeddings', 'migration_log');
        """
        
        data = {'sql': sql_query}
        response = requests.post(sql_endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result:
                print(f"  SUCCESS: 找到 {len(result)} 個表")
                for table in result:
                    print(f"    - {table.get('table_name')}")
            else:
                print("  WARNING: 沒有找到目標表")
        else:
            print(f"  ERROR: SQL 查詢失敗 (狀態碼: {response.status_code})")
            print(f"    錯誤: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ERROR: SQL 查詢異常: {e}")
    
    print("\n" + "=" * 50)
    print("驗證完成！")

if __name__ == "__main__":
    verify_database_structure()
