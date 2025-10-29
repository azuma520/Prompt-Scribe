#!/usr/bin/env python3
"""
測試語義搜尋 API 端點

測試新整合的 /api/inspire/search 端點功能。

Version: 2.0.0
Date: 2025-10-22
"""

import asyncio
import json
import time
from typing import Dict, Any
import httpx
from dotenv import load_dotenv
import os

class SemanticSearchAPITester:
    """語義搜尋 API 測試器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/inspire/search"
        
    async def test_semantic_search_api(self):
        """測試語義搜尋 API"""
        print("=" * 70)
        print("Semantic Search API Testing")
        print("Testing /api/inspire/search endpoint")
        print("=" * 70)
        
        # 測試查詢
        test_queries = [
            {
                "query": "beautiful anime girl",
                "top_k": 5,
                "min_similarity": 0.3,
                "user_access_level": "all-ages"
            },
            {
                "query": "fantasy landscape",
                "top_k": 3,
                "min_similarity": 0.4,
                "user_access_level": "all-ages"
            },
            {
                "query": "cute character",
                "top_k": 5,
                "min_similarity": 0.2,
                "user_access_level": "all-ages"
            },
            {
                "query": "dark atmosphere",
                "top_k": 4,
                "min_similarity": 0.3,
                "user_access_level": "r15"
            }
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, test_case in enumerate(test_queries, 1):
                print(f"\n{i}. Testing query: '{test_case['query']}'")
                
                try:
                    start_time = time.time()
                    
                    response = await client.post(
                        self.api_url,
                        json=test_case,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    end_time = time.time()
                    request_time = (end_time - start_time) * 1000
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        print(f"SUCCESS (HTTP {response.status_code})")
                        print(f"   Request time: {request_time:.1f}ms")
                        print(f"   Server time: {result.get('search_time_ms', 0):.1f}ms")
                        print(f"   Results found: {result.get('total_found', 0)}")
                        print(f"   Embedding count: {result.get('embedding_count', 0)}")
                        
                        # 顯示結果
                        results = result.get('results', [])
                        if results:
                            print("   Top results:")
                            for j, res in enumerate(results[:3], 1):
                                print(f"     {j}. {res['name']} (similarity: {res['similarity']:.3f}, posts: {res['post_count']:,})")
                        else:
                            print("   No results found")
                            
                    else:
                        print(f"FAILED (HTTP {response.status_code})")
                        print(f"   Error: {response.text}")
                        
                except Exception as e:
                    print(f"ERROR: {e}")
        
        print("\n" + "=" * 70)
        print("Semantic Search API Testing COMPLETED!")
        print("=" * 70)
    
    async def test_api_health(self):
        """測試 API 健康狀態"""
        print("\nTesting API health...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 測試 Inspire Agent 健康檢查
                health_url = f"{self.base_url}/api/inspire/health"
                response = await client.get(health_url)
                
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"SUCCESS: Inspire Agent Health: {health_data.get('status', 'unknown')}")
                    
                    if 'storage' in health_data:
                        storage = health_data['storage']
                        print(f"   Database: {storage.get('database_status', 'unknown')}")
                        print(f"   Embeddings: {storage.get('embedding_count', 0)} tags")
                else:
                    print(f"FAILED: Health check failed: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"ERROR: Health check error: {e}")

# 主執行函數
async def main():
    """主執行函數"""
    # 載入環境變數
    try:
        load_dotenv()
    except Exception:
        pass
    
    # 檢查必要的環境變數
    required_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_SERVICE_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"ERROR: Missing environment variables: {', '.join(missing_vars)}")
        print("Please run setup_env_local.ps1 first")
        return
    
    tester = SemanticSearchAPITester()
    
    # 測試 API 健康狀態
    await tester.test_api_health()
    
    # 測試語義搜尋 API
    await tester.test_semantic_search_api()

if __name__ == "__main__":
    asyncio.run(main())
