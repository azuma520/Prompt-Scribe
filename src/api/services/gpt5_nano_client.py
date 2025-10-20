"""
GPT-5 Nano 客戶端服務
用於與 OpenAI GPT-5 Nano 模型進行交互
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger(__name__)


class GPT5NanoClient:
    """GPT-5 Nano 客戶端類別"""
    
    def __init__(self):
        """初始化 GPT-5 Nano 客戶端"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # 使用真實存在的模型
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.timeout = int(os.getenv("OPENAI_TIMEOUT", "30"))
        self.enabled = os.getenv("ENABLE_OPENAI_INTEGRATION", "false").lower() == "true"
        
        # 初始化 OpenAI 客戶端
        if self.api_key and openai:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
            if not self.api_key:
                logger.warning("OpenAI API key not found in environment variables")
            if not openai:
                logger.warning("OpenAI library not installed")
    
    def is_available(self) -> bool:
        """檢查 GPT-5 Nano 是否可用"""
        return (
            self.enabled and 
            self.client is not None and 
            self.api_key is not None
        )
    
    async def generate_tags(
        self, 
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        生成標籤推薦
        
        Args:
            description: 用戶描述
            context: 額外上下文資訊
            
        Returns:
            標籤推薦結果或 None
        """
        if not self.is_available():
            logger.warning("GPT-5 Nano not available, skipping")
            return None
        
        try:
            # 構建系統提示詞
            system_prompt = self._build_system_prompt(context)
            
            # 構建用戶提示詞
            user_prompt = self._build_user_prompt(description, context)
            
            # 調用 OpenAI API
            logger.info(f"Calling GPT-5 Nano for description: {description[:100]}...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=self.max_tokens,  # 使用新版 API 參數
                temperature=self.temperature,
                timeout=self.timeout
            )
            
            # 解析回應
            content = response.choices[0].message.content
            logger.info(f"GPT-5 Nano response received: {len(content)} characters")
            
            # 解析 JSON 回應
            result = self._parse_response(content)
            
            # 記錄使用量
            self._log_usage(response)
            
            return result
            
        except Exception as e:
            logger.error(f"GPT-5 Nano API call failed: {e}")
            return None
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """構建系統提示詞"""
        base_prompt = """你是一個專業的標籤推薦助手。根據用戶的描述，推薦最相關的標籤組合。

請以 JSON 格式返回，包含以下欄位：
{
    "tags": ["標籤1", "標籤2", "標籤3"],
    "categories": ["分類1", "分類2"],
    "confidence": 0.95,
    "reasoning": "推薦理由",
    "suggestions": ["建議1", "建議2"]
}

要求：
1. 標籤要具體、相關、有用
2. 分類要準確
3. 信心度要合理（0-1之間）
4. 推薦理由要簡潔明瞭
5. 建議要實用
6. 只返回 JSON，不要其他文字"""
        
        if context:
            context_info = f"\n\n額外上下文：{json.dumps(context, ensure_ascii=False)}"
            base_prompt += context_info
        
        return base_prompt
    
    def _build_user_prompt(self, description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """構建用戶提示詞"""
        prompt = f"請為以下描述推薦標籤：{description}"
        
        if context and context.get("existing_tags"):
            prompt += f"\n\n現有標籤：{', '.join(context['existing_tags'])}"
        
        if context and context.get("user_preferences"):
            prompt += f"\n\n用戶偏好：{context['user_preferences']}"
        
        return prompt
    
    def _parse_response(self, content: str) -> Optional[Dict[str, Any]]:
        """解析 GPT-5 Nano 回應"""
        try:
            # 嘗試直接解析 JSON
            result = json.loads(content)
            
            # 驗證必要欄位
            required_fields = ["tags", "categories", "confidence"]
            if not all(field in result for field in required_fields):
                logger.warning("GPT-5 Nano response missing required fields")
                return None
            
            # 驗證標籤格式
            if not isinstance(result["tags"], list) or len(result["tags"]) == 0:
                logger.warning("GPT-5 Nano response has invalid tags")
                return None
            
            # 添加時間戳
            result["generated_at"] = datetime.now().isoformat()
            result["source"] = "gpt-5-nano"
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT-5 Nano JSON response: {e}")
            logger.error(f"Raw response: {content}")
            return None
    
    def _log_usage(self, response) -> None:
        """記錄 API 使用量"""
        try:
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                logger.info(
                    f"GPT-5 Nano usage - "
                    f"Input: {usage.prompt_tokens}, "
                    f"Output: {usage.completion_tokens}, "
                    f"Total: {usage.total_tokens}"
                )
                
                # 估算成本（需要根據實際價格調整）
                estimated_cost = usage.total_tokens * 0.00001  # 假設價格
                logger.info(f"Estimated cost: ${estimated_cost:.4f}")
                
        except Exception as e:
            logger.error(f"Failed to log usage: {e}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """測試 GPT-5 Nano 連接"""
        test_result = {
            "available": False,
            "error": None,
            "config": {},
            "test_response": None
        }
        
        try:
            # 檢查配置
            test_result["config"] = {
                "api_key_set": bool(self.api_key),
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "timeout": self.timeout,
                "enabled": self.enabled
            }
            
            if not self.is_available():
                test_result["error"] = "GPT-5 Nano not available"
                return test_result
            
            # 測試 API 調用
            test_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一個測試助手。請回應 'Hello, GPT-5 Nano!'"},
                    {"role": "user", "content": "請回應測試訊息"}
                ],
                max_completion_tokens=50,  # 使用新版 API 參數
                temperature=0.1,
                timeout=10
            )
            
            test_result["available"] = True
            test_result["test_response"] = test_response.choices[0].message.content
            
        except Exception as e:
            test_result["error"] = str(e)
            logger.error(f"GPT-5 Nano connection test failed: {e}")
        
        return test_result


# 全域實例
_gpt5_nano_client = None


def get_gpt5_nano_client() -> GPT5NanoClient:
    """獲取 GPT-5 Nano 客戶端實例"""
    global _gpt5_nano_client
    if _gpt5_nano_client is None:
        _gpt5_nano_client = GPT5NanoClient()
    return _gpt5_nano_client
