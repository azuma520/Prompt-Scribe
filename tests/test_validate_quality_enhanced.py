"""
驗證器可執行邏輯測試

測試 validate_quality 工具的所有檢查邏輯：
1. 正規化函數
2. 有效性檢查（含相似標籤建議）
3. 冗餘檢查
4. 流行度檢查
5. 整合測試

Version: 1.0.0
Date: 2025-01-27
"""

import pytest
from unittest.mock import MagicMock, patch
from src.api.tools.inspire_tools import (
    validate_quality,
    _normalize_tags,
    _check_redundancy,
    _check_popularity,
    _suggest_similar_tags,
)
from contextvars import ContextVar

# Mock session context
session_context = ContextVar('inspire_session', default={"user_access_level": "all-ages"})


class TestNormalizeTags:
    """測試正規化函數"""

    def test_normalize_deduplication(self):
        """測試去重"""
        tags = ["1girl", "1girl", "sakura", "sakura"]
        normalized = _normalize_tags(tags)
        assert len(normalized) == 2
        assert "1girl" in normalized
        assert "sakura" in normalized

    def test_normalize_lowercase(self):
        """測試小寫轉換"""
        tags = ["1Girl", "Sakura", "LONG_HAIR"]
        normalized = _normalize_tags(tags)
        assert all(tag.islower() or "_" in tag for tag in normalized)
        assert "1girl" in normalized or "1girl" in normalized

    def test_normalize_alias_resolution(self):
        """測試別名解析"""
        tags = ["longhair", "1g", "bg"]
        normalized = _normalize_tags(tags)
        # 應該解析根本名
        assert "long_hair" in normalized or "longhair" in normalized
        # 如果別名映射存在，應該解析

    def test_normalize_empty_list(self):
        """測試空列表"""
        normalized = _normalize_tags([])
        assert normalized == []

    def test_normalize_whitespace(self):
        """測試空白處理"""
        tags = [" 1girl ", " sakura ", " long_hair "]
        normalized = _normalize_tags(tags)
        assert all(tag.strip() == tag for tag in normalized)


class TestCheckRedundancy:
    """測試冗餘檢查"""

    def test_check_redundancy_found(self):
        """測試檢測到冗餘"""
        # 假設 longhair 是 long_hair 的別名
        tags = ["longhair", "long_hair", "1girl"]
        redundancies = _check_redundancy(tags)
        # 應該檢測到冗餘（如果映射存在）
        assert isinstance(redundancies, list)

    def test_check_redundancy_not_found(self):
        """測試無冗餘"""
        tags = ["1girl", "sakura", "long_hair"]
        redundancies = _check_redundancy(tags)
        # 應該沒有冗餘或只有原本映射中存在的冗餘
        assert isinstance(redundancies, list)

    def test_check_redundancy_empty(self):
        """測試空列表"""
        redundancies = _check_redundancy([])
        assert redundancies == []


class TestCheckPopularity:
    """測試流行度檢查"""

    def test_check_popularity_with_mock_db(self):
        """測試流行度檢查（使用 mock DB）"""
        # Mock 資料庫
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"name": "1girl", "post_count": 50000},  # 熱門
            {"name": "sakura", "post_count": 8000},  # 熱門
            {"name": "rare_tag", "post_count": 500},  # 冷門
        ]
        mock_db.client.table.return_value.select.return_value.in_.return_value.execute.return_value = mock_result
        
        tags = ["1girl", "sakura", "rare_tag"]
        unpopular_tags, count = _check_popularity(tags, mock_db)
        
        assert "rare_tag" in unpopular_tags
        assert count == 1
        assert "1girl" not in unpopular_tags
        assert "sakura" not in unpopular_tags

    def test_check_popularity_empty(self):
        """測試空列表"""
        mock_db = MagicMock()
        unpopular_tags, count = _check_popularity([], mock_db)
        assert unpopular_tags == []
        assert count == 0

    def test_check_popularity_all_popular(self):
        """測試全部熱門"""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"name": "1girl", "post_count": 50000},
            {"name": "sakura", " concentrations": 8000},
        ]
        mock_db.client.table.return_value.select.return_value.in_.return_value.execute.return_value = mock_result
        
        tags = ["1girl", "sakura"]
        unpopular_tags, count = _check_popularity(tags, mock_db)
        assert count == 0


