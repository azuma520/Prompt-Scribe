"""
內容安全過濾器（P0）

實現三層安全檢查：
1. 封禁詞檢測（本地列表）
2. OpenAI Moderation API 整合
3. 安全替代方案

Version: 1.0.0
Date: 2025-01-27
"""

import logging
from typing import List, Dict, Tuple, Optional, Set
from openai import AsyncOpenAI

from ..inspire_config.content_rating import (
    BLOCKED_KEYWORDS,
    R18_KEYWORDS,
    R15_KEYWORDS,
    classify_content_level,
    filter_tags_by_user_access,
    ContentLevel,
)

logger = logging.getLogger(__name__)


class ContentSafetyFilter:
    """
    內容安全過濾器（P0）
    
    三層防護：
    1. 封禁詞檢測（本地）：絕對禁止的關鍵字
    2. Moderation API（遠端）：檢查使用者輸入的整體內容
    3. 安全替代方案：被封禁時提供替代方向
    """

    def __init__(
        self,
        openai_client: Optional[AsyncOpenAI] = None,
        enable_moderation: bool = True,
    ):
        """
        初始化安全過濾器
        
        Args:
            openai_client: OpenAI 客戶端（用於 Moderation API）
            enable_moderation: 是否啟用 Moderation API（預設啟用）
        """
        self.openai_client = openai_client
        self.enable_moderation = enable_moderation

        # 封禁清單（從 content_rating 導入，擴充以確保完整性）
        self.blocked_keywords: Set[str] = set(BLOCKED_KEYWORDS)

        # 記錄統計
        self.stats = {
            "blocks_prevented": 0,
            "moderation_checks": 0,
            "alternatives_suggested": 0,
        }

        logger.info("✅ ContentSafetyFilter initialized")

    def is_blocked(self, tag: str) -> bool:
        """
        檢查標籤是否被封禁（本地檢測）
        
        Args:
            tag: 標籤名稱
            
        Returns:
            True 如果被封禁，False 否則
        """
        tag_lower = tag.lower()
        
        # 檢查封禁關鍵字
        for keyword in self.blocked_keywords:
            if keyword in tag_lower:
                return True
        
        # 使用內容分級系統檢查
        content_level = classify_content_level(tag)
        return content_level == "blocked"

    async def filter_tags(
        self,
        tags: List[str],
        user_access_level: ContentLevel = "all-ages",
    ) -> Tuple[List[str], List[str], Dict]:
        """
        過濾標籤列表（應用內容安全規則）
        
        Args:
            tags: 要過濾的標籤列表
            user_access_level: 使用者權限等級
            
        Returns:
            (safe_tags, removed_tags, metadata)
        """
        safe_tags = []
        removed_tags = []
        metadata = {
            "blocked_count": 0,
            "nsfw_count": 0,
            "r15_filtered": 0,
            "reasons": [],
        }

        # 使用現有的分級過濾邏輯
        allowed, removed, filter_meta = filter_tags_by_user_access(
            tags, user_access_level
        )

        # 額外檢查：確保封禁詞被完全移除
        for tag in allowed:
            if self.is_blocked(tag):
                # 如果通過了分級系統但仍被封禁，額外移除
                allowed.remove(tag)
                removed.append(tag)
                metadata["blocked_count"] += 1
                metadata["reasons"].append(f"'{tag}' 在封禁清單中（額外檢查）")

        # 合併結果
        safe_tags = allowed
        removed_tags = removed

        # 合併元數據
        metadata.update(filter_meta)

        # 更新統計
        if metadata["blocked_count"] > 0:
            self.stats["blocks_prevented"] += metadata["blocked_count"]

        logger.debug(
            f"🔒 Filtered {len(removed_tags)} tags, {len(safe_tags)} safe tags remaining"
        )

        return safe_tags, removed_tags, metadata

    async def check_user_input(self, text: str) -> Tuple[bool, str]:
        """
        檢查使用者輸入（使用 OpenAI Moderation API）
        
        Args:
            text: 使用者輸入文字
            
        Returns:
            (is_safe, reason)
        """
        # 如果未啟用 Moderation 或沒有客戶端，跳過檢查
        if not self.enable_moderation or not self.openai_client:
            logger.debug("⚠️ Moderation API not enabled or client unavailable")
            return True, ""

        try:
            self.stats["moderation_checks"] += 1

            # 呼叫 OpenAI Moderation API
            response = await self.openai_client.moderations.create(input=text)
            result = response.results[0]

            if result.flagged:
                # 找出被標記的類別
                flagged_categories = []
                for category, flagged in result.categories.model_dump().items():
                    if flagged:
                        # 將 snake_case 轉換為可讀的文字
                        category_readable = category.replace("_", " ").title()
                        flagged_categories.append(category_readable)

                reason = f"輸入包含不適當內容：{', '.join(flagged_categories)}"
                logger.warning(f"🚫 Moderation API flagged: {reason}")

                return False, reason

            return True, ""

        except Exception as e:
            logger.error(f"❌ Moderation API 錯誤：{e}")
            # 失敗時保守處理：允許但記錄警告
            # 這是為了避免 Moderation API 故障影響使用者體驗
            return True, ""

    async def suggest_safe_alternative(
        self, blocked_tags: List[str]
    ) -> List[str]:
        """
        為被封禁的標籤建議安全替代方案
        
        根據設計文檔，提供三個固定方向：
        1. 光影意象
        2. 自然元素
        3. 抽象幾何
        
        Args:
            blocked_tags: 被封禁的標籤列表
            
        Returns:
            安全替代標籤列表
        """
        if not blocked_tags:
            return []

        alternatives = []
        self.stats["alternatives_suggested"] += len(blocked_tags)

        # 為每個封禁標籤提供替代
        for tag in blocked_tags:
            tag_lower = tag.lower()

            # 根據封禁類型提供替代
            if any(kw in tag_lower for kw in ["loli", "shota", "child", "kid"]):
                # 未成年人相關 → 光影意象、自然元素
                alternatives.extend(
                    [
                        "1girl",
                        "solo",
                        "soft_lighting",
                        "atmospheric",
                        "natural_elements",
                    ]
                )
            elif any(kw in tag_lower for kw in R18_KEYWORDS):
                # R18 內容 → 藝術性、抽象
                alternatives.extend(
                    ["artistic", "aesthetic", "elegant", "abstract", "minimalist"]
                )
            else:
                # 其他封禁 → 通用安全替代
                alternatives.extend(
                    [
                        "masterpiece",
                        "beautiful",
                        "detailed",
                        "high_quality",
                        "atmospheric",
                    ]
                )

        # 去重並限制數量
        unique_alternatives = list(set(alternatives))[:10]

        logger.info(
            f"🔄 Suggested {len(unique_alternatives)} safe alternatives for {len(blocked_tags)} blocked tags"
        )

        return unique_alternatives

    def get_stats(self) -> Dict:
        """獲取統計資訊"""
        return self.stats.copy()

    def reset_stats(self):
        """重置統計資訊"""
        self.stats = {
            "blocks_prevented": 0,
            "moderation_checks": 0,
            "alternatives_suggested": 0,
        }


# ============================================
# 依賴注入（FastAPI）
# ============================================


def get_safety_filter() -> ContentSafetyFilter:
    """
    獲取 ContentSafetyFilter 實例（依賴注入）
    
    Args:
        openai_client: OpenAI 客戶端（可選）
        
    Returns:
        ContentSafetyFilter 實例
    """
    from ..config import settings

    openai_client: Optional[AsyncOpenAI] = None
    # 嘗試創建一個 OpenAI 客戶端（若有金鑰）
    if settings.openai_api_key:
        try:
            openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        except Exception as e:
            logger.warning(f"⚠️ Failed to create OpenAI client for moderation: {e}")
            openai_client = None

    return ContentSafetyFilter(
        openai_client=openai_client,
        enable_moderation=settings.openai_api_key is not None,
    )

