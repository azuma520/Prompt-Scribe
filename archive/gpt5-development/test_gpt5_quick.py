#!/usr/bin/env python3
"""
GPT-5 Mini 快速測試腳本
測試基本功能是否正常
"""
import sys
import os
import asyncio

# 修復編碼
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# 添加路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'api'))

async def main():
    """主測試函數"""
    print("=" * 60)
    print("🧪 GPT-5 Mini 快速測試")
    print("=" * 60)
    
    # 檢查環境變數
    print("\n📋 步驟 1: 檢查環境變數")
    print("-" * 60)
    
    from config import settings
    
    print(f"  OPENAI_API_KEY: {'✅ 已設置' if settings.openai_api_key else '❌ 未設置'}")
    if settings.openai_api_key:
        print(f"    前8碼: {settings.openai_api_key[:8]}...")
    print(f"  OPENAI_MODEL: {settings.openai_model}")
    print(f"  ENABLE_OPENAI_INTEGRATION: {settings.enable_openai_integration}")
    
    if not settings.openai_api_key:
        print("\n❌ 錯誤: OPENAI_API_KEY 未設置")
        print("請運行: powershell -ExecutionPolicy Bypass -File setup_env_local.ps1")
        return False
    
    # 初始化客戶端
    print("\n📋 步驟 2: 初始化 GPT-5 Mini 客戶端")
    print("-" * 60)
    
    try:
        from services.gpt5_nano_client import GPT5NanoClient
        client = GPT5NanoClient()
        
        print(f"  ✅ 客戶端初始化成功")
        print(f"  - 模型: {client.model}")
        print(f"  - GPT-5 系列: {'是' if client.is_gpt5 else '否'}")
        print(f"  - 可用性: {'✅ 可用' if client.is_available() else '❌ 不可用'}")
        
        if not client.is_available():
            print("\n❌ 客戶端不可用")
            return False
            
    except Exception as e:
        print(f"\n❌ 客戶端初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 測試連接
    print("\n📋 步驟 3: 測試 API 連接")
    print("-" * 60)
    
    try:
        result = await client.test_connection()
        
        if result.get("available"):
            print("  ✅ API 連接成功")
            if result.get("test_response"):
                print(f"  ✅ 測試回應成功")
                response = result["test_response"]
                print(f"    - Tags: {response.get('tags', [])[:5]}")
                print(f"    - Confidence: {response.get('confidence', 0)}")
        else:
            print(f"  ❌ API 連接失敗: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ 連接測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 測試標籤推薦
    print("\n📋 步驟 4: 測試標籤推薦功能")
    print("-" * 60)
    
    test_cases = [
        {
            "description": "一個長髮藍眼的動漫女孩",
            "expected_tags": ["1girl", "long_hair", "blue_eyes"]
        },
        {
            "description": "戶外場景，日落，城市風景",
            "expected_tags": ["outdoors", "sunset", "cityscape"]
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  測試案例 {i}: {test_case['description']}")
        
        try:
            result = await client.generate_tags(test_case['description'])
            
            if result:
                print(f"    ✅ 成功")
                print(f"    - Tags: {result.get('tags', [])}")
                print(f"    - Confidence: {result.get('confidence', 0)}")
                
                # 檢查是否包含預期的標籤
                returned_tags = result.get('tags', [])
                expected_found = sum(1 for tag in test_case['expected_tags'] if tag in returned_tags)
                print(f"    - 預期標籤匹配: {expected_found}/{len(test_case['expected_tags'])}")
                
                passed += 1
            else:
                print(f"    ❌ 失敗: 無回應")
                failed += 1
                
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")
            failed += 1
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    print(f"  總測試案例: {passed + failed}")
    print(f"  ✅ 通過: {passed}")
    print(f"  ❌ 失敗: {failed}")
    print(f"  成功率: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有測試通過！GPT-5 Mini 集成成功！")
        print("\n下一步:")
        print("  1. 啟動伺服器: python run_server.py")
        print("  2. 測試 API: python test_api.py")
        print("  3. 部署到 Zeabur")
        return True
    else:
        print("\n⚠️ 部分測試失敗，請檢查錯誤訊息")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 測試被中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
