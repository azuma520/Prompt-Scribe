#!/usr/bin/env python3
"""
Supabase 部署主腳本
執行完整的部署流程：檢查環境 -> 遷移數據 -> 設置向量 -> 創建 API
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

def print_header(title):
    """打印標題"""
    print("\n" + "=" * 60)
    print(f"Supabase {title}")
    print("=" * 60)

def print_step(step, description):
    """打印步驟"""
    print(f"\n步驟 {step}: {description}")
    print("-" * 40)

def run_script(script_path, description):
    """運行腳本"""
    print(f"執行: {description}")
    
    try:
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        if result.returncode == 0:
            print(f"V {description} 完成")
            if result.stdout:
                print("輸出:", result.stdout.strip())
        else:
            print(f"X {description} 失敗")
            print("錯誤:", result.stderr.strip())
            return False
            
    except Exception as e:
        print(f"X 執行 {description} 時發生錯誤: {e}")
        return False
    
    return True

def check_prerequisites():
    """檢查前置條件"""
    print_step(1, "檢查前置條件")
    
    # 檢查 .env 文件
    if not os.path.exists('stage1/.env'):
        print("X 找不到 stage1/.env 文件")
        print("請創建 .env 文件並設置 Supabase 配置")
        return False
    
    # 檢查 tags.db 文件
    if not os.path.exists('stage1/output/tags.db'):
        print("X 找不到 stage1/output/tags.db 文件")
        print("請確保 tags.db 文件存在於 stage1/output/ 目錄中")
        return False
    
    # 檢查必要的 Python 包
    required_packages = {
        'psycopg2': 'psycopg2',
        'python-dotenv': 'dotenv', 
        'openai': 'openai',
        'requests': 'requests'
    }
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"X 缺少必要的 Python 包: {', '.join(missing_packages)}")
        print("請運行: pip install " + " ".join(missing_packages))
        return False
    
    print("V 前置條件檢查通過")
    return True

def main():
    """主函數"""
    print_header("Supabase 部署工具")
    
    start_time = datetime.now()
    print(f"開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查前置條件
    if not check_prerequisites():
        sys.exit(1)
    
    # 步驟 1: 檢查環境配置
    print_step(1, "檢查 Supabase 環境配置")
    if not run_script('stage1/supabase_tools/check_env.py', '環境配置檢查'):
        print("X 環境配置檢查失敗，請檢查 .env 文件中的 Supabase 配置")
        sys.exit(1)
    
    # 步驟 2: 遷移數據到 Supabase
    print_step(2, "遷移數據到 Supabase PostgreSQL")
    if not run_script('stage1/supabase_tools/migrate_to_supabase.py', '數據遷移'):
        print("X 數據遷移失敗")
        sys.exit(1)
    
    # 步驟 3: 設置向量資料庫
    print_step(3, "設置 pgvector 向量資料庫")
    if not run_script('stage1/supabase_tools/setup_vector_db.py', '向量資料庫設置'):
        print("X 向量資料庫設置失敗")
        sys.exit(1)
    
    # 步驟 4: 創建 API 端點
    print_step(4, "創建 API 端點和文檔")
    if not run_script('stage1/supabase_tools/create_api_endpoints.py', 'API 端點創建'):
        print("X API 端點創建失敗")
        sys.exit(1)
    
    # 步驟 5: 生成嵌入向量（可選）
    print_step(5, "生成標籤嵌入向量")
    print("這一步需要 OpenAI API，會產生費用")
    response = input("是否繼續生成嵌入向量？(y/N): ").strip().lower()
    
    if response == 'y':
        if not run_script('stage1/supabase_tools/generate_embeddings.py', '嵌入向量生成'):
            print("嵌入向量生成失敗，但不影響基本功能")
    else:
        print("跳過嵌入向量生成")
    
    # 完成
    end_time = datetime.now()
    duration = end_time - start_time
    
    print_header("部署完成！")
    print(f"完成時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"總耗時: {duration}")
    
    print("\nSupabase 部署成功！")
    print("\n接下來您可以：")
    print("1. 查看 API 文檔: stage1/output/API_DOCUMENTATION.md")
    print("2. 使用 Supabase Dashboard 查看數據")
    print("3. 開始使用 REST API 進行標籤搜索")
    print("4. 如果需要，稍後運行嵌入向量生成")
    
    # 顯示環境信息
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    if supabase_url:
        print(f"\nSupabase 專案 URL: {supabase_url}")
        print(f"Dashboard: {supabase_url.replace('.co', '.co/project/default')}")

if __name__ == "__main__":
    main()
