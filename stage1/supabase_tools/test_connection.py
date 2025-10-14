#!/usr/bin/env python3
"""
Supabase 連接測試工具
測試不同的連接方式
"""

import os
import sys
import requests
from dotenv import load_dotenv

def load_env():
    """載入環境變數"""
    # 嘗試從 stage1 目錄載入
    stage1_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(stage1_env_path):
        load_dotenv(stage1_env_path)
        print(f"載入 .env 文件: {stage1_env_path}")
    else:
        load_dotenv()
        print("載入當前目錄的 .env 文件")

def test_rest_api():
    """測試 REST API 連接"""
    print("\n測試 Supabase REST API 連接...")
    
    url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not anon_key:
        print("X 缺少必要的環境變數")
        return False
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 測試基本端點
        response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
        print(f"REST API 狀態: {response.status_code}")
        
        if response.status_code == 200:
            print("V REST API 連接成功")
            return True
        else:
            print(f"X REST API 連接失敗: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("X 連接超時 - 可能是網路問題")
        return False
    except requests.exceptions.ConnectionError:
        print("X 連接錯誤 - 檢查網路和防火牆")
        return False
    except Exception as e:
        print(f"X 其他錯誤: {e}")
        return False

def test_auth_api():
    """測試 Auth API"""
    print("\n測試 Supabase Auth API 連接...")
    
    url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}'
    }
    
    try:
        response = requests.get(f"{url}/auth/v1/settings", headers=headers, timeout=10)
        print(f"Auth API 狀態: {response.status_code}")
        
        if response.status_code in [200, 404]:  # 404 也是正常的，表示 API 可達
            print("V Auth API 連接成功")
            return True
        else:
            print(f"X Auth API 連接失敗: {response.text}")
            return False
            
    except Exception as e:
        print(f"X Auth API 錯誤: {e}")
        return False

def test_project_info():
    """測試專案信息"""
    print("\n檢查專案信息...")
    
    url = os.getenv('SUPABASE_URL')
    print(f"專案 URL: {url}")
    
    if url:
        # 提取專案 ID
        if 'supabase.co' in url:
            project_id = url.split('//')[1].split('.')[0]
            print(f"專案 ID: {project_id}")
            
            # 檢查是否是新版本 URL 格式
            if project_id.startswith('sb_'):
                print("檢測到新版 API Key 格式")
            else:
                print("檢測到舊版專案 ID 格式")
    
    return True

def main():
    """主函數"""
    print("Supabase 連接診斷工具")
    print("=" * 50)
    
    # 載入環境變數
    load_env()
    
    # 檢查專案信息
    test_project_info()
    
    # 測試 REST API
    rest_success = test_rest_api()
    
    # 測試 Auth API
    auth_success = test_auth_api()
    
    # 總結
    print("\n" + "=" * 50)
    print("診斷結果:")
    print(f"REST API: {'V 成功' if rest_success else 'X 失敗'}")
    print(f"Auth API: {'V 成功' if auth_success else 'X 失敗'}")
    
    if rest_success or auth_success:
        print("\nV 至少一個 API 連接成功，可以繼續部署")
    else:
        print("\nX 所有連接都失敗，請檢查:")
        print("1. 網路連接")
        print("2. 防火牆設置")
        print("3. Supabase 專案狀態")
        print("4. API Keys 是否正確")

if __name__ == "__main__":
    main()
