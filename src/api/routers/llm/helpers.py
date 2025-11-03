"""
LLM Helpers Router
LLM 輔助功能端點
"""
from fastapi import APIRouter, HTTPException, Query, Depends
import logging
from typing import Optional

from ...models.requests import LLMSearchByKeywordsRequest, CategoryEnum
from ...models.responses import SearchByKeywordsResponse, SearchResult, PopularityTier, MatchType
from ...services.supabase_client import get_supabase_service, SupabaseService
from ...services.keyword_expander import get_keyword_expander, KeywordExpander

logger = logging.getLogger(__name__)

router = APIRouter()


def calculate_popularity_tier(post_count: int) -> PopularityTier:
    """計算流行度等級"""
    if post_count > 100000:
        return PopularityTier.VERY_POPULAR
    elif post_count > 10000:
        return PopularityTier.POPULAR
    elif post_count > 1000:
        return PopularityTier.MODERATE
    else:
        return PopularityTier.NICHE


@router.post(
    "/search-by-keywords",
    response_model=SearchByKeywordsResponse,
    summary="🔍 智能關鍵字搜尋",
    description="""
    **基於關鍵字的智能搜尋（無需向量化）**
    
    特點：
    - 自動擴展同義詞
    - 智能排序（相關性 + 流行度）
    - 支援多語言輸入
    - 快速響應（< 300ms）
    
    適合 80% 的常規查詢。
    """
)
async def search_by_keywords(
    request: LLMSearchByKeywordsRequest,
    db: SupabaseService = Depends(get_supabase_service),
    expander: KeywordExpander = Depends(get_keyword_expander)
):
    """智能關鍵字搜尋"""
    try:
        # 1. 擴展關鍵字
        original_keywords, expanded_keywords = expander.expand_query(request.keywords)
        logger.info(f"Search keywords: {original_keywords} -> {expanded_keywords}")
        
        # 2. 搜尋標籤
        results = await db.search_tags_by_keywords(
            keywords=expanded_keywords,
            limit=request.max_results,
            min_popularity=100 if request.boost_popular else 0
        )
        
        # 3. 構建結果
        search_results = []
        for tag in results:
            # 確定匹配類型
            tag_name = tag['name']
            match_type = MatchType.CATEGORY_MATCH
            matched_keyword = ""
            
            if tag_name in original_keywords:
                match_type = MatchType.EXACT_MATCH
                matched_keyword = tag_name
            elif tag_name in expanded_keywords:
                match_type = MatchType.SYNONYM_MATCH
                # 找出原始關鍵字
                for orig_kw in original_keywords:
                    if tag_name in expander.expand_keyword(orig_kw):
                        matched_keyword = f"{orig_kw} → {tag_name}"
                        break
            else:
                # 部分匹配
                for kw in original_keywords:
                    if kw in tag_name or tag_name in kw:
                        match_type = MatchType.PARTIAL_MATCH
                        matched_keyword = kw
                        break
            
            # 計算相關性分數
            relevance_score = 0.98 if match_type == MatchType.EXACT_MATCH else \
                             0.92 if match_type == MatchType.SYNONYM_MATCH else \
                             0.85 if match_type == MatchType.PARTIAL_MATCH else 0.70
            
            search_results.append(
                SearchResult(
                    tag=tag_name,
                    relevance_score=relevance_score,
                    match_type=match_type,
                    matched_keyword=matched_keyword or "分類匹配",
                    popularity_tier=calculate_popularity_tier(tag['post_count']),
                    post_count=tag['post_count']
                )
            )
        
        return SearchByKeywordsResponse(
            query=request.keywords,
            expanded_keywords=expanded_keywords,
            results=search_results
        )
        
    except Exception as e:
        logger.error(f"Error in search_by_keywords: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/popular-by-category",
    response_model=list,
    summary="📊 分類熱門標籤",
    description="""
    **取得特定分類中最熱門的標籤**
    
    使用場景：
    - LLM 需要某個分類的常用標籤
    - 提供給用戶選擇的標籤清單
    - 了解各分類的代表性標籤
    """
)
async def get_popular_by_category(
    category: Optional[CategoryEnum] = Query(None, description="分類名稱（空值表示所有分類）"),
    limit: int = Query(20, ge=1, le=100, description="返回數量"),
    min_popularity: int = Query(1000, ge=0, description="最低流行度"),
    db: SupabaseService = Depends(get_supabase_service)
):
    """取得分類熱門標籤"""
    try:
        tags, _ = await db.get_tags(
            limit=limit,
            category=category.value if category else None,
            order_by='post_count',
            order_desc=True
        )
        
        # 過濾流行度
        filtered_tags = [
            tag for tag in tags 
            if tag['post_count'] >= min_popularity
        ]
        
        # 構建回應
        results = []
        for tag in filtered_tags:
            results.append({
                'tag': tag['name'],
                'category': tag['main_category'],
                'popularity_score': tag['post_count'],
                'tier': calculate_popularity_tier(tag['post_count']).value,
                'usage_tip': f"用於 {tag['main_category']} 分類，使用次數 {tag['post_count']:,}"
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error in get_popular_by_category: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

