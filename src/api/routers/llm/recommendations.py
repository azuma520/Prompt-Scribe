"""
LLM Recommendations Router
LLM 智能標籤推薦端點
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
import time
from typing import List, Dict

from ...models.requests import LLMRecommendRequest
from ...models.responses import (
    TagRecommendationResponse, 
    LLMTagRecommendation,
    QualityAssessment,
    RecommendationMetadata,
    PopularityTier
)
from ...services.supabase_client import get_supabase_service, SupabaseService
from ...services.keyword_expander import get_keyword_expander, KeywordExpander
from ...services.gpt5_nano_client import get_gpt5_nano_client, GPT5NanoClient

logger = logging.getLogger(__name__)

router = APIRouter()


async def convert_gpt5_result_to_response(
    gpt5_result: Dict,
    db: SupabaseService,
    request: LLMRecommendRequest
) -> TagRecommendationResponse:
    """將 GPT-5 Nano 結果轉換為標準回應格式"""
    try:
        # 獲取 GPT-5 推薦的標籤
        gpt5_tags = gpt5_result.get("tags", [])
        gpt5_categories = gpt5_result.get("categories", [])
        gpt5_confidence = gpt5_result.get("confidence", 0.8)
        gpt5_reasoning = gpt5_result.get("reasoning", "")
        gpt5_suggestions = gpt5_result.get("suggestions", [])
        
        # 從資料庫查詢標籤詳細資訊
        recommended_tags = []
        for tag_name in gpt5_tags:
            tag_info = await db.get_tag_by_name(tag_name)
            if tag_info:
                # 構建 LLMTagRecommendation 物件
                llm_tag = LLMTagRecommendation(
                    tag=tag_info['name'],
                    category=tag_info.get('main_category', tag_info.get('sub_category', 'UNKNOWN')),
                    subcategory=tag_info.get('sub_category'),
                    post_count=tag_info.get('post_count', 0),
                    confidence=gpt5_confidence,  # 保持 0-1 範圍
                    weight=int(gpt5_confidence * 10),  # 轉換為 1-10 分數
                    popularity_tier=calculate_popularity_tier(tag_info.get('post_count', 0)),
                    match_reason=gpt5_reasoning,
                    usage_context=get_usage_context(tag_info.get('main_category', 'UNKNOWN')),
                    related_tags=[]  # 暫時為空，可以後續擴展
                )
                recommended_tags.append(llm_tag)
        
        # 計算分類分佈
        category_distribution = {}
        for tag in recommended_tags:
            category = tag.category
            category_distribution[category] = category_distribution.get(category, 0) + 1
        
        # 構建品質評估
        quality_assessment = QualityAssessment(
            overall_score=gpt5_confidence,
            warnings=[],
            suggestions=gpt5_suggestions
        )
        
        # 構建建議的 prompt
        suggested_prompt = ", ".join([tag.tag for tag in recommended_tags])
        
        # 構建回應
        response = TagRecommendationResponse(
            query=request.description,
            recommended_tags=recommended_tags,
            category_distribution=category_distribution,
            quality_assessment=quality_assessment,
            suggested_prompt=suggested_prompt,
            metadata=RecommendationMetadata(
                processing_time_ms=0,  # 會在外部設置
                total_candidates=len(gpt5_tags),
                algorithm="gpt-5-nano",
                cache_hit=False,
                keywords_extracted=gpt5_tags,
                keywords_expanded=gpt5_tags
            )
        )
        
        logger.info(f"GPT-5 Nano generated {len(recommended_tags)} tags")
        return response
        
    except Exception as e:
        logger.error(f"Failed to convert GPT-5 result: {e}")
        raise HTTPException(status_code=500, detail="Failed to process GPT-5 result")


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


def get_usage_context(category: str) -> str:
    """根據分類返回使用情境說明"""
    context_map = {
        "CHARACTER": "角色核心標籤，影響人物基本特徵和數量",
        "CHARACTER_RELATED": "角色相關標籤，描述外觀、服裝和細節特徵",
        "ACTION_POSE": "動作姿態標籤，影響人物動作、表情和姿勢",
        "ENVIRONMENT": "環境標籤，設定場景背景、地點和氛圍",
        "ART_STYLE": "藝術風格標籤，影響整體畫風和視覺呈現",
        "OBJECTS": "物件標籤，添加場景中的道具和物品",
        "COMPOSITION": "構圖標籤，影響視角、景深和畫面構成",
        "VISUAL_EFFECTS": "視覺效果標籤，添加光影、特效和氛圍",
        "QUALITY": "品質標籤，提升整體畫質和精細度",
        "TECHNICAL": "技術標籤，控制生成參數和風格細節",
    }
    return context_map.get(category, "通用標籤，可用於各種場景")


def calculate_confidence(tag_name: str, keywords: List[str], expanded_keywords: List[str]) -> float:
    """
    計算推薦信心度
    
    Args:
        tag_name: 標籤名稱
        keywords: 原始關鍵字
        expanded_keywords: 擴展後的關鍵字
    """
    # 完全匹配
    if tag_name in keywords:
        return 0.98
    
    # 擴展匹配
    if tag_name in expanded_keywords:
        return 0.92
    
    # 部分匹配
    for keyword in keywords:
        if keyword in tag_name or tag_name in keyword:
            return 0.85
    
    # 分類匹配
    return 0.70


@router.post(
    "/recommend-tags",
    response_model=TagRecommendationResponse,
    summary="🤖 智能標籤推薦",
    description="""
    **LLM 專用的一站式標籤推薦端點**
    
    輸入自然語言描述，返回最適合的標籤組合，包含:
    - 智能關鍵字提取和擴展
    - 分類平衡優化
    - 流行度加權排序
    - 詳細的使用建議和解釋
    
    這是 LLM 最常用的端點，一次調用完成所有工作。
    """
)
async def recommend_tags(
    request: LLMRecommendRequest,
    db: SupabaseService = Depends(get_supabase_service),
    expander: KeywordExpander = Depends(get_keyword_expander)
):
    """智能標籤推薦"""
    start_time = time.time()
    
    try:
        # 0. 嘗試使用 GPT-5 Nano（如果可用）
        gpt5_client = get_gpt5_nano_client()
        if gpt5_client.is_available():
            logger.info("Using GPT-5 Nano for tag recommendation")
            gpt5_result = await gpt5_client.generate_tags(request.description)
            
            if gpt5_result:
                # 轉換 GPT-5 結果為標準格式
                return await convert_gpt5_result_to_response(gpt5_result, db, request)
            else:
                logger.warning("GPT-5 Nano failed, falling back to keyword matching")
        
        # 回退到原有的關鍵字匹配邏輯
        logger.info("Using keyword-based tag recommendation")
        # 1. 提取和擴展關鍵字
        original_keywords, expanded_keywords = expander.expand_query(request.description)
        logger.info(f"Keywords: {original_keywords} -> {expanded_keywords}")
        
        # 2. 搜尋候選標籤
        candidates = await db.search_tags_by_keywords(
            keywords=expanded_keywords,
            limit=request.max_tags * 3,  # 獲取更多候選
            min_popularity=request.min_popularity
        )
        
        # 3. 排序和評分
        scored_tags = []
        for tag in candidates:
            # 計算信心度
            confidence = calculate_confidence(
                tag['name'], 
                original_keywords, 
                expanded_keywords
            )
            
            # 計算綜合權重 (相關性 70% + 流行度 30%)
            relevance_weight = confidence * 0.7
            popularity_weight = min(tag['post_count'] / 100000, 1.0) * 0.3
            combined_weight = relevance_weight + popularity_weight
            
            scored_tags.append({
                'tag': tag,
                'confidence': confidence,
                'weight': int(combined_weight * 10)
            })
        
        # 按綜合權重排序
        scored_tags.sort(key=lambda x: x['weight'], reverse=True)
        
        # 4. 分類平衡 (如果啟用)
        if request.balance_categories:
            # 簡化實現：確保至少包含 2-3 個不同分類
            selected_tags = []
            categories_used = set()
            
            # 第一輪：選擇高分標籤
            for item in scored_tags:
                if len(selected_tags) >= request.max_tags:
                    break
                selected_tags.append(item)
                categories_used.add(item['tag']['main_category'])
            
            scored_tags = selected_tags
        else:
            scored_tags = scored_tags[:request.max_tags]
        
        # 5. 構建推薦列表
        recommendations = []
        for item in scored_tags:
            tag = item['tag']
            recommendations.append(
                LLMTagRecommendation(
                    tag=tag['name'],
                    confidence=item['confidence'],
                    popularity_tier=calculate_popularity_tier(tag['post_count']),
                    post_count=tag['post_count'],
                    category=tag['main_category'] or 'UNKNOWN',
                    subcategory=tag.get('sub_category'),
                    match_reason=f"匹配關鍵字: {', '.join(original_keywords[:3])}",
                    usage_context=get_usage_context(tag['main_category']),
                    weight=item['weight'],
                    related_tags=[]  # TODO: 實作相關標籤推薦
                )
            )
        
        # 6. 計算分類分佈
        category_distribution = {}
        for rec in recommendations:
            category_distribution[rec.category] = category_distribution.get(rec.category, 0) + 1
        
        # 7. 品質評估
        overall_score = int(sum(r.confidence for r in recommendations) / len(recommendations) * 100) if recommendations else 0
        balance_score = min(len(category_distribution) * 25, 100)  # 越多分類越好
        popularity_score = int(sum(r.post_count for r in recommendations) / len(recommendations) / 10000) if recommendations else 0
        popularity_score = min(popularity_score, 100)
        
        quality_assessment = QualityAssessment(
            overall_score=overall_score,
            balance_score=balance_score,
            popularity_score=popularity_score,
            warnings=[]
        )
        
        # 添加警告
        if len(recommendations) < request.max_tags:
            quality_assessment.warnings.append(
                f"僅找到 {len(recommendations)} 個標籤，少於請求的 {request.max_tags} 個"
            )
        if balance_score < 50:
            quality_assessment.warnings.append("標籤分類較為單一，建議增加不同類型的關鍵字")
        
        # 8. 生成建議的 prompt
        suggested_prompt = ", ".join([r.tag for r in recommendations])
        
        # 9. 元資料
        processing_time = (time.time() - start_time) * 1000
        metadata = RecommendationMetadata(
            processing_time_ms=round(processing_time, 2),
            total_candidates=len(candidates),
            algorithm="keyword_matching_v1",
            cache_hit=False,
            keywords_extracted=original_keywords,
            keywords_expanded=expanded_keywords
        )
        
        return TagRecommendationResponse(
            query=request.description,
            recommended_tags=recommendations,
            category_distribution=category_distribution,
            quality_assessment=quality_assessment,
            suggested_prompt=suggested_prompt,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error in recommend_tags: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/test-openai-config",
    summary="🔧 測試 OpenAI 配置",
    description="""
    **測試 GPT-5 Nano 配置和連接**
    
    檢查：
    - API 金鑰是否設置
    - 環境變數是否正確
    - 模型是否可用
    - 連接測試
    """
)
async def test_openai_config():
    """測試 OpenAI 配置"""
    gpt5_client = get_gpt5_nano_client()
    test_result = await gpt5_client.test_connection()
    
    return {
        "status": "success",
        "message": "OpenAI 配置測試完成",
        "result": test_result
    }

