"""
Usage Logger Service
使用數據記錄服務 - 收集 API 使用數據用於分析和優化
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json

from services.supabase_client import get_supabase_service

logger = logging.getLogger(__name__)


class UsageLogger:
    """使用數據記錄器"""
    
    def __init__(self):
        """初始化記錄器"""
        self.enabled = True  # 可通過配置控制
        self._buffer = []  # 緩衝區（批量寫入）
        self._buffer_size = 10  # 每 10 條記錄批量寫入
    
    async def log_api_call(
        self,
        endpoint: str,
        method: str = "POST",
        query_params: Optional[Dict] = None,
        request_body: Optional[Dict] = None,
        response_data: Optional[Dict] = None,
        response_time_ms: Optional[float] = None,
        status_code: int = 200,
        cache_hit: bool = False,
        error_message: Optional[str] = None
    ):
        """
        記錄 API 調用
        
        Args:
            endpoint: API 端點
            method: HTTP 方法
            query_params: 查詢參數
            request_body: 請求體
            response_data: 回應數據（可選，避免記錄大量數據）
            response_time_ms: 響應時間（毫秒）
            status_code: HTTP 狀態碼
            cache_hit: 是否命中快取
            error_message: 錯誤訊息
        """
        if not self.enabled:
            return
        
        try:
            log_entry = {
                'endpoint': endpoint,
                'method': method,
                'query_params': query_params or {},
                'request_body': request_body or {},
                'response_time_ms': int(response_time_ms) if response_time_ms else None,
                'status_code': status_code,
                'cache_hit': cache_hit,
                'error_message': error_message,
                'timestamp': datetime.now().isoformat()
            }
            
            # 添加摘要資訊（避免存儲大量數據）
            if response_data:
                log_entry['response_summary'] = self._summarize_response(
                    endpoint, 
                    response_data
                )
            
            # 添加到緩衝區
            self._buffer.append(log_entry)
            
            # 批量寫入
            if len(self._buffer) >= self._buffer_size:
                await self._flush_buffer()
            
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")
    
    def _summarize_response(self, endpoint: str, data: Dict) -> Dict:
        """
        摘要回應數據（只保留關鍵資訊）
        """
        summary = {}
        
        if endpoint == "/api/llm/recommend-tags":
            summary = {
                'recommended_count': len(data.get('recommended_tags', [])),
                'top_3_tags': [
                    t.get('tag') for t in data.get('recommended_tags', [])[:3]
                ],
                'quality_score': data.get('quality_assessment', {}).get('overall_score'),
            }
        elif endpoint == "/api/llm/validate-prompt":
            summary = {
                'overall_score': data.get('overall_score'),
                'issues_count': len(data.get('issues', [])),
            }
        elif endpoint == "/api/v1/search":
            summary = {
                'results_count': len(data.get('data', [])),
            }
        
        return summary
    
    async def _flush_buffer(self):
        """批量寫入緩衝區數據到資料庫"""
        if not self._buffer:
            return
        
        try:
            # 這裡可以選擇寫入 Supabase 或本地文件
            # 為了簡單，先寫入本地日誌
            for entry in self._buffer:
                logger.info(
                    f"API_USAGE: {entry['endpoint']} | "
                    f"{entry['response_time_ms']}ms | "
                    f"cache={entry['cache_hit']} | "
                    f"status={entry['status_code']}"
                )
            
            # 清空緩衝區
            self._buffer = []
            
        except Exception as e:
            logger.error(f"Failed to flush usage log buffer: {e}")
    
    async def log_recommendation(
        self,
        query: str,
        recommended_tags: List[str],
        response_time_ms: float,
        quality_score: int,
        cache_hit: bool = False
    ):
        """
        記錄標籤推薦（簡化版）
        
        專門用於分析推薦品質
        """
        await self.log_api_call(
            endpoint="/api/llm/recommend-tags",
            method="POST",
            request_body={'description': query},
            response_data={
                'recommended_tags': [{'tag': t} for t in recommended_tags],
                'quality_assessment': {'overall_score': quality_score}
            },
            response_time_ms=response_time_ms,
            cache_hit=cache_hit
        )
    
    async def log_search(
        self,
        query: str,
        results_count: int,
        response_time_ms: float,
        cache_hit: bool = False
    ):
        """記錄搜尋查詢"""
        await self.log_api_call(
            endpoint="/api/v1/search",
            method="POST",
            request_body={'query': query},
            response_data={'data': [{}] * results_count},  # 只記錄數量
            response_time_ms=response_time_ms,
            cache_hit=cache_hit
        )


# 全域記錄器實例
_usage_logger: Optional[UsageLogger] = None


def get_usage_logger() -> UsageLogger:
    """獲取使用數據記錄器單例"""
    global _usage_logger
    if _usage_logger is None:
        _usage_logger = UsageLogger()
    return _usage_logger


# 統計分析函數（用於分析收集的數據）
class UsageAnalytics:
    """使用數據分析"""
    
    @staticmethod
    async def get_popular_queries(limit: int = 20) -> List[Dict]:
        """獲取熱門查詢（需要實作資料庫存儲）"""
        # TODO: 從資料庫查詢
        return []
    
    @staticmethod
    async def get_average_response_time_by_endpoint() -> Dict[str, float]:
        """獲取各端點平均響應時間"""
        # TODO: 從日誌計算
        return {}
    
    @staticmethod
    async def get_cache_hit_rate() -> float:
        """獲取快取命中率"""
        # TODO: 從日誌計算
        return 0.0
    
    @staticmethod
    async def get_quality_score_distribution() -> Dict:
        """獲取品質評分分佈"""
        # TODO: 從日誌計算
        return {}