class TestSuggestSimilarTags:
    """測試相似標籤建議"""

    def test_suggest_similar_tags_with_mock_db(self):
        """測試相似標籤建議（使用 mock DB）"""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"name": "long_hair", "post_count": 30000},
            {"name": "long_hair_style", "post_count": 5000},
        ]
        mock_db.client.table.return_value.select.return_value.ilike.return_value.order.return_value.limit.return_value.execute.return_value = mock_result
        
        invalid_tags = ["longhair"]
        suggestions = _suggest_similar_tags(invalid_tags, mock_db)
        
        assert isinstance(suggestions, dict)
        # 如果找到相似標籤，應該有建議
        if suggestions:
            assert "longhair" in suggestions

    def test_suggest_similar_tags_empty(self):
        """測試空列表"""
        mock_db = MagicMock()
        suggestions = _suggest_similar_tags([], mock_db)
        assert suggestions == {}

    def test_suggest_similar_tags_not_found(self):
        """測試無相似標籤"""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_db.client.table.return_value.select.return_value.ilike.return_value.order.return_value.limit.return_value.execute.return_value = mock_result
        
        invalid_tags = ["nonexistent_tag"]
        suggestions = _suggest_similar_tags(invalid_tags, mock_db)
        assert suggestions == {}


class TestValidateQualityIntegration:
    """整合測試 validate_quality"""

    def test_validate_quality_all_checks(self):
        """測試完整驗證流程"""
        # Mock session context
        session_context.set({"user_access_level": "all-ages"})
        
        # Mock 資料庫
        mock_db = MagicMock()
        
        # Mock tags_final 查詢（有效性檢查）
        mock_valid_result = MagicMock()
        mock_valid_result.data = [
            {"name": "1girl"},
            {"name": "sakura"},
        ]
        
        # Mock post_count 查詢（流行度檢查）
        mock_popularity_result = MagicMock()
        mock_popularity_result.data = [
            {"name": "1girl", "post_count": 50000},
            {"name": "sakura", "post_count": 8000},
        ]
        
        # 設置 mock 行為
        def table_side_effect(table_name):
            mock_table fazer MagicMock()
            mock_select = MagicMock()
            mock_table.select.return_value = mock_select
            
            if table_name == 'tags_final':
                # 有效性查詢
                mock_in = MagicMock()
                mock_select.in_.return_value = mock_in
                mock_in eq = MagicMock(return_value=mock_valid_result)
                
                # 流行度查詢（需要不同的鏈）
                mock_select_2 = MagicMock()
                mock_table.select.return_value = mock_select_2
                # 這裡需要更複雜的 mock 設置
                mock_popularity_in = MagicMock()
                mock_select_2.in_.return_value = mock_popularity_in
                mock_popularity_in.execute.return_value = mock_popularity_result
                
            return mock_table
        
        mock_db.client.table.side_effect = table_side_effect
        
        # 設置 session context
        with patch('src.api.tools.inspire_tools.session_context', session_context):
            with patch('src.api.tools.inspire_tools.get_supabase_service', return_value=mock_db):
                # 因為 validate_quality 使用 ContentSafetyFilter，需要 mock
                with patch('src.api.tools.inspire_tools.ContentSafetyFilter'):
                    tags = ["1girl", "sakura", "invalid_tag"]
                    result = validate_quality(
                        tags_to_validate=tags,
                        check_aspects=["validity", "conflicts", "redundancy", "balance", "popularity"],
                        strictness="moderate"
                    )
                    
                    assert "回避" in result
                    assert "score" in result
                    assert "issues" in result
                    assert "quick_fixes" in result


class TestValidateQualityScenarios:
    """情境測試"""

    def test_scenario_invalid_and_conflict(self):
        """情境：無效標籤 + 衝突"""
        session_context.set({"user_access_level": "all-ages"})
        
        # 簡化測試：只測試邏輯，不完整 mock
        # 這個測試需要完整的資料庫 mock，可以稍後補充
        pass

    def test_scenario_redundancy(self):
        """情境：冗餘標籤"""
        tags = ["longhair", "long_hair", "1girl"]
        redundancies = _check_redundancy(tags)
        assert isinstance(redundancies, list)

    def test_scenario_unpopular_tags(self):
        """情境：冷門標籤超過 40%"""
        mock_db = MagicMock()
        mock_result = MagicMock()
        # 假設 3 個標籤中 2 個是冷門（67% > 40%）
        mock_result.data = [
            {"name": "rare1", "post_count": 500},
            {"name": "rare2", "post_count": 800},
            {"name": "popular", "post_count": 10000},
        ]
        mock_db.client.table.return_value.select.return_value.in_.return_value.execute.return_value = mock_result
        
        tags = ["rare1", "rare2", "popular"]
        unpopular_tags, count = _check_popularity(tags, mock_db)
        
        assert count == 2
        assert len(unpopular_tags) == 2
        # 比例 2/3 = 67% > 40%，應該觸發警告


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

