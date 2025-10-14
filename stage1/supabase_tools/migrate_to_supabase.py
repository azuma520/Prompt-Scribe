#!/usr/bin/env python3
"""
SQLite 到 Supabase PostgreSQL 遷移工具
將 tags.db 數據遷移到 Supabase
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
import requests

def load_env():
    """載入環境變數"""
    load_dotenv()
    
    return {
        'supabase_url': os.getenv('SUPABASE_URL'),
        'supabase_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
        'db_path': 'stage1/output/tags.db'
    }

def get_supabase_connection():
    """獲取 Supabase PostgreSQL 連接"""
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    # 從 Supabase URL 提取連接信息
    # https://xxx.supabase.co -> xxx.supabase.co
    host = url.replace('https://', '').replace('http://', '')
    
    # 構建 PostgreSQL 連接字串
    conn_string = f"host={host} port=5432 dbname=postgres user=postgres password={service_key} sslmode=require"
    
    try:
        conn = psycopg2.connect(conn_string)
        return conn
    except Exception as e:
        print(f"X 無法連接到 Supabase: {e}")
        return None

def create_tables(cursor):
    """創建 PostgreSQL 表結構"""
    print("📋 創建 PostgreSQL 表結構...")
    
    # 創建 tags_final 表
    create_tags_table = """
    CREATE TABLE IF NOT EXISTS tags_final (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        main_category VARCHAR(100),
        sub_category VARCHAR(100),
        classification_source VARCHAR(100),
        classification_confidence DECIMAL(5,3),
        post_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cursor.execute(create_tags_table)
    
    # 創建索引
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags_final(name);",
        "CREATE INDEX IF NOT EXISTS idx_tags_main_category ON tags_final(main_category);",
        "CREATE INDEX IF NOT EXISTS idx_tags_sub_category ON tags_final(sub_category);",
        "CREATE INDEX IF NOT EXISTS idx_tags_confidence ON tags_final(classification_confidence);",
        "CREATE INDEX IF NOT EXISTS idx_tags_post_count ON tags_final(post_count);"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print("✅ 表結構創建完成")

def migrate_data(sqlite_path, cursor):
    """遷移數據"""
    print(f"📦 開始遷移數據從 {sqlite_path}...")
    
    # 連接到 SQLite 數據庫
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # 獲取所有數據
        sqlite_cursor.execute("""
            SELECT name, main_category, sub_category, classification_source, 
                   classification_confidence, post_count
            FROM tags_final
            ORDER BY name
        """)
        
        rows = sqlite_cursor.fetchall()
        total_rows = len(rows)
        
        print(f"📊 找到 {total_rows:,} 筆記錄需要遷移")
        
        if total_rows == 0:
            print("⚠️ 沒有數據需要遷移")
            return
        
        # 分批插入數據
        batch_size = 1000
        inserted_count = 0
        error_count = 0
        
        for i in range(0, total_rows, batch_size):
            batch = rows[i:i + batch_size]
            
            try:
                # 使用 execute_values 進行批量插入
                execute_values(
                    cursor,
                    """
                    INSERT INTO tags_final (name, main_category, sub_category, 
                                          classification_source, classification_confidence, post_count)
                    VALUES %s
                    ON CONFLICT (name) DO UPDATE SET
                        main_category = EXCLUDED.main_category,
                        sub_category = EXCLUDED.sub_category,
                        classification_source = EXCLUDED.classification_source,
                        classification_confidence = EXCLUDED.classification_confidence,
                        post_count = EXCLUDED.post_count,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    batch,
                    template=None,
                    page_size=1000
                )
                
                inserted_count += len(batch)
                print(f"✅ 已遷移 {inserted_count:,}/{total_rows:,} 筆記錄 ({inserted_count/total_rows*100:.1f}%)")
                
            except Exception as e:
                print(f"❌ 批次插入錯誤: {e}")
                error_count += len(batch)
        
        print(f"\n📊 遷移完成:")
        print(f"  ✅ 成功: {inserted_count:,} 筆")
        print(f"  ❌ 失敗: {error_count:,} 筆")
        
    finally:
        sqlite_conn.close()

def verify_migration(cursor):
    """驗證遷移結果"""
    print("\n🔍 驗證遷移結果...")
    
    # 檢查總記錄數
    cursor.execute("SELECT COUNT(*) FROM tags_final")
    total_count = cursor.fetchone()[0]
    print(f"📊 總記錄數: {total_count:,}")
    
    # 檢查分類統計
    cursor.execute("""
        SELECT main_category, COUNT(*) as count, 
               ROUND(AVG(classification_confidence), 3) as avg_confidence
        FROM tags_final 
        WHERE main_category IS NOT NULL
        GROUP BY main_category 
        ORDER BY count DESC
    """)
    
    categories = cursor.fetchall()
    print(f"\n📈 主分類統計:")
    for category, count, avg_conf in categories:
        print(f"  {category:25} {count:6,} 筆 (平均信心度: {avg_conf})")
    
    # 檢查信心度分佈
    cursor.execute("""
        SELECT 
            CASE 
                WHEN classification_confidence >= 0.9 THEN '高信心度 (≥0.9)'
                WHEN classification_confidence >= 0.8 THEN '中高信心度 (0.8-0.9)'
                WHEN classification_confidence >= 0.7 THEN '中等信心度 (0.7-0.8)'
                ELSE '低信心度 (<0.7)'
            END as confidence_range,
            COUNT(*) as count
        FROM tags_final 
        WHERE classification_confidence IS NOT NULL
        GROUP BY 
            CASE 
                WHEN classification_confidence >= 0.9 THEN '高信心度 (≥0.9)'
                WHEN classification_confidence >= 0.8 THEN '中高信心度 (0.8-0.9)'
                WHEN classification_confidence >= 0.7 THEN '中等信心度 (0.7-0.8)'
                ELSE '低信心度 (<0.7)'
            END
        ORDER BY count DESC
    """)
    
    confidence_stats = cursor.fetchall()
    print(f"\n📊 信心度分佈:")
    for range_name, count in confidence_stats:
        print(f"  {range_name:20} {count:6,} 筆")

def main():
    """主函數"""
    print("SQLite 到 Supabase 遷移工具")
    print("=" * 50)
    
    # 載入環境變數
    env = load_env()
    
    # 檢查 SQLite 文件是否存在
    if not os.path.exists(env['db_path']):
        print(f"X 找不到 SQLite 文件: {env['db_path']}")
        sys.exit(1)
    
    print(f"V 找到 SQLite 文件: {env['db_path']}")
    
    # 連接到 Supabase
    print("連接到 Supabase...")
    conn = get_supabase_connection()
    if not conn:
        sys.exit(1)
    
    try:
        cursor = conn.cursor()
        
        # 創建表結構
        create_tables(cursor)
        
        # 遷移數據
        migrate_data(env['db_path'], cursor)
        
        # 提交事務
        conn.commit()
        
        # 驗證遷移結果
        verify_migration(cursor)
        
        print("\n遷移完成！")
        print("數據已成功遷移到 Supabase PostgreSQL")
        
    except Exception as e:
        print(f"X 遷移過程中發生錯誤: {e}")
        conn.rollback()
        sys.exit(1)
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
