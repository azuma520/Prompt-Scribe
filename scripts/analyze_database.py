#!/usr/bin/env python3
"""
分析資料庫結構和標籤分佈
為嵌入生成計畫提供數據基礎
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

def analyze_database():
    """分析資料庫結構和標籤分佈"""
    print("=" * 60)
    print("Database Analysis for Embedding Generation Plan")
    print("=" * 60)
    
    # 載入環境變數
    load_dotenv()
    
    # 建立 Supabase 客戶端
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("ERROR: Missing environment variables")
        return False
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    try:
        # 1. 檢查表結構
        print("\n1. Table Structure Analysis")
        print("-" * 40)
        
        sample_response = supabase.table('tags_final').select('*').limit(1).execute()
        if sample_response.data:
            columns = list(sample_response.data[0].keys())
            print(f"Available columns: {columns}")
            
            # 檢查關鍵欄位
            key_fields = ['id', 'name', 'post_count', 'main_category', 'sub_category', 'embedding']
            missing_fields = [field for field in key_fields if field not in columns]
            if missing_fields:
                print(f"WARNING: Missing fields: {missing_fields}")
            else:
                print("SUCCESS: All required fields present")
        else:
            print("ERROR: No data found in tags_final table")
            return False
        
        # 2. 分析標籤分佈
        print("\n2. Tag Distribution Analysis")
        print("-" * 40)
        
        # 獲取所有標籤的使用次數
        all_tags_response = supabase.table('tags_final').select('post_count').execute()
        if not all_tags_response.data:
            print("ERROR: Unable to fetch tag data")
            return False
        
        counts = [tag['post_count'] for tag in all_tags_response.data]
        total_tags = len(counts)
        
        print(f"Total tags in database: {total_tags}")
        print(f"Max usage count: {max(counts):,}")
        print(f"Min usage count: {min(counts):,}")
        print(f"Average usage count: {sum(counts)/len(counts):,.0f}")
        
        # 3. 分層分析
        print("\n3. Tier Analysis")
        print("-" * 40)
        
        tiers = {
            "Tier 1 (Ultra Popular)": [c for c in counts if c >= 100000],
            "Tier 2 (Very Popular)": [c for c in counts if c >= 50000],
            "Tier 3 (Popular)": [c for c in counts if c >= 10000],
            "Tier 4 (Common)": [c for c in counts if c >= 1000],
            "Tier 5 (Rare)": [c for c in counts if c >= 100],
            "Tier 6 (Very Rare)": [c for c in counts if c < 100]
        }
        
        for tier_name, tier_counts in tiers.items():
            count = len(tier_counts)
            percentage = (count / total_tags) * 100
            print(f"{tier_name}: {count:,} tags ({percentage:.1f}%)")
        
        # 4. 檢查 embedding 欄位狀態
        print("\n4. Embedding Field Status")
        print("-" * 40)
        
        embedding_response = supabase.table('tags_final').select('id, name, embedding').limit(10).execute()
        if embedding_response.data:
            empty_embeddings = sum(1 for tag in embedding_response.data if tag['embedding'] is None)
            total_sample = len(embedding_response.data)
            print(f"Sample size: {total_sample}")
            print(f"Empty embeddings: {empty_embeddings}")
            print(f"Filled embeddings: {total_sample - empty_embeddings}")
            
            if empty_embeddings == total_sample:
                print("STATUS: All embeddings are empty - ready for generation")
            elif empty_embeddings == 0:
                print("STATUS: All embeddings are filled - no generation needed")
            else:
                print("STATUS: Partial embeddings - incremental generation needed")
        
        # 5. 建議實施策略
        print("\n5. Recommended Implementation Strategy")
        print("-" * 40)
        
        # 計算建議的批次大小
        if total_tags <= 1000:
            batch_size = 50
            strategy = "Small dataset - single batch"
        elif total_tags <= 10000:
            batch_size = 100
            strategy = "Medium dataset - multiple batches"
        else:
            batch_size = 200
            strategy = "Large dataset - staged approach"
        
        print(f"Recommended batch size: {batch_size}")
        print(f"Strategy: {strategy}")
        
        # 估算成本
        estimated_cost = (total_tags * 0.0001) / 1000  # 假設每個標籤 0.0001 美元
        print(f"Estimated cost: ${estimated_cost:.2f}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Database analysis failed: {e}")
        return False

if __name__ == "__main__":
    success = analyze_database()
    if success:
        print("\n" + "=" * 60)
        print("Analysis completed successfully!")
        print("Ready to proceed with embedding generation plan.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Analysis failed. Please check database connection.")
        print("=" * 60)
        sys.exit(1)
