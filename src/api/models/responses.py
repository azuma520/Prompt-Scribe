"""
API Response Models
定義所有 API 回應的資料結構
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class PopularityTier(str, Enum):
    """流行度等級"""
    VERY_POPULAR = "very_popular"
    POPULAR = "popular"
    MODERATE = "moderate"
    NICHE = "niche"


class MatchType(str, Enum):
    """匹配類型"""
    EXACT_MATCH = "exact_match"
    PREFIX_MATCH = "prefix_match"
    PARTIAL_MATCH = "partial_match"
    SYNONYM_MATCH = "synonym_match"
    CATEGORY_MATCH = "category_match"


class ValidationResult(str, Enum):
    """驗證結果"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    POOR = "poor"


class IssueSeverity(str, Enum):
    """問題嚴重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(str, Enum):
    """問題類型"""
    CONFLICT = "conflict"
    REDUNDANT = "redundant"
    UNPOPULAR = "unpopular"
    IMBALANCED = "imbalanced"
    MISSING = "missing"


class TagResponse(BaseModel):
    """標籤回應"""
    id: str
    name: str
    danbooru_cat: int
    post_count: int
    main_category: Optional[str]
    sub_category: Optional[str]
    confidence: Optional[float]
    classification_source: Optional[str]


class LLMTagRecommendation(BaseModel):
    """LLM 標籤推薦"""
    tag: str = Field(..., description="標籤名稱")
    confidence: float = Field(..., ge=0.0, le=1.0, description="推薦信心度")
    popularity_tier: PopularityTier = Field(..., description="流行度等級")
    post_count: int = Field(..., description="使用次數")
    category: str = Field(..., description="標籤分類")
    subcategory: Optional[str] = Field(None, description="子分類")
    match_reason: str = Field(..., description="推薦原因")
    usage_context: str = Field(..., description="使用情境和建議")
    weight: int = Field(..., ge=1, le=10, description="推薦權重")
    related_tags: List[str] = Field(default_factory=list, description="相關標籤")


class QualityAssessment(BaseModel):
    """品質評估"""
    overall_score: int = Field(..., ge=0, le=100, description="整體品質分數")
    balance_score: int = Field(..., ge=0, le=100, description="分類平衡分數")
    popularity_score: int = Field(..., ge=0, le=100, description="流行度分數")
    warnings: List[str] = Field(default_factory=list, description="警告訊息")


class RecommendationMetadata(BaseModel):
    """推薦元資料"""
    processing_time_ms: float = Field(..., description="處理時間（毫秒）")
    total_candidates: int = Field(..., description="候選標籤總數")
    algorithm: str = Field(..., description="使用的算法版本")
    cache_hit: bool = Field(False, description="是否命中快取")
    keywords_extracted: Optional[List[str]] = Field(None, description="提取的關鍵字")
    keywords_expanded: Optional[List[str]] = Field(None, description="擴展後的關鍵字")


class TagRecommendationResponse(BaseModel):
    """標籤推薦回應"""
    query: str = Field(..., description="原始查詢描述")
    recommended_tags: List[LLMTagRecommendation] = Field(..., description="推薦的標籤列表")
    category_distribution: Dict[str, int] = Field(..., description="標籤的分類分佈統計")
    quality_assessment: QualityAssessment = Field(..., description="推薦品質評估")
    suggested_prompt: str = Field(..., description="建議的最終 prompt")
    metadata: RecommendationMetadata = Field(..., description="元資料")


class ValidationIssue(BaseModel):
    """驗證問題"""
    type: IssueType = Field(..., description="問題類型")
    severity: IssueSeverity = Field(..., description="嚴重程度")
    tags_involved: List[str] = Field(..., description="涉及的標籤")
    message: str = Field(..., description="問題描述")
    suggestion: str = Field(..., description="解決建議")
    impact_score: int = Field(..., ge=-100, le=0, description="對整體品質的影響")


class RecommendedFix(BaseModel):
    """推薦的修正"""
    action: str = Field(..., description="修正動作: add/remove/replace")
    tag: str = Field(..., description="相關標籤")
    reason: str = Field(..., description="修正原因")


class ValidationSuggestions(BaseModel):
    """驗證建議"""
    recommended_fixes: List[RecommendedFix] = Field(default_factory=list)
    improved_prompt: str = Field(..., description="改進後的 prompt 建議")


class CategoryAnalysis(BaseModel):
    """分類分析"""
    distribution: Dict[str, int] = Field(..., description="分類分佈")
    balance_score: int = Field(..., ge=0, le=100, description="平衡分數")
    recommendations: List[str] = Field(default_factory=list, description="建議")


class ValidationResponse(BaseModel):
    """驗證回應"""
    overall_score: int = Field(..., ge=0, le=100, description="整體品質分數")
    validation_result: ValidationResult = Field(..., description="驗證結果等級")
    issues: List[ValidationIssue] = Field(default_factory=list, description="發現的問題列表")
    suggestions: ValidationSuggestions = Field(..., description="改進建議")
    category_analysis: CategoryAnalysis = Field(..., description="分類分析")


class SearchResult(BaseModel):
    """搜尋結果"""
    tag: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    match_type: MatchType
    matched_keyword: str
    popularity_tier: PopularityTier
    post_count: int


class SearchByKeywordsResponse(BaseModel):
    """關鍵字搜尋回應"""
    query: str
    expanded_keywords: List[str]
    results: List[SearchResult]


class TagListResponse(BaseModel):
    """標籤列表回應"""
    data: List[TagResponse]
    total: int
    limit: int
    offset: int


class StatsResponse(BaseModel):
    """統計資訊回應"""
    total_tags: int
    category_distribution: Dict[str, int]
    classified_count: int
    unclassified_count: int
    classification_rate: float


class ErrorResponse(BaseModel):
    """錯誤回應"""
    error: str
    message: str
    path: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

