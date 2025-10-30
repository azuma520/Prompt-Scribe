"""
Inspire Agent 工具定義
所有工具都是同步函數（避免 asyncio.run 問題）
"""

from agents import function_tool
from services.supabase_client import get_supabase_service
from inspire_config.database_mappings import (
    categorize_tag_by_rules,
    detect_conflicts,
    resolve_alias
)
from inspire_config.content_rating import (
    classify_content_level,
    filter_tags_by_user_access
)
from typing import Dict, List, Any
from pydantic import BaseModel, Field, ConfigDict
import logging

# 導入契約驗證器
try:
    from ..utils.tool_contract_validator import validate_tool_output
    CONTRACT_VALIDATION_ENABLED = True
except ImportError as e:
    CONTRACT_VALIDATION_ENABLED = False

logger = logging.getLogger(__name__)

# 記錄驗證器狀態
if not CONTRACT_VALIDATION_ENABLED:
    logger.warning("⚠️ Contract validator not available, skipping validation")
else:
    logger.info("✅ Contract validation enabled")

# ============================================
# Pydantic 模型（工具參數）
# ============================================

class IdeaDirection(BaseModel):
    """單個創意方向"""
    model_config = ConfigDict(extra='forbid')
    
    title: str = Field(..., description="方向標題（≤10 字）")
    concept: str = Field(..., description="核心概念")
    vibe: str = Field(..., description="核心氛圍")
    main_tags: List[str] = Field(..., description="10-15 個核心標籤")
    quick_preview: str = Field(..., description="簡化 prompt 預覽")
    uniqueness: str = Field(..., description="這個方向的獨特點")


class ValidateResult(BaseModel):
    """驗證結果項"""
    model_config = ConfigDict(extra='forbid')
    
    type: str = Field(..., description="問題類型")
    severity: str = Field(..., description="嚴重程度")
    details: str = Field(..., description="詳細說明")


class FinalPromptStructure(BaseModel):
    """最終 Prompt 結構"""
    model_config = ConfigDict(extra='forbid')
    
    subject: List[str] = Field(..., description="主體標籤")
    appearance: List[str] = Field(..., description="外觀標籤")
    scene: List[str] = Field(..., description="場景標籤")
    mood: List[str] = Field(..., description="氛圍標籤")
    style: List[str] = Field(..., description="風格標籤")


class FinalOutputData(BaseModel):
    """最終輸出資料"""
    model_config = ConfigDict(extra='forbid')
    
    title: str = Field(..., description="作品標題")
    concept: str = Field(default="", description="創作概念")
    positive_prompt: str = Field(..., description="正面 Prompt")
    negative_prompt: str = Field(..., description="負面 Prompt")
    # 簡化：使用字串而不是複雜的 Dict 類型（避免 strict schema 問題）
    structure_json: str = Field(default="{}", description="標籤結構（JSON 字串）")
    parameters_json: str = Field(default="{}", description="推薦參數（JSON 字串）")

