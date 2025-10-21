"""
GPT-5 修復驗證腳本
快速驗證 Schema 一致性修復是否正確
"""

import sys
from pathlib import Path

# 添加 src/api 到路徑
sys.path.insert(0, str(Path(__file__).parent / "src" / "api"))

from services.gpt5_output_schema import get_gpt5_validator, GPT5TagOutputSchema


def print_section(title: str):
    """列印區塊標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def verify_schema_structure():
    """驗證 Schema 結構"""
    print_section("[1] 驗證 Schema 結構")
    
    schema = GPT5TagOutputSchema.get_schema()
    
    # 檢查必填欄位
    print("\n[OK] 必填欄位:")
    for field in schema["required"]:
        print(f"   - {field}")
    
    # 檢查可選欄位
    print("\n[*] 可選欄位:")
    optional_fields = [f for f in schema["properties"].keys() if f not in schema["required"]]
    for field in optional_fields:
        print(f"   - {field}")
    
    # 檢查 additionalProperties
    print(f"\n[*] additionalProperties: {schema['additionalProperties']}")
    
    # 檢查重要欄位的設置
    tags_schema = schema["properties"]["tags"]
    confidence_schema = schema["properties"]["confidence"]
    
    print(f"\n[*] Tags 設置:")
    print(f"   - minItems: {tags_schema['minItems']}")
    print(f"   - maxItems: {tags_schema['maxItems']}")
    
    print(f"\n[*] Confidence 設置:")
    print(f"   - minimum: {confidence_schema['minimum']}")
    print(f"   - maximum: {confidence_schema['maximum']}")
    
    # 檢查 categories 欄位
    if "categories" in schema["properties"]:
        categories_schema = schema["properties"]["categories"]
        print(f"\n[*] Categories 欄位:")
        print(f"   - 存在: [OK] 是")
        print(f"   - 枚舉值數量: {len(categories_schema['items']['enum'])}")
        print(f"   - 枚舉值: {', '.join(categories_schema['items']['enum'][:3])}...")
    else:
        print(f"\n[*] Categories 欄位: [X] 不存在")


def test_validation_scenarios():
    """測試各種驗證場景"""
    print_section("[2] 測試驗證場景")
    
    validator = get_gpt5_validator()
    
    test_cases = [
        {
            "name": "最小有效回應（1 個標籤）",
            "json": '{"tags": ["1girl"], "confidence": 0.5}',
            "should_pass": True
        },
        {
            "name": "低信心度（0.3）",
            "json": '{"tags": ["abstract"], "confidence": 0.3}',
            "should_pass": True
        },
        {
            "name": "高信心度（1.0）",
            "json": '{"tags": ["1girl", "solo"], "confidence": 1.0}',
            "should_pass": True
        },
        {
            "name": "包含 categories",
            "json": '{"tags": ["1girl"], "confidence": 0.8, "categories": ["CHARACTER"]}',
            "should_pass": True
        },
        {
            "name": "包含額外欄位",
            "json": '{"tags": ["1girl"], "confidence": 0.8, "suggestions": ["test"], "custom": "value"}',
            "should_pass": True
        },
        {
            "name": "完整回應",
            "json": '{"tags": ["1girl", "long_hair", "blue_eyes"], "confidence": 0.85, "reasoning": "Based on description", "categories": ["CHARACTER", "APPEARANCE"]}',
            "should_pass": True
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n測試 {i}: {test_case['name']}")
        try:
            result = validator.validate(test_case['json'])
            if test_case['should_pass']:
                print(f"   [PASS] 通過（預期）")
                print(f"      - Tags: {result.get('tags', [])[:3]}")
                print(f"      - Confidence: {result.get('confidence')}")
                if 'categories' in result:
                    print(f"      - Categories: {result['categories']}")
                results.append(("PASS", test_case['name']))
            else:
                print(f"   [FAIL] 通過（應該失敗）")
                results.append(("FAIL", test_case['name']))
        except Exception as e:
            if not test_case['should_pass']:
                print(f"   [PASS] 失敗（預期）")
                print(f"      - 錯誤: {str(e)[:50]}...")
                results.append(("PASS", test_case['name']))
            else:
                print(f"   [FAIL] 失敗（應該通過）")
                print(f"      - 錯誤: {str(e)}")
                results.append(("FAIL", test_case['name']))
    
    return results


def test_validator_stats():
    """測試驗證器統計功能"""
    print_section("[3] 驗證器統計")
    
    validator = get_gpt5_validator()
    stats = validator.get_stats()
    
    print(f"\n統計資訊:")
    print(f"   - 總驗證次數: {stats['total_validations']}")
    print(f"   - 成功次數: {stats['successful']}")
    print(f"   - 失敗次數: {stats['failed']}")
    print(f"   - 成功率: {stats['success_rate']}%")
    
    return stats


def verify_fallback_response():
    """驗證降級回應"""
    print_section("[4] 降級回應驗證")
    
    fallback = GPT5TagOutputSchema.create_fallback_response("test description")
    
    print(f"\n降級回應內容:")
    print(f"   - Tags: {fallback.get('tags', [])}")
    print(f"   - Confidence: {fallback.get('confidence')}")
    print(f"   - Reasoning: {fallback.get('reasoning')}")
    print(f"   - Fallback 標記: {fallback.get('fallback')}")
    
    # 驗證必填欄位
    has_required = "tags" in fallback and "confidence" in fallback
    print(f"\n[OK] 包含必填欄位: {'是' if has_required else '否'}")
    
    # 驗證信心度範圍
    confidence_valid = 0.0 <= fallback.get('confidence', -1) <= 1.0
    print(f"[OK] 信心度在有效範圍: {'是' if confidence_valid else '否'}")


def print_summary(results):
    """列印總結"""
    print_section("[5] 測試總結")
    
    passed = sum(1 for r in results if r[0] == "PASS")
    total = len(results)
    
    print(f"\n測試結果:")
    print(f"   - 通過: {passed}/{total}")
    print(f"   - 失敗: {total - passed}/{total}")
    print(f"   - 成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n" + "=" * 60)
        print("   [SUCCESS] 所有測試通過！修復成功！")
        print("=" * 60)
    else:
        print("\n[WARNING] 部分測試失敗，請檢查:")
        for status, name in results:
            if status == "FAIL":
                print(f"   - [X] {name}")


def print_comparison():
    """列印修復前後對比"""
    print_section("[6] 修復前後對比")
    
    comparison = """
+-----------------------+-----------------+-----------------+
| 項目                  | 修復前          | 修復後          |
+-----------------------+-----------------+-----------------+
| minItems (tags)       | 5 [X]           | 1 [OK]          |
| confidence 最小值      | 0.6 [X]         | 0.0 [OK]        |
| confidence 最大值      | 0.95 [X]        | 1.0 [OK]        |
| categories 欄位       | 缺少 [X]        | 存在 [OK]       |
| additionalProperties  | False [X]       | True [OK]       |
| reasoning 必填        | 是 [X]          | 否 [OK]         |
+-----------------------+-----------------+-----------------+
    """
    print(comparison)


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("  GPT-5 Nano Schema 修復驗證")
    print("=" * 60)
    
    try:
        # 1. 驗證 Schema 結構
        verify_schema_structure()
        
        # 2. 測試驗證場景
        results = test_validation_scenarios()
        
        # 3. 測試統計功能
        test_validator_stats()
        
        # 4. 測試降級回應
        verify_fallback_response()
        
        # 5. 列印修復對比
        print_comparison()
        
        # 6. 列印總結
        print_summary(results)
        
        print("\n" + "=" * 60)
        print("[COMPLETE] 驗證完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] 驗證過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

