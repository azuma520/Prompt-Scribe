"""
GPT-5 Schema 一致性測試
驗證 Responses API 和 Chat Completions API 的 schema 定義一致性
"""

import pytest
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src" / "api"))

from services.gpt5_nano_client import get_gpt5_nano_client
from services.gpt5_output_schema import get_gpt5_validator, GPT5TagOutputSchema


class TestSchemaConsistency:
    """測試 Schema 一致性"""
    
    def test_schema_definitions(self):
        """測試 Schema 定義的基本一致性"""
        validator = get_gpt5_validator()
        schema = GPT5TagOutputSchema.get_schema()
        
        # 驗證必填欄位
        assert "tags" in schema["required"]
        assert "confidence" in schema["required"]
        assert "reasoning" not in schema["required"]  # ✅ 應該是可選的
        
        # 驗證 additionalProperties
        assert schema["additionalProperties"] == True  # ✅ 應該允許額外欄位
        
        print("✅ Schema 定義測試通過")
    
    def test_tags_validation(self):
        """測試標籤欄位驗證"""
        schema = GPT5TagOutputSchema.get_schema()
        tags_schema = schema["properties"]["tags"]
        
        # 驗證最小/最大數量
        assert tags_schema["minItems"] == 1  # ✅ 最小值應該是 1
        assert tags_schema["maxItems"] == 15
        
        print("✅ 標籤驗證測試通過")
    
    def test_confidence_range(self):
        """測試信心度範圍"""
        schema = GPT5TagOutputSchema.get_schema()
        confidence_schema = schema["properties"]["confidence"]
        
        # 驗證範圍
        assert confidence_schema["minimum"] == 0.0  # ✅ 應該是 0.0
        assert confidence_schema["maximum"] == 1.0  # ✅ 應該是 1.0
        
        print("✅ 信心度範圍測試通過")
    
    def test_categories_field_exists(self):
        """測試 categories 欄位存在"""
        schema = GPT5TagOutputSchema.get_schema()
        
        # 驗證 categories 欄位存在
        assert "categories" in schema["properties"]
        categories_schema = schema["properties"]["categories"]
        
        # 驗證枚舉值
        expected_categories = [
            "CHARACTER", "APPEARANCE", "CLOTHING", "ACTION", 
            "SCENE", "STYLE", "OBJECT", "COMPOSITION", "EFFECT"
        ]
        assert categories_schema["items"]["enum"] == expected_categories
        
        print("✅ Categories 欄位測試通過")
    
    def test_minimal_valid_response(self):
        """測試最小有效回應"""
        validator = get_gpt5_validator()
        
        # 最小有效回應（只有必填欄位）
        minimal_response = """
        {
            "tags": ["1girl"],
            "confidence": 0.5
        }
        """
        
        result = validator.validate(minimal_response)
        assert result is not None
        assert len(result["tags"]) == 1  # ✅ 應該接受 1 個標籤
        assert result["confidence"] == 0.5
        
        print("✅ 最小有效回應測試通過")
    
    def test_full_response_with_categories(self):
        """測試完整回應（包含 categories）"""
        validator = get_gpt5_validator()
        
        full_response = """
        {
            "tags": ["1girl", "long_hair", "blue_eyes"],
            "confidence": 0.85,
            "reasoning": "Based on the description",
            "categories": ["CHARACTER", "APPEARANCE"]
        }
        """
        
        result = validator.validate(full_response)
        assert result is not None
        assert "categories" in result  # ✅ 應該包含 categories
        assert len(result["categories"]) == 2
        
        print("✅ 完整回應測試通過")
    
    def test_low_confidence_acceptance(self):
        """測試接受低信心度"""
        validator = get_gpt5_validator()
        
        low_confidence_response = """
        {
            "tags": ["abstract"],
            "confidence": 0.3
        }
        """
        
        result = validator.validate(low_confidence_response)
        assert result is not None
        assert result["confidence"] == 0.3  # ✅ 應該接受低信心度
        
        print("✅ 低信心度測試通過")
    
    def test_additional_properties_allowed(self):
        """測試允許額外屬性"""
        validator = get_gpt5_validator()
        
        response_with_extra = """
        {
            "tags": ["1girl"],
            "confidence": 0.8,
            "suggestions": ["Consider adding more details"],
            "custom_field": "custom_value"
        }
        """
        
        result = validator.validate(response_with_extra)
        assert result is not None
        assert "suggestions" in result  # ✅ 應該保留額外欄位
        assert "custom_field" in result
        
        print("✅ 額外屬性測試通過")


class TestClientConfiguration:
    """測試客戶端配置"""
    
    def test_client_initialization(self):
        """測試客戶端初始化"""
        client = get_gpt5_nano_client()
        
        assert client is not None
        assert hasattr(client, 'is_gpt5')
        assert hasattr(client, 'has_responses_api')
        
        print("✅ 客戶端初始化測試通過")
        print(f"   - 模型: {client.model}")
        print(f"   - GPT-5 系列: {client.is_gpt5}")
        print(f"   - Responses API: {client.has_responses_api}")
    
    def test_validation_stats(self):
        """測試驗證統計功能"""
        client = get_gpt5_nano_client()
        stats = client.get_validation_stats()
        
        assert "total_validations" in stats
        assert "successful" in stats
        assert "failed" in stats
        assert "success_rate" in stats
        
        print("✅ 驗證統計測試通過")
        print(f"   - 總驗證次數: {stats['total_validations']}")
        print(f"   - 成功率: {stats['success_rate']}%")


@pytest.mark.asyncio
async def test_fallback_response():
    """測試降級回應"""
    fallback = GPT5TagOutputSchema.create_fallback_response("test description")
    
    assert "tags" in fallback
    assert "confidence" in fallback
    assert "reasoning" in fallback
    assert fallback["fallback"] == True
    
    # 驗證降級回應的信心度在有效範圍內
    assert 0.0 <= fallback["confidence"] <= 1.0
    
    print("✅ 降級回應測試通過")


def run_all_tests():
    """執行所有測試"""
    print("=" * 60)
    print("🧪 GPT-5 Schema 一致性測試")
    print("=" * 60)
    
    # Schema 一致性測試
    test_schema = TestSchemaConsistency()
    test_schema.test_schema_definitions()
    test_schema.test_tags_validation()
    test_schema.test_confidence_range()
    test_schema.test_categories_field_exists()
    test_schema.test_minimal_valid_response()
    test_schema.test_full_response_with_categories()
    test_schema.test_low_confidence_acceptance()
    test_schema.test_additional_properties_allowed()
    
    print()
    
    # 客戶端配置測試
    test_client = TestClientConfiguration()
    test_client.test_client_initialization()
    test_client.test_validation_stats()
    
    print()
    
    # 降級回應測試
    import asyncio
    asyncio.run(test_fallback_response())
    
    print()
    print("=" * 60)
    print("✅ 所有測試通過！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()





