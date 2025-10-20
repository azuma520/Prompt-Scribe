"""
Smart Combinations Router
智能標籤組合建議端點
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
import logging

from ...models.requests import SmartCombinationRequest
from ...models.responses import (
    SmartCombinationResponse,
    TagAnalysisResponse
)
from ...services.tag_combination_analyzer import (
    suggest_tag_combinations,
    suggest_complementary_tags,
    analyze_tag_balance,
    build_complete_prompts
)
from ...services.cache_manager import cache_with_ttl
from ...services.usage_logger import get_usage_logger
import time

router = APIRouter()
logger = logging.getLogger(__name__)
usage_logger = get_usage_logger()


@router.post(
    "/analyze-tags",
    response_model=TagAnalysisResponse,
    summary="標籤分析",
    description="分析標籤的分類平衡和完整性"
)
async def analyze_tags(request: SmartCombinationRequest):
    """
    分析標籤分類平衡
    
    檢查標籤在各個分類的分佈，提供平衡建議
    """
    start_time = time.time()
    
    try:
        # 分析標籤平衡
        balance = analyze_tag_balance(request.tags)
        
        # 建議互補標籤
        complementary = suggest_complementary_tags(request.tags)
        
        # 記錄使用數據
        response_time = (time.time() - start_time) * 1000
        await usage_logger.log_api_call(
            endpoint="/api/llm/analyze-tags",
            request_body={"tags": request.tags},
            response_time_ms=response_time
        )
        
        return TagAnalysisResponse(
            balance_score=balance['balance_score'],
            num_categories=balance['num_categories'],
            category_distribution=balance['category_distribution'],
            suggestions=balance['suggestions'],
            complementary_tags=complementary
        )
        
    except Exception as e:
        logger.error(f"Tag analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"分析失敗: {str(e)}")


@router.post(
    "/suggest-combinations", 
    response_model=SmartCombinationResponse,
    summary="智能組合建議",
    description="基於現有標籤建議智能組合"
)
@cache_with_ttl(ttl_seconds=3600)  # 1小時快取
async def suggest_combinations(request: SmartCombinationRequest):
    """
    智能標籤組合建議
    
    基於已有標籤，建議完整的組合模式
    """
    start_time = time.time()
    
    try:
        # 獲取組合建議
        combinations = suggest_tag_combinations(
            request.tags, 
            max_combinations=request.max_suggestions or 5
        )
        
        # 建立完整 prompt 建議
        complete_prompts = build_complete_prompts(request.tags, combinations)
        
        # 分析標籤平衡
        balance = analyze_tag_balance(request.tags)
        
        # 建議互補標籤
        complementary = suggest_complementary_tags(request.tags)
        
        response_time = (time.time() - start_time) * 1000
        
        # 記錄使用數據
        await usage_logger.log_api_call(
            endpoint="/api/llm/suggest-combinations",
            request_body={"tags": request.tags, "max_suggestions": request.max_suggestions},
            response_time_ms=response_time,
            cache_hit=False  # 新請求
        )
        
        return SmartCombinationResponse(
            base_tags=request.tags,
            combinations=combinations,
            complete_prompts=complete_prompts,
            balance_analysis={
                "balance_score": balance['balance_score'],
                "category_distribution": balance['category_distribution'],
                "suggestions": balance['suggestions']
            },
            complementary_tags=complementary,
            response_time_ms=round(response_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Combination suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"組合建議失敗: {str(e)}")


@router.get(
    "/combination-patterns",
    summary="獲取組合模式",
    description="獲取所有可用的標籤組合模式"
)
async def get_combination_patterns():
    """
    獲取預定義的組合模式
    
    返回所有可用的標籤組合模式供參考
    """
    try:
        from ...services.tag_combination_analyzer import COMBINATION_PATTERNS
        
        # 整理模式資訊
        patterns = []
        for pattern_id, pattern in COMBINATION_PATTERNS.items():
            patterns.append({
                "id": pattern_id,
                "name": pattern["name"],
                "description": pattern["description"],
                "tags": pattern["tags"],
                "popularity": pattern["popularity"],
                "optional_add": pattern.get("optional_add", [])
            })
        
        return {
            "patterns": patterns,
            "total_count": len(patterns)
        }
        
    except Exception as e:
        logger.error(f"Failed to get patterns: {e}")
        raise HTTPException(status_code=500, detail=f"獲取模式失敗: {str(e)}")


@router.post(
    "/build-prompt",
    summary="建立完整 Prompt",
    description="基於標籤和組合建議建立完整的 prompt"
)
async def build_prompt(
    tags: List[str],
    combination_id: Optional[str] = None,
    include_quality: bool = True
):
    """
    建立完整的 prompt
    
    Args:
        tags: 基礎標籤
        combination_id: 組合模式 ID（可選）
        include_quality: 是否包含品質標籤
    """
    try:
        from ...services.tag_combination_analyzer import COMBINATION_PATTERNS
        
        final_tags = tags.copy()
        
        # 如果指定了組合模式，添加相應標籤
        if combination_id and combination_id in COMBINATION_PATTERNS:
            pattern = COMBINATION_PATTERNS[combination_id]
            for tag in pattern["tags"]:
                if tag not in final_tags:
                    final_tags.append(tag)
            
            # 添加部分可選標籤
            optional_tags = pattern.get("optional_add", [])[:3]
            for tag in optional_tags:
                if tag not in final_tags:
                    final_tags.append(tag)
        
        # 添加品質標籤（如果需要）
        if include_quality:
            quality_tags = ["masterpiece", "best_quality", "highres"]
            for tag in quality_tags:
                if tag not in final_tags:
                    final_tags.append(tag)
        
        # 生成不同版本的 prompt
        basic_prompt = ", ".join(tags)
        enhanced_prompt = ", ".join(final_tags)
        
        return {
            "basic_prompt": basic_prompt,
            "enhanced_prompt": enhanced_prompt,
            "added_tags": [tag for tag in final_tags if tag not in tags],
            "total_tags": len(final_tags),
            "combination_used": combination_id
        }
        
    except Exception as e:
        logger.error(f"Build prompt failed: {e}")
        raise HTTPException(status_code=500, detail=f"建立 prompt 失敗: {str(e)}")
