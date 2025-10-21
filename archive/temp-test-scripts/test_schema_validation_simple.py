"""
簡單的 GPT-5 結構化輸出驗證測試
"""

import json
import sys
import os

# 設置 UTF-8 編碼
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'api'))

try:
    from services.gpt5_output_schema import GPT5TagOutputSchema, GPT5OutputValidator
    print("✅ 成功導入 GPT5TagOutputSchema")
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)


def test_basic_validation():
    """測試基本驗證功能"""
    print("\n🧪 測試基本驗證功能...")
    
    # 測試有效回應
    valid_response = json.dumps({
        "tags": ["1girl", "long_hair", "blue_eyes", "smiling"],
        "confidence": 0.85,
        "reasoning": "這是一個典型的動漫角色描述",
        "categories": ["CHARACTER", "APPEARANCE"]
    })
    
    try:
        result = GPT5TagOutputSchema.validate_response(valid_response)
        print(f"✅ 有效回應驗證成功: {len(result['tags'])} 個標籤")
        print(f"   - 標籤: {result['tags']}")
        print(f"   - 信心度: {result['confidence']}")
        print(f"   - 分類: {result.get('categories', [])}")
    except Exception as e:
        print(f"❌ 有效回應驗證失敗: {e}")
        return False
    
    # 測試無效 JSON
    invalid_json = '{"tags": ["1girl"], "confidence": 0.8'  # 缺少結尾
    
    try:
        GPT5TagOutputSchema.validate_response(invalid_json)
        print("❌ 無效 JSON 應該失敗但沒有")
        return False
    except ValueError as e:
        print(f"✅ 無效 JSON 正確失敗: {e}")
    
    # 測試缺少必要欄位
    missing_fields = json.dumps({
        "tags": ["1girl"]
        # 缺少 confidence
    })
    
    try:
        GPT5TagOutputSchema.validate_response(missing_fields)
        print("❌ 缺少必要欄位應該失敗但沒有")
        return False
    except ValueError as e:
        print(f"✅ 缺少必要欄位正確失敗: {e}")
    
    return True


def test_validator_stats():
    """測試驗證器統計功能"""
    print("\n📊 測試驗證器統計功能...")
    
    validator = GPT5OutputValidator()
    
    # 初始統計
    stats = validator.get_stats()
    print(f"初始統計: {stats}")
    
    # 成功驗證
    valid_response = json.dumps({
        "tags": ["1girl", "smiling"],
        "confidence": 0.8
    })
    
    try:
        result = validator.validate(valid_response)
        print(f"✅ 成功驗證: {result['tags']}")
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")
        return False
    
    # 失敗驗證
    invalid_response = '{"tags": ["1girl"]'  # 無效 JSON
    
    try:
        validator.validate(invalid_response)
        print("❌ 無效回應應該失敗但沒有")
        return False
    except ValueError:
        print("✅ 無效回應正確失敗")
    
    # 檢查統計
    stats = validator.get_stats()
    print(f"最終統計: {stats}")
    
    if stats["total_validations"] == 2 and stats["successful"] == 1 and stats["failed"] == 1:
        print("✅ 統計功能正常")
        return True
    else:
        print("❌ 統計功能異常")
        return False


def test_fallback_response():
    """測試降級回應"""
    print("\n🔄 測試降級回應...")
    
    try:
        fallback = GPT5TagOutputSchema.create_fallback_response("test description")
        print(f"✅ 降級回應創建成功: {fallback['tags']}")
        print(f"   - 降級標記: {fallback.get('fallback', False)}")
        return True
    except Exception as e:
        print(f"❌ 降級回應創建失敗: {e}")
        return False


def test_schema_info():
    """測試 Schema 信息"""
    print("\n📋 測試 Schema 信息...")
    
    try:
        schema = GPT5TagOutputSchema.get_schema()
        print(f"✅ Schema 獲取成功")
        print(f"   - 必要欄位: {schema['required']}")
        print(f"   - 標籤最大數量: {schema['properties']['tags']['maxItems']}")
        
        stats = GPT5TagOutputSchema.get_validation_stats()
        print(f"✅ 驗證統計信息: {stats}")
        return True
    except Exception as e:
        print(f"❌ Schema 信息獲取失敗: {e}")
        return False


def main():
    """主測試函數"""
    print("🚀 開始 GPT-5 結構化輸出驗證測試")
    print("=" * 50)
    
    tests = [
        test_basic_validation,
        test_validator_stats,
        test_fallback_response,
        test_schema_info
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 測試 {test.__name__} 發生異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！GPT-5 結構化輸出驗證系統運行正常")
        return True
    else:
        print("⚠️ 部分測試失敗，請檢查相關功能")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
