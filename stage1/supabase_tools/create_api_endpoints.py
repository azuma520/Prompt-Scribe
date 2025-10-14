#!/usr/bin/env python3
"""
Supabase API 端點創建工具
創建標籤搜索和管理的 API 端點
"""

import os
import sys
import json
from dotenv import load_dotenv
import psycopg2
import requests

def load_env():
    """載入環境變數"""
    load_dotenv()
    
    return {
        'supabase_url': os.getenv('SUPABASE_URL'),
        'supabase_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
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

def create_search_functions(cursor):
    """創建搜索相關的 PostgreSQL 函數"""
    print("🔧 創建搜索函數...")
    
    # 文本搜索函數
    text_search_function = """
    CREATE OR REPLACE FUNCTION search_tags_by_text(
        search_query text,
        category_filter text DEFAULT NULL,
        min_confidence float DEFAULT 0.0,
        limit_count int DEFAULT 20
    )
    RETURNS TABLE (
        name varchar,
        main_category varchar,
        sub_category varchar,
        classification_confidence decimal,
        post_count int,
        similarity_score float
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            tf.name,
            tf.main_category,
            tf.sub_category,
            tf.classification_confidence,
            tf.post_count,
            CASE 
                WHEN tf.name ILIKE '%' || search_query || '%' THEN 1.0
                WHEN tf.name ILIKE search_query || '%' THEN 0.9
                WHEN tf.name ILIKE '%' || search_query THEN 0.8
                ELSE 0.7
            END as similarity_score
        FROM tags_final tf
        WHERE (
            tf.name ILIKE '%' || search_query || '%'
            OR tf.main_category ILIKE '%' || search_query || '%'
            OR tf.sub_category ILIKE '%' || search_query || '%'
        )
        AND (category_filter IS NULL OR tf.main_category = category_filter)
        AND tf.classification_confidence >= min_confidence
        ORDER BY similarity_score DESC, tf.post_count DESC
        LIMIT limit_count;
    END;
    $$;
    """
    
    cursor.execute(text_search_function)
    
    # 分類統計函數
    category_stats_function = """
    CREATE OR REPLACE FUNCTION get_category_statistics()
    RETURNS TABLE (
        main_category varchar,
        tag_count bigint,
        total_usage bigint,
        avg_confidence decimal,
        max_confidence decimal,
        min_confidence decimal
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            tf.main_category,
            COUNT(*) as tag_count,
            SUM(tf.post_count) as total_usage,
            ROUND(AVG(tf.classification_confidence), 3) as avg_confidence,
            MAX(tf.classification_confidence) as max_confidence,
            MIN(tf.classification_confidence) as min_confidence
        FROM tags_final tf
        WHERE tf.main_category IS NOT NULL
        GROUP BY tf.main_category
        ORDER BY tag_count DESC;
    END;
    $$;
    """
    
    cursor.execute(category_stats_function)
    
    # 熱門標籤函數
    popular_tags_function = """
    CREATE OR REPLACE FUNCTION get_popular_tags(
        category_filter text DEFAULT NULL,
        min_usage int DEFAULT 1000,
        limit_count int DEFAULT 50
    )
    RETURNS TABLE (
        name varchar,
        main_category varchar,
        sub_category varchar,
        post_count int,
        classification_confidence decimal
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            tf.name,
            tf.main_category,
            tf.sub_category,
            tf.post_count,
            tf.classification_confidence
        FROM tags_final tf
        WHERE tf.post_count >= min_usage
        AND (category_filter IS NULL OR tf.main_category = category_filter)
        ORDER BY tf.post_count DESC
        LIMIT limit_count;
    END;
    $$;
    """
    
    cursor.execute(popular_tags_function)
    
    print("✅ 搜索函數創建完成")

def create_api_views(cursor):
    """創建 API 視圖"""
    print("📋 創建 API 視圖...")
    
    # 標籤摘要視圖
    summary_view = """
    CREATE OR REPLACE VIEW tag_summary AS
    SELECT 
        tf.name,
        tf.main_category,
        tf.sub_category,
        tf.classification_confidence,
        tf.post_count,
        tf.created_at,
        tf.updated_at,
        CASE 
            WHEN te.tag_name IS NOT NULL THEN true 
            ELSE false 
        END as has_embedding
    FROM tags_final tf
    LEFT JOIN tag_embeddings te ON tf.name = te.tag_name;
    """
    
    cursor.execute(summary_view)
    
    # 分類統計視圖
    category_view = """
    CREATE OR REPLACE VIEW category_overview AS
    SELECT 
        main_category,
        COUNT(*) as tag_count,
        SUM(post_count) as total_usage,
        ROUND(AVG(classification_confidence), 3) as avg_confidence,
        COUNT(CASE WHEN classification_confidence >= 0.9 THEN 1 END) as high_confidence_count,
        COUNT(CASE WHEN classification_confidence < 0.7 THEN 1 END) as low_confidence_count
    FROM tags_final
    WHERE main_category IS NOT NULL
    GROUP BY main_category
    ORDER BY tag_count DESC;
    """
    
    cursor.execute(category_view)
    
    print("✅ API 視圖創建完成")

def setup_rls_policies(cursor):
    """設置行級安全策略"""
    print("🔐 設置行級安全策略...")
    
    # 為 tags_final 表設置 RLS
    cursor.execute("ALTER TABLE tags_final ENABLE ROW LEVEL SECURITY;")
    
    # 讀取策略
    read_policy = """
    CREATE POLICY "Allow anonymous read access to tags_final" ON tags_final
    FOR SELECT USING (true);
    """
    
    cursor.execute(read_policy)
    
    # 為視圖設置 RLS
    cursor.execute("ALTER VIEW tag_summary SET (security_invoker = true);")
    cursor.execute("ALTER VIEW category_overview SET (security_invoker = true);")
    
    print("✅ 行級安全策略設置完成")

def create_api_documentation():
    """創建 API 文檔"""
    print("📚 創建 API 文檔...")
    
    api_docs = """# Prompt-Scribe Tags API 文檔

## 基礎 URL
```
{supabase_url}/rest/v1/
```

## 認證
所有請求都需要包含 API Key：
```
apikey: {supabase_anon_key}
Authorization: Bearer {supabase_anon_key}
```

## API 端點

### 1. 搜索標籤
```http
POST /rpc/search_tags_by_text
Content-Type: application/json

{{
  "search_query": "anime",
  "category_filter": "CHARACTER_RELATED",
  "min_confidence": 0.8,
  "limit_count": 20
}}
```

### 2. 獲取分類統計
```http
POST /rpc/get_category_statistics
Content-Type: application/json

{{}}
```

### 3. 獲取熱門標籤
```http
POST /rpc/get_popular_tags
Content-Type: application/json

{{
  "category_filter": "CHARACTER_RELATED",
  "min_usage": 1000,
  "limit_count": 50
}}
```

### 4. 向量相似度搜索
```http
POST /rpc/search_similar_tags
Content-Type: application/json

{{
  "query_embedding": [0.1, 0.2, ...],  // 1536 維向量
  "match_threshold": 0.7,
  "match_count": 10
}}
```

### 5. 直接查詢標籤
```http
GET /tag_summary?select=*&limit=20
GET /category_overview?select=*
GET /tags_final?select=*&name=eq.anime
```

## 響應格式
所有 API 返回 JSON 格式數據，包含：
- 標籤名稱
- 主分類
- 子分類
- 分類信心度
- 使用次數
- 相似度分數（適用於搜索）

## 錯誤處理
- 400: 請求參數錯誤
- 401: 認證失敗
- 404: 資源不存在
- 500: 服務器錯誤
"""
    
    # 獲取環境變數
    env = load_env()
    anon_key = os.getenv('SUPABASE_ANON_KEY', 'your-anon-key')
    
    # 替換模板變數
    api_docs = api_docs.format(
        supabase_url=env['supabase_url'],
        supabase_anon_key=anon_key
    )
    
    # 保存文檔
    with open('stage1/output/API_DOCUMENTATION.md', 'w', encoding='utf-8') as f:
        f.write(api_docs)
    
    print("✅ API 文檔已創建: stage1/output/API_DOCUMENTATION.md")

def test_api_endpoints():
    """測試 API 端點"""
    print("🧪 測試 API 端點...")
    
    env = load_env()
    url = env['supabase_url']
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not anon_key:
        print("⚠️ 缺少 SUPABASE_ANON_KEY，跳過 API 測試")
        return
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }
    
    # 測試基本查詢
    try:
        response = requests.get(f"{url}/rest/v1/tag_summary?select=*&limit=5", headers=headers)
        if response.status_code == 200:
            print("✅ 標籤摘要 API 測試成功")
        else:
            print(f"❌ 標籤摘要 API 測試失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ API 測試錯誤: {e}")
    
    # 測試分類統計
    try:
        response = requests.get(f"{url}/rest/v1/category_overview?select=*", headers=headers)
        if response.status_code == 200:
            print("✅ 分類統計 API 測試成功")
        else:
            print(f"❌ 分類統計 API 測試失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ API 測試錯誤: {e}")

def main():
    """主函數"""
    print("🚀 Supabase API 端點創建工具")
    print("=" * 50)
    
    # 載入環境變數
    env = load_env()
    
    # 連接到 Supabase
    print("🔗 連接到 Supabase...")
    conn = get_supabase_connection()
    if not conn:
        sys.exit(1)
    
    try:
        cursor = conn.cursor()
        
        # 創建搜索函數
        create_search_functions(cursor)
        
        # 創建 API 視圖
        create_api_views(cursor)
        
        # 設置安全策略
        setup_rls_policies(cursor)
        
        # 提交所有更改
        conn.commit()
        
        # 創建 API 文檔
        create_api_documentation()
        
        # 測試 API 端點
        test_api_endpoints()
        
        print("\n🎉 API 端點創建完成！")
        print("📚 API 文檔已生成: stage1/output/API_DOCUMENTATION.md")
        print("🔗 您現在可以使用 Supabase 的自動生成的 REST API")
        
    except Exception as e:
        print(f"❌ 創建過程中發生錯誤: {e}")
        conn.rollback()
        sys.exit(1)
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
