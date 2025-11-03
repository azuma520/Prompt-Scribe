"""
Logging Middleware
日誌中間件 - 自動記錄所有 API 請求
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging

try:
    from src.api.services.usage_logger import get_usage_logger
except ImportError:
    from services.usage_logger import get_usage_logger

logger = logging.getLogger(__name__)


class UsageLoggingMiddleware(BaseHTTPMiddleware):
    """
    使用數據記錄中間件
    
    自動記錄所有 API 請求的:
    - 端點和方法
    - 響應時間
    - 狀態碼
    - 快取命中狀態
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.usage_logger = get_usage_logger()
    
    async def dispatch(self, request: Request, call_next):
        """處理請求並記錄"""
        # 記錄開始時間
        start_time = time.time()
        
        # 執行請求
        response = await call_next(request)
        
        # 計算響應時間
        process_time = (time.time() - start_time) * 1000  # 毫秒
        
        # 檢查是否為 API 端點（排除 /docs, /health 等）
        path = request.url.path
        if path.startswith('/api/'):
            # 記錄使用數據
            try:
                await self.usage_logger.log_api_call(
                    endpoint=path,
                    method=request.method,
                    query_params=dict(request.query_params),
                    response_time_ms=process_time,
                    status_code=response.status_code,
                    cache_hit=response.headers.get('X-Cache-Hit', 'false') == 'true'
                )
            except Exception as e:
                logger.error(f"Failed to log usage: {e}")
        
        # 添加響應時間到 headers（用於監控）
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        # 記錄慢請求
        if process_time > 1000:  # > 1 秒
            logger.warning(
                f"Slow request: {request.method} {path} "
                f"took {process_time:.2f}ms"
            )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    請求日誌中間件（詳細版）
    
    記錄請求和回應的詳細資訊（可選啟用）
    """
    
    async def dispatch(self, request: Request, call_next):
        """處理請求並記錄詳細資訊"""
        # 記錄請求
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # 執行請求
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # 記錄回應
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"status={response.status_code} time={process_time:.2f}ms"
        )
        
        return response

