#!/usr/bin/env python
"""測試 GPT-5 API 並查看詳細日誌"""
import asyncio
import logging
import sys
import os

# 添加 src/api 到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'api'))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from services.gpt5_nano_client import get_gpt5_nano_client

async def test_gpt5():
    """測試 GPT-5 客戶端"""
    print("=" * 60)
    print("Testing GPT-5 Nano Client")
    print("=" * 60)
    
    # 獲取客戶端
    client = get_gpt5_nano_client()
    
    # 檢查是否可用
    if not client.is_available():
        print("[ERROR] GPT-5 client not available")
        print(f"   Config: {client.config}")
        return
    
    print("[OK] GPT-5 client available")
    print(f"   Model: {client.model}")
    print()
    
    # 測試連接
    print("Testing connection...")
    test_result = await client.test_connection()
    print(f"   Result: {test_result}")
    print()
    
    # 生成標籤
    print("Generating tags...")
    description = "1girl"
    print(f"   Description: {description}")
    print()
    
    result = await client.generate_tags(description)
    
    if result:
        print("[SUCCESS] Tags generated")
        print(f"   Result keys: {list(result.keys())}")
        print(f"   Tags: {result.get('tags', [])}")
        print(f"   Confidence: {result.get('confidence', 0)}")
        print(f"   Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
        print(f"   Categories: {result.get('categories', [])}")
    else:
        print("[ERROR] Failed to generate tags")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_gpt5())

