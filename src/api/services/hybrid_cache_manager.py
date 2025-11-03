"""
Hybrid Cache Manager
混合快取管理器 - 結合記憶體快取和 Redis 快取的雙層架構
"""
import logging
import time
from typing import Any, Optional, Dict
from functools import wraps
import asyncio

from .cache_manager import get_cache_manager
from .redis_cache_manager import get_redis_cache_manager

logger = logging.getLogger(__name__)


class HybridCacheManager:
    """
    混合快取管理器
    
    L1: 記憶體快取（極快，但容量有限）
    L2: Redis 快取（較快，容量大，持久化）
    """
    
    def __init__(
        self,
        l1_ttl: int = 300,      # L1 快取 5 分鐘
        l2_ttl: int = 3600,     # L2 快取 1 小時
        l1_max_size: int = 1000, # L1 最大條目數
        auto_promote: bool = True # 自動提升熱資料到 L1
    ):
        self.l1_ttl = l1_ttl
        self.l2_ttl = l2_ttl
        self.l1_max_size = l1_max_size
        self.auto_promote = auto_promote
        
        # 快取統計
        self.stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0,
            'promotions': 0,  # L2 → L1 提升次數
            'demotions': 0,   # L1 → L2 降級次數
            'total_requests': 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """
        分層獲取快取值
        
        1. 先檢查 L1 (記憶體)
        2. 再檢查 L2 (Redis)
        3. 如果 L2 命中且啟用自動提升，將資料提升到 L1
        """
        self.stats['total_requests'] += 1
        
        # L1: 記憶體快取
        try:
            memory_cache = get_cache_manager()
            l1_result = memory_cache.get(key)
            
            if l1_result is not None:
                self.stats['l1_hits'] += 1
                logger.debug(f"L1 cache hit: {key}")
                return l1_result
        except Exception as e:
            logger.warning(f"L1 cache error: {e}")
        
        # L2: Redis 快取
        try:
            redis_cache = await get_redis_cache_manager()
            l2_result = await redis_cache.get(key)
            
            if l2_result is not None:
                self.stats['l2_hits'] += 1
                logger.debug(f"L2 cache hit: {key}")
                
                # 自動提升到 L1
                if self.auto_promote:
                    await self._promote_to_l1(key, l2_result)
                
                return l2_result
        except Exception as e:
            logger.warning(f"L2 cache error: {e}")
        
        # 快取未命中
        self.stats['misses'] += 1
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        l1_ttl: Optional[int] = None,
        l2_ttl: Optional[int] = None
    ) -> bool:
        """
        設置快取值到兩層
        
        同時寫入 L1 和 L2，確保資料一致性
        """
        l1_ttl = l1_ttl or self.l1_ttl
        l2_ttl = l2_ttl or self.l2_ttl
        
        success_count = 0
        
        # 寫入 L1
        try:
            memory_cache = get_cache_manager()
            memory_cache.set(key, value, ttl=l1_ttl)
            success_count += 1
            logger.debug(f"Set L1 cache: {key}")
        except Exception as e:
            logger.warning(f"L1 set error: {e}")
        
        # 寫入 L2
        try:
            redis_cache = await get_redis_cache_manager()
            await redis_cache.set(key, value, ttl=l2_ttl)
            success_count += 1
            logger.debug(f"Set L2 cache: {key}")
        except Exception as e:
            logger.warning(f"L2 set error: {e}")
        
        return success_count > 0
    
    async def delete(self, key: str) -> bool:
        """刪除兩層快取的值"""
        success_count = 0
        
        # 刪除 L1
        try:
            memory_cache = get_cache_manager()
            if memory_cache.delete(key):
                success_count += 1
        except Exception as e:
            logger.warning(f"L1 delete error: {e}")
        
        # 刪除 L2
        try:
            redis_cache = await get_redis_cache_manager()
            if await redis_cache.delete(key):
                success_count += 1
        except Exception as e:
            logger.warning(f"L2 delete error: {e}")
        
        return success_count > 0
    
    async def _promote_to_l1(self, key: str, value: Any):
        """將資料從 L2 提升到 L1"""
        try:
            memory_cache = get_cache_manager()
            memory_cache.set(key, value, ttl=self.l1_ttl)
            self.stats['promotions'] += 1
            logger.debug(f"Promoted to L1: {key}")
        except Exception as e:
            logger.warning(f"Promotion failed: {e}")
    
    async def _demote_to_l2_only(self, key: str):
        """將資料從 L1 降級（僅保留在 L2）"""
        try:
            memory_cache = get_cache_manager()
            memory_cache.delete(key)
            self.stats['demotions'] += 1
            logger.debug(f"Demoted from L1: {key}")
        except Exception as e:
            logger.warning(f"Demotion failed: {e}")
    
    async def warm_cache(self, key: str, value: Any):
        """預熱快取（寫入兩層）"""
        await self.set(key, value)
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取快取統計"""
        total = self.stats['total_requests']
        
        if total == 0:
            return {**self.stats, 'l1_hit_rate': 0, 'l2_hit_rate': 0, 'overall_hit_rate': 0}
        
        l1_hit_rate = self.stats['l1_hits'] / total
        l2_hit_rate = self.stats['l2_hits'] / total
        overall_hit_rate = (self.stats['l1_hits'] + self.stats['l2_hits']) / total
        
        return {
            **self.stats,
            'l1_hit_rate': round(l1_hit_rate, 3),
            'l2_hit_rate': round(l2_hit_rate, 3),
            'overall_hit_rate': round(overall_hit_rate, 3)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        l1_status = "healthy"
        l2_status = "unknown"
        
        # 檢查 L1
        try:
            memory_cache = get_cache_manager()
            # 同步調用，不需要 await
            l1_value = memory_cache.cache.get("health_check")
            l1_status = "healthy" if l1_value is not None else "empty"
        except Exception as e:
            l1_status = f"error: {e}"
        
        # 檢查 L2
        try:
            redis_cache = await get_redis_cache_manager()
            l2_health = await redis_cache.health_check()
            l2_status = l2_health.get('status', 'unknown')
        except Exception as e:
            l2_status = f"error: {e}"
        
        return {
            'l1_status': l1_status,
            'l2_status': l2_status,
            'overall_status': 'healthy' if l1_status == 'healthy' else 'partial',
            'stats': self.get_stats()
        }


# 全域混合快取管理器
_hybrid_cache_manager: Optional[HybridCacheManager] = None


def get_hybrid_cache_manager() -> HybridCacheManager:
    """獲取混合快取管理器單例"""
    global _hybrid_cache_manager
    if _hybrid_cache_manager is None:
        _hybrid_cache_manager = HybridCacheManager()
    return _hybrid_cache_manager


def hybrid_cache_with_ttl(
    l1_ttl: int = 300,
    l2_ttl: int = 3600,
    key_func=None
):
    """
    混合快取裝飾器
    
    自動使用雙層快取策略
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
            
            # 嘗試從快取獲取
            cache_manager = get_hybrid_cache_manager()
            cached_result = await cache_manager.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # 執行原函數
            result = await func(*args, **kwargs)
            
            # 存入快取
            await cache_manager.set(cache_key, result, l1_ttl=l1_ttl, l2_ttl=l2_ttl)
            
            return result
        
        return wrapper
    return decorator


