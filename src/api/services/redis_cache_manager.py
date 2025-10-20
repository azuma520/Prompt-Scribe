"""
Redis Cache Manager
Redis 快取管理器 - 提供持久化和分散式快取功能
"""
import redis.asyncio as redis
import json
import logging
import time
from typing import Any, Optional, Dict, Union
from functools import wraps
import hashlib
import pickle
import os

logger = logging.getLogger(__name__)


class RedisCacheManager:
    """Redis 快取管理器"""
    
    def __init__(
        self,
        redis_url: str = None,
        default_ttl: int = 3600,
        key_prefix: str = "prompt_scribe:",
        max_retries: int = 3
    ):
        """
        初始化 Redis 快取管理器
        
        Args:
            redis_url: Redis 連接 URL
            default_ttl: 預設 TTL（秒）
            key_prefix: 快取鍵前綴
            max_retries: 最大重試次數
        """
        self.redis_url = redis_url or os.getenv(
            'REDIS_URL', 
            'redis://localhost:6379/0'
        )
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.max_retries = max_retries
        
        # Redis 連接池
        self._redis: Optional[redis.Redis] = None
        self._connection_pool: Optional[redis.ConnectionPool] = None
        
        # 統計資訊
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0,
            'total_requests': 0
        }
        
        # 可用性標記
        self.is_available = False
    
    async def connect(self):
        """建立 Redis 連接"""
        try:
            # 建立連接池
            self._connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                decode_responses=False,  # 保持二進制以支援 pickle
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # 建立 Redis 客戶端
            self._redis = redis.Redis(connection_pool=self._connection_pool)
            
            # 測試連接
            await self._redis.ping()
            self.is_available = True
            
            logger.info("✅ Redis cache connected successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}, falling back to memory cache")
            self.is_available = False
    
    async def disconnect(self):
        """關閉 Redis 連接"""
        if self._redis:
            await self._redis.close()
        if self._connection_pool:
            await self._connection_pool.disconnect()
    
    def _make_key(self, key: str) -> str:
        """生成完整的快取鍵"""
        return f"{self.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """序列化值"""
        try:
            # 嘗試 JSON 序列化（更輕量）
            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(value, ensure_ascii=False).encode('utf-8')
            else:
                # 使用 pickle 處理複雜對象
                return pickle.dumps(value)
        except Exception:
            # 最後退回到 pickle
            return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """反序列化值"""
        try:
            # 嘗試 JSON 反序列化
            text = data.decode('utf-8')
            return json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError):
            # 使用 pickle 反序列化
            return pickle.loads(data)
    
    async def get(self, key: str) -> Optional[Any]:
        """獲取快取值"""
        if not self.is_available:
            return None
        
        self.stats['total_requests'] += 1
        
        try:
            redis_key = self._make_key(key)
            data = await self._redis.get(redis_key)
            
            if data is None:
                self.stats['misses'] += 1
                return None
            
            value = self._deserialize_value(data)
            self.stats['hits'] += 1
            
            logger.debug(f"Cache hit: {key}")
            return value
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """設置快取值"""
        if not self.is_available:
            return False
        
        try:
            redis_key = self._make_key(key)
            serialized_value = self._serialize_value(value)
            
            ttl = ttl or self.default_ttl
            
            await self._redis.setex(redis_key, ttl, serialized_value)
            self.stats['sets'] += 1
            
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """刪除快取值"""
        if not self.is_available:
            return False
        
        try:
            redis_key = self._make_key(key)
            result = await self._redis.delete(redis_key)
            
            if result > 0:
                self.stats['deletes'] += 1
                logger.debug(f"Cache deleted: {key}")
                return True
            
            return False
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """檢查鍵是否存在"""
        if not self.is_available:
            return False
        
        try:
            redis_key = self._make_key(key)
            result = await self._redis.exists(redis_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    async def clear_all(self) -> bool:
        """清空所有快取（危險操作）"""
        if not self.is_available:
            return False
        
        try:
            # 只刪除有前綴的鍵
            pattern = f"{self.key_prefix}*"
            keys = await self._redis.keys(pattern)
            
            if keys:
                await self._redis.delete(*keys)
                logger.warning(f"Cleared {len(keys)} cache keys")
            
            return True
            
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """獲取鍵的剩餘 TTL"""
        if not self.is_available:
            return None
        
        try:
            redis_key = self._make_key(key)
            ttl = await self._redis.ttl(redis_key)
            
            if ttl == -2:  # 鍵不存在
                return None
            elif ttl == -1:  # 鍵存在但無過期時間
                return -1
            else:
                return ttl
                
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取快取統計"""
        total_requests = self.stats['total_requests']
        hit_rate = (
            self.stats['hits'] / total_requests 
            if total_requests > 0 else 0
        )
        
        return {
            **self.stats,
            'hit_rate': round(hit_rate, 3),
            'is_available': self.is_available,
            'redis_url': self.redis_url.split('@')[-1] if '@' in self.redis_url else self.redis_url,
            'key_prefix': self.key_prefix
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            if not self.is_available:
                return {
                    'status': 'unavailable',
                    'message': 'Redis not connected'
                }
            
            # Ping 測試
            start_time = time.time()
            await self._redis.ping()
            ping_time = (time.time() - start_time) * 1000
            
            # 獲取資訊
            info = await self._redis.info()
            
            return {
                'status': 'healthy',
                'ping_ms': round(ping_time, 2),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'unknown'),
                'redis_version': info.get('redis_version', 'unknown')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


# 全域 Redis 快取管理器實例
_redis_cache_manager: Optional[RedisCacheManager] = None


async def get_redis_cache_manager() -> RedisCacheManager:
    """獲取 Redis 快取管理器單例"""
    global _redis_cache_manager
    
    if _redis_cache_manager is None:
        _redis_cache_manager = RedisCacheManager()
        await _redis_cache_manager.connect()
    
    return _redis_cache_manager


def redis_cache_with_ttl(ttl_seconds: int = 3600, key_func=None):
    """
    Redis 快取裝飾器
    
    Args:
        ttl_seconds: 快取過期時間（秒）
        key_func: 自定義鍵生成函數
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成快取鍵
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 預設鍵生成策略
                key_data = {
                    'func': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
                key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
                cache_key = hashlib.md5(key_str.encode()).hexdigest()
            
            # 嘗試從快取獲取
            try:
                cache_manager = await get_redis_cache_manager()
                cached_result = await cache_manager.get(cache_key)
                
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                    return cached_result
                
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")
            
            # 執行原函數
            result = await func(*args, **kwargs)
            
            # 存入快取
            try:
                cache_manager = await get_redis_cache_manager()
                await cache_manager.set(cache_key, result, ttl_seconds)
                logger.debug(f"Cached result for {func.__name__}: {cache_key}")
                
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")
            
            return result
        
        return wrapper
    return decorator


# 快取預熱功能
class CacheWarmer:
    """快取預熱器"""
    
    def __init__(self, cache_manager: RedisCacheManager):
        self.cache_manager = cache_manager
    
    async def warm_popular_tags(self, top_n: int = 100):
        """預熱熱門標籤"""
        try:
            logger.info("Cache warming skipped: SupabaseService.get_popular_tags not implemented")
            # TODO: 實現 get_popular_tags 方法後再啟用
            # from services.supabase_client import get_supabase_service
            # service = get_supabase_service()
            # popular_tags = await service.get_popular_tags(top_n)
            # for tag in popular_tags:
            #     cache_key = f"popular_tag:{tag['tag']}"
            #     await self.cache_manager.set(cache_key, tag, ttl=7200)
            # logger.info(f"✅ Warmed up {len(popular_tags)} popular tags")
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
    
    async def warm_categories(self):
        """預熱分類資訊"""
        try:
            from services.supabase_client import get_supabase_service
            
            service = get_supabase_service()
            
            # 獲取分類統計
            categories = await service.get_category_stats()
            
            cache_key = "category_stats"
            await self.cache_manager.set(cache_key, categories, ttl=3600)  # 1小時
            
            logger.info("✅ Warmed up category statistics")
            
        except Exception as e:
            logger.error(f"Category warming failed: {e}")


# 測試和範例
if __name__ == "__main__":
    import asyncio
    
    async def test_redis_cache():
        """測試 Redis 快取"""
        manager = RedisCacheManager()
        await manager.connect()
        
        # 測試基本操作
        await manager.set("test_key", {"data": "test_value"}, ttl=60)
        result = await manager.get("test_key")
        print(f"Cache test result: {result}")
        
        # 測試統計
        stats = manager.get_stats()
        print(f"Cache stats: {stats}")
        
        # 測試健康檢查
        health = await manager.health_check()
        print(f"Health check: {health}")
        
        await manager.disconnect()
    
    # 執行測試
    asyncio.run(test_redis_cache())