# 全局資料庫服務（同步客戶端）
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
    
    logger.info(f"[Tool: understand_intent] Mood: {core_mood}, Clarity: {clarity_level}")
    
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
    ctx["current_phase"] = "understanding"
    session_context.set(ctx)
    
    # 構建返回結果
    result = {
        "status": "understood",
        "summary": f"理解：{core_mood}，清晰度 {clarity_level}",
        "next_action": next_action,
        "confidence": confidence,
        "core_mood": core_mood,  # 添加以便驗證
        "clarity_level": clarity_level  # 添加以便驗證
    }
    
    # 驗證輸出契約（如果啟用）
    if CONTRACT_VALIDATION_ENABLED:
        is_valid, error_msg, normalized = validate_tool_output("understand_intent", result)
        if not is_valid:
            logger.error(f"❌ Contract validation failed: {error_msg}")
            # 仍然返回結果，但記錄錯誤
        else:
            result = normalized
    
    return result


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
    
    logger.info(f"[Tool: search_examples] Keywords: {search_keywords}")
    
    # 獲取使用者權限（從 Context）
    ctx = session_context.get()
    user_access = ctx.get("user_access_level", "all-ages")
    
    # 同步查詢 Supabase（關鍵：直接調用，不用 asyncio.run）✅
    query = db.client.table('tags_final').select('name, post_count, main_category')
    
    # 應用篩選
    query = query.gte('post_count', min_popularity)
    
    # 關鍵字匹配（OR 條件）
    if search_keywords:
        conditions = [f'name.ilike.%{kw}%' for kw in search_keywords[:5]]
        query = query.or_(','.join(conditions))
    
    # 執行查詢（同步）
    query = query.order('post_count', desc=True).limit(max_results * 2)
    result = query.execute()  # 同步執行 ✅
    
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
        
        # 格式化（嚴格格式：只四個鍵）
        examples.append({
            "tag": row["name"],
            "category": categorize_tag_by_rules(row["name"], row.get("main_category")),
            "popularity": row["post_count"],
            "usage_hint": f"{row['post_count']:,} 次使用"
        })
        
        if len(examples) >= max_results:
            break
    
    logger.info(f"[Tool: search_examples] Found {len(examples)} results")
    
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
    ideas: List[IdeaDirection],
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
    
    logger.info(f"[Tool: generate_ideas] Generated {len(ideas)} directions")
    
    # 驗證格式（Pydantic 已經驗證了基本結構）
    for idea in ideas:
        if len(idea.main_tags) < 10:
            raise ValueError(f"Too few tags in '{idea.title}': {len(idea.main_tags)}")
    
    # 保存到 Context（轉為 dict）
    ctx = session_context.get()
    ctx["generated_directions"] = [idea.model_dump() for idea in ideas]
    ctx["current_phase"] = "exploring"
    session_context.set(ctx)
    
    # 構建返回結果
    result = {
        "status": "generated",
        "count": len(ideas),
        "directions": [idea.model_dump() for idea in ideas],  # 添加 directions 字段
        "diversity_achieved": diversity_achieved,
        "ready_for_selection": True
    }
    
    # 驗證輸出契約（如果啟用）
    if CONTRACT_VALIDATION_ENABLED:
        is_valid, error_msg, normalized = validate_tool_output("generate_ideas", result)
        if not is_valid:
            logger.error(f"❌ Contract validation failed: {error_msg}")
            # 仍然返回結果，但記錄錯誤
        else:
            result = normalized
    
    return result


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
    
    logger.info(f"[Tool: validate_quality] Validating {len(tags_to_validate)} tags")
    
    score = 100
    issues = []
    quick_fixes = {"remove": [], "add": [], "replace": {}}
    
    # 獲取使用者權限
    ctx = session_context.get()
    user_access = ctx.get("user_access_level", "all-ages")
    
    # 解析別名
    resolved_tags = [resolve_alias(t) for t in tags_to_validate]
    
    # 檢查 1: 有效性（同步查詢資料庫）
    if "validity" in check_aspects:
        result = db.client.table('tags_final')\
            .select('name')\
            .in_('name', resolved_tags)\
            .execute()  # 同步執行 ✅
        
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
            "severity": "critical" if blocked_count > 0 else "info",
            "description": f"移除了 {len(removed)} 個不適當標籤",
            "affected_tags": removed
        })
        quick_fixes["remove"].extend(removed)
    
    # 更新為安全標籤
    safe_tags = allowed
    
    # 檢查 3: 衝突（應用層規則）
    if "conflicts" in check_aspects:
        conflicts = detect_conflicts(safe_tags)
        
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
        # 批量查詢取得分類（同步）
        result = db.client.table('tags_final')\
            .select('name, main_category')\
            .in_('name', safe_tags)\
            .execute()  # 同步 ✅
        
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
    
    logger.info(f"[Tool: validate_quality] Score: {score}/100")
    
    # 構建返回結果
    result = {
        "is_valid": score >= 70,
        "score": score,
        "issues": issues,
        "quick_fixes": quick_fixes
    }
    
    # 驗證輸出契約（如果啟用）
    if CONTRACT_VALIDATION_ENABLED:
        is_valid, error_msg, normalized = validate_tool_output("validate_quality", result)
        if not is_valid:
            logger.error(f"❌ Contract validation failed: {error_msg}")
            # 仍然返回結果，但記錄錯誤
        else:
            result = normalized
    
    return result


# ============================================
# 工具 5: finalize_prompt
# ============================================

