"""
Inspire Agent 資料庫封裝層
集中管理所有資料庫操作和業務邏輯

設計原則：
1. 統一接口：所有工具通過這個封裝層訪問資料庫
2. 業務邏輯集中：NSFW 過濾、別名解析等只在這裡實作
3. 錯誤處理統一：所有異常在這裡處理，不拋給工具
4. 支援快取：熱門查詢可以快取
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging

from services.supabase_client import get_supabase_service
from inspire_config.content_rating import (
    classify_content_level,
    filter_tags_by_user_access
)
from inspire_config.database_mappings import (
    categorize_tag_by_rules,
    detect_conflicts,
    resolve_alias
)

logger = logging.getLogger(__name__)


class InspireDBWrapper:
    """
    Inspire Agent 資料庫封裝
    提供高階的、業務導向的資料庫操作接口
    """
    
    def __init__(self):
        self.db = get_supabase_service()
        self.client = self.db.client
    
    # ============================================
    # Session 管理（inspire_sessions 表）
    # ============================================
    
    def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        user_access_level: str = "all-ages"
    ) -> Dict[str, Any]:
        """
        創建新的 Inspire Session
        
        Args:
            session_id: Session 唯一 ID
            user_id: 使用者 ID（可選）
            user_access_level: 使用者權限級別（all-ages/r15/r18）
        
        Returns:
            創建的 Session 資料
        """
        try:
            result = self.client.table('inspire_sessions').insert({
                "session_id": session_id,
                "user_id": user_id,
                "user_access_level": user_access_level,
                "current_phase": "understanding",
                "total_cost": 0.0,
                "total_tokens": 0,
                "tool_call_count": {}
            }).execute()
            
            logger.info(f"✅ Session created: {session_id}")
            return result.data[0] if result.data else {}
        
        except Exception as e:
            logger.error(f"❌ Failed to create session {session_id}: {e}")
            return {"error": str(e)}
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取 Session 資料
        
        Args:
            session_id: Session ID
        
        Returns:
            Session 資料，如果不存在則返回 None
        """
        try:
            result = self.client.table('inspire_sessions')\
                .select('*')\
                .eq('session_id', session_id)\
                .execute()
            
            if result.data:
                return result.data[0]
            else:
                logger.warning(f"⚠️ Session not found: {session_id}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Failed to get session {session_id}: {e}")
            return None
    
    def update_session_phase(
        self,
        session_id: str,
        phase: str
    ) -> bool:
        """
        更新 Session 狀態機
        
        Args:
            session_id: Session ID
            phase: 新狀態（understanding/exploring/refining/finalizing/completed/aborted）
        
        Returns:
            是否成功
        """
        try:
            self.client.table('inspire_sessions')\
                .update({
                    "current_phase": phase,
                    "updated_at": datetime.now().isoformat()
                })\
                .eq('session_id', session_id)\
                .execute()
            
            logger.info(f"✅ Session {session_id} phase updated: {phase}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to update session phase: {e}")
            return False
    
    def update_session_cost(
        self,
        session_id: str,
        cost: float,
        tokens: int
    ) -> Dict[str, Any]:
        """
        更新 Session 成本追蹤
        自動檢查是否超過上限
        
        Args:
            session_id: Session ID
            cost: 新增的成本
            tokens: 新增的 token 數
        
        Returns:
            {
                "success": bool,
                "over_limit": bool,
                "current_cost": float,
                "current_tokens": int
            }
        """
        COST_LIMIT = 0.015  # $0.015 上限
        
        try:
            # 獲取當前值
            session = self.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            new_cost = session["total_cost"] + cost
            new_tokens = session["total_tokens"] + tokens
            
            # 更新
            self.client.table('inspire_sessions')\
                .update({
                    "total_cost": new_cost,
                    "total_tokens": new_tokens,
                    "updated_at": datetime.now().isoformat()
                })\
                .eq('session_id', session_id)\
                .execute()
            
            over_limit = new_cost >= COST_LIMIT
            
            if over_limit:
                logger.warning(f"⚠️ Session {session_id} cost limit reached: ${new_cost:.6f}")
            
            return {
                "success": True,
                "over_limit": over_limit,
                "current_cost": new_cost,
                "current_tokens": new_tokens
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to update session cost: {e}")
            return {"success": False, "error": str(e)}
    
    def update_session_data(
        self,
        session_id: str,
        **kwargs
    ) -> bool:
        """
        更新 Session 業務資料（extracted_intent, generated_directions 等）
        
        Args:
            session_id: Session ID
            **kwargs: 要更新的欄位
        
        Returns:
            是否成功
        """
        try:
            update_data = {**kwargs, "updated_at": datetime.now().isoformat()}
            
            self.client.table('inspire_sessions')\
                .update(update_data)\
                .eq('session_id', session_id)\
                .execute()
            
            logger.info(f"Session {session_id} data updated: {list(kwargs.keys())}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to update session data: {e}")
            return False
    
    def complete_session(
        self,
        session_id: str,
        quality_score: int,
        final_output: Dict[str, Any]
    ) -> bool:
        """
        標記 Session 為完成
        
        Args:
            session_id: Session ID
            quality_score: 品質分數（0-100）
            final_output: 最終輸出
        
        Returns:
            是否成功
        """
        try:
            self.client.table('inspire_sessions')\
                .update({
                    "current_phase": "completed",
                    "quality_score": quality_score,
                    "final_output": final_output,
                    "completed_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                })\
                .eq('session_id', session_id)\
                .execute()
            
            logger.info(f"✅ Session {session_id} completed (score: {quality_score})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to complete session: {e}")
            return False
    
    # ============================================
    # 標籤查詢（tags_final 表）
    # ============================================
    
    def search_tags_by_keywords(
        self,
        keywords: List[str],
        user_access: str = "all-ages",
        min_popularity: int = 1000,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        根據關鍵字搜尋標籤
        自動應用 NSFW 過濾、別名解析
        
        契約保證：
        - 返回的標籤一定存在於資料庫
        - 已過濾 NSFW（根據 user_access）
        - 返回格式：[{tag, category, popularity, usage_hint}]
        
        Args:
            keywords: 搜尋關鍵字列表
            user_access: 使用者權限（all-ages/r15/r18）
            min_popularity: 最低使用次數
            max_results: 最多返回幾個
        
        Returns:
            標籤列表（標準格式）
        """
        try:
            # 構建查詢
            query = self.client.table('tags_final')\
                .select('name, post_count, main_category')\
                .gte('post_count', min_popularity)
            
            # 關鍵字匹配（OR 條件）
            if keywords:
                conditions = [f'name.ilike.%{kw}%' for kw in keywords[:5]]
                query = query.or_(','.join(conditions))
            
            # 執行查詢（多查一些，過濾後可能不夠）
            query = query.order('post_count', desc=True).limit(max_results * 3)
            result = query.execute()
            
            # 過濾 NSFW + 格式化
            examples = []
            for row in result.data:
                tag_name = row["name"]
                
                # 檢測內容等級
                content_level = classify_content_level(tag_name)
                
                # 封禁內容跳過
                if content_level == "blocked":
                    continue
                
                # 檢查權限
                if content_level == "r18" and user_access not in ["r18"]:
                    continue
                
                if content_level == "r15" and user_access == "all-ages":
                    continue
                
                # 格式化（嚴格契約格式）
                examples.append({
                    "tag": tag_name,
                    "category": categorize_tag_by_rules(tag_name, row.get("main_category")),
                    "popularity": row["post_count"],
                    "usage_hint": f"{row['post_count']:,} 次使用"
                })
                
                if len(examples) >= max_results:
                    break
            
            logger.info(f"✅ Search found {len(examples)} tags for keywords: {keywords}")
            return examples
        
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []  # 契約保證：不拋異常，返回空列表
    
    def validate_tags_exist(
        self,
        tags: List[str],
        user_access: str = "all-ages"
    ) -> Tuple[List[str], List[str]]:
        """
        批量驗證標籤是否有效
        自動應用別名解析和 NSFW 過濾
        
        契約保證：
        - 返回 (有效標籤列表, 無效標籤列表)
        - 有效標籤已通過 NSFW 檢查
        - 已解析別名
        
        Args:
            tags: 要驗證的標籤列表
            user_access: 使用者權限
        
        Returns:
            (valid_tags, invalid_tags)
        """
        try:
            # 解析別名
            resolved_tags = [resolve_alias(t) for t in tags]
            
            # 查詢資料庫
            result = self.client.table('tags_final')\
                .select('name')\
                .in_('name', resolved_tags)\
                .execute()
            
            valid_tags_set = {row["name"] for row in result.data}
            
            # 分離有效和無效
            db_valid = [t for t in resolved_tags if t in valid_tags_set]
            db_invalid = [t for t in resolved_tags if t not in valid_tags_set]
            
            # 應用 NSFW 過濾
            allowed, removed, _ = filter_tags_by_user_access(db_valid, user_access)
            
            # 被過濾的標籤也算「無效」
            final_invalid = db_invalid + removed
            
            logger.info(f"✅ Validated {len(tags)} tags: {len(allowed)} valid, {len(final_invalid)} invalid")
            return (allowed, final_invalid)
        
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return ([], tags)  # 契約保證：失敗時全部算無效
    
    def get_tags_details(
        self,
        tags: List[str]
    ) -> List[Dict[str, Any]]:
        """
        批量獲取標籤詳細資訊
        
        Args:
            tags: 標籤列表
        
        Returns:
            標籤資訊列表
        """
        try:
            result = self.client.table('tags_final')\
                .select('name, main_category, post_count')\
                .in_('name', tags)\
                .execute()
            
            return result.data
        
        except Exception as e:
            logger.error(f"❌ Failed to get tag details: {e}")
            return []
    
    def get_popular_tags(
        self,
        user_access: str = "all-ages",
        min_popularity: int = 10000,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        獲取熱門標籤（用於推薦）
        
        Args:
            user_access: 使用者權限
            min_popularity: 最低人氣
            max_results: 最多幾個
        
        Returns:
            熱門標籤列表
        """
        try:
            result = self.client.table('tags_final')\
                .select('name, post_count, main_category')\
                .gte('post_count', min_popularity)\
                .order('post_count', desc=True)\
                .limit(max_results * 2)\
                .execute()
            
            # 過濾 NSFW
            popular = []
            for row in result.data:
                content_level = classify_content_level(row["name"])
                
                if content_level == "blocked":
                    continue
                
                if content_level == "r18" and user_access not in ["r18"]:
                    continue
                
                if content_level == "r15" and user_access == "all-ages":
                    continue
                
                popular.append({
                    "tag": row["name"],
                    "category": categorize_tag_by_rules(row["name"], row.get("main_category")),
                    "popularity": row["post_count"]
                })
                
                if len(popular) >= max_results:
                    break
            
            logger.info(f"✅ Got {len(popular)} popular tags")
            return popular
        
        except Exception as e:
            logger.error(f"❌ Failed to get popular tags: {e}")
            return []
    
    # ============================================
    # 工具統計（用於監控）
    # ============================================
    
    def increment_tool_call(
        self,
        session_id: str,
        tool_name: str
    ) -> bool:
        """
        記錄工具調用次數
        
        Args:
            session_id: Session ID
            tool_name: 工具名稱
        
        Returns:
            是否成功
        """
        try:
            session = self.get_session(session_id)
            if not session:
                return False
            
            tool_call_count = session.get("tool_call_count", {})
            tool_call_count[tool_name] = tool_call_count.get(tool_name, 0) + 1
            
            self.client.table('inspire_sessions')\
                .update({"tool_call_count": tool_call_count})\
                .eq('session_id', session_id)\
                .execute()
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to increment tool call: {e}")
            return False


# 全局單例
_db_wrapper: Optional[InspireDBWrapper] = None


def get_inspire_db_wrapper() -> InspireDBWrapper:
    """獲取全局 DB 封裝實例（單例）"""
    global _db_wrapper
    
    if _db_wrapper is None:
        _db_wrapper = InspireDBWrapper()
    
    return _db_wrapper

