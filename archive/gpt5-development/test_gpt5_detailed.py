"""
Detailed GPT-5 Nano test
"""

import requests
import json
import sys
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://127.0.0.1:8000"

print("GPT-5 Nano 詳細測試")
print("=" * 60)

# Test OpenAI config
print("1. 檢查 OpenAI 配置...")
try:
    response = requests.get(f"{base_url}/api/llm/test-openai-config")
    result = response.json()
    
    print(f"狀態碼: {response.status_code}")
    print(f"可用性: {result.get('available', False)}")
    print(f"錯誤: {result.get('error', 'None')}")
    
    if result.get('config'):
        config = result['config']
        print(f"API Key 設置: {config.get('api_key_set', False)}")
        print(f"模型: {config.get('model', 'N/A')}")
        print(f"啟用狀態: {config.get('enabled', False)}")
        print(f"最大 Tokens: {config.get('max_tokens', 'N/A')}")
        print(f"超時時間: {config.get('timeout', 'N/A')}秒")
    
    if result.get('validation_stats'):
        stats = result['validation_stats']
        print(f"驗證統計:")
        print(f"  - 總驗證次數: {stats.get('total_validations', 0)}")
        print(f"  - 成功次數: {stats.get('successful', 0)}")
        print(f"  - 失敗次數: {stats.get('failed', 0)}")
        print(f"  - 成功率: {stats.get('success_rate', 0)}%")
    
    print("✅ OpenAI 配置檢查完成")
    
except Exception as e:
    print(f"❌ OpenAI 配置檢查失敗: {e}")

print()

# Test tag recommendation with different descriptions
test_cases = [
    "一個長髮藍眼的動漫女孩",
    "a beautiful anime girl with long blonde hair",
    "戶外場景，日落，城市風景",
    "masterpiece, high quality, detailed artwork"
]

for i, description in enumerate(test_cases, 1):
    print(f"{i+1}. 測試標籤推薦: {description}")
    try:
        payload = {"description": description}
        response = requests.post(f"{base_url}/api/llm/recommend-tags", json=payload)
        result = response.json()
        
        print(f"   狀態碼: {response.status_code}")
        print(f"   標籤: {result.get('tags', [])}")
        print(f"   信心度: {result.get('confidence', 0)}")
        print(f"   理由: {result.get('reasoning', 'N/A')}")
        print(f"   分類: {result.get('categories', [])}")
        print(f"   降級方案: {result.get('fallback', False)}")
        print(f"   驗證方法: {result.get('validation_method', 'N/A')}")
        print(f"   來源: {result.get('source', 'N/A')}")
        
        if result.get('tags'):
            print("   ✅ 推薦成功")
        else:
            print("   ⚠️  無標籤返回")
            
    except Exception as e:
        print(f"   ❌ 測試失敗: {e}")
    
    print()

print("=" * 60)
print("GPT-5 Nano 詳細測試完成！")
