"""
Cache Strategy Manager
快取策略管理器 - 根據配置選擇最適合的快取策略
"""
import logging
from typing import Any, Optional, Dict
from functools import wraps

from config import settings
from services.cache_manager import get_cache_manager
from services.hybrid_cache_manager import get_hybrid_cache_manager

logger = logging.getLogger(__name__)


class CacheStrategyManager:
    """快取策略管理器"""
    
    def __init__(self):
        self.strategy = settings.cache_strategy.lower()
        self.cache_manager = None
        
        logger.info(f"🔧 Cache strategy: {self.strategy}")
    
    async def get_cache_manager(self):
        """獲取對應的快取管理器"""
        if self.cache_manager is not None:
            return self.cache_manager
        
        if self.strategy == "memory":
            # 純記憶體快取
            self.cache_manager = get_cache_manager()
            logger.info("✅ Using memory cache strategy")
            
        elif self.strategy == "redis":
            # 純 Redis 快取
            from services.redis_cache_manager import get_redis_cache_manager
            self.cache_manager = await get_redis_cache_manager()
            logger.info("✅ Using Redis cache strategy")
            
        elif self.strategy == "hybrid":
            # 混合快取（預設）
            self.cache_manager = get_hybrid_cache_manager()
            logger.info("✅ Using hybrid cache strategy (L1: Memory, L2: Redis)")
            
        else:
            # 降級到記憶體快取
            logger.warning(f"Unknown cache strategy: {self.strategy}, falling back to memory")
            self.cache_manager = get_cache_manager()
        
        return self.cache_manager
    
    async def get(self, key: str) -> Optional[Any]:
        """獲取快取值"""
        cache_manager = await self.get_cache_manager()
        
        if self.strategy == "memory":
            return cache_manager.get(key)
        else:
            return await cache_manager.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """設置快取值"""
        cache_manager = await self.get_cache_manager()
        
        if self.strategy == "memory":
            cache_manager.set(key, value, ttl=ttl or 3600)
            return True
        else:
            return await cache_manager.set(key, value, ttl or 3600)
    
    async def delete(self, key: str) -> bool:
        """刪除快取值"""
        cache_manager = await self.get_cache_manager()
        
        if self.strategy == "memory":
            return cache_manager.delete(key)
        else:
            return await cache_manager.delete(key)
    
    async def get_stats(self) -> Dict[str, Any]:
        """獲取快取統計"""
        cache_manager = await self.get_cache_manager()
        
        base_stats = {
            'strategy': self.strategy,
            'settings': {
                'redis_enabled': settings.redis_enabled,
                'redis_url': settings.redis_url.split('@')[-1] if '@' in settings.redis_url else settings.redis_url,
                'cache_strategy': settings.cache_strategy
            }
        }
        
        if hasattr(cache_manager, 'get_stats'):
            cache_stats = cache_manager.get_stats()
            base_stats.update(cache_stats)
        
        return base_stats
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            cache_manager = await self.get_cache_manager()
            
            if hasattr(cache_manager, 'health_check'):
                health = await cache_manager.health_check()
            else:
                # 簡單測試
                test_key = "health_check_test"
                await self.set(test_key, "test_value", ttl=10)
                result = await self.get(test_key)
                await self.delete(test_key)
                
                health = {
                    'status': 'healthy' if result == "test_value" else 'error',
                    'strategy': self.strategy
                }
            
            return health
            
        except Exception as e:
            return {
                'status': 'error',
                'strategy': self.strategy,
                'error': str(e)
            }


# 全域策略管理器
_strategy_manager: Optional[CacheStrategyManager] = None


async def get_cache_strategy_manager() -> CacheStrategyManager:
    """獲取快取策略管理器單例"""
    global _strategy_manager
    if _strategy_manager is None:
        _strategy_manager = CacheStrategyManager()
    return _strategy_manager


def smart_cache_with_ttl(ttl_seconds: int = 3600, key_func=None):
    """
    智能快取裝飾器
    
    根據配置自動選擇最佳快取策略
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成快取鍵
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                import hashlib
                import json
                key_data = {
                    'func': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
                key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
                cache_key = hashlib.md5(key_str.encode()).hexdigest()
            
            # 使用策略管理器
            strategy_manager = await get_cache_strategy_manager()
            
            # 嘗試從快取獲取
            cached_result = await strategy_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit ({strategy_manager.strategy}): {func.__name__}")
                return cached_result
            
            # 執行原函數
            result = await func(*args, **kwargs)
            
            # 存入快取
            await strategy_manager.set(cache_key, result, ttl=ttl_seconds)
            logger.debug(f"Cached result ({strategy_manager.strategy}): {func.__name__}")
            
            return result
        
        return wrapper
    return decorator
