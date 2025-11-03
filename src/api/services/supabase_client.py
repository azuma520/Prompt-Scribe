"""
Supabase Client Service
提供資料庫連接和查詢功能
"""
from supabase import create_client, Client
import httpx
from typing import Optional, Dict, Any, List
import logging
from functools import lru_cache

# 先獨立解決 settings 匯入（避免其他模組匯入失敗時退回到錯誤路徑）
try:
    from ..config import settings  # 套件相對匯入（最穩定）
except Exception:
    try:
        from src.api.config import settings  # 專案根啟動
    except Exception:
        from config import settings  # 本地退回

# 其他服務模組分開匯入，避免影響 settings 匯入結果
try:
    from .cache_manager import cache_short, cache_medium
    from .relevance_scorer import rank_tags_by_relevance
    from .keyword_analyzer import get_keyword_analyzer
except Exception:
    try:
        # 優先再嘗試套件內相對匯入（部分執行環境第一次可能未建構套件上下文）
        from .cache_manager import cache_short, cache_medium
        from .relevance_scorer import rank_tags_by_relevance
        from .keyword_analyzer import get_keyword_analyzer
    except Exception:
        # 專案根絕對路徑
        from src.api.services.cache_manager import cache_short, cache_medium
        from src.api.services.relevance_scorer import rank_tags_by_relevance
        from src.api.services.keyword_analyzer import get_keyword_analyzer

logger = logging.getLogger(__name__)