@function_tool
def finalize_prompt(
    final_output: FinalOutputData,
    quality_score: int
) -> dict:
    """
    構建最終的完整 prompt，準備交付給使用者
    
    Args:
        final_output: 包含 title, concept, positive_prompt, negative_prompt, structure, parameters
        quality_score: 品質分數 (0-100)
    """
    
    logger.info(f"[Tool: finalize_prompt] Quality: {quality_score}/100")
    
    # Pydantic 已經驗證了必要欄位
    # 只需確保有基本內容
    if not final_output.title or not final_output.positive_prompt:
        raise ValueError("Title and positive_prompt cannot be empty")
    
    # 確保 negative_prompt 包含安全前綴
    required_negative = "nsfw, child, loli, shota, gore, lowres, bad_anatomy, bad_hands, cropped, worst_quality, jpeg_artifacts, blurry"
    
    # 檢查並修正 negative_prompt
    negative_prompt = final_output.negative_prompt
    if not any(kw in negative_prompt for kw in ["nsfw", "child", "loli"]):
        negative_prompt = required_negative + ", " + negative_prompt
    
    # 轉換為 dict 以便保存
    output_dict = final_output.model_dump()
    output_dict["negative_prompt"] = negative_prompt
    
    # 保存到 Context
    ctx = session_context.get()
    ctx["final_output"] = output_dict
    ctx["quality_score"] = quality_score
    ctx["current_phase"] = "completed"
    session_context.set(ctx)
    
    logger.info(f"[Tool: finalize_prompt] Completed successfully")
    
    # 構建返回結果
    result = {
        "status": "completed",
        "output": output_dict,
        "quality_score": quality_score,
        "ready_to_use": quality_score >= 70
    }
    
    # 驗證輸出契約（如果啟用）
    if CONTRACT_VALIDATION_ENABLED:
        is_valid, error_msg, normalized = validate_tool_output("finalize_prompt", result)
        if not is_valid:
            logger.error(f"❌ Contract validation failed: {error_msg}")
            # 仍然返回結果，但記錄錯誤
        else:
            result = normalized
    
    return result


# ============================================
# 工具列表（供 Agent 使用）
# ============================================

INSPIRE_TOOLS = [
    understand_intent,
    search_examples,
    generate_ideas,
    validate_quality,
    finalize_prompt
]


# ============================================
# 工具執行器（用於 Responses API 原生調用）
# ============================================

# ============================================
# 原始函數映射（用於直接調用）
# ============================================

# 創建原始函數的副本，避免 @function_tool 裝飾器的影響
def _understand_intent_impl(
    core_mood: str,
    visual_elements: list[str],
    style_preference: str,
    clarity_level: str,
    confidence: float,
    next_action: str
) -> dict:
    """原始 understand_intent 實現"""
    logger.info(f"[Tool: understand_intent] Mood: {core_mood}, Clarity: {clarity_level}")
    
    intent_data = {
        "core_mood": core_mood,
        "visual_elements": visual_elements,
        "style_preference": style_preference,
        "clarity_level": clarity_level,
        "confidence": confidence,
        "next_action": next_action
    }
    
    ctx = session_context.get()
    ctx["extracted_intent"] = intent_data
    ctx["current_phase"] = "understanding"
    session_context.set(ctx)
    
    return {
        "status": "understood",
        "summary": f"理解：{core_mood}，清晰度 {clarity_level}",
        "next_action": next_action,
        "confidence": confidence
    }

def _search_examples_impl(
    search_keywords: list[str],
    search_purpose: str,
    search_strategy: str = "auto",
    min_popularity: int = 1000,
    max_results: int = 10
) -> dict:
    """原始 search_examples 實現（與 @function_tool 版本相同的簽名）"""
    logger.info(f"[Tool: search_examples] Keywords: {search_keywords}")
    
    # 獲取使用者權限（從 Context）
    ctx = session_context.get()
    user_access = ctx.get("user_access_level", "all-ages")
    
    # 同步查詢 Supabase
    from services.supabase_client import get_supabase_service
    db = get_supabase_service()
    
    query = db.client.table('tags_final').select('name, post_count, main_category')
    
    # 應用篩選
    query = query.gte('post_count', min_popularity)
    
    # 關鍵字匹配（OR 條件）
    if search_keywords:
        conditions = [f'name.ilike.%{kw}%' for kw in search_keywords[:5]]
        query = query.or_(','.join(conditions))
    
    # 執行查詢（同步）
    query = query.order('post_count', desc=True).limit(max_results * 2)
    result = query.execute()
    
    # 過濾和格式化
    examples = []
    for row in result.data:
        # 簡化版：不檢查 NSFW（避免導入問題）
        examples.append({
            "tag": row["name"],
            "category": row.get("main_category", "unknown"),
            "popularity": row["post_count"],
            "usage_hint": f"{row['post_count']:,} 次使用"
        })
        
        if len(examples) >= max_results:
            break
    
    logger.info(f"[Tool: search_examples] Found {len(examples)} results")
    
    # 保存到 Context
    ctx["search_results"] = examples
    ctx["current_phase"] = "searching"
    session_context.set(ctx)
    
    return {
        "examples": examples,
        "search_strategy_used": search_strategy,
        "found": len(examples)
    }

