"""
Inspire Agent Session 管理器
支援環境自動切換：
- 開發環境：SQLiteSession
- 生產環境：RedisSession（如果可用）
"""

import os
import logging
from typing import Optional
from agents import SQLiteSession

logger = logging.getLogger(__name__)

# 嘗試導入 RedisSession（可能需要額外安裝）
try:
    from agents.extensions.memory import RedisSession
    REDIS_AVAILABLE = True
except ImportError:
    try:
        # 備用導入路徑
        from agents import RedisSession
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False
        logger.warning("RedisSession not available. Using SQLiteSession for all environments.")


class InspireSessionManager:
    """
    管理 Inspire Agent 的 Session 存儲
    根據環境自動選擇 SQLite 或 Redis
    """
    
    def __init__(self):
        self.env = os.getenv("ENVIRONMENT", "development")
        self.redis_url = os.getenv("REDIS_URL", None)
        
        # SQLite 配置
        self.sqlite_dir = os.getenv("SQLITE_SESSION_DIR", "data/sessions")
        self.ensure_sqlite_dir()
        
        logger.info(f"[InspireSessionManager] Environment: {self.env}")
        logger.info(f"[InspireSessionManager] Redis available: {REDIS_AVAILABLE}")
    
    def ensure_sqlite_dir(self):
        """確保 SQLite 目錄存在"""
        os.makedirs(self.sqlite_dir, exist_ok=True)
    
    def create_session(self, session_id: str):
        """
        根據環境創建適當的 Session
        
        Args:
            session_id: Session 唯一 ID
        
        Returns:
            Session 實例（SQLiteSession 或 RedisSession）
        """
        
        # 生產環境：優先使用 Redis
        if self.env == "production":
            if REDIS_AVAILABLE and self.redis_url:
                logger.info(f"[Session: {session_id}] Using RedisSession (production)")
                return RedisSession.from_url(
                    session_id=session_id,
                    url=self.redis_url
                )
            else:
                logger.warning(f"[Session: {session_id}] Redis not available, falling back to SQLite")
        
        # 開發環境或 Redis 不可用：使用 SQLite
        db_path = os.path.join(self.sqlite_dir, "conversations.db")
        logger.info(f"[Session: {session_id}] Using SQLiteSession: {db_path}")
        
        return SQLiteSession(
            session_id=session_id,
            db_path=db_path
        )
    
    def get_session_storage_info(self) -> dict:
        """
        獲取當前 Session 存儲配置資訊
        
        Returns:
            配置資訊字典
        """
        if self.env == "production" and REDIS_AVAILABLE and self.redis_url:
            storage_type = "redis"
            storage_location = self.redis_url
        else:
            storage_type = "sqlite"
            storage_location = os.path.join(self.sqlite_dir, "conversations.db")
        
        return {
            "environment": self.env,
            "storage_type": storage_type,
            "storage_location": storage_location,
            "redis_available": REDIS_AVAILABLE
        }


# 全局單例
_session_manager: Optional[InspireSessionManager] = None


def get_session_manager() -> InspireSessionManager:
    """獲取全局 Session 管理器（單例）"""
    global _session_manager
    
    if _session_manager is None:
        _session_manager = InspireSessionManager()
    
    return _session_manager


# 便捷函數
def create_inspire_session(session_id: str):
    """
    創建 Inspire Session（便捷函數）
    
    Args:
        session_id: Session 唯一 ID
    
    Returns:
        Session 實例
    """
    manager = get_session_manager()
    return manager.create_session(session_id)