class SupabaseService:
    """Supabase 資料庫服務"""
    
    def __init__(self):
        """初始化 Supabase 客戶端"""
        self._client: Optional[Client] = None
        self._initialized = False
    
    @property
    def client(self) -> Client:
        """獲取 Supabase 客戶端實例"""
        if not self._initialized:
            # 建立 httpx 客戶端，支援代理
            proxies: dict | None = None
            if settings.all_proxy or settings.http_proxy or settings.https_proxy:
                proxies = {}
                if settings.all_proxy:
                    proxies = {"all://": settings.all_proxy}
                else:
                    if settings.http_proxy:
                        proxies["http://"] = settings.http_proxy
                    if settings.https_proxy:
                        proxies["https://"] = settings.https_proxy

            # 以 Service Key 優先，否則退回 Anon Key（寫入操作需要 service_role）
            supabase_key = getattr(settings, 'supabase_service_key', None) or settings.supabase_anon_key

            if proxies:
                httpx_client = httpx.Client(
                    proxies=proxies,
                    timeout=settings.request_timeout_seconds,
                    trust_env=False,  # 忽略系統／環境代理，僅依據 .env 設定
                )
                self._client = create_client(
                    settings.supabase_url,
                    supabase_key,
                    http_client=httpx_client,
                )
            else:
                # 無代理時使用預設客戶端，避免不相容參數
                self._client = create_client(
                    settings.supabase_url,
                    supabase_key,
                )
            self._initialized = True
            logger.info("✅ Supabase client initialized")
        return self._client
    
    async def test_connection(self) -> bool:
        """測試資料庫連接"""
        try:
            # 簡單查詢測試連接
            result = self.client.table('tags_final').select('count').limit(1).execute()
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    @cache_short
    async def get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根據名稱查詢單一標籤（帶快取）"""
        try:
            result = self.client.table('tags_final')\
                .select('*')\
                .eq('name', name)\
                .limit(1)\
                .execute()
            
            if result.data:
                tag = result.data[0]
                # 統一輸出型別
                if 'id' in tag and not isinstance(tag['id'], str):
                    tag['id'] = str(tag['id'])
                return tag
            return None
        except Exception as e:
            logger.error(f"Error fetching tag '{name}': {e}")
            raise
    
    @cache_short
    async def get_tags_by_names(self, names: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        批量查詢多個標籤（優化版本，避免 N+1 查詢，帶快取）
        
        Args:
            names: 標籤名稱列表
            
        Returns:
            字典，鍵為標籤名稱，值為標籤資料（若不存在則為 None）
        """
        try:
            if not names:
                return {}
            
            # 使用 IN 查詢一次性獲取所有標籤
            result = self.client.table('tags_final')\
                .select('*')\
                .in_('name', names)\
                .execute()
            
            # 建立名稱到資料的映射
            tag_map = {}
            for tag in result.data:
                # 統一輸出型別
                if 'id' in tag and not isinstance(tag['id'], str):
                    tag['id'] = str(tag['id'])
                tag_map[tag['name']] = tag
            
            # 確保所有請求的標籤都有對應條目（即使不存在）
            result_dict = {}
            for name in names:
                result_dict[name] = tag_map.get(name, None)
            
            logger.info(f"✅ Batch fetched {len(result.data)}/{len(names)} tags")
            return result_dict
            
        except Exception as e:
            logger.error(f"Error batch fetching tags: {e}")
            raise
    
    async def get_tags(
        self,
        limit: int = 20,
        offset: int = 0,
        category: Optional[str] = None,
        name_filter: Optional[str] = None,
        order_by: str = 'post_count',
        order_desc: bool = True
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        查詢標籤列表
        
        Returns:
            (標籤列表, 總數)
        """
        try:
            # 建立查詢
            query = self.client.table('tags_final').select('*', count='exact')
            
            # 應用篩選
            if category:
                query = query.eq('main_category', category)
            if name_filter:
                query = query.ilike('name', f'%{name_filter}%')
            
            # 排序
            query = query.order(order_by, desc=order_desc)
            
            # 分頁
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            
            total = result.count if result.count else 0
            # 統一輸出型別
            rows = result.data or []
            for row in rows:
                if 'id' in row and not isinstance(row['id'], str):
                    row['id'] = str(row['id'])
            return rows, total
            
        except Exception as e:
            logger.error(f"Error fetching tags: {e}")
            raise
    
    @cache_short
    async def search_tags_by_keywords(
        self,
        keywords: List[str],
        limit: int = 20,
        category: Optional[str] = None,
        min_popularity: int = 100,
        use_relevance_ranking: bool = True
    ) -> List[Dict[str, Any]]:
        """
        根據關鍵字搜尋標籤（帶快取和相關性排序）
        
        Args:
            keywords: 關鍵字列表
            limit: 最多返回結果數
            category: 分類篩選
            min_popularity: 最低流行度
            use_relevance_ranking: 使用相關性排序（預設 True）
        """
        try:
            # 使用 OR 查詢多個關鍵字
            query = self.client.table('tags_final').select('*')
            
            # 基本篩選
            query = query.gte('post_count', min_popularity)
            if category:
                query = query.eq('main_category', category)
            
            # 關鍵字匹配 (任一關鍵字)
            # 使用 OR 條件匹配任何關鍵字
            if keywords:
                # 限制 OR 條件數量避免查詢過長
                conditions = []
                for keyword in keywords[:20]:  # 最多 20 個關鍵字
                    conditions.append(f'name.ilike.%{keyword}%')
                
                # 應用 OR 條件
                if conditions:
                    query = query.or_(','.join(conditions))
            
            # 執行查詢（獲取更多候選以便排序）
            candidate_limit = limit * 3 if use_relevance_ranking else limit
            query = query.order('post_count', desc=True).limit(candidate_limit)
            result = query.execute()
            
            rows = result.data or []
            for row in rows:
                if 'id' in row and not isinstance(row['id'], str):
                    row['id'] = str(row['id'])
            
            # 如果啟用相關性排序，重新排序結果
            if use_relevance_ranking and keywords and rows:
                logger.info(f"Applying relevance ranking to {len(rows)} candidates")
                analyzer = get_keyword_analyzer()
                rows = rank_tags_by_relevance(
                    rows,
                    keywords,
                    analyzer,
                    relevance_weight=0.7,  # 相關性 70% + 流行度 30%
                )
                rows = rows[:limit]  # 取前 N 個
            
            return rows
            
        except Exception as e:
            logger.error(f"Error searching tags: {e}")
            raise
    
    async def get_category_stats(self) -> Dict[str, int]:
        """獲取分類統計"""
        try:
            # 注意: 這需要建立 RPC 函數或使用聚合查詢
            # 暫時返回模擬資料
            result = self.client.table('tags_final')\
                .select('main_category')\
                .not_.is_('main_category', 'null')\
                .execute()
            
            # 統計分類
            stats = {}
            for row in result.data:
                cat = row['main_category']
                stats[cat] = stats.get(cat, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error fetching category stats: {e}")
            raise
    
    async def get_total_tags_count(self) -> int:
        """獲取標籤總數"""
        try:
            result = self.client.table('tags_final')\
                .select('*', count='exact')\
                .limit(1)\
                .execute()
            return result.count if result.count else 0
        except Exception as e:
            logger.error(f"Error counting tags: {e}")
            raise


# 全域服務實例
@lru_cache()
def get_supabase_service() -> SupabaseService:
    """獲取 Supabase 服務單例"""
    return SupabaseService()

