"""
Tags Router - 基礎標籤查詢端點
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging

# 絕對相對匯入（包內相對路徑）
from ...models.requests import TagQueryRequest, CategoryEnum
from ...models.responses import TagResponse, TagListResponse, ErrorResponse
from ...services.supabase_client import get_supabase_service, SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/tags",
    response_model=TagListResponse,
    summary="查詢標籤列表",
    description="""
    查詢標籤列表,支援分頁、篩選和排序
    
    **篩選選項**:
    - name: 標籤名稱篩選(部分匹配)
    - category: 分類篩選
    
    **排序選項**:
    - order_by: 排序欄位(預設: post_count)
    - order_desc: 是否降序(預設: true)
    """
)
async def get_tags(
    name: Optional[str] = Query(None, description="標籤名稱篩選"),
    category: Optional[CategoryEnum] = Query(None, description="分類篩選"),
    limit: int = Query(20, ge=1, le=100, description="返回數量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    order_by: str = Query("post_count", description="排序欄位"),
    order_desc: bool = Query(True, description="降序排序"),
    db: SupabaseService = Depends(get_supabase_service)
):
    """查詢標籤列表"""
    try:
        tags, total = await db.get_tags(
            limit=limit,
            offset=offset,
            category=category.value if category else None,
            name_filter=name,
            order_by=order_by,
            order_desc=order_desc
        )
        
        return TagListResponse(
            data=[TagResponse(**tag) for tag in tags],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error in get_tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tags/{tag_name}",
    response_model=TagResponse,
    summary="查詢單一標籤",
    description="根據標籤名稱查詢詳細資訊"
)
async def get_tag_by_name(
    tag_name: str,
    db: SupabaseService = Depends(get_supabase_service)
):
    """查詢單一標籤"""
    try:
        tag = await db.get_tag_by_name(tag_name)
        
        if not tag:
            raise HTTPException(
                status_code=404,
                detail=f"Tag '{tag_name}' not found"
            )
        
        return TagResponse(**tag)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_tag_by_name: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/categories",
    response_model=dict,
    summary="查詢所有分類",
    description="返回所有可用的標籤分類列表"
)
async def get_categories():
    """查詢所有分類"""
    categories = [cat.value for cat in CategoryEnum]
    return {
        "categories": categories,
        "total": len(categories)
    }

