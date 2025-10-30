"""
內容安全過濾器測試

測試 ContentSafetyFilter 的所有功能：
1. 封禁詞檢測
2. 標籤過濾
3. Moderation API 整合（mock）
4. 安全替代方案

Version: 1.0.0
Date: 2025-01-27
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.api.services.content_safety_filter import ContentSafetyFilter
from openai import AsyncOpenAI


class TestContentSafetyFilter:
    """ContentSafetyFilter 單元測試"""

    def test_is_blocked(self):
        """測試封禁詞檢測"""
        filter = ContentSafetyFilter(enable_moderation=False)
        
        # 應該被封禁
        assert filter.is_blocked("loli") == True
        assert filter.is_blocked("shota") == True
        assert filter.is_blocked("child") == True
        assert filter.is_blocked("young_girl") == True
        
        # 不應該被封禁
        assert filter.is_blocked("1girl") == False
        assert filter.is_blocked("sakura") == False
        assert filter.is_blocked("cute") == False

    @pytest.mark.asyncio
    async def test_filter_tags_blocked(self):
        """測試標籤過濾（封禁詞）"""
        filter = ContentSafetyFilter(enable_moderation=False)
        
        tags = ["1girl", "loli", "cute", "shota", "sakura"]
        safe_tags, removed_tags, metadata = await filter.filter_tags(tags)
        
        # 驗證結果
        assert "loli" not in safe_tags
        assert "shota" not in safe_tags
        assert "1girl" in safe_tags
        assert "cute" in safe_tags
        assert "sakura" in safe_tags
        
        assert "loli" in removed_tags
        assert "shota" in removed_tags
        
        assert metadata["blocked_count"] >= 2

    @pytest.mark.asyncio
    async def test_filter_tags_user_access(self):
        """測試使用者權限過濾"""
        filter = ContentSafetyFilter(enable_moderation=False)
        
        # All-ages 使用者
        tags = ["1girl", "长长的头发", "breasts", "nsfw"]
        safe_tags, removed_tags, metadata = await filter.filter_tags(tags, "all-ages")
        
        # 應該移除 R15 和 R18 內容
        assert "nsfw" not in safe_tags
        # "breasts" 可能是 R15，應該被移除
        assert "1girl" in safe_tags
        
        # R18 使用者
        safe_tags_r18, removed_tags_r18, _ = await filter.filter_tags(tags, "r18")
        # R18 使用者應該能看到更多內容
        assert len(safe_tags_r18) >= len(safe_tags)

    @pytest.mark.asyncio
    async def test_check_user_input_safe(self):
        """測試 Moderation API（安全輸入）"""
        # Mock Moderation API 回應（安全）
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_result.flagged = False
        mock_response.results = [mock_result]
        
        mock_client = MagicMock(spec=AsyncOpenAI)
        mock_client.moderations.create = AsyncMock(return_value=mock_response)
        
        filter = ContentSafetyFilter(openai_client=mock_client, enable_moderation=True)
        
        is_safe, reason = await filter.check_user_input("櫻花樹下的和服少女")
        assert is_safe == True
        assert reason == ""

    @pytest.mark.asyncio
    async def test_check_user_input_unsafe(self):
        """測試 Moderation API（不安全輸入）"""
        # Mock Moderation API 回應（不安全）
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_result.flagged = True
        mock_result.categories = MagicMock()
        mock_result.categories.model_dump.return_value = {
            "sexual": True,
            "violence": False
        }
        mock_response.results = [mock_result]
        
        mock_client = MagicMock(spec=AsyncOpenAI)
        mock_client.moderations.create = AsyncMock(return_value=mock_response)
        
        filter = ContentSafetyFilter(openai_client=mock_client, enable_moderation=True)
        
        is_safe, reason = await filter.check_user_input("不當內容")
        assert is_safe == False
        assert "不適當內容" in reason

    @pytest.mark.asyncio
    async def test_suggest_safe_alternative(self):
        """測試安全替代方案"""
        filter = ContentSafetyFilter(enable_moderation=False)
        
        # 測試未成年人相關封禁
        blocked_tags = ["loli", "child"]
        alternatives = await filter.suggest_safe_alternative(blocked_tags)
        
        assert len(alternatives) > 0
        assert "1girl" in alternatives or "solo" in alternatives
        # 不應該包含封禁詞
        assert "loli" not in alternatives
        assert "child" not in alternatives

    @pytest.mark.asyncio
    async def test_suggest_safe_alternative_r18(self):
        """測試 R18 內容替代方案"""
        filter = ContentSafetyFilter(enable_moderation=False)
        
        blocked_tags = ["nsfw", "explicit"]
        alternatives = await filter.suggest_safe_alternative(blocked_tags)
        
        assert len(alternatives) > 0
        # 應該包含藝術性替代
        assert any(kw in alternatives for kw in ["artistic", "aesthetic", "elegant"])

    def test_get_stats(self):
        """測試統計資訊"""
        filter = ContentSafetyFilter(enable_moderation=False)
        
        # 初始統計應該為 0
        stats = filter.get_stats()
        assert stats["blocks_prevented"] == 0
        assert stats["moderation_checks"] == 0
        assert stats["alternatives_suggested"] == 0

    def test_reset_stats(self):
        """測試重置統計"""
        filter = ContentSafetyFilter(enable_moderation=False)
        
        # 手動設置統計
        filter.stats["blocks_prevented"] = 10
        filter.stats["moderation_checks"] = 5
        
        # 重置
        filter.reset_stats()
        
        stats = filter.get_stats()
        assert stats["blocks_prevented"] == 0
        assert stats["moderation_checks"] == 0

    @pytest.mark.asyncio
    async def test_moderation_api_error_handling(self):
        """測試 Moderation API 錯誤處理"""
        # Mock API 錯誤
        mock_client = MagicMock(spec=AsyncOpenAI)
        mock_client.moderations.create = AsyncMock(side_effect=Exception("API Error"))
        
        filter = ContentSafetyFilter(openai_client=mock_client, enable_moderation=True)
        
        # 錯誤時應該保守處理（允許但記錄）
        is_safe, reason = await filter.check_user_input("測試內容")
        assert is_safe == True  # 失敗時允許
        assert reason == ""

    @pytest.mark.asyncio
    async def test_filter_tags_empty_list(self):
        """測試空列表過濾"""
        filter = ContentSafetyFilter(enable_moderation=False)
        
        safe_tags, removed_tags, metadata = await filter.filter_tags([])
        
        assert len(safe_tags) == 0
        assert len(removed_tags) == 0
        assert metadata["blocked_count"] == 0

    @pytest.mark.asyncio
    async def test_integration_filter_and_alternative(self):
        """整合測試：過濾 + 替代方案"""
        filter = ContentSafetyFilter(enable_moderation=False)
        
        # 包含封禁詞的標籤列表
        tags = ["1girl", "loli", "cute", "shota", "sakura"]
        safe_tags, removed_tags, metadata = await filter.filter_tags(tags)
        
        # 獲取替代方案
        if removed_tags:
            alternatives = await filter.suggest_safe_alternative(removed_tags)
            
            # 驗證：safe_tags + alternatives 應該包含安全內容
            all_safe = safe_tags + alternatives[:3]  # 只取前 3 個替代
            
            assert len(all_safe) > 0
            # 不應該包含封禁詞
            assert "loli" not in all_safe
            assert "shota" not in all_safe
            # 應該有安全替代
            assert any(tag in all_safe for tag in ["1girl", "solo", "sakura"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

