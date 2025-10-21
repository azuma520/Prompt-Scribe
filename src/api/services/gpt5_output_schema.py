"""
GPT-5 Nano 輸出模式驗證
基於 OpenAI Agents SDK 的結構化輸出方法
"""

import json
import jsonschema
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GPT5TagOutputSchema:
    """GPT-5 Nano 標籤推薦的輸出模式驗證"""
    
    # JSON Schema 定義
    SCHEMA = {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {
                    "type": "string",
                    "minLength": 1,
                    "pattern": "^[a-zA-Z0-9_]+$"  # 只允許字母、數字、底線
                },
                "description": "推薦的標籤列表",
                "minItems": 1,
                "maxItems": 15
            },
            "confidence": {
                "type": "number",
                "description": "推薦信心度 (0.0-1.0)",
                "minimum": 0.0,
                "maximum": 1.0
            },
            "reasoning": {
                "type": "string",
                "description": "推薦理由",
                "minLength": 1,
                "maxLength": 500
            },
            "categories": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "CHARACTER", "APPEARANCE", "CLOTHING", "ACTION", 
                        "SCENE", "STYLE", "OBJECT", "COMPOSITION", "EFFECT"
                    ]
                },
                "description": "標籤分類",
                "uniqueItems": True
            },
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "額外建議",
                "maxItems": 5
            }
        },
        "required": ["tags", "confidence"],
        "additionalProperties": False
    }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """獲取 JSON Schema"""
        return cls.SCHEMA
    
    @classmethod
    def validate_response(cls, response: str) -> Dict[str, Any]:
        """
        驗證 GPT-5 回應是否符合預期格式
        
        Args:
            response: GPT-5 返回的 JSON 字串
            
        Returns:
            驗證後的資料字典
            
        Raises:
            ValueError: 當 JSON 格式或結構驗證失敗時
        """
        try:
            # 1. 解析 JSON
            data = json.loads(response)
            logger.debug(f"JSON 解析成功: {len(str(data))} 字符")
            
            # 2. 使用 JSON Schema 驗證
            jsonschema.validate(data, cls.SCHEMA)
            logger.debug("JSON Schema 驗證成功")
            
            # 3. 額外的業務邏輯驗證
            cls._validate_business_rules(data)
            
            # 4. 添加元資料
            data["validated_at"] = datetime.now().isoformat()
            data["schema_version"] = "1.0"
            
            logger.info(f"✅ 輸出驗證成功: {len(data.get('tags', []))} 個標籤")
            return data
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON 解析失敗: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
            
        except jsonschema.ValidationError as e:
            error_msg = f"JSON Schema 驗證失敗: {e.message}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"   錯誤路徑: {' -> '.join(str(p) for p in e.absolute_path)}")
            raise ValueError(error_msg)
            
        except Exception as e:
            error_msg = f"驗證過程發生未預期錯誤: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
    
    @classmethod
    def _validate_business_rules(cls, data: Dict[str, Any]) -> None:
        """額外的業務邏輯驗證"""
        
        # 驗證標籤數量合理性
        tags = data.get("tags", [])
        if len(tags) < 3:
            logger.warning(f"標籤數量較少: {len(tags)} 個")
        elif len(tags) > 10:
            logger.warning(f"標籤數量較多: {len(tags)} 個")
        
        # 驗證信心度合理性
        confidence = data.get("confidence", 0)
        if confidence < 0.5:
            logger.warning(f"信心度較低: {confidence}")
        elif confidence > 0.95:
            logger.warning(f"信心度過高: {confidence}")
        
        # 驗證標籤格式
        for i, tag in enumerate(tags):
            if not tag.replace("_", "").replace("-", "").isalnum():
                logger.warning(f"標籤 {i+1} 格式可能不標準: {tag}")
        
        # 驗證分類與標籤的對應關係
        categories = data.get("categories", [])
        if categories and len(categories) > len(tags):
            logger.warning(f"分類數量 ({len(categories)}) 多於標籤數量 ({len(tags)})")
    
    @classmethod
    def create_fallback_response(cls, description: str) -> Dict[str, Any]:
        """創建降級回應（當 GPT-5 不可用時）"""
        return {
            "tags": ["1girl", "solo", "artistic"],
            "confidence": 0.6,
            "reasoning": "使用關鍵字匹配降級方案",
            "categories": ["CHARACTER", "STYLE"],
            "suggestions": ["請配置 OpenAI API 以啟用 AI 推薦"],
            "validated_at": datetime.now().isoformat(),
            "schema_version": "1.0",
            "fallback": True
        }
    
    @classmethod
    def get_validation_stats(cls) -> Dict[str, Any]:
        """獲取驗證統計信息"""
        return {
            "schema_version": "1.0",
            "required_fields": ["tags", "confidence"],
            "optional_fields": ["reasoning", "categories", "suggestions"],
            "max_tags": 15,
            "min_tags": 1,
            "confidence_range": [0.0, 1.0],
            "supported_categories": [
                "CHARACTER", "APPEARANCE", "CLOTHING", "ACTION", 
                "SCENE", "STYLE", "OBJECT", "COMPOSITION", "EFFECT"
            ]
        }


class GPT5OutputValidator:
    """GPT-5 輸出驗證器（主要接口）"""
    
    def __init__(self):
        self.schema = GPT5TagOutputSchema()
        self.validation_count = 0
        self.success_count = 0
        self.error_count = 0
    
    def validate(self, response: str) -> Dict[str, Any]:
        """驗證 GPT-5 回應"""
        self.validation_count += 1
        
        try:
            result = self.schema.validate_response(response)
            self.success_count += 1
            return result
        except ValueError as e:
            self.error_count += 1
            logger.error(f"驗證失敗 (#{self.validation_count}): {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取驗證統計"""
        success_rate = (self.success_count / self.validation_count * 100) if self.validation_count > 0 else 0
        
        return {
            "total_validations": self.validation_count,
            "successful": self.success_count,
            "failed": self.error_count,
            "success_rate": round(success_rate, 2),
            "schema_info": self.schema.get_validation_stats()
        }
    
    def reset_stats(self) -> None:
        """重置統計"""
        self.validation_count = 0
        self.success_count = 0
        self.error_count = 0


# 全域驗證器實例
_validator = None

def get_gpt5_validator() -> GPT5OutputValidator:
    """獲取 GPT-5 輸出驗證器實例（單例模式）"""
    global _validator
    if _validator is None:
        _validator = GPT5OutputValidator()
    return _validator
