"""
語義搜尋服務

提供基於嵌入向量的語義搜尋功能，整合到 Inspire Agent 中。

Version: 2.0.0
Date: 2025-10-22
"""

import os
import json
import time
import logging
from typing import List, Dict, Optional
import numpy as np
from openai import AsyncOpenAI
from supabase import Client

from .inspire_db_wrapper import InspireDBWrapper
from ..models.inspire_models import SemanticSearchRequest, SemanticSearchResponse, SemanticSearchResult

logger = logging.getLogger(__name__)

class SemanticSearchService:
    """語義搜尋服務"""
    
    def __init__(self, db_wrapper: InspireDBWrapper, openai_client: AsyncOpenAI):
        self.db_wrapper = db_wrapper
        self.openai_client = openai_client
        self.supabase: Client = db_wrapper.client
    
    async def search(self, request: SemanticSearchRequest) -> SemanticSearchResponse:
        """
        執行語義搜尋
        
        Args:
            request: 搜尋請求
            
        Returns:
            SemanticSearchResponse: 搜尋結果
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Starting semantic search for query: '{request.query}'")
            
            # 1. 生成查詢嵌入向量
            query_embedding = await self._generate_query_embedding(request.query)
            if not query_embedding:
                raise ValueError("Failed to generate query embedding")
            
            # 2. 優先透過 pgvector RPC 在資料庫端做全庫相似度排序
            results = await self._search_via_rpc(
                query_embedding=query_embedding,
                top_k=request.top_k,
                min_similarity=request.min_similarity,
                user_access_level=request.user_access_level
            )

            # 若 RPC 不可用，退回應用端本地計算（最多取 1000 筆）
            if not results:
                results = await self._search_similar_tags(
                    query_embedding=query_embedding,
                    top_k=request.top_k,
                    min_similarity=request.min_similarity,
                    user_access_level=request.user_access_level
                )
            
            # 3. 獲取嵌入向量統計
            embedding_count = await self._get_embedding_count()
            
            search_time_ms = (time.time() - start_time) * 1000
            
            logger.info(f"✅ Semantic search completed in {search_time_ms:.1f}ms, found {len(results)} results")
            
            return SemanticSearchResponse(
                query=request.query,
                results=results,
                total_found=len(results),
                search_time_ms=search_time_ms,
                embedding_count=embedding_count
            )
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            raise

    async def _search_via_rpc(
        self,
        query_embedding: List[float],
        top_k: int,
        min_similarity: float,
        user_access_level: str
    ) -> List[SemanticSearchResult]:
        """使用 Supabase RPC（pgvector）在資料庫端做相似度排序。"""
        try:
            # 調用在 DB 內定義的 RPC：semantic_tag_search
            # 期望 DB 端已存在：embedding_vec vector(1536)、ivfflat 索引、RPC 函數
            payload = {
                "query_embedding": query_embedding,
                "match_count": top_k * 3,  # 多取一點再做業務加權
                "min_similarity": max(min_similarity, 0.0),
            }

            # Supabase Python Client 的 RPC 調用
            resp = self.supabase.rpc("semantic_tag_search", payload).execute()
            rows = resp.data or []
            if rows:
                logger.info("Using pgvector RPC for semantic search results")

            # 應用簡單的權重重排序（類別 + 熱度）
            scored: List[tuple[float, SemanticSearchResult]] = []
            for row in rows:
                similarity = float(row.get("similarity", 0.0))
                name = row.get("name") or row.get("tag_name")
                post_count = int(row.get("post_count", 0))
                main_category = row.get("main_category")
                sub_category = row.get("sub_category")

                if not self._is_content_allowed(name or "", user_access_level):
                    continue

                # 類別/熱度微量加權
                score = similarity
                if main_category:
                    score += 0.03
                if sub_category:
                    score += 0.02
                score += min(post_count, 1_000_000) / 1_000_000 * 0.02

                result = SemanticSearchResult(
                    name=name or "",
                    post_count=post_count,
                    similarity=similarity,
                    main_category=main_category,
                    sub_category=sub_category,
                )
                scored.append((score, result))

            # 依加權分數排序，取前 top_k
            if not scored:
                return []
            scored.sort(key=lambda x: x[0], reverse=True)
            return [r for _, r in scored[:top_k]]

        except Exception as e:
            # 若 RPC 不存在或錯誤，返回空陣列以觸發本地退回方案
            logger.warning(f"⚠️ RPC semantic_tag_search not available or failed: {e}")
            return []
    
    async def _generate_query_embedding(self, query: str) -> List[float]:
        """生成查詢嵌入向量"""
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate query embedding: {e}")
            return []
    
    async def _search_similar_tags(
        self, 
        query_embedding: List[float], 
        top_k: int,
        min_similarity: float,
        user_access_level: str
    ) -> List[SemanticSearchResult]:
        """搜尋相似標籤"""
        try:
            # 獲取所有有嵌入向量的標籤（限制數量以提高性能）
            response = self.supabase.table('tags_final').select(
                'id, name, post_count, main_category, sub_category, embedding'
            ).not_.is_('embedding', 'null').limit(1000).execute()
            
            if not response.data:
                return []
            
            # 計算相似度
            similarities = []
            for tag in response.data:
                if tag['embedding']:
                    embedding_value = tag['embedding']
                    
                    # 處理嵌入向量格式（JSON 字符串或直接數組）
                    if isinstance(embedding_value, str):
                        try:
                            embedding_value = json.loads(embedding_value)
                        except Exception:
                            continue
                    
                    similarity = self._cosine_similarity(query_embedding, embedding_value)
                    
                    # 應用相似度閾值
                    if similarity >= min_similarity:
                        # 檢查內容分級
                        if self._is_content_allowed(tag['name'], user_access_level):
                            similarities.append(SemanticSearchResult(
                                name=tag['name'],
                                post_count=tag['post_count'],
                                similarity=similarity,
                                main_category=tag.get('main_category'),
                                sub_category=tag.get('sub_category')
                            ))
            
            # 按相似度排序並返回前 k 個
            similarities.sort(key=lambda x: x.similarity, reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Failed to search similar tags: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """計算餘弦相似度"""
        try:
            # 強制轉換為 float 類型以避免 unicode 數組問題
            vec1 = np.asarray(vec1, dtype=float)
            vec2 = np.asarray(vec2, dtype=float)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0
            
            return float(dot_product / (norm1 * norm2))
            
        except Exception as e:
            logger.error(f"❌ Cosine similarity calculation failed: {e}")
            return 0
    
    def _is_content_allowed(self, tag_name: str, user_access_level: str) -> bool:
        """檢查內容是否允許（基於使用者權限）"""
        # 簡單的內容分級檢查
        nsfw_keywords = ['nude', 'sex', 'explicit', 'adult']
        
        if user_access_level == "all-ages":
            return not any(keyword in tag_name.lower() for keyword in nsfw_keywords)
        
        return True  # r15 和 r18 允許所有內容
    
    async def _get_embedding_count(self) -> int:
        """獲取可用嵌入向量數量"""
        try:
            response = self.supabase.table('tags_final').select(
                'id', count='exact'
            ).not_.is_('embedding', 'null').execute()
            
            return response.count or 0
            
        except Exception as e:
            logger.error(f"❌ Failed to get embedding count: {e}")
            return 0

# 依賴注入函數
def get_semantic_search_service(
    db_wrapper: InspireDBWrapper = None,
    openai_client: AsyncOpenAI = None
) -> SemanticSearchService:
    """獲取語義搜尋服務實例"""
    if not db_wrapper:
        from services.inspire_db_wrapper import get_db_wrapper
        db_wrapper = get_db_wrapper()
    
    if not openai_client:
        from config import settings
        openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    return SemanticSearchService(db_wrapper, openai_client)
