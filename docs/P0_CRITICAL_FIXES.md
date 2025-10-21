"""
Inspire Agent 工具定義
所有工具都是同步函數（避免 asyncio.run 問題）
"""

from agents import function_tool
from services.supabase_client import get_supabase_service
from config.database_mappings import (
    categorize_tag_by_rules,
    detect_conflicts,
    resolve_alias
)
from config.content_rating import (
    classify_content_level,
    filter_tags_by_user_access
)
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# 全局資料庫服務
db = get_supabase_service()

# Session Context（工具間共享）
from contextvars import ContextVar
session_context = ContextVar('inspire_session', default={})


# ============================================
# 工具 1: understand_intent
# ============================================

@function_tool
def understand_intent(
    core_mood: str,
    visual_elements: list[str],
    style_preference: str,
    clarity_level: str,
    confidence: float,
    next_action: str
) -> dict:
    """
    理解使用者的創作意圖、情緒和氛圍
    
    Args:
        core_mood: 核心情緒/感覺（1-2 個詞）如：孤獨、夢幻、溫柔
        visual_elements: 提到的視覺元素（角色、場景、物件等）
        style_preference: 藝術風格偏好 (anime/realistic/artistic/mixed/unspecified)
        clarity_level: 描述的清晰程度 (crystal_clear/mostly_clear/somewhat_vague/very_vague)
        confidence: 理解的信心度 (0-1)
        next_action: 建議的下一步 (generate_directly/ask_clarification/search_references)
    """
    
    logger.info(f"[understand_intent] Mood: {core_mood}, Clarity: {clarity_level}")
    
    # 構建意圖資料
    intent_data = {
        "core_mood": core_mood,
        "visual_elements": visual_elements,
        "style_preference": style_preference,
        "clarity_level": clarity_level,
        "confidence": confidence,
        "next_action": next_action
    }
    
    # 保存到 Context（其他工具可讀）
    ctx = session_context.get()
    ctx["extracted_intent"] = intent_data
    session_context.set(ctx)
    
    # 返回給 Agent
    return {
        "status": "understood",
        "summary": f"理解：{core_mood}，清晰度 {clarity_level}",
        "next_action": next_action,
        "confidence": confidence
    }


# ============================================
# 工具 2: search_examples
# ============================================

@function_tool
def search_examples(
    search_keywords: list[str],
    search_purpose: str,
    search_strategy: str = "auto",
    min_popularity: int = 1000,
    max_results: int = 10
) -> dict:
    """
    從 Danbooru 資料庫（140K+ 標籤）搜尋類似的高品質參考案例
    
    Args:
        search_keywords: 搜尋的關鍵字（情緒、氛圍、視覺元素）
        search_purpose: 搜尋目的 (find_mood_tags/find_scene_tags/find_style_tags/validate_combination)
        search_strategy: 搜尋策略 (keyword/semantic/auto) - MVP 只支援 keyword
        min_popularity: 最低使用次數（確保品質）
        max_results: 最多返回幾個結果
    """
    
    logger.info(f"[search_examples] Keywords: {search_keywords}, Min popularity: {min_popularity}")
    
    # 獲取使用者權限（從 Context）
    ctx = session_context.get()
    user_access = ctx.get("user_access_level", "all-ages")
    
    # 同步查詢 Supabase（直接調用，不用 asyncio.run）✅
    query = db.client.table('tags_final').select('name, post_count, main_category')
    
    # 應用篩選
    query = query.gte('post_count', min_popularity)
    
    # 關鍵字匹配（OR 條件）
    if search_keywords:
        conditions = [f'name.ilike.%{kw}%' for kw in search_keywords[:5]]
        query = query.or_(','.join(conditions))
    
    # 執行查詢
    query = query.order('post_count', desc=True).limit(max_results * 2)  # 多查一些，過濾後可能不夠
    result = query.execute()
    
    # 過濾 NSFW（基於使用者權限）
    examples = []
    for row in result.data:
        # 檢測內容等級
        content_level = classify_content_level(row["name"])
        
        # 封禁內容跳過
        if content_level == "blocked":
            continue
        
        # 檢查權限
        if content_level == "r18" and user_access not in ["r18"]:
            continue
        
        if content_level == "r15" and user_access == "all-ages":
            continue
        
        # 格式化（嚴格格式）
        examples.append({
            "tag": row["name"],
            "category": categorize_tag_by_rules(row["name"], row.get("main_category")),
            "popularity": row["post_count"],
            "usage_hint": f"{row['post_count']:,} 次使用"
        })
        
        if len(examples) >= max_results:
            break
    
    logger.info(f"[search_examples] Found {len(examples)} examples")
    
    return {
        "examples": examples,
        "search_strategy_used": "keyword",
        "found": len(examples)
    }


# ============================================
# 工具 3: generate_ideas
# ============================================

@function_tool
def generate_ideas(
    ideas: list[dict],
    generation_basis: str = "",
    diversity_achieved: str = "moderate"
) -> dict:
    """
    生成 2-3 個不同的創意方向供使用者選擇
    
    Args:
        ideas: 創意方向列表，每個包含：
            - title: 方向標題
            - concept: 核心概念
            - vibe: 核心氛圍
            - main_tags: 10-15 個核心標籤
            - quick_preview: 簡化 prompt 預覽
            - uniqueness: 這個方向的獨特點
        generation_basis: 基於什麼資訊生成
        diversity_achieved: 方向之間的差異程度 (low/moderate/high)
    """
    
    logger.info(f"[generate_ideas] Generated {len(ideas)} directions")
    
    # 驗證格式
    for idea in ideas:
        assert "title" in idea, "Missing 'title' in idea"
        assert "main_tags" in idea, "Missing 'main_tags' in idea"
        assert len(idea["main_tags"]) >= 10, f"Too few tags: {len(idea['main_tags'])}"
    
    # 保存到 Context
    ctx = session_context.get()
    ctx["generated_directions"] = ideas
    session_context.set(ctx)
    
    return {
        "status": "generated",
        "num_directions": len(ideas),
        "diversity_level": diversity_achieved,
        "ready_for_selection": True
    }


