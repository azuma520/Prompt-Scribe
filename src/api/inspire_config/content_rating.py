"""
內容分級系統
支援全年齡、付費用戶、封禁內容的多級管理
"""

from typing import Literal

ContentLevel = Literal["all-ages", "r15", "r18", "blocked"]

# ============================================
# 內容分級關鍵字
# ============================================

# 永久封禁（絕對不開放，P0 法律合規）
BLOCKED_KEYWORDS = [
    # 未成年人相關（嚴格禁止）
    "loli", "shota", "child", "kid", "kids", "toddler",
    "baby", "underage", "young_girl", "young_boy",
    "child_", "children", "preteen", "minor",
    
    # 暴力極端（可選，依平台政策）
    "guro", "ryona", "snuff"
]

# R18 內容（付費 + 年齡驗證可用）
R18_KEYWORDS = [
    # 裸露
    "nsfw", "nude", "naked", "topless", "bottomless",
    
    # 性相關
    "sex", "penis", "vagina", "pussy", "cock", "dick",
    "cum", "semen", "orgasm", "ejaculation",
    
    # 身體部位（明確性暗示）
    "nipples", "areola", "genitals", "anus",
    
    # 明確內容
    "porn", "hentai", "xxx", "explicit", "r-18", "r18",
    "penetration", "intercourse"
]

# R15 內容（年齡驗證可用，不需付費）
R15_KEYWORDS = [
    # 身體部位（非明確）
    "breasts", "large_breasts", "medium_breasts", "small_breasts",
    "ass", "butt", "thighs",
    
    # 服裝（性暗示）
    "lingerie", "bikini_bottom", "see-through",
    
    # 姿勢（性暗示）
    "spread_legs", "sexually_suggestive",
    
    # 部分裸露
    "partial_nudity", "nipple_slip"
]

# All-Ages（所有用戶可用）
SAFE_CONTENT = [
    # 其他所有不在上述列表中的標籤
    # 預設都是 all-ages
]


# ============================================
# 分級函數
# ============================================

def classify_content_level(tag_name: str) -> ContentLevel:
    """
    基於關鍵字分類內容等級
    
    Args:
        tag_name: 標籤名稱
    
    Returns:
        "blocked" | "r18" | "r15" | "all-ages"
    """
    
    tag_lower = tag_name.lower()
    
    # 優先級 1: 檢查封禁（最嚴格）
    if any(kw in tag_lower for kw in BLOCKED_KEYWORDS):
        return "blocked"
    
    # 優先級 2: 檢查 R18
    if any(kw in tag_lower for kw in R18_KEYWORDS):
        return "r18"
    
    # 優先級 3: 檢查 R15
    if any(kw in tag_lower for kw in R15_KEYWORDS):
        return "r15"
    
    # 預設：全年齡
    return "all-ages"


def filter_tags_by_user_access(
    tags: list[str],
    user_access_level: ContentLevel = "all-ages"
) -> tuple[list[str], list[str], dict]:
    """
    根據使用者權限過濾標籤
    
    Args:
        tags: 標籤列表
        user_access_level: 使用者權限
            - "all-ages": 免費用戶（預設）
            - "r15": 年齡驗證用戶
            - "r18": 付費 + 年齡驗證用戶
            - "blocked": 不應使用（系統保留）
    
    Returns:
        (allowed_tags, removed_tags, metadata)
    """
    
    # 定義權限等級
    ACCESS_HIERARCHY = {
        "all-ages": 0,
        "r15": 1,
        "r18": 2,
        "blocked": 999  # 永不允許
    }
    
    user_level = ACCESS_HIERARCHY.get(user_access_level, 0)
    
    allowed = []
    removed = []
    metadata = {
        "blocked_count": 0,
        "r18_filtered": 0,
        "r15_filtered": 0,
        "reasons": []
    }
    
    for tag in tags:
        tag_level_name = classify_content_level(tag)
        tag_level = ACCESS_HIERARCHY[tag_level_name]
        
        # 封禁內容永不允許
        if tag_level_name == "blocked":
            removed.append(tag)
            metadata["blocked_count"] += 1
            metadata["reasons"].append(f"'{tag}' 已封禁")
            continue
        
        # 檢查權限
        if tag_level <= user_level:
            allowed.append(tag)
        else:
            removed.append(tag)
            
            if tag_level_name == "r18":
                metadata["r18_filtered"] += 1
                metadata["reasons"].append(f"'{tag}' 需要付費會員")
            elif tag_level_name == "r15":
                metadata["r15_filtered"] += 1
                metadata["reasons"].append(f"'{tag}' 需要年齡驗證")
    
    return allowed, removed, metadata


# ============================================
# 使用範例
# ============================================

if __name__ == "__main__":
    # 測試分級
    test_tags = [
        "1girl",           # all-ages
        "swimsuit",        # all-ages（泳裝本身是安全的）
        "breasts",         # r15
        "nipples",         # r18
        "loli"             # blocked
    ]
    
    print("Tag Classification:")
    for tag in test_tags:
        level = classify_content_level(tag)
        print(f"  {tag:20} → {level}")
    
    print("\n" + "="*50)
    
    # 測試免費用戶過濾
    print("\nFree User (all-ages):")
    allowed, removed, meta = filter_tags_by_user_access(test_tags, "all-ages")
    print(f"  Allowed: {allowed}")
    print(f"  Removed: {removed}")
    print(f"  Reasons: {meta['reasons']}")
    
    # 測試付費用戶過濾
    print("\nPaid User (r18):")
    allowed, removed, meta = filter_tags_by_user_access(test_tags, "r18")
    print(f"  Allowed: {allowed}")
    print(f"  Removed: {removed}")
    print(f"  Reasons: {meta['reasons']}")

