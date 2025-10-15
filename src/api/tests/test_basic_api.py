"""
Basic API Tests
測試基礎 API 端點
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """測試健康檢查端點"""
    
    def test_health_check(self):
        """測試 /health 端點"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data


class TestRootEndpoint:
    """測試根端點"""
    
    def test_root(self):
        """測試 / 端點"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "endpoints" in data


# 注意: 以下測試需要實際的 Supabase 連接才能執行
# 請先配置 .env 檔案後再運行這些測試

@pytest.mark.skip(reason="需要 Supabase 連接")
class TestTagsEndpoint:
    """測試標籤查詢端點"""
    
    def test_get_tags(self):
        """測試 GET /api/v1/tags"""
        response = client.get("/api/v1/tags?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert len(data["data"]) <= 5
    
    def test_get_tags_with_category(self):
        """測試帶分類篩選的標籤查詢"""
        response = client.get("/api/v1/tags?category=CHARACTER&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_get_tag_by_name(self):
        """測試 GET /api/v1/tags/{name}"""
        response = client.get("/api/v1/tags/1girl")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "1girl"


@pytest.mark.skip(reason="需要 Supabase 連接")
class TestSearchEndpoint:
    """測試搜尋端點"""
    
    def test_search_tags(self):
        """測試 POST /api/v1/search"""
        response = client.post(
            "/api/v1/search",
            json={"query": "girl", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


@pytest.mark.skip(reason="需要 Supabase 連接")
class TestStatisticsEndpoint:
    """測試統計端點"""
    
    def test_get_stats(self):
        """測試 GET /api/v1/stats"""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_tags" in data
        assert "category_distribution" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

