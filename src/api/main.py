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
import asyncio

from config import settings

# 配置日誌
logging.basicConfig(
    level=settings.log_level,
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# 嘗試導入 UsageLoggingMiddleware（可選功能）
try:
    from middleware.logging_middleware import UsageLoggingMiddleware
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    MIDDLEWARE_AVAILABLE = False
    logger.warning("⚠️ Usage logging middleware not available")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時執行
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📊 Supabase URL: {settings.supabase_url}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    
    # 初始化快取策略
    try:
        from services.cache_strategy import get_cache_strategy_manager
        strategy_manager = await get_cache_strategy_manager()
        health = await strategy_manager.health_check()
        logger.info(f"💾 Cache system: {health.get('status', 'unknown')} ({settings.cache_strategy})")
        
        # 如果是 Redis 或混合模式，嘗試快取預熱
        if settings.cache_strategy in ['redis', 'hybrid'] and settings.redis_enabled:
            from services.redis_cache_manager import CacheWarmer, get_redis_cache_manager
            try:
                redis_manager = await get_redis_cache_manager()
                if redis_manager.is_available:
                    warmer = CacheWarmer(redis_manager)
                    # 異步預熱（不阻塞啟動）
                    asyncio.create_task(warmer.warm_popular_tags(50))
                    logger.info("🔥 Cache warming started in background")
            except Exception as e:
                logger.warning(f"Cache warming failed: {e}")
                
    except Exception as e:
        logger.warning(f"Cache initialization failed: {e}")
    
    yield
    
    # 關閉時執行
    logger.info("👋 Shutting down API server")
    
    # 清理 Redis 連接
    if settings.cache_strategy in ['redis', 'hybrid']:
        try:
            from services.redis_cache_manager import get_redis_cache_manager
            redis_manager = await get_redis_cache_manager()
            await redis_manager.disconnect()
            logger.info("🔌 Redis connections closed")
        except Exception as e:
            logger.warning(f"Redis cleanup error: {e}")


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

# 使用數據記錄中間件（如果可用）
if MIDDLEWARE_AVAILABLE:
    app.add_middleware(UsageLoggingMiddleware)
    logger.info("✅ Usage logging middleware enabled")


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
    from services.cache_strategy import get_cache_strategy_manager
    
    strategy_manager = await get_cache_strategy_manager()
    return await strategy_manager.get_stats()


# 快取健康檢查端點
@app.get("/cache/health")
async def cache_health():
    """快取健康檢查端點"""
    from services.cache_strategy import get_cache_strategy_manager
    
    strategy_manager = await get_cache_strategy_manager()
    return await strategy_manager.health_check()


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
from routers.llm import recommendations, validation, helpers, smart_combinations

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
app.include_router(
    smart_combinations.router,
    prefix=f"{settings.api_prefix}/llm",
    tags=["LLM Smart Combinations"]
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

