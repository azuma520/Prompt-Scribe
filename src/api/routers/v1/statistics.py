"""
Statistics Router - 統計資訊端點
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from ...models.responses import StatsResponse
from ...services.supabase_client import get_supabase_service, SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="獲取統計資訊",
    description="""
    獲取資料庫統計資訊
    
    **包含資訊**:
    - 總標籤數
    - 分類分佈
    - 已分類/未分類數量
    - 分類覆蓋率
    """
)
async def get_statistics(
    db: SupabaseService = Depends(get_supabase_service)
):
    """獲取統計資訊"""
    try:
        # 獲取總標籤數
        total_tags = await db.get_total_tags_count()
        
        # 獲取分類統計
        category_dist = await db.get_category_stats()
        
        # 計算已分類和未分類數量
        classified_count = sum(category_dist.values())
        unclassified_count = total_tags - classified_count
        classification_rate = (classified_count / total_tags * 100) if total_tags > 0 else 0
        
        return StatsResponse(
            total_tags=total_tags,
            category_distribution=category_dist,
            classified_count=classified_count,
            unclassified_count=unclassified_count,
            classification_rate=round(classification_rate, 2)
        )
    except Exception as e:
        logger.error(f"Error in get_statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

