"""
Inspire Agent 工具 I/O 契約測試

根據 INSPIRE_P0_CHECKLIST.md 的要求，測試所有工具的輸入輸出契約。
"""

import pytest
from typing import Dict, Any
from pydantic import ValidationError

# 導入工具
from src.api.tools.inspire_tools import (
    understand_intent,
    generate_ideas,
    validate_quality,
    finalize_prompt,
    IdeaDirection,
    FinalOutputData
)
from src.api.utils.tool_contract_validator import (
    validate_understand_intent_output,
    validate_generate_ideas_output,
    validate_validate_quality_output,
    validate_finalize_prompt_output
)


# ============================================
# 測試 understand_intent
# ============================================

class TestUnderstandIntent:
    """測試 understand_intent 工具契約"""
    
    def test_valid_output_structure(self):
        """測試有效輸出結構（嚴格 6 個鍵）"""
        output = {
            "status": "understood",
            "summary": "理解：夢幻，清晰度 crystal_clear",
            "next_action": "generate_directly",
            "confidence": 0.85,
            "core_mood": "夢幻",
            "clarity_level": "crystal_clear"
        }
        
        is_valid, error, normalized = validate_understand_intent_output(output)
        assert is_valid, f"Validation failed: {error}"
        assert normalized is not None
        assert "status" in normalized
        assert "confidence" in normalized
        assert 0.0 <= normalized["confidence"] <= 1.0
    
    def test_invalid_confidence_range(self):
        """測試無效的信心度範圍"""
        output = {
            "status": "understood",
            "summary": "理解：夢幻",
            "next_action": "generate_directly",
            "confidence": 1.5,  # 超出範圍
            "core_mood": "夢幻",
            "clarity_level": "crystal_clear"
        }
        
        is_valid, error, _ = validate_understand_intent_output(output)
        assert not is_valid, "Should fail validation for confidence > 1.0"
    
    def test_invalid_clarity_level(self):
        """測試無效的清晰度枚舉值"""
        output = {
            "status": "understood",
            "summary": "理解：夢幻",
            "next_action": "generate_directly",
            "confidence": 0.8,
            "core_mood": "夢幻",
            "clarity_level": "invalid_level"  # 無效值
        }
        
        is_valid, error, _ = validate_understand_intent_output(output)
        assert not is_valid, "Should fail validation for invalid clarity_level"
    
    def test_invalid_next_action(self):
        """測試無效的下一步行動"""
        output = {
            "status": "understood",
            "summary": "理解：夢幻",
            "next_action": "invalid_action",  # 無效值
            "confidence": 0.8,
            "core_mood": "夢幻",
            "clarity_level": "crystal_clear"
        }
        
        is_valid, error, _ = validate_understand_intent_output(output)
        assert not is_valid, "Should fail validation for invalid next_action"
    
    def test_missing_required_fields(self):
        """測試缺失必要欄位"""
        output = {
            "status": "understood",
            # 缺少其他必要欄位
        }
        
        is_valid, error, _ = validate_understand_intent_output(output)
        assert not is_valid, "Should fail validation for missing fields"


# ============================================
# 測試 generate_ideas
# ============================================

