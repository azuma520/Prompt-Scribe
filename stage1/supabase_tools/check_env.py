#!/usr/bin/env python3
"""
Supabase 環境檢查工具
檢查 .env 文件中的 Supabase 配置是否正確
"""

import os
import sys
from dotenv import load_dotenv
import requests

def check_env_config():
    """檢查環境配置"""
    print("檢查 Supabase 環境配置...")
    
    # 載入 .env 文件
    # 嘗試從 stage1 目錄載入
    stage1_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    
    if os.path.exists(stage1_env_path):
        load_dotenv(stage1_env_path)
        print(f"載入 .env 文件: {stage1_env_path}")
    elif os.path.exists(root_env_path):
        load_dotenv(root_env_path)
        print(f"載入 .env 文件: {root_env_path}")
    else:
        load_dotenv()
        print("載入當前目錄的 .env 文件")
    
    # 檢查必要的環境變數
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your-'):
            missing_vars.append(var)
            print(f"X {var}: 未設置或使用預設值")
        else:
            print(f"V {var}: 已設置")
    
    if missing_vars:
        print(f"\nX 缺少必要的環境變數: {', '.join(missing_vars)}")
        print("請在 .env 文件中設置這些變數")
        return False
    
    return True

def test_supabase_connection():
    """測試 Supabase 連接"""
    print("\n測試 Supabase 連接...")
    
    url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not anon_key:
        print("X 缺少 Supabase URL 或 API Key")
        return False
    
    try:
        # 測試 API 連接 - 新版本格式
        headers = {
            'Authorization': f'Bearer {anon_key}',
            'apikey': anon_key,
            'Content-Type': 'application/json'
        }
        
        # 嘗試新的 API 端點格式
        try:
            response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
        except Exception as e:
            print(f"嘗試舊版 API 端點失敗: {e}")
            # 嘗試新版本端點
            response = requests.get(f"{url}/api/v1/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("V Supabase API 連接成功")
            return True
        else:
            print(f"X Supabase API 連接失敗: {response.status_code}")
            print(f"回應: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"X 連接錯誤: {e}")
        return False

def main():
    """主函數"""
    print("Supabase 環境檢查工具")
    print("=" * 50)
    
    # 檢查環境配置
    if not check_env_config():
        sys.exit(1)
    
    # 測試連接
    if not test_supabase_connection():
        sys.exit(1)
    
    print("\n環境檢查完成！所有配置都正確")
    print("可以開始部署流程了")

if __name__ == "__main__":
    main()
