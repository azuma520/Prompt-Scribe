#!/usr/bin/env python3
"""
驗證 Supabase 連線和權限
檢查 SUPABASE_SERVICE_KEY 是否正確設定
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

def verify_supabase_connection():
    """驗證 Supabase 連線"""
    print("Verifying Supabase connection...")
    
    # 載入環境變數
    load_dotenv()
    
    # 獲取環境變數
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
    
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Service Key: {'Set' if SUPABASE_SERVICE_KEY else 'Not Set'}")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("ERROR: Missing required environment variables")
        print("Please run setup_env_local.ps1 and set correct SUPABASE_SERVICE_KEY")
        return False
    
    if SUPABASE_SERVICE_KEY == "請在這裡貼上您的真實 SUPABASE_SERVICE_KEY":
        print("ERROR: SUPABASE_SERVICE_KEY not updated")
        print("Please edit setup_env_local.ps1 and replace placeholder with real service_role key")
        return False
    
    try:
        # 建立 Supabase 客戶端
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # 測試連線 - 查詢 tags_final 表
        print("Testing database connection...")
        response = supabase.table('tags_final').select('id, name, post_count').limit(5).execute()
        
        if response.data:
            print(f"SUCCESS: Connected! Found {len(response.data)} tag records")
            print("Sample data:")
            for i, tag in enumerate(response.data[:3], 1):
                print(f"  {i}. {tag['name']} (count: {tag['post_count']})")
            
            # 檢查 embedding 欄位是否存在
            print("\nChecking embedding field...")
            sample_response = supabase.table('tags_final').select('id, name, embedding').limit(1).execute()
            if sample_response.data:
                sample_tag = sample_response.data[0]
                if 'embedding' in sample_tag:
                    if sample_tag['embedding'] is None:
                        print("embedding field exists but empty (normal, waiting for embedding generation)")
                    else:
                        print("embedding field has data")
                else:
                    print("ERROR: embedding field does not exist, need to run database setup")
                    return False
            
            return True
        else:
            print("ERROR: Connection failed - unable to get data")
            return False
            
    except Exception as e:
        print(f"ERROR: Connection error: {e}")
        if "Invalid API key" in str(e):
            print("TIP: Please check if SUPABASE_SERVICE_KEY is correct")
        return False

def check_environment():
    """檢查環境設定"""
    print("Checking environment settings...")
    
    # 檢查必要的環境變數
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY", 
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        elif var == "SUPABASE_SERVICE_KEY" and value == "Please paste your real SUPABASE_SERVICE_KEY here":
            missing_vars.append(f"{var} (needs update)")
    
    if missing_vars:
        print("ERROR: Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nSOLUTION:")
        print("  1. Run setup_env_local.ps1")
        print("  2. Ensure all API keys are correctly set")
        return False
    else:
        print("SUCCESS: All required environment variables are set")
        return True

if __name__ == "__main__":
    print("=" * 50)
    print("Supabase Connection Verification Tool")
    print("=" * 50)
    
    # 檢查環境
    env_ok = check_environment()
    
    if env_ok:
        # 驗證連線
        connection_ok = verify_supabase_connection()
        
        if connection_ok:
            print("\nSUCCESS: All checks passed! You can start using embedding generation")
        else:
            print("\nERROR: Connection verification failed, please check settings")
            sys.exit(1)
    else:
        print("\nERROR: Environment setup incomplete, please complete setup first")
        sys.exit(1)
