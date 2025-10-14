#!/usr/bin/env python3
"""
Supabase 向量資料庫設置工具
啟用 pgvector 擴展並創建向量表
"""

import os
import sys
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
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

def enable_pgvector_extension(cursor):
    """啟用 pgvector 擴展"""
    print("🔧 啟用 pgvector 擴展...")
    
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅ pgvector 擴展已啟用")
        return True
    except Exception as e:
        print(f"❌ 啟用 pgvector 擴展失敗: {e}")
        return False

def create_vector_tables(cursor):
    """創建向量表"""
    print("📋 創建向量表結構...")
    
    # 創建標籤嵌入表
    create_embeddings_table = """
    CREATE TABLE IF NOT EXISTS tag_embeddings (
        id SERIAL PRIMARY KEY,
        tag_name VARCHAR(255) UNIQUE NOT NULL,
        embedding vector(1536),  -- OpenAI ada-002 嵌入維度
        model_name VARCHAR(100) DEFAULT 'text-embedding-ada-002',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tag_name) REFERENCES tags_final(name) ON DELETE CASCADE
    );
    """
    
    cursor.execute(create_embeddings_table)
    
    # 創建向量索引
    vector_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_tag_embeddings_vector ON tag_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);",
        "CREATE INDEX IF NOT EXISTS idx_tag_embeddings_tag_name ON tag_embeddings(tag_name);"
    ]
    
    for index_sql in vector_indexes:
        try:
            cursor.execute(index_sql)
        except Exception as e:
            print(f"⚠️ 創建索引警告: {e}")
    
    print("✅ 向量表結構創建完成")

def create_vector_functions(cursor):
    """創建向量搜索函數"""
    print("🔧 創建向量搜索函數...")
    
    # 創建相似度搜索函數
    similarity_search_function = """
    CREATE OR REPLACE FUNCTION search_similar_tags(
        query_embedding vector(1536),
        match_threshold float DEFAULT 0.5,
        match_count int DEFAULT 10
    )
    RETURNS TABLE (
        tag_name varchar,
        main_category varchar,
        sub_category varchar,
        similarity float,
        post_count int
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            te.tag_name,
            tf.main_category,
            tf.sub_category,
            1 - (te.embedding <=> query_embedding) as similarity,
            tf.post_count
        FROM tag_embeddings te
        JOIN tags_final tf ON te.tag_name = tf.name
        WHERE 1 - (te.embedding <=> query_embedding) > match_threshold
        ORDER BY te.embedding <=> query_embedding
        LIMIT match_count;
    END;
    $$;
    """
    
    cursor.execute(similarity_search_function)
    print("✅ 向量搜索函數創建完成")

def create_embedding_batch_function(cursor):
    """創建批量嵌入處理函數"""
    print("🔧 創建批量嵌入處理函數...")
    
    batch_embedding_function = """
    CREATE OR REPLACE FUNCTION get_tags_for_embedding(
        batch_size int DEFAULT 100,
        offset_val int DEFAULT 0
    )
    RETURNS TABLE (
        tag_name varchar,
        main_category varchar,
        sub_category varchar,
        post_count int
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            tf.name,
            tf.main_category,
            tf.sub_category,
            tf.post_count
        FROM tags_final tf
        LEFT JOIN tag_embeddings te ON tf.name = te.tag_name
        WHERE te.tag_name IS NULL  -- 只返回還沒有嵌入的標籤
        ORDER BY tf.post_count DESC
        LIMIT batch_size
        OFFSET offset_val;
    END;
    $$;
    """
    
    cursor.execute(batch_embedding_function)
    print("✅ 批量嵌入處理函數創建完成")

def create_rls_policies(cursor):
    """創建行級安全策略"""
    print("🔐 設置行級安全策略...")
    
    # 啟用 RLS
    cursor.execute("ALTER TABLE tag_embeddings ENABLE ROW LEVEL SECURITY;")
    
    # 創建讀取策略（允許匿名用戶讀取）
    read_policy = """
    CREATE POLICY "Allow anonymous read access to tag_embeddings" ON tag_embeddings
    FOR SELECT USING (true);
    """
    
    cursor.execute(read_policy)
    
    # 創建寫入策略（需要服務角色）
    write_policy = """
    CREATE POLICY "Allow service role full access to tag_embeddings" ON tag_embeddings
    FOR ALL USING (auth.role() = 'service_role');
    """
    
    cursor.execute(write_policy)
    
    print("✅ 行級安全策略設置完成")

def verify_vector_setup(cursor):
    """驗證向量設置"""
    print("\n🔍 驗證向量設置...")
    
    # 檢查 pgvector 擴展
    cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
    vector_ext = cursor.fetchone()
    
    if vector_ext:
        print("✅ pgvector 擴展已安裝")
    else:
        print("❌ pgvector 擴展未安裝")
        return False
    
    # 檢查向量表
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'tag_embeddings';
    """)
    
    if cursor.fetchone():
        print("✅ tag_embeddings 表已創建")
    else:
        print("❌ tag_embeddings 表未創建")
        return False
    
    # 檢查函數
    cursor.execute("""
        SELECT routine_name 
        FROM information_schema.routines 
        WHERE routine_schema = 'public' 
        AND routine_name IN ('search_similar_tags', 'get_tags_for_embedding');
    """)
    
    functions = cursor.fetchall()
    if len(functions) >= 2:
        print("✅ 向量搜索函數已創建")
    else:
        print("❌ 向量搜索函數未完全創建")
        return False
    
    print("\n🎉 向量資料庫設置驗證完成！")
    return True

def main():
    """主函數"""
    print("🚀 Supabase 向量資料庫設置工具")
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
        
        # 啟用 pgvector 擴展
        if not enable_pgvector_extension(cursor):
            sys.exit(1)
        
        # 創建向量表
        create_vector_tables(cursor)
        
        # 創建向量函數
        create_vector_functions(cursor)
        
        # 創建批量嵌入函數
        create_embedding_batch_function(cursor)
        
        # 設置安全策略
        create_rls_policies(cursor)
        
        # 提交所有更改
        conn.commit()
        
        # 驗證設置
        if verify_vector_setup(cursor):
            print("\n🎉 向量資料庫設置完成！")
            print("現在可以開始生成標籤嵌入向量了")
        else:
            print("\n❌ 向量設置驗證失敗")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ 設置過程中發生錯誤: {e}")
        conn.rollback()
        sys.exit(1)
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
