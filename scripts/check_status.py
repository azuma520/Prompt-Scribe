#!/usr/bin/env python3
"""
簡單的嵌入進度檢查腳本
檢查當前嵌入生成的狀況
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def check_current_status():
    """檢查當前狀況"""
    print("=" * 60)
    print("Current Embedding Status Check")
    print("=" * 60)
    
    # 載入環境變數
    load_dotenv()
    
    # 檢查環境變數
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("ERROR: Missing environment variables")
        return False
    
    # 建立 Supabase 客戶端
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    try:
        # 檢查總數
        total_response = supabase.table('tags_final').select('id', count='exact').execute()
        total_tags = total_response.count
        
        # 檢查已嵌入的數量
        embedded_response = supabase.table('tags_final').select('id', count='exact').not_.is_('embedding', 'null').execute()
        embedded_count = embedded_response.count
        
        print(f"Total tags: {total_tags:,}")
        print(f"Embedded tags: {embedded_count:,}")
        print(f"Progress: {(embedded_count/total_tags)*100:.2f}%")
        
        # 檢查最近處理的標籤
        print(f"\nRecent embedded tags (top 5 by usage):")
        recent_response = supabase.table('tags_final').select(
            'name, post_count'
        ).not_.is_('embedding', 'null').order('post_count', desc=True).limit(5).execute()
        
        for i, tag in enumerate(recent_response.data, 1):
            print(f"  {i}. {tag['name']} - {tag['post_count']:,}")
        
        # 檢查 Ultra Popular 階段狀況
        ultra_popular_response = supabase.table('tags_final').select(
            'id', count='exact'
        ).gte('post_count', 100000).execute()
        ultra_total = ultra_popular_response.count
        
        ultra_embedded_response = supabase.table('tags_final').select(
            'id', count='exact'
        ).gte('post_count', 100000).not_.is_('embedding', 'null').execute()
        ultra_embedded = ultra_embedded_response.count
        
        print(f"\nUltra Popular Stage (>=100k):")
        print(f"  Total: {ultra_total:,}")
        print(f"  Embedded: {ultra_embedded:,}")
        print(f"  Remaining: {ultra_total - ultra_embedded:,}")
        print(f"  Progress: {(ultra_embedded/ultra_total)*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Check failed: {e}")
        return False

if __name__ == "__main__":
    check_current_status()
