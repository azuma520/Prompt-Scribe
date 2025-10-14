#!/usr/bin/env python3
"""
標籤嵌入向量生成工具
為標籤生成 OpenAI 嵌入向量並存儲到 Supabase
"""

import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
import requests
import openai

def load_env():
    """載入環境變數"""
    load_dotenv()
    
    # 設置 OpenAI API Key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    return {
        'supabase_url': os.getenv('SUPABASE_URL'),
        'supabase_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
        'openai_api_key': os.getenv('OPENAI_API_KEY')
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

def get_tags_for_embedding(cursor, batch_size=50, offset=0):
    """獲取需要生成嵌入的標籤"""
    cursor.execute("""
        SELECT tag_name, main_category, sub_category, post_count
        FROM get_tags_for_embedding(%s, %s)
    """, (batch_size, offset))
    
    return cursor.fetchall()

def generate_embedding(text, model="text-embedding-ada-002"):
    """生成標籤的嵌入向量"""
    try:
        response = openai.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ 生成嵌入失敗 '{text}': {e}")
        return None

def batch_generate_embeddings(tags, batch_size=50):
    """批量生成嵌入向量"""
    embeddings = []
    
    for i, (tag_name, main_category, sub_category, post_count) in enumerate(tags):
        # 構建標籤描述文本
        tag_text = tag_name
        if main_category:
            tag_text += f" ({main_category}"
            if sub_category:
                tag_text += f"/{sub_category}"
            tag_text += ")"
        
        print(f"🔄 生成嵌入 {i+1}/{len(tags)}: {tag_text}")
        
        # 生成嵌入
        embedding = generate_embedding(tag_text)
        if embedding:
            embeddings.append((tag_name, embedding, "text-embedding-ada-002"))
        
        # 控制 API 調用頻率
        time.sleep(0.1)
    
    return embeddings

def save_embeddings_to_db(cursor, embeddings):
    """將嵌入向量保存到資料庫"""
    if not embeddings:
        return 0
    
    try:
        execute_values(
            cursor,
            """
            INSERT INTO tag_embeddings (tag_name, embedding, model_name)
            VALUES %s
            ON CONFLICT (tag_name) DO UPDATE SET
                embedding = EXCLUDED.embedding,
                model_name = EXCLUDED.model_name,
                updated_at = CURRENT_TIMESTAMP
            """,
            embeddings,
            template=None,
            page_size=100
        )
        
        return len(embeddings)
        
    except Exception as e:
        print(f"❌ 保存嵌入向量失敗: {e}")
        return 0

def get_embedding_stats(cursor):
    """獲取嵌入統計信息"""
    cursor.execute("SELECT COUNT(*) FROM tag_embeddings")
    total_embeddings = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tags_final")
    total_tags = cursor.fetchone()[0]
    
    coverage = (total_embeddings / total_tags * 100) if total_tags > 0 else 0
    
    return total_embeddings, total_tags, coverage

def main():
    """主函數"""
    print("🚀 標籤嵌入向量生成工具")
    print("=" * 50)
    
    # 載入環境變數
    env = load_env()
    
    if not env['openai_api_key']:
        print("❌ 缺少 OpenAI API Key")
        sys.exit(1)
    
    # 連接到 Supabase
    print("🔗 連接到 Supabase...")
    conn = get_supabase_connection()
    if not conn:
        sys.exit(1)
    
    try:
        cursor = conn.cursor()
        
        # 獲取統計信息
        total_embeddings, total_tags, coverage = get_embedding_stats(cursor)
        print(f"📊 當前嵌入覆蓋率: {total_embeddings:,}/{total_tags:,} ({coverage:.1f}%)")
        
        if coverage >= 100:
            print("🎉 所有標籤都已有嵌入向量！")
            return
        
        # 批量處理標籤
        batch_size = 50
        offset = 0
        total_processed = 0
        
        while True:
            print(f"\n📦 處理批次 (偏移: {offset}, 大小: {batch_size})")
            
            # 獲取需要處理的標籤
            tags = get_tags_for_embedding(cursor, batch_size, offset)
            
            if not tags:
                print("✅ 沒有更多標籤需要處理")
                break
            
            print(f"🔄 找到 {len(tags)} 個標籤需要處理")
            
            # 生成嵌入向量
            embeddings = batch_generate_embeddings(tags, batch_size)
            
            if embeddings:
                # 保存到資料庫
                saved_count = save_embeddings_to_db(cursor, embeddings)
                conn.commit()
                
                total_processed += saved_count
                print(f"✅ 已保存 {saved_count} 個嵌入向量")
                
                # 更新統計信息
                total_embeddings, total_tags, coverage = get_embedding_stats(cursor)
                print(f"📊 進度: {total_embeddings:,}/{total_tags:,} ({coverage:.1f}%)")
                
            else:
                print("❌ 沒有成功生成任何嵌入向量")
            
            offset += batch_size
            
            # 檢查是否完成
            if len(tags) < batch_size:
                break
        
        print(f"\n🎉 嵌入生成完成！")
        print(f"📊 總計處理: {total_processed} 個標籤")
        print(f"📊 最終覆蓋率: {total_embeddings:,}/{total_tags:,} ({coverage:.1f}%)")
        
    except Exception as e:
        print(f"❌ 處理過程中發生錯誤: {e}")
        conn.rollback()
        sys.exit(1)
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