# 智能快取策略
class SmartCacheStrategy:
    """智能快取策略"""
    
    def __init__(self, hybrid_manager: HybridCacheManager):
        self.hybrid_manager = hybrid_manager
        self.access_patterns = {}  # 記錄存取模式
    
    def should_promote(self, key: str) -> bool:
        """判斷是否應該提升到 L1"""
        pattern = self.access_patterns.get(key, {'count': 0, 'last_access': 0})
        
        # 如果最近訪問頻繁，提升到 L1
        current_time = time.time()
        if current_time - pattern['last_access'] < 300:  # 5分鐘內
            if pattern['count'] >= 3:  # 訪問3次以上
                return True
        
        return False
    
    def record_access(self, key: str):
        """記錄訪問模式"""
        current_time = time.time()
        
        if key not in self.access_patterns:
            self.access_patterns[key] = {'count': 1, 'last_access': current_time}
        else:
            pattern = self.access_patterns[key]
            pattern['count'] += 1
            pattern['last_access'] = current_time
    
    async def optimize_cache(self):
        """優化快取分佈"""
        # 定期清理冷資料
        current_time = time.time()
        cold_keys = []
        
        for key, pattern in self.access_patterns.items():
            if current_time - pattern['last_access'] > 3600:  # 1小時無訪問
                cold_keys.append(key)
        
        # 從 L1 移除冷資料
        for key in cold_keys:
            await self.hybrid_manager._demote_to_l2_only(key)
            del self.access_patterns[key]
        
        logger.info(f"Optimized cache: removed {len(cold_keys)} cold entries from L1")
