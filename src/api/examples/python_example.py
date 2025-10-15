"""
Prompt-Scribe API - Python 使用範例
展示如何在 Python 中使用 API
"""
import requests
import json
from typing import Dict, List, Optional


# API 配置
API_BASE_URL = "http://localhost:8000"  # 修改為你的 API 地址
API_KEY = "your-api-key-here"  # 如果需要


class PromptScribeClient:
    """Prompt-Scribe API 客戶端"""
    
    def __init__(self, base_url: str = API_BASE_URL, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def recommend_tags(
        self,
        description: str,
        max_tags: int = 10,
        exclude_adult: bool = True,
        balance_categories: bool = True
    ) -> Dict:
        """
        智能標籤推薦
        
        Args:
            description: 圖像描述
            max_tags: 最多返回標籤數
            exclude_adult: 排除成人內容
            balance_categories: 平衡分類
        
        Returns:
            推薦結果字典
        """
        url = f"{self.base_url}/api/llm/recommend-tags"
        payload = {
            "description": description,
            "max_tags": max_tags,
            "exclude_adult": exclude_adult,
            "balance_categories": balance_categories
        }
        
        response = self.session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def validate_prompt(
        self,
        tags: List[str],
        strict_mode: bool = False
    ) -> Dict:
        """
        驗證標籤品質
        
        Args:
            tags: 標籤列表
            strict_mode: 嚴格模式
        
        Returns:
            驗證結果字典
        """
        url = f"{self.base_url}/api/llm/validate-prompt"
        payload = {
            "tags": tags,
            "strict_mode": strict_mode
        }
        
        response = self.session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def search_by_keywords(
        self,
        keywords: str,
        max_results: int = 10
    ) -> Dict:
        """
        關鍵字搜尋
        
        Args:
            keywords: 搜尋關鍵字
            max_results: 最多結果數
        
        Returns:
            搜尋結果字典
        """
        url = f"{self.base_url}/api/llm/search-by-keywords"
        payload = {
            "keywords": keywords,
            "max_results": max_results
        }
        
        response = self.session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_popular_by_category(
        self,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        獲取分類熱門標籤
        
        Args:
            category: 分類名稱（空值表示所有分類）
            limit: 返回數量
        
        Returns:
            標籤列表
        """
        url = f"{self.base_url}/api/llm/popular-by-category"
        params = {"limit": limit}
        if category:
            params["category"] = category
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()


def example_1_basic_recommendation():
    """範例 1: 基本標籤推薦"""
    print("=" * 60)
    print("範例 1: 基本標籤推薦")
    print("=" * 60)
    
    client = PromptScribeClient()
    
    # 用戶輸入
    user_description = "a lonely girl in cyberpunk city at night"
    
    # 獲取推薦
    result = client.recommend_tags(
        description=user_description,
        max_tags=10
    )
    
    # 顯示結果
    print(f"\n🔍 查詢: {result['query']}")
    print(f"\n📊 品質評估:")
    print(f"  - 整體分數: {result['quality_assessment']['overall_score']}/100")
    print(f"  - 平衡分數: {result['quality_assessment']['balance_score']}/100")
    print(f"  - 流行度分數: {result['quality_assessment']['popularity_score']}/100")
    
    print(f"\n🏷️ 推薦標籤 ({len(result['recommended_tags'])} 個):")
    for i, tag in enumerate(result['recommended_tags'][:5], 1):
        print(f"  {i}. {tag['tag']}")
        print(f"     - 信心度: {tag['confidence']:.2f}")
        print(f"     - 流行度: {tag['popularity_tier']}")
        print(f"     - 原因: {tag['match_reason']}")
        print()
    
    print(f"\n✨ 建議的 Prompt:")
    print(f"  {result['suggested_prompt']}")
    
    print(f"\n⏱️ 處理時間: {result['metadata']['processing_time_ms']:.2f}ms")


def example_2_validation():
    """範例 2: 標籤驗證"""
    print("\n" + "=" * 60)
    print("範例 2: 標籤驗證")
    print("=" * 60)
    
    client = PromptScribeClient()
    
    # 要驗證的標籤
    tags = ["1girl", "solo", "school_uniform", "classroom"]
    
    # 驗證
    result = client.validate_prompt(tags=tags)
    
    # 顯示結果
    print(f"\n🔍 驗證標籤: {', '.join(tags)}")
    print(f"\n📊 驗證結果: {result['validation_result'].upper()}")
    print(f"整體分數: {result['overall_score']}/100")
    
    if result['issues']:
        print(f"\n⚠️ 發現問題 ({len(result['issues'])} 個):")
        for issue in result['issues']:
            print(f"  - {issue['message']}")
            print(f"    建議: {issue['suggestion']}")
    else:
        print("\n✅ 沒有發現問題")
    
    print(f"\n💡 分類分析:")
    for cat, count in result['category_analysis']['distribution'].items():
        print(f"  - {cat}: {count} 個標籤")
    
    print(f"\n📝 建議:")
    for rec in result['category_analysis']['recommendations']:
        print(f"  - {rec}")


def example_3_complete_workflow():
    """範例 3: 完整工作流程"""
    print("\n" + "=" * 60)
    print("範例 3: 完整工作流程 (推薦 + 驗證)")
    print("=" * 60)
    
    client = PromptScribeClient()
    
    # 步驟 1: 獲取推薦
    print("\n步驟 1: 獲取標籤推薦...")
    description = "cute anime girl with long pink hair"
    result = client.recommend_tags(
        description=description,
        max_tags=8,
        balance_categories=True
    )
    
    suggested_tags = [tag['tag'] for tag in result['recommended_tags']]
    print(f"推薦標籤: {', '.join(suggested_tags)}")
    
    # 步驟 2: 驗證品質
    print("\n步驟 2: 驗證標籤品質...")
    validation = client.validate_prompt(tags=suggested_tags)
    
    print(f"驗證分數: {validation['overall_score']}/100")
    
    if validation['overall_score'] >= 80:
        print("✅ 品質良好，可以使用")
        final_prompt = validation['suggestions']['improved_prompt']
    else:
        print("⚠️ 品質需要改進")
        final_prompt = validation['suggestions']['improved_prompt']
    
    print(f"\n✨ 最終 Prompt:")
    print(f"  {final_prompt}")


def example_4_search():
    """範例 4: 關鍵字搜尋"""
    print("\n" + "=" * 60)
    print("範例 4: 關鍵字搜尋")
    print("=" * 60)
    
    client = PromptScribeClient()
    
    # 搜尋
    keywords = "cyberpunk neon"
    result = client.search_by_keywords(
        keywords=keywords,
        max_results=5
    )
    
    print(f"\n🔍 搜尋: {keywords}")
    print(f"擴展後的關鍵字: {', '.join(result['expanded_keywords'])}")
    
    print(f"\n📋 搜尋結果 ({len(result['results'])} 個):")
    for i, tag in enumerate(result['results'], 1):
        print(f"  {i}. {tag['tag']}")
        print(f"     - 相關度: {tag['relevance_score']:.2f}")
        print(f"     - 匹配類型: {tag['match_type']}")
        print(f"     - 匹配關鍵字: {tag['matched_keyword']}")


def example_5_popular_tags():
    """範例 5: 熱門標籤"""
    print("\n" + "=" * 60)
    print("範例 5: 取得熱門標籤")
    print("=" * 60)
    
    client = PromptScribeClient()
    
    # 取得 CHARACTER 分類的熱門標籤
    tags = client.get_popular_by_category(
        category="CHARACTER",
        limit=10
    )
    
    print(f"\n🔥 CHARACTER 分類熱門標籤:")
    for i, tag in enumerate(tags, 1):
        print(f"  {i}. {tag['tag']}")
        print(f"     - 流行度: {tag['tier']}")
        print(f"     - 使用次數: {tag['popularity_score']:,}")


if __name__ == "__main__":
    print("🤖 Prompt-Scribe API - Python 使用範例\n")
    
    try:
        # 執行所有範例
        example_1_basic_recommendation()
        example_2_validation()
        example_3_complete_workflow()
        example_4_search()
        example_5_popular_tags()
        
        print("\n" + "=" * 60)
        print("✅ 所有範例執行完成!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 錯誤: 無法連接到 API")
        print("請確保 API 服務正在運行: python src/api/main.py")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")

