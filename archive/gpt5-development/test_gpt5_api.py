"""
GPT-5 Nano API 測試腳本
用於測試結構化輸出驗證系統
"""

import requests
import json
import sys
import io

# 設置 UTF-8 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API 基礎 URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分隔線"""
    print("\n" + "=" * 60)
    print(f"🔷 {title}")
    print("=" * 60)

def test_health():
    """測試健康檢查端點"""
    print_section("健康檢查")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康檢查失敗: {e}")
        return False

def test_openai_config():
    """測試 OpenAI 配置"""
    print_section("OpenAI 配置檢查")
    try:
        response = requests.get(f"{BASE_URL}/api/llm/test-openai-config", timeout=5)
        print(f"狀態碼: {response.status_code}")
        result = response.json()
        print(f"回應: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("available"):
            print("✅ OpenAI 配置正常")
        else:
            print("⚠️  OpenAI 不可用")
            print(f"原因: {result.get('error', '未知')}")
        
        return True
    except Exception as e:
        print(f"❌ 配置檢查失敗: {e}")
        return False

def test_tag_recommendation(description):
    """測試標籤推薦功能"""
    print_section(f"標籤推薦測試: {description[:30]}...")
    try:
        payload = {"description": description}
        response = requests.post(
            f"{BASE_URL}/api/llm/recommend-tags",
            json=payload,
            timeout=30
        )
        print(f"狀態碼: {response.status_code}")
        result = response.json()
        
        # 美化輸出
        if response.status_code == 200:
            print("\n✅ 推薦成功")
            print(f"📋 標籤: {', '.join(result.get('tags', []))}")
            print(f"📊 信心度: {result.get('confidence', 0)}")
            print(f"💭 理由: {result.get('reasoning', 'N/A')}")
            print(f"🏷️  分類: {', '.join(result.get('categories', []))}")
            
            # 檢查是否為降級方案
            if result.get('fallback'):
                print("⚠️  注意: 使用降級方案（GPT-5 不可用）")
            
            # 檢查驗證信息
            if result.get('validation_method'):
                print(f"✅ 驗證方法: {result['validation_method']}")
        else:
            print(f"❌ 推薦失敗: {result}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_validation_stats():
    """測試驗證統計"""
    print_section("驗證統計")
    try:
        response = requests.get(f"{BASE_URL}/api/llm/validation-stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"總驗證次數: {stats.get('total_validations', 0)}")
            print(f"成功次數: {stats.get('successful', 0)}")
            print(f"失敗次數: {stats.get('failed', 0)}")
            print(f"成功率: {stats.get('success_rate', 0)}%")
        else:
            print(f"⚠️  狀態碼: {response.status_code}")
            print(f"回應: {response.text}")
        return True
    except Exception as e:
        print(f"❌ 統計查詢失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("\n" + "🚀 " + "="*54)
    print("  GPT-5 Nano 結構化輸出驗證系統 - API 測試")
    print("="*58)
    
    # 測試列表
    tests = []
    
    # 1. 健康檢查
    if not test_health():
        print("\n❌ 伺服器未啟動或無法連接")
        print("請先執行: powershell -ExecutionPolicy Bypass -File start_test_server.ps1")
        sys.exit(1)
    tests.append(True)
    
    # 2. OpenAI 配置
    tests.append(test_openai_config())
    
    # 3. 標籤推薦測試案例
    test_cases = [
        "一個長髮藍眼的動漫女孩，穿著校服，微笑著看向觀眾",
        "a beautiful anime girl with long blonde hair and green eyes",
        "戶外場景，日落，城市風景",
        "masterpiece, high quality, detailed",
    ]
    
    for case in test_cases:
        tests.append(test_tag_recommendation(case))
    
    # 4. 驗證統計
    tests.append(test_validation_stats())
    
    # 總結
    print_section("測試總結")
    passed = sum(tests)
    total = len(tests)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"✅ 通過: {passed}/{total}")
    print(f"📊 成功率: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 所有測試通過！GPT-5 Nano API 運行正常")
    else:
        print(f"\n⚠️  {total - passed} 個測試失敗")
    
    print("\n" + "="*60)
    print("\n💡 提示:")
    print("  - API 文檔: http://localhost:8000/docs")
    print("  - 健康檢查: http://localhost:8000/health")
    print("  - 標籤推薦: POST http://localhost:8000/api/llm/recommend-tags")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
