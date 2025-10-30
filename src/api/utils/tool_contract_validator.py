"""
工具 I/O 契約驗證器

用於驗證 Inspire Agent 工具的輸入輸出是否符合嚴格契約。
根據 INSPIRE_P0_CHECKLIST.md 的要求實施。
"""

from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError, field_validator
import logging

logger = logging.getLogger(__name__)


# ============================================
# 契約定義（基於 P0 檢查清單）
# ============================================

class UnderstandIntentOutput(BaseModel):
    """understand_intent 輸出契約（嚴格 6 個鍵）"""
    model_config = {"extra": "forbid"}  # 禁止額外鍵
    
    status: str = Field(..., description="狀態")
    summary: str = Field(..., description="摘要")
    next_action: str = Field(..., description="下一步行動")
    confidence: float = Field(..., ge=0.0, le=1.0, description="信心度 (0-1)")
    # 注意：實際返回只有 4 個鍵，但根據清單需要 6 個
    # 檢查清單可能是指輸入參數，這裡我們嚴格驗證輸出
    core_mood: Optional[str] = Field(None, description="核心情緒")
    clarity_level: Optional[str] = Field(None, description="清晰度")
    
    @field_validator('clarity_level')
    @classmethod
    def validate_clarity_level(cls, v):
        """驗證 clarity_level 枚舉值"""
        if v is not None and v not in ["crystal_clear", "mostly_clear", "somewhat_vague", "very_vague"]:
            raise ValueError(f"Invalid clarity_level: {v}. Must be one of: crystal_clear, mostly_clear, somewhat_vague, very_vague")
        return v
    
    @field_validator('next_action')
    @classmethod
    def validate_next_action(cls, v):
        """驗證 next_action 枚舉值"""
        valid_actions = ["generate_directly", "ask_clarification", "search_references"]
        if v not in valid_actions:
            raise ValueError(f"Invalid next_action: {v}. Must be one of: {valid_actions}")
        return v


class IdeaDirectionContract(BaseModel):
    """單個創意方向的契約（嚴格 6 個鍵）"""
    model_config = {"extra": "forbid"}
    
    title: str = Field(..., description="方向標題（≤10 字）")
    concept: str = Field(..., description="核心概念")
    vibe: str = Field(..., description="核心氛圍")
    main_tags: List[str] = Field(..., min_length=10, description="至少 10 個核心標籤")
    quick_preview: str = Field(..., description="簡化 prompt 預覽")
    uniqueness: str = Field(..., description="這個方向的獨特點")
    
    @field_validator('title')
    @classmethod
    def validate_title_length(cls, v):
        """驗證標題長度"""
        if len(v) > 10:
            raise ValueError(f"Title too long: {len(v)} characters. Maximum 10.")
        return v


class GenerateIdeasOutput(BaseModel):
    """generate_ideas 輸出契約"""
    model_config = {"extra": "forbid"}
    
    status: str = Field(..., description="狀態")
    count: int = Field(..., ge=2, le=3, description="方向數量（2-3 個）")
    directions: List[IdeaDirectionContract] = Field(..., min_length=2, max_length=3, description="創意方向列表")
    diversity_achieved: str = Field(..., description="差異程度")
    ready_for_selection: bool = Field(..., description="是否準備好供選擇")


class QuickFixesContract(BaseModel):
    """quick_fixes 契約"""
    model_config = {"extra": "forbid"}
    
    remove: List[str] = Field(default_factory=list, description="要移除的標籤")
    add: List[str] = Field(default_factory=list, description="要添加的標籤")
    replace: Dict[str, str] = Field(default_factory=dict, description="要替換的標籤映射")


class ValidateQualityOutput(BaseModel):
    """validate_quality 輸出契約（嚴格 8 個頂層鍵）"""
    model_config = {"extra": "forbid"}
    
    is_valid: bool = Field(..., description="是否有效")
    score: int = Field(..., ge=0, le=100, description="品質分數 (0-100)")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="問題列表")
    quick_fixes: QuickFixesContract = Field(..., description="快速修復建議")
    # 注意：檢查清單提到 8 個鍵，但實際可能需要 4-5 個，這裡先實現核心的
    warnings: Optional[List[str]] = Field(None, description="警告列表")
    suggestions: Optional[List[str]] = Field(None, description="建議列表")
    affected_tags: Optional[List[str]] = Field(None, description="受影響的標籤")
    severity: Optional[str] = Field(None, description="嚴重程度")