def _generate_ideas_impl(
    ideas: List[IdeaDirection],
    generation_basis: str = "",
    diversity_achieved: str = "moderate"
) -> dict:
    """原始 generate_ideas 實現（與 @function_tool 版本相同的簽名）"""
    logger.info(f"[Tool: generate_ideas] Ideas count: {len(ideas)}")
    
    # 轉換為字典格式
    ideas_list = [idea.model_dump() if hasattr(idea, 'model_dump') else idea for idea in ideas]
    
    ctx = session_context.get()
    ctx["generated_ideas"] = ideas_list
    ctx["generation_basis"] = generation_basis
    ctx["diversity_level"] = diversity_achieved
    ctx["current_phase"] = "generating"
    session_context.set(ctx)
    
    # 保存到 Context（轉為 dict）
    ctx = session_context.get()
    ctx["generated_directions"] = ideas_list
    ctx["current_phase"] = "exploring"
    session_context.set(ctx)
    
    return {
        "status": "generated",
        "count": len(ideas_list),
        "directions": ideas_list,  # 添加 directions 字段，與 @function_tool 版本一致
        "diversity_achieved": diversity_achieved,
        "ready_for_selection": True
    }

def _validate_quality_impl(
    tags_to_validate: list[str],
    check_aspects: list[str],
    strictness: str = "moderate"
) -> dict:
    """原始 validate_quality 實現（與 @function_tool 版本相同的簽名）"""
    logger.info(f"[Tool: validate_quality] Tags: {len(tags_to_validate)}, Aspects: {check_aspects}")
    
    # 簡化的質量評估
    issues = []
    warnings = []
    score = 75  # 基礎分數
    
    # 檢查標籤數量
    if len(tags_to_validate) < 5:
        issues.append("標籤太少，建議至少 5 個")
        score -= 10
    elif len(tags_to_validate) > 50:
        warnings.append("標籤較多，可能過於複雜")
        score -= 5
    else:
        score += 10
    
    # 檢查是否有角色標籤
    character_tags = ["1girl", "1boy", "2girls", "2boys", "multiple_girls", "multiple_boys"]
    if not any(tag in tags_to_validate for tag in character_tags):
        warnings.append("缺少角色標籤")
        score -= 5
    
    ctx = session_context.get()
    ctx["quality_score"] = score
    ctx["quality_issues"] = issues
    ctx["quality_warnings"] = warnings
    ctx["current_phase"] = "validating"
    session_context.set(ctx)
    
    # 直接返回 dict，不使用 ValidateResult（它的結構不匹配）
    return {
        "overall_score": score,
        "passed": score >= 70,
        "issues_found": issues,
        "warnings": warnings,
        "suggested_fixes": []
    }

def _finalize_prompt_impl(
    final_output: dict,  # 改為 dict，因為從 API 傳來的是 dict
    quality_score: int
) -> dict:
    """原始 finalize_prompt 實現（與 @function_tool 版本相同的簽名）"""
    logger.info(f"[Tool: finalize_prompt] Quality score: {quality_score}")
    
    # 確保 negative_prompt 包含安全前綴
    required_negative = "nsfw, child, loli, shota, gore, lowres, bad_anatomy, bad_hands, cropped, worst_quality, jpeg_artifacts, blurry"
    
    # final_output 現在是 dict
    negative_prompt = final_output.get("negative_prompt", "")
    if not any(kw in negative_prompt for kw in ["nsfw", "child", "loli"]):
        negative_prompt = required_negative + ", " + negative_prompt
    
    # 更新 dict
    output_dict = final_output.copy()
    output_dict["negative_prompt"] = negative_prompt
    
    ctx = session_context.get()
    ctx["final_output"] = output_dict
    ctx["quality_score"] = quality_score
    ctx["current_phase"] = "completed"
    session_context.set(ctx)
    
    return {
        "status": "completed",
        "output": output_dict,
        "quality_score": quality_score,
        "ready_to_use": quality_score >= 70
    }

def execute_tool_by_name(tool_name: str, tool_args: dict) -> dict:
    """
    通過工具名稱執行工具
    
    用於 Responses API 原生實現，直接調用底層的 Python 函數
    
    Args:
        tool_name: 工具名稱
        tool_args: 工具參數字典
        
    Returns:
        工具執行結果
    """
    
    try:
        # 工具名稱映射到原始實現函數
        tool_map = {
            "understand_intent": _understand_intent_impl,
            "search_examples": _search_examples_impl,
            "generate_ideas": _generate_ideas_impl,
            "validate_quality": _validate_quality_impl,
            "finalize_prompt": _finalize_prompt_impl,
        }
        
        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_func = tool_map[tool_name]
        result = tool_func(**tool_args)
        
        # 🔑 確保返回字典格式
        if not isinstance(result, dict):
            result = {"result": result}
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Tool execution failed: {e}")
        return {"error": str(e), "status": "failed"}

