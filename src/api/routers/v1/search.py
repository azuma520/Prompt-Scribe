"""
Search Router - 搜尋端點
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from ...models.requests import SearchRequest
from ...models.responses import TagResponse, TagListResponse
from ...services.supabase_client import get_supabase_service, SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/search",
    response_model=TagListResponse,
    summary="文字搜尋",
    description="""
    簡單的文字搜尋功能
    
    **搜尋方式**:
    - 支援模糊匹配(ILIKE)
    - 支援分類篩選
    - 自動按流行度排序
    """
)
async def search_tags(
    request: SearchRequest,
    db: SupabaseService = Depends(get_supabase_service)
):
    """文字搜尋標籤"""
    try:
        # 提取關鍵字(簡化版:用空格分割)
        keywords = request.query.lower().split()
        
        # 執行搜尋
        results = await db.search_tags_by_keywords(
            keywords=keywords,
            limit=request.limit,
            category=request.category.value if request.category else None,
            min_popularity=request.min_popularity
        )
        
        return TagListResponse(
            data=[TagResponse(**tag) for tag in results],
            total=len(results),
            limit=request.limit,
            offset=0
        )
    except Exception as e:
        logger.error(f"Error in search_tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

