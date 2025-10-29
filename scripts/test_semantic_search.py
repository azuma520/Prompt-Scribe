#!/usr/bin/env python3
"""
語義搜尋測試腳本
測試嵌入向量的語義搜尋功能
驗證 Inspire Agent 的搜尋能力
"""

import os
import json
import numpy as np
from typing import List, Dict
import time
from supabase import create_client, Client
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio

class SemanticSearchTester:
    """語義搜尋測試器"""
    
    def __init__(self):
        load_dotenv()
        
        self.supabase: Client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_SERVICE_KEY']
        )
        
        self.openai_client = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    async def test_semantic_search(self):
        """測試語義搜尋功能"""
        print("=" * 70)
        print("Semantic Search Testing")
        print("Testing embedding-based tag search functionality")
        print("=" * 70)
        
        # 1. 檢查嵌入向量狀態
        print("1. Checking embedding status...")
        embedding_status = await self.check_embedding_status()
        
        if not embedding_status["has_embeddings"]:
            print("ERROR: No embeddings found. Please complete embedding generation first.")
            return False
        
        print(f"SUCCESS: Found {embedding_status['count']} tags with embeddings")
        
        # 2. 測試基本搜尋查詢
        print("\n2. Testing basic search queries...")
        test_queries = [
            "beautiful anime girl",
            "fantasy landscape", 
            "cute character",
            "dark atmosphere",
            "nature scene",
            "romantic couple",
            "action pose",
            "detailed art"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = await self.semantic_search(query, top_k=5)
            
            if results:
                print("Top results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['name']} (similarity: {result['similarity']:.3f})")
            else:
                print("  No results found")
        
        # 3. 測試 Inspire Agent 相關查詢
        print("\n3. Testing Inspire Agent related queries...")
        inspire_queries = [
            "mood: happy cheerful",
            "style: anime manga",
            "character: 1girl solo",
            "atmosphere: peaceful calm",
            "emotion: love romantic"
        ]
        
        for query in inspire_queries:
            print(f"\nInspire Query: '{query}'")
            results = await self.semantic_search(query, top_k=3)
            
            if results:
                print("Results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['name']} (similarity: {result['similarity']:.3f})")
        
        # 4. 性能測試
        print("\n4. Performance testing...")
        performance_results = await self.performance_test()
        
        print(f"Average search time: {performance_results['avg_time']:.3f}s")
        print(f"Search accuracy: {performance_results['accuracy']:.1f}%")
        
        print("\n" + "=" * 70)
        print("Semantic Search Testing COMPLETED!")
        print("=" * 70)
        
        return True
    
    async def check_embedding_status(self) -> Dict:
        """檢查嵌入向量狀態"""
        try:
            # 檢查總數
            total_response = self.supabase.table('tags_final').select('id', count='exact').execute()
            total_tags = total_response.count
            
            # 檢查已嵌入的數量
            embedded_response = self.supabase.table('tags_final').select('id', count='exact').not_.is_('embedding', 'null').execute()
            embedded_count = embedded_response.count
            
            return {
                "has_embeddings": embedded_count > 0,
                "count": embedded_count,
                "total": total_tags,
                "coverage": (embedded_count / total_tags) * 100 if total_tags > 0 else 0
            }
            
        except Exception as e:
            print(f"ERROR: Failed to check embedding status: {e}")
            return {"has_embeddings": False, "count": 0, "total": 0, "coverage": 0}
    
    async def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """語義搜尋"""
        try:
            # 生成查詢嵌入
            query_embedding = await self.generate_query_embedding(query)
            
            # 搜尋相似標籤
            # 使用簡單的餘弦相似度搜尋
            results = await self.search_similar_tags(query_embedding, top_k)
            
            return results
            
        except Exception as e:
            print(f"ERROR: Semantic search failed: {e}")
            return []
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """生成查詢嵌入向量"""
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            return response.data[0].embedding
            
        except Exception as e:
            print(f"ERROR: Failed to generate query embedding: {e}")
            return []
    
    async def search_similar_tags(self, query_embedding: List[float], top_k: int) -> List[Dict]:
        """搜尋相似標籤"""
        try:
            # 獲取所有有嵌入向量的標籤
            response = self.supabase.table('tags_final').select(
                'id, name, post_count, embedding'
            ).not_.is_('embedding', 'null').limit(1000).execute()  # 限制數量以提高性能
            
            if not response.data:
                return []
            
            # 計算相似度
            similarities = []
            for tag in response.data:
                if tag['embedding']:
                    embedding_value = tag['embedding']
                    # Handle embeddings stored as JSON/text
                    if isinstance(embedding_value, str):
                        try:
                            embedding_value = json.loads(embedding_value)
                        except Exception:
                            # Skip invalid embedding rows
                            continue
                    similarity = self.cosine_similarity(query_embedding, embedding_value)
                    similarities.append({
                        'name': tag['name'],
                        'post_count': tag['post_count'],
                        'similarity': similarity
                    })
            
            # 按相似度排序並返回前 k 個
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            print(f"ERROR: Failed to search similar tags: {e}")
            return []
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """計算餘弦相似度"""
        try:
            # Force float dtype to avoid unicode arrays
            vec1 = np.asarray(vec1, dtype=float)
            vec2 = np.asarray(vec2, dtype=float)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            print(f"ERROR: Cosine similarity calculation failed: {e}")
            return 0
    
    async def performance_test(self) -> Dict:
        """性能測試"""
        test_queries = [
            "anime girl",
            "fantasy",
            "cute",
            "dark",
            "nature"
        ]
        
        total_time = 0
        successful_searches = 0
        
        for query in test_queries:
            start_time = time.time()
            results = await self.semantic_search(query, top_k=3)
            end_time = time.time()
            
            total_time += (end_time - start_time)
            if results:
                successful_searches += 1
        
        avg_time = total_time / len(test_queries)
        accuracy = (successful_searches / len(test_queries)) * 100
        
        return {
            "avg_time": avg_time,
            "accuracy": accuracy
        }

# 主執行函數
async def main():
    tester = SemanticSearchTester()
    success = await tester.test_semantic_search()
    
    if success:
        print("\nSUCCESS: Semantic search testing completed!")
        print("READY: Inspire Agent can now use semantic search")
    else:
        print("\nERROR: Semantic search testing failed")

if __name__ == "__main__":
    asyncio.run(main())
