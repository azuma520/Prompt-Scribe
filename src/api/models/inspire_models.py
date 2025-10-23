"""
Inspire Agent API Models

定義 Inspire Agent 相關的請求和回應模型。

Version: 2.0.0
Date: 2025-10-22
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# 請求模型 (Request Models)
# ============================================================================

class InspireStartRequest(BaseModel):
    """開始 Inspire 對話的請求"""
    
    message: str = Field(
        ...,
        description="使用者的初始輸入（如：'櫻花樹下的和服少女'）",
        min_length=1,
        max_length=500
    )
    user_id: Optional[str] = Field(
        None,
        description="使用者 ID（用於統計和個性化）"
    )
    user_access_level: Literal["all-ages", "r15", "r18"] = Field(
        "all-ages",
        description="使用者內容分級權限"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="使用者偏好設定（語言、詳細度等）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "櫻花樹下的和服少女，溫柔寧靜的氛圍",
                "user_access_level": "all-ages",
                "preferences": {
                    "language": "zh",
                    "verbosity": "concise"
                }
            }
        }


class InspireContinueRequest(BaseModel):
    """繼續 Inspire 對話的請求"""
    
    session_id: str = Field(
        ...,
        description="Session ID（從 start 回應中獲得）"
    )
    message: str = Field(
        ...,
        description="使用者的回應訊息",
        min_length=1,
        max_length=500
    )
    action: Optional[Dict[str, Any]] = Field(
        None,
        description="特殊動作（如選擇方向、反饋等）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123-def456",
                "message": "選擇第 2 個方向",
                "action": {
                    "type": "select",
                    "data": {"selected_direction": 1}
                }
            }
        }


class InspireFeedbackRequest(BaseModel):
    """提交使用者反饋的請求"""
    
    session_id: str = Field(..., description="Session ID")
    satisfaction: int = Field(
        ...,
        ge=1,
        le=5,
        description="滿意度評分（1-5 星）"
    )
    feedback_text: Optional[str] = Field(
        None,
        max_length=500,
        description="文字反饋"
    )
    would_use_again: bool = Field(
        default=True,
        description="是否願意再次使用"
    )


# ============================================================================
# 回應模型 (Response Models)
# ============================================================================

class DirectionCard(BaseModel):
    """創意方向卡片"""
    
    title: str = Field(..., description="方向標題（≤10 字）")
    description: str = Field(..., description="簡短描述（1-2 句）")
    main_tags: List[str] = Field(..., description="核心標籤（5-8 個）")
    style: str = Field(..., description="風格類型（如：優雅、活潑、夢幻）")
    mood: str = Field(..., description="氛圍感覺")
    preview_prompt: str = Field(..., description="預覽用的簡化 Prompt")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "🌸 傳統優雅版",
                "description": "經典和服少女，寧靜優雅的氛圍",
                "main_tags": ["1girl", "kimono", "cherry_blossoms", "solo", "gentle_smile"],
                "style": "traditional_elegant",
                "mood": "peaceful_serene",
                "preview_prompt": "1girl, kimono, cherry blossoms, gentle smile"
            }
        }


class FinalOutput(BaseModel):
    """最終輸出的完整 Prompt"""
    
    title: str = Field(..., description="作品標題")
    concept: str = Field(..., description="創作概念說明")
    
    positive_prompt: str = Field(..., description="正面 Prompt（完整）")
    negative_prompt: str = Field(..., description="負面 Prompt（完整）")
    
    structure: Dict[str, List[str]] = Field(
        ...,
        description="分段結構（subject, appearance, scene, mood, style）"
    )
    
    parameters: Dict[str, Any] = Field(
        ...,
        description="推薦生成參數"
    )
    
    usage_tips: str = Field(..., description="使用提示")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "櫻花樹下的和服少女",
                "concept": "傳統日式美學與寧靜氛圍的結合",
                "positive_prompt": "1girl, solo, kimono, cherry_blossoms, gentle_smile...",
                "negative_prompt": "nsfw, lowres, bad anatomy, worst quality...",
                "structure": {
                    "subject": ["1girl", "solo"],
                    "appearance": ["kimono", "long_hair"],
                    "scene": ["cherry_blossoms", "tree"],
                    "mood": ["peaceful", "serene"],
                    "style": ["anime", "detailed"]
                },
                "parameters": {
                    "steps": 28,
                    "cfg_scale": 7,
                    "sampler": "DPM++ 2M Karras"
                },
                "usage_tips": "建議使用 512x768 解析度，emphasize 櫻花效果"
            }
        }


class SessionMetadata(BaseModel):
    """Session 元數據"""
    
    session_id: str
    created_at: datetime
    updated_at: datetime
    current_phase: str
    total_tool_calls: int = 0
    total_cost: float = 0.0
    total_tokens: int = 0
    quality_score: Optional[int] = None
    generated_directions: Optional[List[Dict[str, Any]]] = None  # 添加 generated_directions 欄位


class InspireResponse(BaseModel):
    """Inspire Agent 回應（通用基類）"""
    
    session_id: str = Field(..., description="Session ID")
    type: Literal["message", "directions", "completed", "error"] = Field(
        ...,
        description="回應類型"
    )
    message: str = Field(..., description="Agent 的文字回應")
    
    phase: str = Field(..., description="當前對話階段")
    metadata: SessionMetadata = Field(..., description="Session 元數據")


class InspireStartResponse(InspireResponse):
    """開始對話的回應"""
    
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="額外資料（如創意方向）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123-def456",
                "type": "directions",
                "message": "這個場景真美！給你三個方向：",
                "phase": "exploring",
                "data": {
                    "directions": [
                        {
                            "title": "🌸 傳統優雅版",
                            "description": "經典和服少女...",
                            "main_tags": ["1girl", "kimono"]
                        }
                    ]
                },
                "metadata": {
                    "session_id": "abc123",
                    "created_at": "2025-10-22T10:00:00Z",
                    "updated_at": "2025-10-22T10:00:05Z",
                    "current_phase": "exploring",
                    "total_tool_calls": 2,
                    "total_cost": 0.0003,
                    "total_tokens": 1200
                }
            }
        }


class InspireContinueResponse(InspireResponse):
    """繼續對話的回應"""
    
    data: Optional[Dict[str, Any]] = Field(None, description="額外資料")
    is_completed: bool = Field(default=False, description="是否已完成")
    final_output: Optional[FinalOutput] = Field(
        None,
        description="最終輸出（如果已完成）"
    )


class InspireStatusResponse(BaseModel):
    """查詢 Session 狀態的回應"""
    
    session_id: str
    status: Literal["active", "completed", "abandoned", "error"]
    metadata: SessionMetadata
    conversation_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="對話歷史（最近 10 條）"
    )


class InspireErrorResponse(BaseModel):
    """錯誤回應"""
    
    error: str = Field(..., description="錯誤類型")
    message: str = Field(..., description="錯誤訊息")
    details: Optional[Dict[str, Any]] = Field(None, description="詳細資訊")
    session_id: Optional[str] = Field(None, description="Session ID（如果有）")


# ============================================================================
# 內部模型 (Internal Models)
# ============================================================================

class InspireSession(BaseModel):
    """Inspire Session 資料模型（內部使用）"""
    
    id: str
    user_id: Optional[str] = None
    user_access_level: str = "all-ages"
    
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    current_phase: str = "understanding"
    
    # 對話資料
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    tool_call_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # 提取的資訊
    extracted_intent: Optional[Dict[str, Any]] = None
    generated_directions: Optional[List[Dict[str, Any]]] = None
    selected_direction: Optional[Dict[str, Any]] = None
    final_output: Optional[Dict[str, Any]] = None
    
    # 性能指標
    total_tokens_used: int = 0
    total_cost: float = 0.0
    processing_time_ms: Optional[float] = None
    
    # 品質指標
    quality_score: Optional[int] = None
    user_satisfaction: Optional[int] = None
    completion_reason: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123-def456",
                "user_id": "user_123",
                "user_access_level": "all-ages",
                "created_at": "2025-10-22T10:00:00Z",
                "updated_at": "2025-10-22T10:05:00Z",
                "status": "active",
                "current_phase": "exploring",
                "total_tokens_used": 1500,
                "total_cost": 0.0005
            }
        }
    
    def record_tool_call(self, tool_name: str, tool_data: Dict[str, Any]):
        """記錄工具調用"""
        self.tool_call_history.append({
            "tool": tool_name,
            "data": tool_data,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_message(self, role: str, content: str):
        """添加對話訊息"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

