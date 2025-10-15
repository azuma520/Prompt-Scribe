"""
LLM Endpoints Tests
測試 LLM 專用端點
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


# 注意: 以下測試需要實際的 Supabase 連接才能執行
# 請先配置 .env 檔案後再運行這些測試

@pytest.mark.skip(reason="需要 Supabase 連接")
class TestRecommendTags:
    """測試標籤推薦端點"""
    
    def test_recommend_tags_basic(self):
        """測試基本標籤推薦"""
        response = client.post(
            "/api/llm/recommend-tags",
            json={
                "description": "a cute girl",
                "max_tags": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # 驗證回應結構
        assert "query" in data
        assert "recommended_tags" in data
        assert "category_distribution" in data
        assert "quality_assessment" in data
        assert "suggested_prompt" in data
        assert "metadata" in data
        
        # 驗證標籤數量
        assert len(data["recommended_tags"]) <= 5
        
        # 驗證每個標籤的結構
        if data["recommended_tags"]:
            tag = data["recommended_tags"][0]
            assert "tag" in tag
            assert "confidence" in tag
            assert "popularity_tier" in tag
            assert "category" in tag
            assert "match_reason" in tag
            assert "usage_context" in tag
    
    def test_recommend_tags_with_options(self):
        """測試帶選項的標籤推薦"""
        response = client.post(
            "/api/llm/recommend-tags",
            json={
                "description": "cyberpunk city",
                "max_tags": 10,
                "exclude_adult": True,
                "balance_categories": True,
                "min_popularity": 1000
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommended_tags"]) <= 10
    
    def test_recommend_tags_empty_description(self):
        """測試空描述"""
        response = client.post(
            "/api/llm/recommend-tags",
            json={
                "description": "",
                "max_tags": 5
            }
        )
        assert response.status_code == 422  # Validation error


@pytest.mark.skip(reason="需要 Supabase 連接")
class TestValidatePrompt:
    """測試標籤驗證端點"""
    
    def test_validate_prompt_basic(self):
        """測試基本標籤驗證"""
        response = client.post(
            "/api/llm/validate-prompt",
            json={
                "tags": ["1girl", "solo", "school_uniform"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # 驗證回應結構
        assert "overall_score" in data
        assert "validation_result" in data
        assert "issues" in data
        assert "suggestions" in data
        assert "category_analysis" in data
    
    def test_validate_prompt_with_conflicts(self):
        """測試有衝突的標籤"""
        response = client.post(
            "/api/llm/validate-prompt",
            json={
                "tags": ["solo", "2girls"]  # 衝突
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["issues"]) > 0
        assert data["overall_score"] < 100
    
    def test_validate_prompt_empty_tags(self):
        """測試空標籤列表"""
        response = client.post(
            "/api/llm/validate-prompt",
            json={
                "tags": []
            }
        )
        assert response.status_code == 422  # Validation error


@pytest.mark.skip(reason="需要 Supabase 連接")
class TestSearchByKeywords:
    """測試關鍵字搜尋端點"""
    
    def test_search_by_keywords_basic(self):
        """測試基本關鍵字搜尋"""
        response = client.post(
            "/api/llm/search-by-keywords",
            json={
                "keywords": "girl uniform",
                "max_results": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # 驗證回應結構
        assert "query" in data
        assert "expanded_keywords" in data
        assert "results" in data
        
        # 驗證擴展關鍵字
        assert len(data["expanded_keywords"]) >= 2
        
        # 驗證結果結構
        if data["results"]:
            result = data["results"][0]
            assert "tag" in result
            assert "relevance_score" in result
            assert "match_type" in result
            assert "popularity_tier" in result


@pytest.mark.skip(reason="需要 Supabase 連接")
class TestPopularByCategory:
    """測試分類熱門標籤端點"""
    
    def test_popular_by_category_all(self):
        """測試取得所有分類的熱門標籤"""
        response = client.get("/api/llm/popular-by-category?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_popular_by_category_specific(self):
        """測試取得特定分類的熱門標籤"""
        response = client.get(
            "/api/llm/popular-by-category?category=CHARACTER&limit=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # 驗證所有標籤都是指定分類
        for tag in data:
            assert tag["category"] == "CHARACTER"


class TestKeywordExpander:
    """測試關鍵字擴展功能"""
    
    def test_keyword_expander_import(self):
        """測試關鍵字擴展器可以導入"""
        from services.keyword_expander import get_keyword_expander
        expander = get_keyword_expander()
        assert expander is not None
    
    def test_keyword_expansion(self):
        """測試關鍵字擴展"""
        from services.keyword_expander import expand_keywords
        
        keywords = ["girl", "happy"]
        expanded = expand_keywords(keywords)
        
        # 應該包含原始關鍵字
        assert "girl" in expanded
        assert "happy" in expanded
        
        # 應該有擴展的同義詞
        assert len(expanded) > len(keywords)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

