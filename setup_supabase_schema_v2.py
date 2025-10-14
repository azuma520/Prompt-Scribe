#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立 Supabase 資料庫結構的腳本 (使用 REST API)
"""

import os
import requests
import json
from dotenv import load_dotenv

def setup_supabase_schema():
    """在 Supabase 中建立資料庫結構"""
    
    # 載入環境變數
    load_dotenv("specs/001-sqlite-ags-db/.env")
    
    # 取得環境變數
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERROR: 找不到 SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    # 準備請求標頭
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # 讀取 SQL 腳本
    sql_file = "specs/001-sqlite-ags-db/contracts/database_schema.sql"
    
    if not os.path.exists(sql_file):
        print(f"ERROR: 找不到 SQL 腳本檔案: {sql_file}")
        return False
    
    print(f"讀取 SQL 腳本: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("開始執行 SQL 腳本...")
    
    # 使用 Supabase REST API 執行 SQL
    sql_endpoint = f"{supabase_url}/rest/v1/rpc/exec"
    
    # 分割 SQL 語句
    sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(sql_statements):
        if not statement or statement.startswith('--'):
            continue
            
        try:
            print(f"執行語句 {i+1}/{len(sql_statements)}...")
            
            # 準備請求資料
            data = {
                'sql': statement
            }
            
            # 發送請求
            response = requests.post(sql_endpoint, headers=headers, json=data)
            
            if response.status_code == 200:
                success_count += 1
                print(f"  SUCCESS: 成功")
                
                # 如果有結果，顯示前幾個字符
                if response.text and response.text != 'null':
                    result_preview = response.text[:100]
                    print(f"  結果預覽: {result_preview}...")
            else:
                error_count += 1
                print(f"  ERROR: 失敗 (狀態碼: {response.status_code})")
                print(f"  錯誤: {response.text[:200]}...")
                
        except Exception as e:
            error_count += 1
            print(f"  ERROR: 執行錯誤: {str(e)[:100]}...")
    
    print(f"\n執行完成!")
    print(f"成功: {success_count} 個語句")
    print(f"失敗: {error_count} 個語句")
    
    # 驗證表是否建立成功
    print("\n驗證表結構...")
    verify_tables(supabase_url, headers)
    
    return success_count > 0

def verify_tables(supabase_url, headers):
    """驗證表是否建立成功"""
    
    tables_to_check = ['tags_final', 'tag_embeddings', 'migration_log']
    
    for table_name in tables_to_check:
        try:
            # 嘗試查詢表
            table_url = f"{supabase_url}/rest/v1/{table_name}?select=*&limit=1"
            response = requests.get(table_url, headers=headers)
            
            if response.status_code == 200:
                print(f"  SUCCESS: {table_name} 表已建立")
            else:
                print(f"  ERROR: {table_name} 表建立失敗 (狀態碼: {response.status_code})")
                
        except Exception as e:
            print(f"  ERROR: {table_name} 表驗證錯誤: {e}")

if __name__ == "__main__":
    print("開始建立 Supabase 資料庫結構...")
    print("=" * 50)
    
    success = setup_supabase_schema()
    
    if success:
        print("\n" + "=" * 50)
        print("資料庫結構建立完成！")
        print("現在可以開始遷移資料了。")
    else:
        print("\n" + "=" * 50)
        print("資料庫結構建立失敗，請檢查錯誤訊息。")
