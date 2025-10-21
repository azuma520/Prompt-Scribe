"""
測試 GPT-5 結構化輸出驗證
"""

import json
import pytest
from src.api.services.gpt5_output_schema import (
    GPT5TagOutputSchema, 
    GPT5OutputValidator, 
    get_gpt5_validator
)


class TestGPT5TagOutputSchema:
    """測試 GPT-5 標籤輸出模式"""
    
    def test_valid_response(self):
        """測試有效的回應"""
        valid_response = json.dumps({
            "tags": ["1girl", "long_hair", "blue_eyes", "smiling"],
            "confidence": 0.85,
            "reasoning": "這是一個典型的動漫角色描述",
            "categories": ["CHARACTER", "APPEARANCE"]
        })
        
        result = GPT5TagOutputSchema.validate_response(valid_response)
        
        assert result["tags"] == ["1girl", "long_hair", "blue_eyes", "smiling"]
        assert result["confidence"] == 0.85
        assert "validated_at" in result
        assert "schema_version" in result
    
    def test_minimal_valid_response(self):
        """測試最小有效回應（只有必要欄位）"""
        minimal_response = json.dumps({
            "tags": ["1girl", "solo"],
            "confidence": 0.7
        })
        
        result = GPT5TagOutputSchema.validate_response(minimal_response)
        assert len(result["tags"]) == 2
        assert result["confidence"] == 0.7
    
    def test_invalid_json(self):
        """測試無效的 JSON"""
        invalid_json = '{"tags": ["1girl"], "confidence": 0.8'  # 缺少結尾
        
        with pytest.raises(ValueError, match="JSON 解析失敗"):
            GPT5TagOutputSchema.validate_response(invalid_json)
    
    def test_missing_required_fields(self):
        """測試缺少必要欄位"""
        missing_fields = json.dumps({
            "tags": ["1girl"]
            # 缺少 confidence
        })
        
        with pytest.raises(ValueError, match="JSON Schema 驗證失敗"):
            GPT5TagOutputSchema.validate_response(missing_fields)
    
    def test_invalid_confidence_range(self):
        """測試無效的信心度範圍"""
        invalid_confidence = json.dumps({
            "tags": ["1girl"],
            "confidence": 1.5  # 超過最大值
        })
        
        with pytest.raises(ValueError, match="JSON Schema 驗證失敗"):
            GPT5TagOutputSchema.validate_response(invalid_confidence)
    
    def test_invalid_tag_format(self):
        """測試無效的標籤格式"""
        invalid_tags = json.dumps({
            "tags": ["1girl", "long hair"],  # 包含空格
            "confidence": 0.8
        })
        
        with pytest.raises(ValueError, match="JSON Schema 驗證失敗"):
            GPT5TagOutputSchema.validate_response(invalid_tags)
    
    def test_too_many_tags(self):
        """測試標籤數量過多"""
        too_many_tags = json.dumps({
            "tags": [f"tag{i}" for i in range(20)],  # 20 個標籤
            "confidence": 0.8
        })
        
        with pytest.raises(ValueError, match="JSON Schema 驗證失敗"):
            GPT5TagOutputSchema.validate_response(too_many_tags)
    
    def test_invalid_categories(self):
        """測試無效的分類"""
        invalid_categories = json.dumps({
            "tags": ["1girl"],
            "confidence": 0.8,
            "categories": ["INVALID_CATEGORY"]
        })
        
        with pytest.raises(ValueError, match="JSON Schema 驗證失敗"):
            GPT5TagOutputSchema.validate_response(invalid_categories)
    
    def test_fallback_response(self):
        """測試降級回應"""
        fallback = GPT5TagOutputSchema.create_fallback_response("test description")
        
        assert "tags" in fallback
        assert "confidence" in fallback
        assert "fallback" in fallback
        assert fallback["fallback"] is True
        assert len(fallback["tags"]) > 0


class TestGPT5OutputValidator:
    """測試 GPT-5 輸出驗證器"""
    
    def test_validator_initialization(self):
        """測試驗證器初始化"""
        validator = GPT5OutputValidator()
        
        stats = validator.get_stats()
        assert stats["total_validations"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0
        assert stats["success_rate"] == 0
    
    def test_successful_validation(self):
        """測試成功驗證"""
        validator = GPT5OutputValidator()
        
        valid_response = json.dumps({
            "tags": ["1girl", "smiling"],
            "confidence": 0.8
        })
        
        result = validator.validate(valid_response)
        assert result["tags"] == ["1girl", "smiling"]
        
        stats = validator.get_stats()
        assert stats["total_validations"] == 1
        assert stats["successful"] == 1
        assert stats["failed"] == 0
        assert stats["success_rate"] == 100.0
    
    def test_failed_validation(self):
        """測試失敗驗證"""
        validator = GPT5OutputValidator()
        
        invalid_response = '{"tags": ["1girl"]'  # 無效 JSON
        
        with pytest.raises(ValueError):
            validator.validate(invalid_response)
        
        stats = validator.get_stats()
        assert stats["total_validations"] == 1
        assert stats["successful"] == 0
        assert stats["failed"] == 1
        assert stats["success_rate"] == 0.0
    
    def test_multiple_validations(self):
        """測試多次驗證"""
        validator = GPT5OutputValidator()
        
        # 成功驗證
        valid_response = json.dumps({
            "tags": ["1girl"],
            "confidence": 0.8
        })
        validator.validate(valid_response)
        
        # 失敗驗證
        invalid_response = '{"invalid": "json"'
        try:
            validator.validate(invalid_response)
        except ValueError:
            pass
        
        # 再次成功驗證
        validator.validate(valid_response)
        
        stats = validator.get_stats()
        assert stats["total_validations"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == 66.67
    
    def test_reset_stats(self):
        """測試重置統計"""
        validator = GPT5OutputValidator()
        
        # 進行一些驗證
        valid_response = json.dumps({
            "tags": ["1girl"],
            "confidence": 0.8
        })
        validator.validate(valid_response)
        
        assert validator.get_stats()["total_validations"] == 1
        
        # 重置統計
        validator.reset_stats()
        
        stats = validator.get_stats()
        assert stats["total_validations"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0


class TestSingletonValidator:
    """測試單例驗證器"""
    
    def test_singleton_pattern(self):
        """測試單例模式"""
        validator1 = get_gpt5_validator()
        validator2 = get_gpt5_validator()
        
        assert validator1 is validator2
    
    def test_shared_state(self):
        """測試共享狀態"""
        validator1 = get_gpt5_validator()
        validator2 = get_gpt5_validator()
        
        # 使用 validator1 進行驗證
        valid_response = json.dumps({
            "tags": ["1girl"],
            "confidence": 0.8
        })
        validator1.validate(valid_response)
        
        # 檢查 validator2 的統計
        stats = validator2.get_stats()
        assert stats["total_validations"] == 1
        assert stats["successful"] == 1


if __name__ == "__main__":
    # 運行測試
    pytest.main([__file__, "-v"])
