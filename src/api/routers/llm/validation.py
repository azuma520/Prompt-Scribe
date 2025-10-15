"""
LLM Validation Router
LLM 標籤品質驗證端點
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import List, Dict, Set

from models.requests import LLMValidateRequest
from models.responses import (
    ValidationResponse,
    ValidationIssue,
    ValidationSuggestions,
    RecommendedFix,
    CategoryAnalysis,
    ValidationResult,
    IssueSeverity,
    IssueType
)
from services.supabase_client import get_supabase_service, SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter()


# 衝突規則定義
CONFLICT_RULES = [
    {
        'tags': ['solo', '2girls'],
        'message': "'solo' 表示單獨一人，與 '2girls' 衝突",
        'suggestion': "移除 'solo' 或 'solo + 2girls'"
    },
    {
        'tags': ['solo', '2boys'],
        'message': "'solo' 表示單獨一人，與 '2boys' 衝突",
        'suggestion': "移除 'solo' 或改用其他標籤"
    },
    {
        'tags': ['solo', 'multiple_girls'],
        'message': "'solo' 與 'multiple_girls' 衝突",
        'suggestion': "移除 'solo'"
    },
    {
        'tags': ['1girl', '1boy', 'solo'],
        'message': "'solo' 表示單人，但有 '1girl' 和 '1boy'",
        'suggestion': "移除 'solo'，添加 '2people'"
    },
]


def detect_conflicts(tags: List[str]) -> List[ValidationIssue]:
    """檢測標籤衝突"""
    issues = []
    tags_set = set(tag.lower() for tag in tags)
    
    for rule in CONFLICT_RULES:
        rule_tags = set(t.lower() for t in rule['tags'])
        if rule_tags.issubset(tags_set):
            issues.append(
                ValidationIssue(
                    type=IssueType.CONFLICT,
                    severity=IssueSeverity.HIGH,
                    tags_involved=rule['tags'],
                    message=rule['message'],
                    suggestion=rule['suggestion'],
                    impact_score=-20
                )
            )
    
    return issues


def detect_redundant(tags: List[str], tag_data: Dict) -> List[ValidationIssue]:
    """檢測冗餘標籤"""
    issues = []
    
    # 檢測完全重複
    seen = set()
    for tag in tags:
        if tag.lower() in seen:
            issues.append(
                ValidationIssue(
                    type=IssueType.REDUNDANT,
                    severity=IssueSeverity.MEDIUM,
                    tags_involved=[tag],
                    message=f"標籤 '{tag}' 重複出現",
                    suggestion=f"移除重複的 '{tag}'",
                    impact_score=-10
                )
            )
        seen.add(tag.lower())
    
    return issues


def check_popularity(tags: List[str], tag_data: Dict) -> List[ValidationIssue]:
    """檢查流行度"""
    issues = []
    
    for tag, data in tag_data.items():
        if data and data.get('post_count', 0) < 100:
            issues.append(
                ValidationIssue(
                    type=IssueType.UNPOPULAR,
                    severity=IssueSeverity.LOW,
                    tags_involved=[tag],
                    message=f"標籤 '{tag}' 使用次數較少 ({data.get('post_count', 0)})",
                    suggestion="考慮使用更流行的相似標籤",
                    impact_score=-5
                )
            )
    
    return issues


def analyze_category_balance(tag_data: Dict) -> CategoryAnalysis:
    """分析分類平衡"""
    distribution = {}
    
    for tag, data in tag_data.items():
        if data and data.get('main_category'):
            cat = data['main_category']
            distribution[cat] = distribution.get(cat, 0) + 1
    
    # 計算平衡分數
    num_categories = len(distribution)
    if num_categories >= 4:
        balance_score = 95
    elif num_categories == 3:
        balance_score = 85
    elif num_categories == 2:
        balance_score = 70
    else:
        balance_score = 50
    
    # 生成建議
    recommendations = []
    if num_categories < 3:
        recommendations.append("標籤分類較為單一，建議添加不同類型的標籤")
    if 'ENVIRONMENT' not in distribution:
        recommendations.append("考慮添加環境或場景標籤")
    if 'ART_STYLE' not in distribution:
        recommendations.append("考慮添加藝術風格標籤以增強視覺效果")
    if not recommendations:
        recommendations.append("標籤分類分佈良好")
    
    return CategoryAnalysis(
        distribution=distribution,
        balance_score=balance_score,
        recommendations=recommendations
    )


@router.post(
    "/validate-prompt",
    response_model=ValidationResponse,
    summary="🔍 標籤品質驗證",
    description="""
    **驗證標籤組合的品質和合理性**
    
    檢查項目：
    - 衝突檢測（如 "solo" + "2girls"）
    - 冗餘檢測（重複標籤）
    - 流行度警告（過於冷門）
    - 分類平衡性（是否過於單一）
    
    返回詳細的改進建議和修正方案。
    """
)
async def validate_prompt(
    request: LLMValidateRequest,
    db: SupabaseService = Depends(get_supabase_service)
):
    """驗證標籤品質"""
    try:
        # 1. 獲取所有標籤的資料
        tag_data = {}
        for tag in request.tags:
            data = await db.get_tag_by_name(tag)
            tag_data[tag] = data
        
        # 2. 檢測各種問題
        issues = []
        
        # 衝突檢測
        conflicts = detect_conflicts(request.tags)
        issues.extend(conflicts)
        
        # 冗餘檢測
        redundant = detect_redundant(request.tags, tag_data)
        issues.extend(redundant)
        
        # 流行度檢查
        if request.strict_mode:
            popularity_issues = check_popularity(request.tags, tag_data)
            issues.extend(popularity_issues)
        
        # 3. 計算整體分數
        overall_score = 100
        for issue in issues:
            overall_score += issue.impact_score
        overall_score = max(0, min(100, overall_score))
        
        # 4. 確定驗證結果等級
        if overall_score >= 90:
            result = ValidationResult.EXCELLENT
        elif overall_score >= 75:
            result = ValidationResult.GOOD
        elif overall_score >= 60:
            result = ValidationResult.WARNING
        else:
            result = ValidationResult.POOR
        
        # 5. 生成修正建議
        recommended_fixes = []
        
        for issue in issues:
            if issue.type == IssueType.CONFLICT:
                # 對於衝突，建議移除其中一個
                if 'solo' in issue.tags_involved:
                    recommended_fixes.append(
                        RecommendedFix(
                            action="remove",
                            tag="solo",
                            reason="與多人標籤衝突"
                        )
                    )
            elif issue.type == IssueType.REDUNDANT:
                # 對於冗餘，建議移除重複
                recommended_fixes.append(
                    RecommendedFix(
                        action="remove",
                        tag=issue.tags_involved[0],
                        reason="重複標籤"
                    )
                )
        
        # 6. 生成改進後的 prompt
        improved_tags = request.tags.copy()
        for fix in recommended_fixes:
            if fix.action == "remove" and fix.tag in improved_tags:
                improved_tags.remove(fix.tag)
        
        improved_prompt = ", ".join(improved_tags)
        
        suggestions = ValidationSuggestions(
            recommended_fixes=recommended_fixes,
            improved_prompt=improved_prompt
        )
        
        # 7. 分析分類平衡
        category_analysis = analyze_category_balance(tag_data)
        
        return ValidationResponse(
            overall_score=overall_score,
            validation_result=result,
            issues=issues,
            suggestions=suggestions,
            category_analysis=category_analysis
        )
        
    except Exception as e:
        logger.error(f"Error in validate_prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

