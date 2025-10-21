"""
GPT-5 Nano 實際環境測試腳本
用於驗證 OpenAI 配置和 API 調用

使用方式:
    python tests/test_gpt5_nano_live.py
"""

import asyncio
import sys
import os

# 添加 src/api 到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))

from services.gpt5_nano_client import get_gpt5_nano_client
from config import settings
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_config_status():
    """打印配置狀態"""
    print("\n" + "=" * 80)
    print("📋 GPT-5 Nano 配置狀態檢查")
    print("=" * 80)
    
    config_items = [
        ("OPENAI_API_KEY", settings.openai_api_key, bool(settings.openai_api_key)),
        ("OPENAI_MODEL", settings.openai_model, True),
        ("OPENAI_MAX_TOKENS", settings.openai_max_tokens, True),
        ("OPENAI_TEMPERATURE", settings.openai_temperature, True),
        ("OPENAI_TIMEOUT", settings.openai_timeout, True),
        ("ENABLE_OPENAI_INTEGRATION", settings.enable_openai_integration, settings.enable_openai_integration),
    ]
    
    for name, value, is_valid in config_items:
        status = "✅" if is_valid else "❌"
        display_value = "*" * 10 if name == "OPENAI_API_KEY" and value else value
        print(f"{status} {name}: {display_value}")
    
    print("=" * 80 + "\n")


async def test_connection():
    """測試 OpenAI 連接"""
    print("\n" + "=" * 80)
    print("🔌 測試 1: OpenAI 連接測試")
    print("=" * 80)
    
    try:
        client = get_gpt5_nano_client()
        result = await client.test_connection()
        
        print(f"\n連接狀態: {'✅ 成功' if result['available'] else '❌ 失敗'}")
        
        if result['available']:
            print(f"測試回應: {result['test_response']}")
            print("\n配置詳情:")
            for key, value in result['config'].items():
                print(f"  - {key}: {value}")
        else:
            print(f"錯誤: {result['error']}")
        
        print("=" * 80)
        return result['available']
        
    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")
        print("=" * 80)
        return False


async def test_tag_generation():
    """測試標籤生成"""
    print("\n" + "=" * 80)
    print("🏷️  測試 2: 標籤生成測試")
    print("=" * 80)
    
    test_descriptions = [
        "a cute girl with long hair in school uniform",
        "lonely girl in cyberpunk city at night",
        "beautiful sunset over mountains",
    ]
    
    client = get_gpt5_nano_client()
    
    for i, description in enumerate(test_descriptions, 1):
        print(f"\n測試案例 {i}: {description}")
        print("-" * 80)
        
        try:
            result = await client.generate_tags(description)
            
            if result:
                print("✅ 生成成功!")
                print(f"Tags: {', '.join(result.get('tags', []))}")
                print(f"Confidence: {result.get('confidence', 0):.2f}")
                print(f"Reasoning: {result.get('reasoning', 'N/A')}")
                print(f"Source: {result.get('source', 'N/A')}")
                print(f"Generated at: {result.get('generated_at', 'N/A')}")
            else:
                print("❌ 生成失敗")
        
        except Exception as e:
            print(f"❌ 錯誤: {e}")
        
        print("-" * 80)
        
        # 添加延遲避免速率限制
        if i < len(test_descriptions):
            await asyncio.sleep(2)
    
    print("=" * 80)


async def test_api_endpoint():
    """測試 API 端點"""
    print("\n" + "=" * 80)
    print("🌐 測試 3: API 端點測試")
    print("=" * 80)
    
    try:
        import httpx
        
        # 測試配置端點
        print("\n測試 /api/llm/test-openai-config")
        print("-" * 80)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("http://localhost:8000/api/llm/test-openai-config")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 端點響應成功")
                print(f"Status: {data.get('status')}")
                print(f"Message: {data.get('message')}")
                
                result = data.get('result', {})
                print(f"\n配置測試結果:")
                print(f"  - Available: {result.get('available')}")
                print(f"  - Error: {result.get('error', 'None')}")
                
                if result.get('config'):
                    print(f"\n配置:")
                    for key, value in result['config'].items():
                        print(f"    • {key}: {value}")
            else:
                print(f"❌ 端點響應失敗: HTTP {response.status_code}")
                print(f"回應: {response.text}")
        
        # 測試推薦端點
        print("\n\n測試 /api/llm/recommend-tags")
        print("-" * 80)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/llm/recommend-tags",
                json={"description": "cute girl with long hair", "max_tags": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 推薦端點響應成功")
                print(f"Query: {data.get('query')}")
                print(f"Algorithm: {data['metadata'].get('algorithm')}")
                print(f"Tags: {len(data.get('recommended_tags', []))} 個")
                
                for tag in data.get('recommended_tags', [])[:5]:
                    print(f"  - {tag['tag']}: {tag['confidence']:.2f}")
            else:
                print(f"❌ 推薦端點響應失敗: HTTP {response.status_code}")
                print(f"回應: {response.text}")
        
        print("=" * 80)
        
    except ImportError:
        print("❌ httpx 未安裝，跳過 API 端點測試")
        print("安裝: pip install httpx")
        print("=" * 80)
    except Exception as e:
        print(f"❌ API 測試失敗: {e}")
        print("=" * 80)


async def run_all_tests():
    """運行所有測試"""
    print("\n")
    print("🚀 " + "=" * 76)
    print("🚀 GPT-5 Nano 完整測試套件")
    print("🚀 " + "=" * 76)
    
    # 1. 配置檢查
    print_config_status()
    
    # 2. 連接測試
    connection_ok = await test_connection()
    
    if not connection_ok:
        print("\n⚠️  警告: OpenAI 連接測試失敗，但會繼續其他測試（使用降級方案）")
    
    # 3. 標籤生成測試
    await test_tag_generation()
    
    # 4. API 端點測試
    print("\n💡 提示: 確保 API 服務正在運行 (python local_test.py)")
    user_input = input("\n是否測試 API 端點? (y/n): ").lower()
    
    if user_input == 'y':
        await test_api_endpoint()
    else:
        print("跳過 API 端點測試")
    
    # 測試總結
    print("\n" + "=" * 80)
    print("✅ 測試完成!")
    print("=" * 80)
    print("\n下一步:")
    print("1. 如果連接測試失敗，檢查 Zeabur 環境變數配置")
    print("2. 確保 OPENAI_API_KEY 和 ENABLE_OPENAI_INTEGRATION=true 已設置")
    print("3. 如果 API 測試失敗，確保本地服務正在運行")
    print("4. 查看日誌了解詳細錯誤信息")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n測試被用戶中斷")
    except Exception as e:
        print(f"\n\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

