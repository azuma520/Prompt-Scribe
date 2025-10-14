import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
import time

# 載入環境變數
load_dotenv('stage1/.env')

def migrate_data_batch(batch_size=1000):
    """批量遷移數據從 SQLite 到 Supabase"""
    
    # SQLite 連接
    sqlite_conn = sqlite3.connect('stage1/output/tags.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Supabase 連接
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("錯誤: 缺少 Supabase 環境變數")
        return
    
    # 從 URL 提取連接信息
    host = supabase_url.replace('https://', '').replace('.supabase.co', '')
    
    try:
        # 連接 Supabase PostgreSQL
        conn = psycopg2.connect(
            host=f"db.{host}.supabase.co",
            database="postgres",
            user="postgres",
            password=supabase_key,
            port=5432,
            sslmode="require"
        )
        cursor = conn.cursor()
        
        # 獲取總記錄數
        sqlite_cursor.execute('SELECT COUNT(*) FROM tags_final')
        total_records = sqlite_cursor.fetchone()[0]
        print(f'總記錄數: {total_records:,}')
        
        # 檢查已遷移的記錄數
        cursor.execute('SELECT COUNT(*) FROM tags_final')
        migrated_count = cursor.fetchone()[0]
        print(f'已遷移記錄數: {migrated_count:,}')
        
        if migrated_count >= total_records:
            print("所有數據已遷移完成！")
            return
        
        # 批量遷移
        offset = migrated_count
        batch_num = 1
        
        while offset < total_records:
            print(f'處理批次 {batch_num} (記錄 {offset+1} - {min(offset+batch_size, total_records)})')
            
            # 從 SQLite 讀取數據
            sqlite_cursor.execute('''
                SELECT name, main_category, sub_category, classification_source, 
                       classification_confidence, post_count
                FROM tags_final
                LIMIT ? OFFSET ?
            ''', (batch_size, offset))
            
            batch_data = sqlite_cursor.fetchall()
            
            if not batch_data:
                break
            
            # 插入到 Supabase
            insert_query = '''
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
            '''
            
            execute_values(cursor, insert_query, batch_data)
            conn.commit()
            
            print(f'  批次 {batch_num} 完成: {len(batch_data)} 筆記錄')
            
            offset += batch_size
            batch_num += 1
            
            # 短暫暫停避免過載
            time.sleep(0.1)
        
        print("數據遷移完成！")
        
        # 最終統計
        cursor.execute('SELECT COUNT(*) FROM tags_final')
        final_count = cursor.fetchone()[0]
        print(f'最終記錄數: {final_count:,}')
        
    except Exception as e:
        print(f"錯誤: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
        sqlite_conn.close()

if __name__ == '__main__':
    migrate_data_batch()
