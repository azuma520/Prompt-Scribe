"""
Prompt-Scribe API - Main Application
專案: PLAN-2025-005 - API 優化與 LLM 友好設計

核心理念: 讓 API 承擔複雜性,讓 LLM 保持簡單
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from config import settings

# 配置日誌
logging.basicConfig(
    level=settings.log_level,
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時執行
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📊 Supabase URL: {settings.supabase_url}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    
    yield
    
    # 關閉時執行
    logger.info("👋 Shutting down API server")


# 創建 FastAPI 應用
app = FastAPI(
    title=settings.app_name,
    description="""
    🤖 **LLM 友好的 Prompt-Scribe 標籤 API**
    
    ## 核心功能
    
    ### 🎯 LLM 專用端點
    - **智能標籤推薦**: 一次 API 調用完成所有工作
    - **品質驗證**: 檢測衝突、冗餘、優化建議
    - **智能搜尋**: 關鍵字擴展 + 流行度排序
    
    ### 📚 基礎端點
    - 標籤查詢、搜尋、統計
    - 支援分頁、篩選、排序
    
    ## 設計原則
    
    1. **簡單優於複雜**: 關鍵字搜尋優先,向量搜尋延後
    2. **一次調用完成**: LLM 無需管理多個 API
    3. **結構化回應**: 包含解釋和使用建議
    4. **高效能**: 快取機制 + 索引優化
    
    ## 技術棧
    
    - **Framework**: FastAPI 0.109+
    - **Database**: Supabase (PostgreSQL 15+)
    - **Cache**: In-memory (LRU)
    - **Language**: Python 3.9+
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json"
)


# CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 請求計時中間件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加請求處理時間到回應標頭"""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # 轉換為毫秒
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    
    # 記錄慢請求
    if process_time > 1000:  # 超過 1 秒
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {process_time:.2f}ms"
        )
    
    return response


# 全域異常處理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全域異常處理器"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "path": str(request.url)
        }
    )


# 根端點
@app.get("/")
async def root():
    """API 根端點"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "llm": f"{settings.api_prefix}/llm",
            "v1": f"{settings.api_prefix}/v1",
        },
        "description": "LLM 友好的標籤推薦 API"
    }


# 健康檢查端點
@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": time.time()
    }


# 快取統計端點
@app.get("/cache/stats")
async def cache_statistics():
    """快取統計端點"""
    from services.cache_manager import get_cache_stats
    return get_cache_stats()


# 導入路由
from routers.v1 import tags, search, statistics

# 註冊 V1 路由
app.include_router(
    tags.router, 
    prefix=f"{settings.api_prefix}/v1", 
    tags=["Tags (Basic)"]
)
app.include_router(
    search.router, 
    prefix=f"{settings.api_prefix}/v1", 
    tags=["Search"]
)
app.include_router(
    statistics.router, 
    prefix=f"{settings.api_prefix}/v1", 
    tags=["Statistics"]
)

# 導入 LLM 路由
from routers.llm import recommendations, validation, helpers

# 註冊 LLM 路由
app.include_router(
    recommendations.router,
    prefix=f"{settings.api_prefix}/llm",
    tags=["LLM Tools"]
)
app.include_router(
    validation.router,
    prefix=f"{settings.api_prefix}/llm",
    tags=["LLM Tools"]
)
app.include_router(
    helpers.router,
    prefix=f"{settings.api_prefix}/llm",
    tags=["LLM Tools"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