class TestGenerateIdeas:
    """測試 generate_ideas 工具契約"""
    
    def test_valid_output_structure(self):
        """測試有效輸出結構（2-3 個方向，每個 6 個鍵）"""
        output = {
            "status": "generated",
            "count": 2,
            "directions": [
                {
                    "title": "夢幻版",
                    "concept": "夢幻場景",
                    "vibe": "溫馨",
                    "main_tags": ["1girl", "sakura", "kimono", "spring", "soft_lighting", 
                                "cherry_blossoms", "peaceful", "calm", "beautiful", "detailed",
                                "high_quality", "masterpiece"],  # 至少 10 個
                    "quick_preview": "1girl, sakura, kimono",
                    "uniqueness": "櫻花與和服的組合"
                },
                {
                    "title": "寫實版",
                    "concept": "寫實場景",
                    "vibe": "寧靜",
                    "main_tags": ["1girl", "kimono", "traditional", "japanese", "photography",
                                "realistic", "detailed", "high_resolution", "portrait", "day",
                                "outdoor", "nature"],  # 至少 10 個
                    "quick_preview": "1girl, kimono, traditional",
                    "uniqueness": "寫實攝影風格"
                }
            ],
            "diversity_achieved": "high",
            "ready_for_selection": True
        }
        
        is_valid, error, normalized = validate_generate_ideas_output(output)
        assert is_valid, f"Validation failed: {error}"
        assert normalized is not None
        assert 2 <= len(normalized["directions"]) <= 3
    
    def test_too_few_directions(self):
        """測試方向數量太少"""
        output = {
            "status": "generated",
            "count": 1,  # 少於 2 個
            "directions": [
                {
                    "title": "單一方向",
                    "concept": "概念",
                    "vibe": "氛圍",
                    "main_tags": ["1girl"] * 10,
                    "quick_preview": "預覽",
                    "uniqueness": "獨特點"
                }
            ],
            "diversity_achieved": "low",
            "ready_for_selection": True
        }
        
        is_valid, error, _ = validate_generate_ideas_output(output)
        assert not is_valid, "Should fail validation for count < 2"
    
    def test_too_many_tags_in_direction(self):
        """測試方向中標籤數量不足"""
        output = {
            "status": "generated",
            "count": 2,
            "directions": [
                {
                    "title": "標籤不足",
                    "concept": "概念",
                    "vibe": "氛圍",
                    "main_tags": ["1girl", "sakura"],  # 少於 10 個
                    "quick_preview": "預覽",
                    "uniqueness": "獨特點"
                }
            ],
            "diversity_achieved": "low",
            "ready_for_selection": True
        }
        
        is_valid, error, _ = validate_generate_ideas_output(output)
        assert not is_valid, "Should fail validation for tags < 10"
    
    def test_title_too_long(self):
        """測試標題過長"""
        output = {
            "status": "generated",
            "count": 1,
            "directions": [
                {
                    "title": "這個標題太長了超過十個字",  # 超過 10 字
                    "concept": "概念",
                    "vibe": "氛圍",
                    "main_tags": ["1girl"] * 10,
                    "quick_preview": "預覽",
                    "uniqueness": "獨特點"
                }
            ],
            "diversity_achieved": "low",
            "ready_for_selection": True
        }
        
        is_valid, error, _ = validate_generate_ideas_output(output)
        assert not is_valid, "Should fail validation for title > 10 chars"


# ============================================
# 測試 validate_quality
# ============================================

class TestValidateQuality:
    """測試 validate_quality 工具契約"""
    
    def test_valid_output_structure(self):
        """測試有效輸出結構（嚴格 8 個頂層鍵）"""
        output = {
            "is_valid": True,
            "score": 85,
            "issues": [],
            "quick_fixes": {
                "remove": [],
                "add": [],
                "replace": {}
            },
            "warnings": [],
            "suggestions": [],
            "affected_tags": [],
            "severity": "info"
        }
        
        is_valid, error, normalized = validate_validate_quality_output(output)
        assert is_valid, f"Validation failed: {error}"
        assert normalized is not None
        assert 0 <= normalized["score"] <= 100
    
    def test_invalid_score_range(self):
        """測試無效的分數範圍"""
        output = {
            "is_valid": True,
            "score": 150,  # 超出範圍
            "issues": [],
            "quick_fixes": {
                "remove": [],
                "add": [],
                "replace": {}
            }
        }
        
        is_valid, error, _ = validate_validate_quality_output(output)
        assert not is_valid, "Should fail validation for score > 100"
    
    def test_quick_fixes_structure(self):
        """測試 quick_fixes 結構"""
        output = {
            "is_valid": True,
            "score": 75,
            "issues": [],
            "quick_fixes": {
                "remove": ["bad_tag"],
                "add": ["good_tag"],
                "replace": {"old": "new"}
            }
        }
        
        is_valid, error, normalized = validate_validate_quality_output(output)
        assert is_valid, f"Validation failed: {error}"
        assert "remove" in normalized["quick_fixes"]
        assert "add" in normalized["quick_fixes"]
        assert "replace" in normalized["quick_fixes"]


