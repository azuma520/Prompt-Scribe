"""
API Request Models
定義所有 API 請求的資料結構
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class CategoryEnum(str, Enum):
    """標籤分類枚舉"""
    CHARACTER = "CHARACTER"
    CHARACTER_RELATED = "CHARACTER_RELATED"
    OBJECTS = "OBJECTS"
    ENVIRONMENT = "ENVIRONMENT"
    COMPOSITION = "COMPOSITION"
    VISUAL_EFFECTS = "VISUAL_EFFECTS"
    ART_STYLE = "ART_STYLE"
    ACTION_POSE = "ACTION_POSE"
    COPYRIGHT = "COPYRIGHT"
    ARTIST = "ARTIST"
    QUALITY = "QUALITY"
    TECHNICAL = "TECHNICAL"
    ADULT_CONTENT = "ADULT_CONTENT"
    THEME_CONCEPT = "THEME_CONCEPT"


class TagQueryRequest(BaseModel):
    """標籤查詢請求"""
    name: Optional[str] = Field(None, description="標籤名稱篩選")
    category: Optional[CategoryEnum] = Field(None, description="分類篩選")
    limit: int = Field(20, ge=1, le=100, description="返回數量")
    offset: int = Field(0, ge=0, description="偏移量")
    order_by: str = Field("post_count", description="排序欄位")
    order_desc: bool = Field(True, description="降序排序")


class SearchRequest(BaseModel):
    """搜尋請求"""
    query: str = Field(..., min_length=1, max_length=200, description="搜尋關鍵字")
    limit: int = Field(20, ge=1, le=100, description="最多返回結果數")
    category: Optional[CategoryEnum] = Field(None, description="分類篩選")
    min_popularity: int = Field(100, ge=0, description="最低流行度")


class LLMRecommendRequest(BaseModel):
    """LLM 標籤推薦請求"""
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="用戶對想要生成圖像的自然語言描述",
        examples=["a lonely girl in cyberpunk city at night"]
    )
    max_tags: int = Field(
        10,
        ge=1,
        le=50,
        description="最多返回的標籤數量"
    )
    exclude_adult: bool = Field(
        True,
        description="是否排除成人內容標籤"
    )
    min_popularity: int = Field(
        100,
        ge=0,
        description="最低流行度閾值"
    )
    balance_categories: bool = Field(
        True,
        description="是否平衡不同分類的標籤"
    )
    preferred_categories: Optional[List[CategoryEnum]] = Field(
        None,
        description="優先推薦的分類"
    )
    language_hint: str = Field(
        "auto",
        description="輸入語言提示"
    )
    
    @validator('description')
    def validate_description(cls, v):
        """驗證描述內容"""
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()


class LLMValidateRequest(BaseModel):
    """LLM 標籤驗證請求"""
    tags: List[str] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="要驗證的標籤列表",
        examples=[["1girl", "solo", "school_uniform"]]
    )
    strict_mode: bool = Field(
        False,
        description="嚴格模式"
    )
    auto_fix: bool = Field(
        False,
        description="是否自動修正問題"
    )
    
    @validator('tags')
    def validate_tags(cls, v):
        """驗證標籤列表"""
        # 去除空字串和重複
        cleaned = list(set(tag.strip() for tag in v if tag.strip()))
        if not cleaned:
            raise ValueError('Tags list cannot be empty')
        return cleaned


class LLMSearchByKeywordsRequest(BaseModel):
    """LLM 關鍵字搜尋請求"""
    keywords: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="搜尋關鍵字（空格分隔）",
        examples=["lonely cyberpunk girl"]
    )
    max_results: int = Field(
        10,
        ge=1,
        le=50,
        description="最多返回結果數"
    )
    category_hints: Optional[List[CategoryEnum]] = Field(
        None,
        description="分類提示"
    )
    boost_popular: bool = Field(
        True,
        description="是否提升熱門標籤的排序"
    )


class SmartCombinationRequest(BaseModel):
    """智能組合建議請求"""
    tags: List[str] = Field(
        ..., 
        min_items=1,
        max_items=20,
        description="基礎標籤列表",
        examples=[["1girl", "long_hair"]]
    )
    max_suggestions: int = Field(
        5,
        ge=1,
        le=10,
        description="最多建議數量"
    )
    include_analysis: bool = Field(
        True,
        description="是否包含分析結果"
    )
    
    @validator('tags')
    def validate_tags(cls, v):
        """驗證標籤列表"""
        cleaned = list(set(tag.strip() for tag in v if tag.strip()))
        if not cleaned:
            raise ValueError('Tags list cannot be empty')
        return cleaned
