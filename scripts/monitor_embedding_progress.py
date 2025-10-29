#!/usr/bin/env python3
"""
嵌入生成進度監控腳本
實時監控嵌入生成的進度和狀態
"""

import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client

def monitor_embedding_progress():
    """監控嵌入生成進度"""
    print("=" * 60)
    print("Embedding Generation Progress Monitor")
    print("=" * 60)
    
    # 載入環境變數
    load_dotenv()
    
    # 檢查環境變數
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("ERROR: Missing environment variables. Please run setup_env_local.ps1 first.")
        return False
    
    # 建立 Supabase 客戶端
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    try:
        # 獲取總標籤數
        total_response = supabase.table('tags_final').select('id', count='exact').execute()
        total_tags = total_response.count
        
        # 獲取已生成嵌入的標籤數
        embedded_response = supabase.table('tags_final').select('id', count='exact').not_.is_('embedding', 'null').execute()
        embedded_tags = embedded_response.count
        
        # 計算進度
        progress_percentage = (embedded_tags / total_tags) * 100
        
        print(f"Total tags: {total_tags:,}")
        print(f"Embedded tags: {embedded_tags:,}")
        print(f"Progress: {progress_percentage:.2f}%")
        
        # 分階段統計
        print(f"\nStage breakdown:")
        
        stages = [
            ("Ultra Popular (>=100k)", 100000),
            ("Very Popular (>=50k)", 50000),
            ("Popular (>=10k)", 10000),
            ("Common (>=1k)", 1000)
        ]
        
        for stage_name, min_count in stages:
            # 該階段的總標籤數
            stage_total_response = supabase.table('tags_final').select('id', count='exact').gte('post_count', min_count).execute()
            stage_total = stage_total_response.count
            
            # 該階段已嵌入的標籤數
            stage_embedded_response = supabase.table('tags_final').select('id', count='exact').gte('post_count', min_count).not_.is_('embedding', 'null').execute()
            stage_embedded = stage_embedded_response.count
            
            if stage_total > 0:
                stage_progress = (stage_embedded / stage_total) * 100
                print(f"  {stage_name}: {stage_embedded:,}/{stage_total:,} ({stage_progress:.1f}%)")
            else:
                print(f"  {stage_name}: 0/0 (N/A)")
        
        # 估算剩餘時間
        if embedded_tags > 0:
            # 假設平均處理速度（基於測試結果）
            avg_time_per_tag = 0.21  # 秒/標籤
            remaining_tags = total_tags - embedded_tags
            estimated_remaining_time = remaining_tags * avg_time_per_tag
            
            hours = estimated_remaining_time // 3600
            minutes = (estimated_remaining_time % 3600) // 60
            
            print(f"\nEstimated remaining time: {hours:.0f}h {minutes:.0f}m")
        
        # 成本估算
        estimated_cost = embedded_tags * 0.00002  # $0.00002 per tag
        print(f"Current cost: ${estimated_cost:.2f}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Monitoring failed: {e}")
        return False

if __name__ == "__main__":
    monitor_embedding_progress()
