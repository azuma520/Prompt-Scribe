"""
LLM Recommendations Router
LLM 智能標籤推薦端點
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
import time
from typing import List, Dict

from models.requests import LLMRecommendRequest
from models.responses import (
    TagRecommendationResponse, 
    LLMTagRecommendation,
    QualityAssessment,
    RecommendationMetadata,
    PopularityTier
)
from services.supabase_client import get_supabase_service, SupabaseService
from services.keyword_expander import get_keyword_expander, KeywordExpander
from services.keyword_analyzer import get_keyword_analyzer, KeywordAnalyzer
from services import get_gpt5_nano_client, GPT5NanoClient, GPT5_AVAILABLE

logger = logging.getLogger(__name__)

router = APIRouter()


async def convert_gpt5_result_to_response(
    gpt5_result: Dict,
    db: SupabaseService,
    request: LLMRecommendRequest
) -> TagRecommendationResponse:
    """將 GPT-5 Nano 結果轉換為標準回應格式"""
    try:
        logger.info(f"🔄 Converting GPT-5 result to response format")
        logger.info(f"GPT-5 result keys: {list(gpt5_result.keys())}")
        logger.info(f"GPT-5 result preview: {str(gpt5_result)[:500]}")
        
        # 獲取 GPT-5 推薦的標籤
        gpt5_tags = gpt5_result.get("tags", [])
        gpt5_categories = gpt5_result.get("categories", [])
        gpt5_confidence = gpt5_result.get("confidence", 0.8)
        gpt5_reasoning = gpt5_result.get("reasoning", "")
        gpt5_suggestions = gpt5_result.get("suggestions", [])
        
        logger.info(f"  - Tags count: {len(gpt5_tags)}")
        logger.info(f"  - Tags: {gpt5_tags}")
        logger.info(f"  - Confidence: {gpt5_confidence}")
        
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
        # 將 0-1 的信心度轉換為 0-100 的分數
        overall_score = int(gpt5_confidence * 100)
        balance_score = min(len(category_distribution) * 25, 100)  # 越多分類越好
        
        # 計算流行度分數（基於標籤的平均 post_count）
        if recommended_tags:
            avg_post_count = sum(tag.post_count for tag in recommended_tags) / len(recommended_tags)
            popularity_score = min(int(avg_post_count / 10000 * 100), 100)
        else:
            popularity_score = 0
        
        quality_assessment = QualityAssessment(
            overall_score=overall_score,
            balance_score=balance_score,
            popularity_score=popularity_score,
            warnings=[]
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
        logger.error(f"❌ Failed to convert GPT-5 result: {e}", exc_info=True)
        logger.error(f"GPT-5 result that caused error: {gpt5_result}")
        raise HTTPException(status_code=500, detail=f"Failed to process GPT-5 result: {str(e)}")


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
    expander: KeywordExpander = Depends(get_keyword_expander),
    analyzer: KeywordAnalyzer = Depends(get_keyword_analyzer),
):
    """智能標籤推薦（兩階段搜尋）"""
    start_time = time.time()
    
    try:
        # GPT-5 Nano 優先邏輯保持不變
        if GPT5_AVAILABLE and get_gpt5_nano_client:
            gpt5_client = get_gpt5_nano_client()
            if gpt5_client.is_available():
                logger.info("Using GPT-5 Nano for tag recommendation")
                gpt5_result = await gpt5_client.generate_tags(request.description)
                if gpt5_result:
                    return await convert_gpt5_result_to_response(gpt5_result, db, request)
                else:
                    logger.warning("GPT-5 Nano failed, falling back to two-stage search")

        logger.info("Using two-stage search tag recommendation")
        
        # 1. 關鍵字提取、擴展與分析
        original_keywords, expanded_keywords = expander.expand_query(request.description)
        if not original_keywords:
            raise HTTPException(status_code=400, detail="無法從描述中提取任何關鍵字")

        keyword_weights = analyzer.analyze_keyword_importance(original_keywords)
        primary_keyword = max(keyword_weights, key=keyword_weights.get)
        logger.info(f"Keywords: {original_keywords} -> Expanded: {len(expanded_keywords)}")
        logger.info(f"Primary keyword: '{primary_keyword}'")

        # 2. STAGE 1: 粗篩 - 使用主要關鍵字獲取大量候選標籤
        # 這裡我們直接呼叫 Supabase client 的方法，而不是 search_tags_by_keywords
        # 因為 search_tags_by_keywords 內部已經包含了排序邏輯，而我們只需要原始數據
        query = db.client.table('tags_final').select('name, post_count, main_category, sub_category') \
                                             .ilike('name', f'%{primary_keyword}%') \
                                             .gte('post_count', request.min_popularity) \
                                             .limit(1000) # 獲取大量候選

        result = await query.execute()
        candidates = result.data

        if not candidates:
            logger.warning(f"No candidates found for primary keyword '{primary_keyword}'")
            # 如果主要關鍵字找不到，可以考慮降級到使用所有關鍵字搜尋
            candidates = await db.search_tags_by_keywords(
                keywords=expanded_keywords,
                limit=request.max_tags * 5,
                min_popularity=request.min_popularity,
                use_relevance_ranking=False # 在此階段不需排序
            )
            if not candidates:
                raise HTTPException(status_code=404, detail="找不到與您的描述相關的標籤")

        logger.info(f"Stage 1 (Coarse Filtering) found {len(candidates)} candidates.")

        # 3. STAGE 2: 精排 - 使用 relevance_scorer 對候選標籤進行排序
        # 我們直接呼叫 relevance_scorer 中的 rank_tags_by_relevance
        from services.relevance_scorer import rank_tags_by_relevance

        ranked_candidates = rank_tags_by_relevance(
            tags=candidates,
            keywords=original_keywords, # 使用原始關鍵字進行精確排序
            analyzer=analyzer,
            relevance_weight=0.7
        )
        
        # 4. 分類平衡 (如果啟用) - 這部分邏輯可以複用
        if request.balance_categories:
            selected_tags = []
            categories_used = set()
            for tag in ranked_candidates:
                if len(selected_tags) >= request.max_tags:
                    break
                # 添加到選擇列表，並記錄其分類
                selected_tags.append(tag)
                categories_used.add(tag.get('main_category'))
            
            # 如果分類不夠多樣，嘗試從候選者中補足
            if len(categories_used) < 3 and len(ranked_candidates) > request.max_tags:
                for tag in ranked_candidates[request.max_tags:]:
                    if len(selected_tags) >= request.max_tags:
                        break
                    if tag.get('main_category') not in categories_used:
                        selected_tags.append(tag)
                        categories_used.add(tag.get('main_category'))

            final_tags = selected_tags
        else:
            final_tags = ranked_candidates[:request.max_tags]

        logger.info(f"Stage 2 (Fine Grained Ranking) selected {len(final_tags)} tags.")
        
        # 5. 構建推薦列表
        recommendations = []
        for tag_data in final_tags:
            # 'relevance_score' 來自 rank_tags_by_relevance 的回傳
            confidence = tag_data.get('relevance_score', 0.7)

            recommendations.append(
                LLMTagRecommendation(
                    tag=tag_data['name'],
                    confidence=confidence,
                    popularity_tier=calculate_popularity_tier(tag_data.get('post_count', 0)),
                    post_count=tag_data.get('post_count', 0),
                    category=tag_data.get('main_category') or 'UNKNOWN',
                    subcategory=tag_data.get('sub_category'),
                    match_reason=f"匹配主要關鍵字: '{primary_keyword}'",
                    usage_context=get_usage_context(tag_data.get('main_category')),
                    weight=int(tag_data.get('final_score', 0.7) * 10),
                    related_tags=[]
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


async def _fallback_recommend_tags(
    request: LLMRecommendRequest,
    db: SupabaseService,
    expander: KeywordExpander,
    start_time: float
) -> TagRecommendationResponse:
    """
    GPT-5 不可用時的降級方案
    使用關鍵字匹配和擴展來生成標籤推薦
    """
    try:
        logger.info("Using fallback keyword matching method")
        
        # 1. 關鍵字提取和擴展
        original_keywords = expander.extract_keywords(request.description)
        expanded_keywords = expander.expand_keywords(original_keywords)
        
        # 2. 搜尋相關標籤
        candidates = []
        for keyword in expanded_keywords:
            tags = await db.search_tags(keyword, limit=10)
            candidates.extend(tags)
        
        # 3. 去重和排序
        seen = set()
        unique_candidates = []
        for tag in candidates:
            if tag['name'] not in seen:
                seen.add(tag['name'])
                unique_candidates.append(tag)
        
        # 按 post_count 排序
        unique_candidates.sort(key=lambda x: x.get('post_count', 0), reverse=True)
        
        # 4. 限制數量
        max_tags = request.max_tags or 20
        top_candidates = unique_candidates[:max_tags]
        
        # 5. 構建推薦標籤
        recommendations = []
        for tag in top_candidates:
            recommendation = LLMTagRecommendation(
                tag=tag['name'],
                confidence=0.7,  # 降級方案的固定信心度
                popularity_tier=calculate_popularity_tier(tag.get('post_count', 0)),
                post_count=tag.get('post_count', 0),
                category=tag.get('main_category', tag.get('sub_category', 'UNKNOWN')),
                subcategory=tag.get('sub_category'),
                match_reason="關鍵字匹配（降級方案）",
                usage_context="基於關鍵字搜尋的推薦",
                weight=7,
                related_tags=[]
            )
            recommendations.append(recommendation)
        
        # 6. 計算分類分佈
        category_distribution = {}
        for rec in recommendations:
            category = rec.category
            category_distribution[category] = category_distribution.get(category, 0) + 1
        
        # 7. 構建品質評估
        quality_assessment = QualityAssessment(
            overall_score=0.7,
            warnings=["使用降級方案：GPT-5 不可用"],
            suggestions=["請配置 OpenAI API 金鑰以啟用 AI 推薦功能"]
        )
        
        # 8. 構建建議的 prompt
        suggested_prompt = ", ".join([rec.tag for rec in recommendations])
        
        # 9. 元資料
        processing_time = (time.time() - start_time) * 1000
        metadata = RecommendationMetadata(
            processing_time_ms=round(processing_time, 2),
            total_candidates=len(candidates),
            algorithm="keyword_matching_fallback",
            cache_hit=False,
            keywords_extracted=original_keywords,
            keywords_expanded=expanded_keywords
        )
        
        logger.info(f"Fallback method generated {len(recommendations)} tags")
        
        return TagRecommendationResponse(
            query=request.description,
            recommended_tags=recommendations,
            category_distribution=category_distribution,
            quality_assessment=quality_assessment,
            suggested_prompt=suggested_prompt,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error in fallback method: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fallback recommendation failed: {str(e)}")

