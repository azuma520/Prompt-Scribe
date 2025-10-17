"""
Cache Manager Service
快取管理服務 - 使用記憶體快取提升效能
"""
from functools import lru_cache, wraps
from typing import Any, Callable, Optional
import hashlib
import json
import time
import logging

logger = logging.getLogger(__name__)


class CacheStats:
    """快取統計"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
    
    @property
    def hit_rate(self) -> float:
        """快取命中率"""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100
    
    def record_hit(self):
        """記錄命中"""
        self.hits += 1
        self.total_requests += 1
    
    def record_miss(self):
        """記錄未命中"""
        self.misses += 1
        self.total_requests += 1
    
    def reset(self):
        """重置統計"""
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
    
    def __repr__(self) -> str:
        return (
            f"CacheStats(hits={self.hits}, misses={self.misses}, "
            f"total={self.total_requests}, hit_rate={self.hit_rate:.2f}%)"
        )


# 全域快取統計
cache_stats = CacheStats()


def generate_cache_key(*args, **kwargs) -> str:
    """
    生成快取鍵
    
    Args:
        *args: 位置參數
        **kwargs: 關鍵字參數
        
    Returns:
        快取鍵字串
    """
    # 將參數轉換為可序列化的字串
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    
    # 使用 MD5 哈希生成短鍵
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_with_ttl(ttl_seconds: int = 3600):
    """
    帶過期時間的快取裝飾器
    
    Args:
        ttl_seconds: 過期時間（秒）
    
    Usage:
        @cache_with_ttl(ttl_seconds=300)
        async def expensive_function(param):
            ...
    """
    cache = {}
    cache_timestamps = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成快取鍵
            cache_key = generate_cache_key(*args, **kwargs)
            
            # 檢查快取
            current_time = time.time()
            if cache_key in cache:
                timestamp = cache_timestamps.get(cache_key, 0)
                
                # 檢查是否過期
                if current_time - timestamp < ttl_seconds:
                    cache_stats.record_hit()
                    logger.debug(f"Cache hit for key: {cache_key[:8]}...")
                    return cache[cache_key]
                else:
                    # 過期，刪除快取
                    del cache[cache_key]
                    del cache_timestamps[cache_key]
                    logger.debug(f"Cache expired for key: {cache_key[:8]}...")
            
            # 未命中，執行函數
            cache_stats.record_miss()
            logger.debug(f"Cache miss for key: {cache_key[:8]}...")
            
            result = await func(*args, **kwargs)
            
            # 儲存到快取
            cache[cache_key] = result
            cache_timestamps[cache_key] = current_time
            
            return result
        
        # 添加快取管理方法
        wrapper.cache_clear = lambda: cache.clear() and cache_timestamps.clear()
        wrapper.cache_info = lambda: {
            'size': len(cache),
            'ttl': ttl_seconds,
            'stats': str(cache_stats)
        }
        
        return wrapper
    
    return decorator


# 常用快取裝飾器預設配置
cache_short = cache_with_ttl(ttl_seconds=300)   # 5 分鐘
cache_medium = cache_with_ttl(ttl_seconds=1800)  # 30 分鐘
cache_long = cache_with_ttl(ttl_seconds=3600)    # 1 小時


def get_cache_stats() -> dict:
    """獲取快取統計資訊"""
    return {
        'hits': cache_stats.hits,
        'misses': cache_stats.misses,
        'total_requests': cache_stats.total_requests,
        'hit_rate': round(cache_stats.hit_rate, 2)
    }


def reset_cache_stats():
    """重置快取統計"""
    cache_stats.reset()
    logger.info("Cache statistics reset")


class MemoryCacheManager:
    """記憶體快取管理器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        self.ttl = 3600  # 預設 1 小時
    
    async def get(self, key: str) -> Optional[Any]:
        """獲取快取值"""
        current_time = time.time()
        if key in self.cache:
            timestamp = self.cache_timestamps.get(key, 0)
            if current_time - timestamp < self.ttl:
                cache_stats.record_hit()
                return self.cache[key]
            else:
                # 過期，刪除快取
                del self.cache[key]
                del self.cache_timestamps[key]
        
        cache_stats.record_miss()
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """設定快取值"""
        current_time = time.time()
        self.cache[key] = value
        self.cache_timestamps[key] = current_time
    
    async def delete(self, key: str) -> bool:
        """刪除快取值"""
        if key in self.cache:
            del self.cache[key]
            del self.cache_timestamps[key]
            return True
        return False
    
    async def clear(self) -> None:
        """清空所有快取"""
        self.cache.clear()
        self.cache_timestamps.clear()
    
    def get_stats(self) -> dict:
        """獲取快取統計"""
        return {
            'type': 'memory',
            'size': len(self.cache),
            'stats': get_cache_stats()
        }


# 全域快取管理器實例
_memory_cache_manager = None


def get_cache_manager():
    """獲取記憶體快取管理器實例"""
    global _memory_cache_manager
    if _memory_cache_manager is None:
        _memory_cache_manager = MemoryCacheManager()
    return _memory_cache_manager
