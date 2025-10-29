#!/usr/bin/env python3
"""
Prompt-Scribe 正確分階段嵌入生成器
嚴格按照優先級順序處理：先完成高價值標籤，再處理下一階段
"""

import asyncio
import time
from typing import List, Dict
from openai import AsyncOpenAI
from supabase import create_client, Client
import os
from dotenv import load_dotenv

class CorrectStagedEmbeddingGenerator:
    """正確的分階段嵌入生成器"""
    
    def __init__(self):
        load_dotenv()
        
        # 初始化客戶端
        self.openai_client = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.supabase: Client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_SERVICE_KEY']
        )
        
        # 配置
        self.model = "text-embedding-3-small"
        self.batch_size = 50
        self.max_retries = 3
        self.timeout = 30
        self.rate_limit_delay = 0.1
        
        # 分階段配置 - 嚴格按優先級
        self.stages = [
            {
                "id": "stage_1",
                "name": "Ultra Popular (>=100k)",
                "min_count": 100000,
                "max_count": float('inf'),
                "priority": 1
            },
            {
                "id": "stage_2", 
                "name": "Very Popular (50k-99k)",
                "min_count": 50000,
                "max_count": 99999,
                "priority": 2
            },
            {
                "id": "stage_3",
                "name": "Popular (10k-49k)",
                "min_count": 10000,
                "max_count": 49999,
                "priority": 3
            },
            {
                "id": "stage_4",
                "name": "Common (1k-9k)",
                "min_count": 1000,
                "max_count": 9999,
                "priority": 4
            }
        ]
        
        # 統計
        self.stats = {
            "total_processed": 0,
            "total_failed": 0,
            "total_cost": 0.0,
            "start_time": None,
            "stage_stats": {}
        }
    
    async def generate_all_stages_correctly(self):
        """正確的分階段生成 - 一個階段完成後再開始下一階段"""
        print("=" * 80)
        print("CORRECT Staged Embedding Generator")
        print("=" * 80)
        print("Strategy: Complete each stage before starting next")
        print("=" * 80)
        
        self.stats["start_time"] = time.time()
        
        # 按優先級順序執行各階段
        for stage in self.stages:
            print(f"\n{'='*20} {stage['name']} {'='*20}")
            
            try:
                await self.process_stage_correctly(stage)
                self.print_stage_summary(stage)
                
                # 檢查是否要繼續下一階段
                if not await self.should_continue_to_next_stage():
                    print(f"\nStopping at {stage['name']} as requested")
                    break
                    
            except Exception as e:
                print(f"ERROR: Stage {stage['id']} failed: {e}")
                self.stats["stage_stats"][stage['id']] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        self.print_final_summary()
    
    async def process_stage_correctly(self, stage: Dict):
        """正確處理單一階段 - 只處理當前階段範圍的標籤"""
        # 獲取該階段範圍的標籤
        tags = await self.get_stage_tags_correctly(stage)
        
        if not tags:
            print(f"No tags found for {stage['name']}")
            return
        
        print(f"Found {len(tags)} tags in {stage['name']}")
        print(f"Range: {stage['min_count']:,} - {stage['max_count']:, if stage['max_count'] != float('inf') else 'inf'}")
        
        # 分批處理
        batches = [tags[i:i+self.batch_size] for i in range(0, len(tags), self.batch_size)]
        stage_stats = {
            "total_tags": len(tags),
            "processed": 0,
            "failed": 0,
            "start_time": time.time()
        }
        
        for batch_idx, batch in enumerate(batches):
            print(f"  Processing batch {batch_idx + 1}/{len(batches)} ({len(batch)} tags)")
            
            try:
                success_count = await self.process_batch(batch)
                stage_stats["processed"] += success_count
                stage_stats["failed"] += len(batch) - success_count
                
                # 進度顯示
                progress = ((batch_idx + 1) / len(batches)) * 100
                print(f"  SUCCESS: Batch completed, progress: {progress:.1f}%")
                
                # 速率限制
                await asyncio.sleep(self.rate_limit_delay)
                
            except Exception as e:
                print(f"  ERROR: Batch failed: {e}")
                stage_stats["failed"] += len(batch)
        
        # 記錄階段統計
        stage_stats["end_time"] = time.time()
        stage_stats["duration"] = stage_stats["end_time"] - stage_stats["start_time"]
        stage_stats["status"] = "completed"
        
        self.stats["stage_stats"][stage['id']] = stage_stats
        self.stats["total_processed"] += stage_stats["processed"]
        self.stats["total_failed"] += stage_stats["failed"]
    
    async def get_stage_tags_correctly(self, stage: Dict) -> List[Dict]:
        """正確獲取階段標籤 - 只獲取當前階段範圍的標籤"""
        try:
            query = self.supabase.table('tags_final').select(
                'id, name, post_count, main_category, sub_category'
            ).gte('post_count', stage['min_count']).is_('embedding', 'null')
            
            if stage['max_count'] != float('inf'):
                query = query.lt('post_count', stage['max_count'] + 1)
            
            response = query.execute()
            
            return response.data
            
        except Exception as e:
            print(f"ERROR: Failed to get tags: {e}")
            return []
    
    async def should_continue_to_next_stage(self) -> bool:
        """檢查是否應該繼續到下一階段"""
        # 這裡可以添加邏輯來決定是否繼續
        # 例如：檢查成本、時間限制等
        return True
    
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
                print(f"    WARNING: Attempt {attempt + 1} failed: {e}")
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
                print(f"    ERROR: Failed to update {tag['name']}: {e}")
        
        return success_count
    
    def print_stage_summary(self, stage: Dict):
        """打印階段摘要"""
        stage_stats = self.stats["stage_stats"][stage['id']]
        
        print(f"\n{stage['name']} COMPLETED")
        print(f"  SUCCESS: {stage_stats['processed']}")
        print(f"  FAILED: {stage_stats['failed']}")
        print(f"  TIME: {stage_stats['duration']:.1f}s")
        print(f"  SUCCESS RATE: {(stage_stats['processed']/stage_stats['total_tags'])*100:.1f}%")
    
    def print_final_summary(self):
        """打印最終摘要"""
        total_time = time.time() - self.stats["start_time"]
        
        print("\n" + "=" * 80)
        print("CORRECT Staged Embedding Generation Completed!")
        print("=" * 80)
        print(f"Total processed tags: {self.stats['total_processed']}")
        print(f"Failed tags: {self.stats['total_failed']}")
        print(f"Total cost: ${self.stats['total_cost']:.2f}")
        print(f"Total time: {total_time/60:.1f} minutes")
        print(f"Overall success rate: {(self.stats['total_processed']/(self.stats['total_processed']+self.stats['total_failed']))*100:.1f}%")
        
        print(f"\nStage details:")
        for stage in self.stages:
            stage_id = stage['id']
            if stage_id in self.stats["stage_stats"]:
                stage_stats = self.stats["stage_stats"][stage_id]
                print(f"  {stage['name']}: {stage_stats['processed']}/{stage_stats['total_tags']} ({stage_stats['duration']:.1f}s)")
        
        print("=" * 80)

# 主執行函數
async def main():
    generator = CorrectStagedEmbeddingGenerator()
    await generator.generate_all_stages_correctly()

if __name__ == "__main__":
    asyncio.run(main())