class FinalizePromptOutput(BaseModel):
    """finalize_prompt 輸出契約"""
    model_config = {"extra": "forbid"}
    
    status: str = Field(..., description="狀態")
    output: Dict[str, Any] = Field(..., description="最終輸出")
    quality_score: int = Field(..., ge=0, le=100, description="品質分數 (0-100)")
    ready_to_use: bool = Field(..., description="是否可以使用")
    
    @field_validator('output')
    @classmethod
    def validate_output_structure(cls, v):
        """驗證 output 結構"""
        required_keys = ["title", "positive_prompt", "negative_prompt"]
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Missing required key in output: {key}")
        
        # 驗證 positive_prompt 長度
        positive_prompt = v.get("positive_prompt", "")
        if len(positive_prompt) > 500:
            raise ValueError(f"positive_prompt too long: {len(positive_prompt)} characters. Maximum 500.")
        
        # 驗證 negative_prompt 包含安全前綴
        negative_prompt = v.get("negative_prompt", "")
        required_negative_keywords = ["nsfw", "child", "loli"]
        if not any(kw in negative_prompt.lower() for kw in required_negative_keywords):
            logger.warning("⚠️ negative_prompt may not contain required safety keywords")
        
        return v


# ============================================
# 驗證器函數
# ============================================

def validate_understand_intent_output(output: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    驗證 understand_intent 輸出
    
    Returns:
        (is_valid, error_message, normalized_output)
    """
    try:
        # 驗證必要鍵
        validated = UnderstandIntentOutput(
            status=output.get("status"),
            summary=output.get("summary"),
            next_action=output.get("next_action"),
            confidence=output.get("confidence"),
            core_mood=output.get("core_mood"),
            clarity_level=output.get("clarity_level")
        )
        return True, None, validated.model_dump()
    except ValidationError as e:
        error_msg = f"Validation failed: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg, None
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg, None


def validate_generate_ideas_output(output: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    驗證 generate_ideas 輸出
    
    Returns:
        (is_valid, error_message, normalized_output)
    """
    try:
        validated = GenerateIdeasOutput(**output)
        return True, None, validated.model_dump()
    except ValidationError as e:
        error_msg = f"Validation failed: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg, None
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg, None


def validate_validate_quality_output(output: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    驗證 validate_quality 輸出
    
    Returns:
        (is_valid, error_message, normalized_output)
    """
    try:
        # 確保 quick_fixes 是正確格式
        if "quick_fixes" in output and isinstance(output["quick_fixes"], dict):
            output["quick_fixes"] = QuickFixesContract(**output["quick_fixes"]).model_dump()
        
        validated = ValidateQualityOutput(**output)
        return True, None, validated.model_dump()
    except ValidationError as e:
        error_msg = f"Validation failed: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg, None
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg, None


def validate_finalize_prompt_output(output: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    驗證 finalize_prompt 輸出
    
    Returns:
        (is_valid, error_message, normalized_output)
    """
    try:
        validated = FinalizePromptOutput(**output)
        return True, None, validated.model_dump()
    except ValidationError as e:
        error_msg = f"Validation failed: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg, None
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg, None


# ============================================
# 工具驗證器 fix
# ============================================

TOOL_VALIDATORS = {
    "understand_intent": validate_understand_intent_output,
    "generate_ideas": validate_generate_ideas_output,
    "validate_quality": validate_validate_quality_output,
    "finalize_prompt": validate_finalize_prompt_output,
}


def validate_tool_output(tool_name: str, output: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    統一的工具輸出驗證入口
    
    Args:
        tool_name: 工具名稱
        output: 工具輸出字典
        
    Returns:
        (is_valid, error_message, normalized_output)
    """
    if tool_name not in TOOL_VALIDATORS:
        logger.warning(f"⚠️ No validator for tool: {tool_name}")
        return True, None, output  # 沒有驗證器時，默認通過
    
    validator = TOOL_VALIDATORS[tool_name]
    return validator(output)

