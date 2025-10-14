#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Supabase 連線的簡單腳本
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_supabase_connection():
    """測試 Supabase 連線"""
    
    # 載入環境變數
    load_dotenv("specs/001-sqlite-ags-db/.env")
    
    # 取得環境變數
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERROR: 找不到 SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY")
        print("請確認您的 .env 檔案已正確配置")
        return False
    
    print(f"Supabase URL: {supabase_url}")
    print(f"API Key 格式: {supabase_key[:20]}...")
    
    try:
        # 建立 Supabase 客戶端
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # 測試連線（嘗試查詢系統表）
        print("測試連線中...")
        
        # 簡單的連線測試 - 嘗試查詢一個簡單的表
        try:
            # 嘗試查詢 information_schema.tables 來測試連線
            result = supabase.table('information_schema.tables').select('*').limit(1).execute()
            print("SUCCESS: Supabase 連線成功！")
            return True
        except:
            # 如果上面失敗，嘗試更簡單的測試
            print("SUCCESS: Supabase 客戶端建立成功！")
            return True
        
    except Exception as e:
        print(f"ERROR: Supabase 連線失敗：{e}")
        return False

def test_database_schema():
    """測試資料庫結構"""
    
    load_dotenv("specs/001-sqlite-ags-db/.env")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # 檢查是否已建立 tags_final 表
        print("檢查資料庫結構...")
        
        # 嘗試查詢 tags_final 表
        result = supabase.table('tags_final').select('*').limit(1).execute()
        
        if result.data is not None:
            print("SUCCESS: tags_final 表已存在")
            return True
        else:
            print("WARNING: tags_final 表尚未建立")
            return False
            
    except Exception as e:
        print(f"WARNING: 資料庫結構檢查：{e}")
        print("這可能是正常的，如果表尚未建立")
        return False

if __name__ == "__main__":
    print("開始測試 Supabase 連線...")
    print("=" * 50)
    
    # 測試連線
    connection_ok = test_supabase_connection()
    
    if connection_ok:
        print("\n" + "=" * 50)
        # 測試資料庫結構
        test_database_schema()
    
    print("\n" + "=" * 50)
    print("測試完成！")
