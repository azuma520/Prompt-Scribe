#!/usr/bin/env python3
"""
部署測試工具
驗證 Supabase 部署是否成功
"""

import os
import sys
import json
from dotenv import load_dotenv
import requests
import psycopg2

def load_env():
    """載入環境變數"""
    load_dotenv()
    
    return {
        'supabase_url': os.getenv('SUPABASE_URL'),
        'supabase_anon_key': os.getenv('SUPABASE_ANON_KEY'),
        'supabase_service_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }

def get_supabase_connection():
    """獲取 Supabase PostgreSQL 連接"""
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    host = url.replace('https://', '').replace('http://', '')
    conn_string = f"host={host} port=5432 dbname=postgres user=postgres password={service_key} sslmode=require"
    
    try:
        conn = psycopg2.connect(conn_string)
        return conn
    except Exception as e:
        print(f"❌ 無法連接到 Supabase: {e}")
        return None

def test_basic_connectivity():
    """測試基本連接"""
    print("🔗 測試 Supabase 連接...")
    
    env = load_env()
    url = env['supabase_url']
    anon_key = env['supabase_anon_key']
    
    if not url or not anon_key:
        print("❌ 缺少必要的環境變數")
        return False
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}'
    }
    
    try:
        response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Supabase API 連接成功")
            return True
        else:
            print(f"❌ API 連接失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")
        return False

def test_database_connection():
    """測試資料庫連接"""
    print("🗄️ 測試 PostgreSQL 連接...")
    
    conn = get_supabase_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL 連接成功: {version[:50]}...")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL 連接失敗: {e}")
        return False
    finally:
        conn.close()

def test_data_migration():
    """測試數據遷移"""
    print("📊 測試數據遷移...")
    
    conn = get_supabase_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 檢查表是否存在
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'tags_final';
        """)
        
        if not cursor.fetchone():
            print("❌ tags_final 表不存在")
            return False
        
        # 檢查數據量
        cursor.execute("SELECT COUNT(*) FROM tags_final;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("❌ tags_final 表為空")
            return False
        
        print(f"✅ 數據遷移成功: {count:,} 筆記錄")
        
        # 檢查分類覆蓋率
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN main_category IS NOT NULL THEN 1 END) as classified,
                ROUND(COUNT(CASE WHEN main_category IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as coverage
            FROM tags_final;
        """)
        
        total, classified, coverage = cursor.fetchone()
        print(f"📈 分類覆蓋率: {classified:,}/{total:,} ({coverage}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 數據檢查失敗: {e}")
        return False
    finally:
        conn.close()

def test_vector_setup():
    """測試向量設置"""
    print("🧠 測試向量資料庫設置...")
    
    conn = get_supabase_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 檢查 pgvector 擴展
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if not cursor.fetchone():
            print("❌ pgvector 擴展未安裝")
            return False
        
        # 檢查嵌入表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'tag_embeddings';
        """)
        
        if not cursor.fetchone():
            print("❌ tag_embeddings 表不存在")
            return False
        
        # 檢查函數
        cursor.execute("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = 'public' 
            AND routine_name = 'search_similar_tags';
        """)
        
        if not cursor.fetchone():
            print("❌ 向量搜索函數不存在")
            return False
        
        print("✅ 向量資料庫設置正確")
        return True
        
    except Exception as e:
        print(f"❌ 向量設置檢查失敗: {e}")
        return False
    finally:
        conn.close()

def test_api_endpoints():
    """測試 API 端點"""
    print("🌐 測試 API 端點...")
    
    env = load_env()
    url = env['supabase_url']
    anon_key = env['supabase_anon_key']
    
    if not url or not anon_key:
        print("❌ 缺少 API 配置")
        return False
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }
    
    # 測試標籤摘要 API
    try:
        response = requests.get(
            f"{url}/rest/v1/tag_summary?select=*&limit=5", 
            headers=headers, 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 標籤摘要 API 正常: 返回 {len(data)} 筆記錄")
        else:
            print(f"❌ 標籤摘要 API 失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API 測試錯誤: {e}")
        return False
    
    # 測試分類統計 API
    try:
        response = requests.get(
            f"{url}/rest/v1/category_overview?select=*", 
            headers=headers, 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 分類統計 API 正常: {len(data)} 個分類")
        else:
            print(f"❌ 分類統計 API 失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API 測試錯誤: {e}")
        return False
    
    return True

def test_search_functions():
    """測試搜索函數"""
    print("🔍 測試搜索函數...")
    
    conn = get_supabase_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 測試文本搜索
        cursor.execute("""
            SELECT * FROM search_tags_by_text('anime', NULL, 0.5, 5);
        """)
        
        results = cursor.fetchall()
        if len(results) > 0:
            print(f"✅ 文本搜索正常: 找到 {len(results)} 個結果")
        else:
            print("⚠️ 文本搜索無結果 (可能正常)")
        
        # 測試分類統計
        cursor.execute("SELECT * FROM get_category_statistics() LIMIT 3;")
        stats = cursor.fetchall()
        
        if len(stats) > 0:
            print(f"✅ 分類統計正常: {len(stats)} 個分類")
            for category, count, usage, avg_conf, max_conf, min_conf in stats[:3]:
                print(f"  {category}: {count} 個標籤, {usage:,} 次使用")
        else:
            print("❌ 分類統計函數失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 搜索函數測試失敗: {e}")
        return False
    finally:
        conn.close()

def generate_test_report():
    """生成測試報告"""
    print("📋 生成測試報告...")
    
    env = load_env()
    
    report = f"""# Supabase 部署測試報告

## 測試時間
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 環境配置
- Supabase URL: {env['supabase_url']}
- 專案名稱: {os.getenv('PROJECT_NAME', 'prompt-scribe-tags')}
- 資料庫區域: {os.getenv('DATABASE_REGION', 'us-east-1')}

## 測試結果
✅ 基本連接測試通過
✅ 資料庫連接測試通過  
✅ 數據遷移測試通過
✅ 向量設置測試通過
✅ API 端點測試通過
✅ 搜索函數測試通過

## 部署狀態
🎉 **部署成功！**

所有核心功能都已正確設置並可正常使用。

## 下一步
1. 查看 Supabase Dashboard 確認數據
2. 使用 API 文檔測試各種端點
3. 根據需要生成嵌入向量
4. 開始整合到您的應用中

---
*此報告由 Supabase 部署測試工具自動生成*
"""
    
    with open('stage1/output/SUPABASE_TEST_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ 測試報告已生成: stage1/output/SUPABASE_TEST_REPORT.md")

def main():
    """主函數"""
    print("🧪 Supabase 部署測試工具")
    print("=" * 50)
    
    tests = [
        ("基本連接", test_basic_connectivity),
        ("資料庫連接", test_database_connection),
        ("數據遷移", test_data_migration),
        ("向量設置", test_vector_setup),
        ("API 端點", test_api_endpoints),
        ("搜索函數", test_search_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 測試: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通過")
            else:
                print(f"❌ {test_name} 失敗")
        except Exception as e:
            print(f"❌ {test_name} 錯誤: {e}")
    
    print(f"\n📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！部署成功！")
        generate_test_report()
    else:
        print(f"❌ {total - passed} 個測試失敗，請檢查部署")
        sys.exit(1)

if __name__ == "__main__":
    main()
