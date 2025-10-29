#!/usr/bin/env python3
"""
Prompt-Scribe 分階段標籤嵌入生成器
基於真實資料庫的 140K+ 標籤
採用分階段優先策略，從高價值標籤開始
"""

import asyncio
import time
import json
from typing import List, Dict, Optional, Tuple
from openai import AsyncOpenAI
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

class StagedEmbeddingGenerator:
    """分階段標籤嵌入生成器"""
    
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
        self.batch_size = 100  # 增加批次大小以處理大量資料
        self.max_retries = 3
        self.timeout = 30
        self.rate_limit_delay = 0.1  # 100ms 延遲
        
        # 分階段配置
        self.stages = {
            "stage_1": {
                "name": "Ultra Popular (≥100k)",
                "min_count": 100000,
                "priority": 5,
                "estimated_cost": 0.36
            },
            "stage_2": {
                "name": "Very Popular (≥50k)", 
                "min_count": 50000,
                "priority": 4,
                "estimated_cost": 0.20
            },
            "stage_3": {
                "name": "Popular (≥10k)",
                "min_count": 10000,
                "priority": 3,
                "estimated_cost": 1.01
            },
            "stage_4": {
                "name": "Common (≥1k)",
                "min_count": 1000,
                "priority": 2,
                "estimated_cost": 6.29
            }
        }
        
        # 統計
        self.stats = {
            "total_processed": 0,
            "total_failed": 0,
            "total_cost": 0.0,
            "start_time": None,
            "stage_stats": {}
        }
    
    async def generate_all_stages(self):
        """生成所有階段的嵌入向量"""
        print("=" * 80)
        print("Prompt-Scribe Staged Embedding Generator")
        print("=" * 80)
        print(f"Database scale: 140,782 tags")
        print(f"Staged strategy: Start with high-value tags")
        print(f"Estimated total cost: $7.86")
        print("=" * 80)
        
        self.stats["start_time"] = time.time()
        
        # 按優先級執行各階段
        for stage_id, stage_config in self.stages.items():
            print(f"\nStarting {stage_config['name']} stage")
            print("-" * 60)
            
            try:
                await self.process_stage(stage_id, stage_config)
                self.print_stage_summary(stage_id, stage_config)
                
            except Exception as e:
                print(f"ERROR: Stage {stage_id} failed: {e}")
                self.stats["stage_stats"][stage_id] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        self.print_final_summary()
    
    async def process_stage(self, stage_id: str, stage_config: Dict):
        """處理單一階段"""
        # 獲取該階段的標籤
        tags = await self.get_stage_tags(stage_config["min_count"])
        
        if not tags:
            print(f"WARNING: Stage {stage_id} found no tags")
            return
        
        print(f"Found {len(tags)} tags")
        
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
        
        self.stats["stage_stats"][stage_id] = stage_stats
        self.stats["total_processed"] += stage_stats["processed"]
        self.stats["total_failed"] += stage_stats["failed"]
    
    async def get_stage_tags(self, min_count: int) -> List[Dict]:
        """獲取指定階段的標籤（只處理當前階段範圍）"""
        try:
            # 定義階段範圍
            stage_ranges = {
                100000: (100000, float('inf')),  # Ultra Popular: >=100k
                50000: (50000, 99999),           # Very Popular: 50k-99k
                10000: (10000, 49999),           # Popular: 10k-49k
                1000: (1000, 9999)               # Common: 1k-9k
            }
            
            min_range, max_range = stage_ranges.get(min_count, (min_count, float('inf')))
            
            query = self.supabase.table('tags_final').select(
                'id, name, post_count, main_category, sub_category'
            ).gte('post_count', min_range).is_('embedding', 'null')
            
            if max_range != float('inf'):
                query = query.lt('post_count', max_range + 1)
            
            response = query.execute()
            
            return response.data
            
        except Exception as e:
            print(f"ERROR: Failed to get tags: {e}")
            return []
    
    async def process_batch(self, batch: List[Dict]) -> int:
        """處理單一批次，返回成功處理的數量"""
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
                
                # 計算成本 (text-embedding-3-small: $0.00002 per 1K tokens)
                estimated_cost = len(texts) * 0.00002  # 簡化估算
                self.stats["total_cost"] += estimated_cost
                
                return [data.embedding for data in response.data]
                
            except Exception as e:
                print(f"    ⚠️ 嘗試 {attempt + 1} 失敗: {e}")
                if attempt == self.max_retries - 1:
                    return []
                await asyncio.sleep(2 ** attempt)  # 指數退避
        
        return []
    
    async def update_database(self, tags: List[Dict], embeddings: List[List[float]]) -> int:
        """更新資料庫，返回成功更新的數量"""
        success_count = 0
        
        for tag, embedding in zip(tags, embeddings):
            try:
                self.supabase.table('tags_final').update({
                    "embedding": embedding
                }).eq('id', tag['id']).execute()
                
                success_count += 1
                
            except Exception as e:
                print(f"    ❌ 更新標籤 {tag['name']} 失敗: {e}")
        
        return success_count
    
    def print_stage_summary(self, stage_id: str, stage_config: Dict):
        """打印階段摘要"""
        stage_stats = self.stats["stage_stats"][stage_id]
        
        print(f"\n{stage_config['name']} stage completed")
        print(f"  SUCCESS: {stage_stats['processed']}")
        print(f"  FAILED: {stage_stats['failed']}")
        print(f"  TIME: {stage_stats['duration']:.1f}s")
        print(f"  SUCCESS RATE: {(stage_stats['processed']/stage_stats['total_tags'])*100:.1f}%")
    
    def print_final_summary(self):
        """打印最終摘要"""
        total_time = time.time() - self.stats["start_time"]
        
        print("\n" + "=" * 80)
        print("Embedding generation completed!")
        print("=" * 80)
        print(f"Total processed tags: {self.stats['total_processed']}")
        print(f"Failed tags: {self.stats['total_failed']}")
        print(f"Total cost: ${self.stats['total_cost']:.2f}")
        print(f"Total time: {total_time:.0f}s")
        print(f"Overall success rate: {(self.stats['total_processed']/(self.stats['total_processed']+self.stats['total_failed']))*100:.1f}%")
        
        print(f"\nStage details:")
        for stage_id, stage_stats in self.stats["stage_stats"].items():
            stage_name = self.stages[stage_id]["name"]
            print(f"  {stage_name}: {stage_stats['processed']}/{stage_stats['total_tags']} ({stage_stats['duration']:.1f}s)")
        
        print("=" * 80)

# 主執行函數
async def main():
    generator = StagedEmbeddingGenerator()
    await generator.generate_all_stages()

if __name__ == "__main__":
    asyncio.run(main())
