"""
GPT-5 Nano 集成測試
"""

import pytest
import os
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

# 設置測試環境變數
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["OPENAI_MODEL"] = "gpt-5-nano"
os.environ["OPENAI_MAX_TOKENS"] = "500"
os.environ["OPENAI_TEMPERATURE"] = "0.7"
os.environ["OPENAI_TIMEOUT"] = "30"
os.environ["ENABLE_OPENAI_INTEGRATION"] = "true"

from src.api.services.gpt5_nano_client import GPT5NanoClient


class TestGPT5NanoClient:
    """GPT-5 Nano 客戶端測試"""
    
    def test_client_initialization(self):
        """測試客戶端初始化"""
        client = GPT5NanoClient()
        
        assert client.api_key == "test-key"
        assert client.model == "gpt-5-nano"
        assert client.max_tokens == 500
        assert client.temperature == 0.7
        assert client.timeout == 30
        assert client.enabled is True
    
    def test_is_available_without_openai(self):
        """測試沒有 OpenAI 庫時是否可用"""
        with patch('src.api.services.gpt5_nano_client.openai', None):
            client = GPT5NanoClient()
            assert client.is_available() is False
    
    def test_is_available_without_api_key(self):
        """測試沒有 API 金鑰時是否可用"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            client = GPT5NanoClient()
            assert client.is_available() is False
    
    @pytest.mark.asyncio
    async def test_generate_tags_success(self):
        """測試成功生成標籤"""
        # Mock OpenAI 客戶端
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {
            "tags": ["美食", "餐廳", "料理"],
            "categories": ["生活", "飲食"],
            "confidence": 0.9,
            "reasoning": "根據描述推薦相關標籤",
            "suggestions": ["可以嘗試不同的料理類型"]
        }
        '''
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        
        with patch('src.api.services.gpt5_nano_client.openai') as mock_openai:
            mock_client = MagicMock()
            mock_openai.OpenAI.return_value = mock_client
            mock_client.chat.completions.acreate = AsyncMock(return_value=mock_response)
            
            client = GPT5NanoClient()
            result = await client.generate_tags("美食推薦")
            
            assert result is not None
            assert result["tags"] == ["美食", "餐廳", "料理"]
            assert result["categories"] == ["生活", "飲食"]
            assert result["confidence"] == 0.9
            assert "generated_at" in result
            assert result["source"] == "gpt-5-nano"
    
    @pytest.mark.asyncio
    async def test_generate_tags_invalid_json(self):
        """測試無效 JSON 回應"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "無效的 JSON 回應"
        
        with patch('src.api.services.gpt5_nano_client.openai') as mock_openai:
            mock_client = MagicMock()
            mock_openai.OpenAI.return_value = mock_client
            mock_client.chat.completions.acreate = AsyncMock(return_value=mock_response)
            
            client = GPT5NanoClient()
            result = await client.generate_tags("測試")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_generate_tags_api_error(self):
        """測試 API 錯誤"""
        with patch('src.api.services.gpt5_nano_client.openai') as mock_openai:
            mock_client = MagicMock()
            mock_openai.OpenAI.return_value = mock_client
            mock_client.chat.completions.acreate = AsyncMock(
                side_effect=Exception("API 錯誤")
            )
            
            client = GPT5NanoClient()
            result = await client.generate_tags("測試")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """測試連接測試成功"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello, GPT-5 Nano!"
        
        with patch('src.api.services.gpt5_nano_client.openai') as mock_openai:
            mock_client = MagicMock()
            mock_openai.OpenAI.return_value = mock_client
            mock_client.chat.completions.acreate = AsyncMock(return_value=mock_response)
            
            client = GPT5NanoClient()
            result = await client.test_connection()
            
            assert result["available"] is True
            assert result["error"] is None
            assert result["test_response"] == "Hello, GPT-5 Nano!"
            assert "config" in result
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self):
        """測試連接測試失敗"""
        with patch('src.api.services.gpt5_nano_client.openai') as mock_openai:
            mock_client = MagicMock()
            mock_openai.OpenAI.return_value = mock_client
            mock_client.chat.completions.acreate = AsyncMock(
                side_effect=Exception("連接失敗")
            )
            
            client = GPT5NanoClient()
            result = await client.test_connection()
            
            assert result["available"] is False
            assert "連接失敗" in result["error"]


class TestGPT5NanoIntegration:
    """GPT-5 Nano 集成測試"""
    
    @pytest.mark.asyncio
    async def test_convert_gpt5_result_to_response(self):
        """測試 GPT-5 結果轉換"""
        from src.api.routers.llm.recommendations import convert_gpt5_result_to_response
        from models.requests import LLMRecommendRequest
        
        # Mock 資料庫服務
        mock_db = MagicMock()
        mock_db.get_tag_by_name = AsyncMock(return_value={
            'name': '美食',
            'category': 'LIFESTYLE',
            'post_count': 10000
        })
        
        # Mock GPT-5 結果
        gpt5_result = {
            "tags": ["美食"],
            "categories": ["生活"],
            "confidence": 0.9,
            "reasoning": "推薦理由",
            "suggestions": ["建議1"],
            "generated_at": "2024-01-01T00:00:00"
        }
        
        request = LLMRecommendRequest(description="美食推薦")
        
        # 測試轉換
        response = await convert_gpt5_result_to_response(gpt5_result, mock_db, request)
        
        assert response.confidence == 0.9
        assert response.reasoning == "推薦理由"
        assert response.suggestions == ["建議1"]
        assert response.metadata.source == "gpt-5-nano"
        assert len(response.recommended_tags) == 1
        assert response.recommended_tags[0].name == "美食"


if __name__ == "__main__":
    # 運行測試
    pytest.main([__file__, "-v"])
