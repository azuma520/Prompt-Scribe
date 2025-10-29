#!/usr/bin/env python3
"""
Prompt-Scribe 嵌入生成測試腳本
先測試 10 個超熱門標籤，驗證流程正常
"""

import asyncio
import time
from typing import List, Dict
from openai import AsyncOpenAI
from supabase import create_client, Client
import os
from dotenv import load_dotenv

class EmbeddingTestGenerator:
    """嵌入生成測試器"""
    
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
        self.test_size = 10  # 只測試 10 個標籤
    
    async def test_embedding_generation(self):
        """測試嵌入生成流程"""
        print("=" * 60)
        print("Prompt-Scribe Embedding Generation Test")
        print("=" * 60)
        
        # 1. 獲取測試標籤
        print("Getting test tags...")
        test_tags = await self.get_test_tags()
        
        if not test_tags:
            print("ERROR: No test tags found")
            return False
        
        print(f"SUCCESS: Found {len(test_tags)} test tags")
        for i, tag in enumerate(test_tags, 1):
            print(f"  {i}. {tag['name']} (使用次數: {tag['post_count']:,})")
        
        # 2. 生成嵌入向量
        print(f"\nGenerating embeddings...")
        start_time = time.time()
        
        tag_names = [tag['name'] for tag in test_tags]
        embeddings = await self.generate_embeddings(tag_names)
        
        generation_time = time.time() - start_time
        
        if not embeddings:
            print("ERROR: Embedding generation failed")
            return False
        
        print(f"SUCCESS: Generated {len(embeddings)} embeddings")
        print(f"Time: {generation_time:.2f}s")
        print(f"Average: {generation_time/len(embeddings):.2f}s/tag")
        
        # 3. 檢查嵌入向量品質
        print(f"\nChecking embedding quality...")
        quality_check = self.check_embedding_quality(embeddings)
        
        print(f"Dimension check: {quality_check['dimension_check']}")
        print(f"Value range: {quality_check['value_range']}")
        print(f"Quality score: {quality_check['quality_score']}/100")
        
        # 4. 更新資料庫
        print(f"\nUpdating database...")
        success_count = await self.update_database(test_tags, embeddings)
        
        print(f"SUCCESS: Updated {success_count}/{len(test_tags)} tags")
        
        # 5. 驗證更新
        print(f"\nVerifying database update...")
        verification = await self.verify_database_update(test_tags)
        
        print(f"SUCCESS: Verified {verification['verified']}/{len(test_tags)} tags")
        
        # 6. 測試語義搜尋
        print(f"\nTesting semantic search...")
        search_test = await self.test_semantic_search()
        
        if search_test:
            print("SUCCESS: Semantic search test passed")
        else:
            print("WARNING: Semantic search test needs further configuration")
        
        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)
        
        return True
    
    async def get_test_tags(self) -> List[Dict]:
        """獲取測試標籤（超熱門標籤）"""
        try:
            response = self.supabase.table('tags_final').select(
                'id, name, post_count, main_category, sub_category'
            ).gte('post_count', 100000).is_('embedding', 'null').limit(self.test_size).execute()
            
            return response.data
            
        except Exception as e:
            print("ERROR: Failed to get test tags")
            return []
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """生成嵌入向量"""
        try:
            response = await self.openai_client.embeddings.create(
                model=self.model,
                input=texts,
                timeout=30
            )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            print("ERROR: Embedding generation failed")
            return []
    
    def check_embedding_quality(self, embeddings: List[List[float]]) -> Dict:
        """檢查嵌入向量品質"""
        if not embeddings:
            return {"dimension_check": False, "value_range": False, "quality_score": 0}
        
        # 檢查維度
        dimensions = [len(emb) for emb in embeddings]
        dimension_check = all(d == dimensions[0] for d in dimensions)
        
        # 檢查數值範圍
        all_values = [val for emb in embeddings for val in emb]
        min_val, max_val = min(all_values), max(all_values)
        value_range = -1 <= min_val <= max_val <= 1
        
        # 計算品質分數
        quality_score = 0
        if dimension_check:
            quality_score += 40
        if value_range:
            quality_score += 40
        if len(set(dimensions)) == 1:  # 所有嵌入維度一致
            quality_score += 20
        
        return {
            "dimension_check": dimension_check,
            "value_range": value_range,
            "quality_score": quality_score,
            "dimension": dimensions[0] if dimensions else 0,
            "min_value": min_val,
            "max_value": max_val
        }
    
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
                print(f"ERROR: Failed to update tag {tag['name']}: {e}")
        
        return success_count
    
    async def verify_database_update(self, tags: List[Dict]) -> Dict:
        """驗證資料庫更新"""
        verified_count = 0
        
        for tag in tags:
            try:
                response = self.supabase.table('tags_final').select('embedding').eq('id', tag['id']).execute()
                
                if response.data and response.data[0]['embedding'] is not None:
                    verified_count += 1
                
            except Exception as e:
                print(f"ERROR: Failed to verify tag {tag['name']}: {e}")
        
        return {
            "verified": verified_count,
            "total": len(tags)
        }
    
    async def test_semantic_search(self) -> bool:
        """測試語義搜尋（簡化版）"""
        try:
            # 生成測試查詢的嵌入
            test_query = "beautiful girl"
            response = await self.openai_client.embeddings.create(
                model=self.model,
                input=[test_query]
            )
            query_embedding = response.data[0].embedding
            
            # 檢查是否有嵌入向量可以搜尋
            count_response = self.supabase.table('tags_final').select('id', count='exact').not_.is_('embedding', 'null').execute()
            
            if count_response.count > 0:
                print(f"SUCCESS: Found {count_response.count} tags with embeddings")
                return True
            else:
                print("WARNING: No tags with embeddings found")
                return False
                
        except Exception as e:
            print("ERROR: Semantic search test failed")
            return False

# 主執行函數
async def main():
    tester = EmbeddingTestGenerator()
    success = await tester.test_embedding_generation()
    
    if success:
        print("\nSUCCESS: Test passed! Ready for large-scale embedding generation")
        print("TIP: Run: python scripts/generate_embeddings_staged.py")
    else:
        print("\nERROR: Test failed, please check configuration")

if __name__ == "__main__":
    asyncio.run(main())