# ============================================
# 工具 4: validate_quality
# ============================================

@function_tool
def validate_quality(
    tags_to_validate: list[str],
    check_aspects: list[str],
    strictness: str = "moderate"
) -> dict:
    """
    驗證 prompt 品質，基於 14 萬標籤資料和 Danbooru 最佳實踐
    
    Args:
        tags_to_validate: 要驗證的標籤列表
        check_aspects: 檢查面向 (validity/conflicts/redundancy/balance/popularity)
        strictness: 檢查嚴格程度 (lenient/moderate/strict)
    """
    
    logger.info(f"[validate_quality] Validating {len(tags_to_validate)} tags")
    
    score = 100
    issues = []
    quick_fixes = {"remove": [], "add": [], "replace": {}}
    
    # 獲取使用者權限
    ctx = session_context.get()
    user_access = ctx.get("user_access_level", "all-ages")
    
    # 解析別名
    resolved_tags = [resolve_alias(t) for t in tags_to_validate]
    
    # 檢查 1: 有效性（查詢資料庫）
    if "validity" in check_aspects:
        # 同步查詢
        result = db.client.table('tags_final')\
            .select('name')\
            .in_('name', resolved_tags)\
            .execute()
        
        valid_tags_set = {row["name"] for row in result.data}
        invalid_tags = [t for t in resolved_tags if t not in valid_tags_set]
        
        if invalid_tags:
            score -= 35
            issues.append({
                "type": "invalid_tag",
                "severity": "critical",
                "description": f"{len(invalid_tags)} 個無效標籤",
                "affected_tags": invalid_tags
            })
            quick_fixes["remove"].extend(invalid_tags)
    
    # 檢查 2: NSFW 和封禁（應用層）
    allowed, removed, meta = filter_tags_by_user_access(resolved_tags, user_access)
    
    if removed:
        blocked_count = meta.get("blocked_count", 0)
        if blocked_count > 0:
            score -= 50  # 封禁內容嚴重扣分
        
        issues.append({
            "type": "content_filtered",
            "severity": "critical" if blocked_count > 0 else "warning",
            "description": f"移除了 {len(removed)} 個不適當標籤",
            "affected_tags": removed
        })
        quick_fixes["remove"].extend(removed)
    
    # 檢查 3: 衝突（應用層規則）
    if "conflicts" in check_aspects:
        conflicts = detect_conflicts(allowed)
        
        if conflicts:
            score -= 25
            for tag_a, tag_b in conflicts:
                issues.append({
                    "type": "conflict",
                    "severity": "warning",
                    "description": f"'{tag_a}' 與 '{tag_b}' 衝突",
                    "affected_tags": [tag_a, tag_b]
                })
                quick_fixes["remove"].append(tag_b)  # 簡化：移除後者
    
    # 檢查 4: 類別平衡
    if "balance" in check_aspects:
        # 批量查詢取得分類
        result = db.client.table('tags_final')\
            .select('name, main_category')\
            .in_('name', allowed)\
            .execute()
        
        categories = set()
        for row in result.data:
            cat = categorize_tag_by_rules(row["name"], row.get("main_category"))
            if cat != "META":
                categories.add(cat)
        
        if len(categories) < 3:
            score -= 20
            issues.append({
                "type": "imbalance",
                "severity": "warning",
                "description": f"類別不足（{len(categories)}/5）",
                "affected_tags": []
            })
    
    logger.info(f"[validate_quality] Score: {score}/100, Issues: {len(issues)}")
    
    return {
        "is_valid": score >= 70,
        "score": score,
        "issues": issues,
        "quick_fixes": quick_fixes,
        "removed_unsafe": removed
    }


# ============================================
# 工具 5: finalize_prompt
# ============================================

@function_tool
def finalize_prompt(
    final_output: dict,
    quality_score: int
) -> dict:
    """
    構建最終的完整 prompt，準備交付給使用者
    
    Args:
        final_output: 包含 title, concept, positive_prompt, negative_prompt, structure, parameters
        quality_score: 品質分數 (0-100)
    """
    
    logger.info(f"[finalize_prompt] Quality: {quality_score}/100")
    
    # 驗證必要欄位
    assert "title" in final_output
    assert "positive_prompt" in final_output
    assert "negative_prompt" in final_output
    
    # 確保 negative_prompt 包含安全前綴
    required_negative = "nsfw, child, loli, shota, gore, lowres, bad_anatomy"
    if required_negative not in final_output["negative_prompt"]:
        final_output["negative_prompt"] = required_negative + ", " + final_output["negative_prompt"]
    
    # 保存到 Context
    ctx = session_context.get()
    ctx["final_output"] = final_output
    ctx["quality_score"] = quality_score
    ctx["current_phase"] = "completed"
    session_context.set(ctx)
    
    return {
        "status": "completed",
        "output": final_output,
        "quality_score": quality_score,
        "ready_to_use": quality_score >= 70
    }

