#!/usr/bin/env python3
"""
Ultra Popular 標籤嵌入生成器
專注完成使用次數 >= 100,000 的超熱門標籤
完成後準備進行語義搜尋測試
"""

import asyncio
import time
from typing import List, Dict
from openai import AsyncOpenAI
from supabase import create_client, Client
import os
from dotenv import load_dotenv

class UltraPopularEmbeddingGenerator:
    """超熱門標籤嵌入生成器"""
    
    def __init__(self):
        # 載入環境變數 (如果 .env 檔案存在)
        try:
            load_dotenv()
        except Exception:
            # 如果 .env 檔案不存在或載入失敗，使用系統環境變數
            pass
        
        # 檢查環境變數，如果沒有則使用預設值
        SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://fumuvmbhmmzkenizksyq.supabase.co')
        SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1bXV2bWJobW16a2VuaXprc3lxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDMxODY5MCwiZXhwIjoyMDc1ODk0NjkwfQ.WKS2py7YkKgyNdpegCYL8GHEVDGtcjtgsJEf1MJBdSI')
        OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
        
        if not OPENAI_API_KEY:
            raise ValueError("Missing OPENAI_API_KEY. Please run setup_env_local.ps1 first.")
        
        # 初始化客戶端
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # 配置
        self.model = "text-embedding-3-small"
        self.batch_size = 50
        self.max_retries = 3
        self.timeout = 30
        self.rate_limit_delay = 0.1
        
        # 統計
        self.stats = {
            "total_tags": 0,
            "processed": 0,
            "failed": 0,
            "start_time": None,
            "total_cost": 0.0
        }
    
    async def complete_ultra_popular_stage(self):
        """完成超熱門標籤階段"""
        print("=" * 70)
        print("Ultra Popular Tags Embedding Generation")
        print("Focus: Complete all tags with >= 100,000 usage")
        print("=" * 70)
        
        # 獲取超熱門標籤
        print("Getting ultra popular tags...")
        tags = await self.get_ultra_popular_tags()
        
        if not tags:
            print("ERROR: No ultra popular tags found")
            return False
        
        self.stats["total_tags"] = len(tags)
        self.stats["start_time"] = time.time()
        
        print(f"Found {len(tags)} ultra popular tags to process")
        print(f"Estimated cost: ${len(tags) * 0.00002:.2f}")
        print(f"Estimated time: {len(tags) * 0.21 / 60:.1f} minutes")
        
        # 分批處理
        batches = [tags[i:i+self.batch_size] for i in range(0, len(tags), self.batch_size)]
        
        for batch_idx, batch in enumerate(batches):
            print(f"\nProcessing batch {batch_idx + 1}/{len(batches)} ({len(batch)} tags)")
            
            try:
                success_count = await self.process_batch(batch)
                self.stats["processed"] += success_count
                self.stats["failed"] += len(batch) - success_count
                
                # 進度顯示
                progress = ((batch_idx + 1) / len(batches)) * 100
                elapsed = time.time() - self.stats["start_time"]
                eta = (elapsed / (batch_idx + 1)) * (len(batches) - batch_idx - 1)
                
                print(f"SUCCESS: Batch completed")
                print(f"Progress: {progress:.1f}% ({self.stats['processed']}/{self.stats['total_tags']})")
                print(f"ETA: {eta/60:.1f} minutes")
                
                # 速率限制
                await asyncio.sleep(self.rate_limit_delay)
                
            except Exception as e:
                print(f"ERROR: Batch failed: {e}")
                self.stats["failed"] += len(batch)
        
        self.print_final_summary()
        return True
    
    async def get_ultra_popular_tags(self) -> List[Dict]:
        """獲取超熱門標籤（使用次數 >= 100,000）"""
        try:
            response = self.supabase.table('tags_final').select(
                'id, name, post_count, main_category, sub_category'
            ).gte('post_count', 100000).is_('embedding', 'null').execute()
            
            return response.data
            
        except Exception as e:
            print(f"ERROR: Failed to get tags: {e}")
            return []
    
    async def process_batch(self, batch: List[Dict]) -> int:
        """處理單一批次"""
        tag_names = [tag['name'] for tag in batch]
        
        # 生成嵌入向量
        embeddings = await self.generate_embeddings(tag_names)
        
        if not embeddings:
            return 0
        
        # 更新資料庫
        success_count = await self.update_database(batch, embeddings)
        
        return success_count
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """生成嵌入向量"""
        for attempt in range(self.max_retries):
            try:
                response = await self.openai_client.embeddings.create(
                    model=self.model,
                    input=texts,
                    timeout=self.timeout
                )
                
                # 計算成本
                estimated_cost = len(texts) * 0.00002
                self.stats["total_cost"] += estimated_cost
                
                return [data.embedding for data in response.data]
                
            except Exception as e:
                print(f"  WARNING: Attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    return []
                await asyncio.sleep(2 ** attempt)
        
        return []
    
    async def update_database(self, tags: List[Dict], embeddings: List[List[float]]) -> int:
        """更新資料庫"""
        success_count = 0
        
        for tag, embedding in zip(tags, embeddings):
            try:
                self.supabase.table('tags_final').update({
                    "embedding": embedding
                }).eq('id', tag['id']).execute()
                
                success_count += 1
                
            except Exception as e:
                print(f"  ERROR: Failed to update {tag['name']}: {e}")
        
        return success_count
    
    def print_final_summary(self):
        """打印最終摘要"""
        total_time = time.time() - self.stats["start_time"]
        
        print("\n" + "=" * 70)
        print("Ultra Popular Stage COMPLETED!")
        print("=" * 70)
        print(f"Total tags: {self.stats['total_tags']}")
        print(f"Processed: {self.stats['processed']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Success rate: {(self.stats['processed']/self.stats['total_tags'])*100:.1f}%")
        print(f"Total cost: ${self.stats['total_cost']:.2f}")
        print(f"Total time: {total_time/60:.1f} minutes")
        print(f"Average time per tag: {total_time/self.stats['processed']:.2f}s")
        print("=" * 70)
        print("READY FOR SEMANTIC SEARCH TESTING!")
        print("=" * 70)

# 主執行函數
async def main():
    generator = UltraPopularEmbeddingGenerator()
    success = await generator.complete_ultra_popular_stage()
    
    if success:
        print("\nSUCCESS: Ultra Popular stage completed!")
        print("NEXT: Ready to test semantic search functionality")
        print("TIP: Run semantic search test script")
    else:
        print("\nERROR: Ultra Popular stage failed")

if __name__ == "__main__":
    asyncio.run(main())
