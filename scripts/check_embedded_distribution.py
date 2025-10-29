#!/usr/bin/env python3
"""
檢查已嵌入標籤的分佈
確認是否按照分階段策略執行
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def check_embedded_tags_distribution():
    """檢查已嵌入標籤的分佈"""
    print("=" * 60)
    print("Checking Embedded Tags Distribution")
    print("=" * 60)
    
    # 載入環境變數
    load_dotenv()
    
    # 建立 Supabase 客戶端
    supabase: Client = create_client(
        os.environ['SUPABASE_URL'],
        os.environ['SUPABASE_SERVICE_KEY']
    )
    
    try:
        # 獲取已嵌入的標籤，按使用次數排序
        response = supabase.table('tags_final').select(
            'name, post_count, main_category'
        ).not_.is_('embedding', 'null').order('post_count', desc=True).limit(20).execute()
        
        if not response.data:
            print("No embedded tags found")
            return
        
        print("Top 20 embedded tags (by usage count):")
        print("-" * 60)
        
        for i, tag in enumerate(response.data, 1):
            print(f"{i:2d}. {tag['name']:<30} {tag['post_count']:>10,} ({tag['main_category']})")
        
        # 檢查分層分佈
        print(f"\nStage distribution analysis:")
        print("-" * 60)
        
        stages = [
            ("Ultra Popular (>=100k)", 100000),
            ("Very Popular (>=50k)", 50000),
            ("Popular (>=10k)", 10000),
            ("Common (>=1k)", 1000)
        ]
        
        for stage_name, min_count in stages:
            count_response = supabase.table('tags_final').select(
                'id', count='exact'
            ).gte('post_count', min_count).not_.is_('embedding', 'null').execute()
            
            print(f"{stage_name}: {count_response.count} embedded")
        
        # 檢查是否有低價值標籤被處理
        low_value_response = supabase.table('tags_final').select(
            'name, post_count'
        ).lt('post_count', 1000).not_.is_('embedding', 'null').limit(5).execute()
        
        if low_value_response.data:
            print(f"\nWARNING: Found low-value tags with embeddings:")
            for tag in low_value_response.data:
                print(f"  - {tag['name']} ({tag['post_count']:,})")
        else:
            print(f"\nSUCCESS: No low-value tags (<1k) have embeddings")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Check failed: {e}")
        return False

if __name__ == "__main__":
    check_embedded_tags_distribution()