# ============================================
# 測試 finalize_prompt
# ============================================

class TestFinalizePrompt:
    """測試 finalize_prompt 工具契約"""
    
    def test_valid_output_structure(self):
        """測試有效輸出結構"""
        output = {
            "status": "completed",
            "output": {
                "title": "作品標題",
                "concept": "創作概念",
                "positive_prompt": "1girl, sakura, kimono",  # < 500 字
                "negative_prompt": "nsfw, child, loli, bad_quality",  # 包含安全前綴
                "structure_json": "{}",
                "parameters_json": "{}"
            },
            "quality_score": 85,
            "ready_to_use": True
        }
        
        is_valid, error, normalized = validate_finalize_prompt_output(output)
        assert is_valid, f"Validation failed: {error}"
        assert normalized is not None
    
    def test_positive_prompt_too_long(self):
        """測試 positive_prompt 過長"""
        output = {
            "status": "completed",
            "output": {
                "title": "標題",
                "positive_prompt": "a" * 600,  # 超過 500 字
                "negative_prompt": "nsfw, child, loli"
            },
            "quality_score": 85,
            "ready_to_use": True
        }
        
        is_valid, error, _ = validate_finalize_prompt_output(output)
        assert not is_valid, "Should fail validation for prompt > 500 chars"
    
    def test_missing_negative_prompt_safety(self):
        """測試 negative_prompt 缺少安全前綴（應該警告但不失敗）"""
        output = {
            "status": "completed",
            "output": {
                "title": "標題",
                "positive_prompt": "1girl",
                "negative_prompt": "bad_quality"  # 缺少安全前綴
            },
            "quality_score": 85,
            "ready_to_use": True
        }
        
        # 這個應該通過驗證，但會記錄警告
        is_valid, error, normalized = validate_finalize_prompt_output(output)
        # 驗證邏輯只警告，不阻止
        assert is_valid or "warning" in (error or "").lower()


# ============================================
# 整合測試（實際調用工具）
# ============================================

class TestToolIntegration:
    """測試實際工具調用的契約符合性"""
    
    def test_understand_intent_integration(self):
        """測試 understand_intent 實際調用"""
        result = understand_intent(
            core_mood="夢幻",
            visual_elements=["櫻花", "和服"],
            style_preference="anime",
            clarity_level="crystal_clear",
            confidence=0.9,
            next_action="generate_directly"
        )
        
        # 驗證輸出
        is_valid, error, _ = validate_understand_intent_output(result)
        assert is_valid, f"Tool output failed validation: {error}"
    
    def test_generate_ideas_integration(self):
        """測試 generate_ideas 實際調用"""
        ideas = [
            IdeaDirection(
                title="夢幻版",
                concept="夢幻場景",
                vibe="溫馨",
                main_tags=["1girl", "sakura", "kimono", "spring", "soft_lighting",
                          "cherry_blossoms", "peaceful", "calm", "beautiful", "detailed",
                          "high_quality"],
                quick_preview="1girl, sakura, kimono",
                uniqueness="櫻花與和服的組合"
            ),
            IdeaDirection(
                title="寫實版",
                concept="寫實場景",
                vibe="寧靜",
                main_tags=["1girl", "kimono", "traditional", "japanese", "photography",
                          "realistic", "detailed", "high_resolution", "portrait", "day",
                          "outdoor", "nature"],
                quick_preview="1girl, kimono, traditional",
                uniqueness="寫實攝影風格"
            )
        ]
        
        result = generate_ideas(
            ideas=ideas,
            generation_basis="使用者輸入",
            diversity_achieved="high"
        )
        
        # 驗證輸出
        is_valid, error, _ = validate_generate_ideas_output(result)
        assert is_valid, f"Tool output failed validation: {error}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

