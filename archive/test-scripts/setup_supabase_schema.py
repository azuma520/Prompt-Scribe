#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立 Supabase 資料庫結構的腳本
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

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
    
    try:
        # 建立 Supabase 客戶端
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # 讀取 SQL 腳本
        sql_file = "specs/001-sqlite-ags-db/contracts/database_schema.sql"
        
        if not os.path.exists(sql_file):
            print(f"ERROR: 找不到 SQL 腳本檔案: {sql_file}")
            return False
        
        print(f"讀取 SQL 腳本: {sql_file}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("開始執行 SQL 腳本...")
        
        # 分割 SQL 語句（簡單分割，按分號）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(sql_statements):
            if not statement:
                continue
                
            try:
                print(f"執行語句 {i+1}/{len(sql_statements)}...")
                
                # 執行 SQL 語句
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                
                success_count += 1
                
                # 如果是 SELECT 語句，顯示結果
                if statement.strip().upper().startswith('SELECT'):
                    if result.data:
                        print(f"  結果: {result.data}")
                
            except Exception as e:
                error_count += 1
                print(f"  WARNING: 語句執行失敗: {str(e)[:100]}...")
                # 繼續執行其他語句
        
        print(f"\n執行完成!")
        print(f"成功: {success_count} 個語句")
        print(f"失敗: {error_count} 個語句")
        
        # 驗證表是否建立成功
        print("\n驗證表結構...")
        verify_tables(supabase)
        
        return True
        
    except Exception as e:
        print(f"ERROR: 建立資料庫結構失敗：{e}")
        return False

def verify_tables(supabase: Client):
    """驗證表是否建立成功"""
    
    tables_to_check = ['tags_final', 'tag_embeddings', 'migration_log']
    
    for table_name in tables_to_check:
        try:
            result = supabase.table(table_name).select('*').limit(1).execute()
            print(f"  ✅ {table_name} 表已建立")
        except Exception as e:
            print(f"  ❌ {table_name} 表建立失敗: {e}")

def check_extensions(supabase: Client):
    """檢查 pgvector 擴展是否啟用"""
    
    try:
        print("\n檢查 pgvector 擴展...")
        
        # 嘗試查詢擴展
        result = supabase.rpc('check_vector_extension').execute()
        
        if result.data:
            print("  ✅ pgvector 擴展已啟用")
        else:
            print("  ⚠️  pgvector 擴展狀態未知")
            
    except Exception as e:
        print(f"  ⚠️  無法檢查 pgvector 擴展: {e}")

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
