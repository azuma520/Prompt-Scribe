#!/usr/bin/env python3
"""
簡單的 Ultra Popular 標籤處理腳本
使用 Supabase MCP 直接處理剩餘的超熱門標籤
"""

import os
import asyncio
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import AsyncOpenAI

async def process_ultra_popular_tags():
    """處理超熱門標籤"""
    print("=" * 70)
    print("Ultra Popular Tags Processing")
    print("=" * 70)
    
    # 載入環境變數 (如果 .env 檔案存在)
    try:
        load_dotenv()
    except Exception:
        # 如果 .env 檔案不存在或載入失敗，使用系統環境變數
        pass
    
    # 從環境變數獲取配置
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY, OPENAI_API_KEY]):
        print("ERROR: Missing environment variables")
        print("Please ensure .env file exists and contains all required variables")
        return False
    
    # 初始化客戶端
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    try:
        # 獲取剩餘的超熱門標籤
        print("Getting remaining ultra popular tags...")
        response = supabase.table('tags_final').select(
            'id, name, post_count'
        ).gte('post_count', 100000).is_('embedding', 'null').limit(100).execute()
        
        if not response.data:
            print("No remaining ultra popular tags found!")
            return True
        
        tags = response.data
        print(f"Found {len(tags)} remaining ultra popular tags")
        
        # 處理標籤
        processed_count = 0
        failed_count = 0
        
        for i, tag in enumerate(tags, 1):
            print(f"Processing {i}/{len(tags)}: {tag['name']} ({tag['post_count']:,})")
            
            try:
                # 生成嵌入向量
                embedding_response = await openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[tag['name']]
                )
                
                embedding = embedding_response.data[0].embedding
                
                # 更新資料庫
                supabase.table('tags_final').update({
                    "embedding": embedding
                }).eq('id', tag['id']).execute()
                
                processed_count += 1
                print(f"  SUCCESS: Updated {tag['name']}")
                
                # 簡單的速率限制
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_count += 1
                print(f"  ERROR: Failed to process {tag['name']}: {e}")
        
        print(f"\nProcessing completed!")
        print(f"Processed: {processed_count}")
        print(f"Failed: {failed_count}")
        print(f"Success rate: {(processed_count/(processed_count+failed_count))*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Processing failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(process_ultra_popular_tags())
    
    if success:
        print("\nSUCCESS: Ultra Popular processing completed!")
        print("TIP: Run check_status.py to see updated progress")
    else:
        print("\nERROR: Processing failed")
