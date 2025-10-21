"""
資料庫映射配置
將現有 tags_final 的 main_category 映射到 Inspire 類別系統
"""

# ============================================
# 分類映射（main_category → Inspire category）
# ============================================

CATEGORY_MAPPING = {
    # 角色相關
    "CHARACTER_RELATED": "CHARACTER",
    "CHARACTER": "CHARACTER",
    "PERSON": "CHARACTER",
    
    # 外觀相關（髮型、眼睛、身體特徵）
    "HAIR": "APPEARANCE",
    "EYES": "APPEARANCE",
    "BODY": "APPEARANCE",
    "FACE": "APPEARANCE",
    "APPEARANCE": "APPEARANCE",
    
    # 服裝相關
    "CLOTHING": "CLOTHING",
    "OUTFIT": "CLOTHING",
    "DRESS": "CLOTHING",
    
    # 場景相關
    "ENVIRONMENT": "SCENE",
    "LOCATION": "SCENE",
    "BACKGROUND": "SCENE",
    "SCENE": "SCENE",
    
    # 風格相關
    "STYLE": "STYLE",
    "ART": "STYLE",
    "TECHNICAL": "STYLE",
    "THEME_CONCEPT": "STYLE",
    
    # 效果相關
    "EFFECT": "EFFECT",
    "LIGHTING": "EFFECT",
    
    # 動作相關
    "ACTION_POSE": "ACTION",
    "POSE": "ACTION",
    "ACTION": "ACTION",
    
    # 情緒相關
    "EXPRESSION": "MOOD",
    "EMOTION": "MOOD",
    
    # 品質相關
    "QUALITY": "QUALITY",
    
    # 組合/元數據
    "COMPOSITION": "META",
    "META": "META",
    
    # NULL 或其他
    None: "META",
    "": "META"
}


def map_category(main_category: str | None) -> str:
    """
    映射分類到 Inspire 類別
    
    Args:
        main_category: tags_final 中的 main_category 值
    
    Returns:
        Inspire 類別（CHARACTER/APPEARANCE/SCENE/...）
    """
    return CATEGORY_MAPPING.get(main_category, "META")


def categorize_tag_by_rules(tag_name: str, main_category: str | None = None) -> str:
    """
    基於規則推斷標籤類別
    
    優先級：
    1. main_category 映射
    2. tag name 規則匹配
    3. 預設 META
    
    Args:
        tag_name: 標籤名稱
        main_category: 資料庫中的 main_category（可選）
    
    Returns:
        Inspire 類別
    """
    
    # 優先使用 main_category
    if main_category:
        mapped = map_category(main_category)
        if mapped != "META":
            return mapped
    
    # 規則匹配（基於 tag name）
    tag_lower = tag_name.lower()
    
    # CHARACTER 規則
    if tag_name in ["1girl", "1boy", "solo", "2girls", "3girls", "multiple_girls", "multiple_boys"]:
        return "CHARACTER"
    
    if tag_lower.startswith("no_humans") or tag_lower.startswith("solo"):
        return "CHARACTER"
    
    # APPEARANCE 規則（髮型、眼睛）
    if tag_lower.endswith("_hair") or tag_lower.endswith("_eyes"):
        return "APPEARANCE"
    
    if any(kw in tag_lower for kw in ["hair", "eyes", "skin", "face", "lips", "nose"]):
        return "APPEARANCE"
    
    # CLOTHING 規則
    if tag_lower.endswith("_dress") or tag_lower.endswith("_uniform") or tag_lower.endswith("_suit"):
        return "CLOTHING"
    
    if any(kw in tag_lower for kw in ["dress", "shirt", "pants", "skirt", "uniform", "jacket", "coat"]):
        return "CLOTHING"
    
    # SCENE 規則
    if tag_name in ["outdoors", "indoors", "forest", "beach", "city", "mountain", "sky", "ocean", "room"]:
        return "SCENE"
    
    if any(kw in tag_lower for kw in ["background", "scenery", "landscape"]):
        return "SCENE"
    
    # STYLE 規則
    if tag_lower.endswith("_style") or tag_lower.endswith("_art"):
        return "STYLE"
    
    if tag_name in ["realistic", "anime", "photorealistic", "abstract", "artistic"]:
        return "STYLE"
    
    # ACTION 規則（動詞 ing 形式）
    if tag_lower.endswith("ing") and tag_name not in ["clothing", "ring", "earring"]:
        return "ACTION"
    
    if tag_name in ["sitting", "standing", "walking", "running", "flying", "swimming", "dancing"]:
        return "ACTION"
    
    # MOOD 規則
    if tag_name in ["smile", "sad", "happy", "angry", "peaceful", "dreamy", "mysterious", "cheerful", "melancholic"]:
        return "MOOD"
    
    # QUALITY 規則
    if tag_name in ["masterpiece", "best_quality", "high_quality", "highly_detailed", "absurdres", "highres"]:
        return "QUALITY"
    
    # EFFECT 規則
    if any(kw in tag_lower for kw in ["lighting", "glow", "particle", "shadow", "light", "effect"]):
        return "EFFECT"
    
    # 預設
    return "META"


# ============================================
# 衝突規則
# ============================================

CONFLICT_PAIRS = [
    # 髮長衝突
    ("long_hair", "short_hair"),
    ("long_hair", "bald"),
    ("long_hair", "no_hair"),
    ("short_hair", "very_long_hair"),
    ("bald", "very_long_hair"),
    
    # 角色數量衝突
    ("solo", "multiple_girls"),
    ("solo", "2girls"),
    ("solo", "3girls"),
    ("solo", "multiple_boys"),
    ("1girl", "no_humans"),
    ("1boy", "no_humans"),
    ("1girl", "1boy"),  # 如果想要單一角色
    
    # 時間衝突
    ("day", "night"),
    ("sunrise", "sunset"),
    ("morning", "evening"),
    
    # 天氣衝突
    ("sunny", "cloudy"),
    ("sunny", "rain"),
    ("clear_sky", "cloudy"),
    
    # 構圖衝突
    ("close-up", "wide_shot"),
    ("close-up", "full_body"),
    ("portrait", "full_body"),
    ("upper_body", "full_body"),
    ("upper_body", "lower_body"),
    
    # 顏色衝突（眼睛）
    ("blue_eyes", "red_eyes"),
    ("blue_eyes", "green_eyes"),
    ("red_eyes", "green_eyes"),
    ("brown_eyes", "blue_eyes"),
    
    # 顏色衝突（頭髮）
    ("blonde_hair", "black_hair"),
    ("blonde_hair", "brown_hair"),
    ("black_hair", "white_hair"),
    
    # 室內/室外
    ("indoors", "outdoors"),
]


def detect_conflicts(tags: list[str]) -> list[tuple[str, str]]:
    """
    檢測標籤衝突
    
    Returns:
        [(tag_a, tag_b), ...]
    """
    conflicts = []
    tags_set = set(t.lower() for t in tags)
    
    for tag_a, tag_b in CONFLICT_PAIRS:
        if tag_a in tags_set and tag_b in tags_set:
            conflicts.append((tag_a, tag_b))
    
    return conflicts


# ============================================
# 別名映射（常見錯誤）
# ============================================

TAG_ALIASES = {
    # 拼寫錯誤
    "longhair": "long_hair",
    "shorthair": "short_hair",
    "blueeyes": "blue_eyes",
    "redeyes": "red_eyes",
    
    # 複數形式
    "1girls": "1girl",
    "2girl": "2girls",
    "3girl": "3girls",
    
    # 常見替代
    "anime": "anime_style",  # 雖然 anime_style 不在資料庫，但語義相似
    "photo": "photorealistic",
    
    # 簡寫
    "bg": "background",
    "1g": "1girl",
    "mc": "main_character",
}


def resolve_alias(tag: str) -> str:
    """
    解析別名為標準標籤
    
    Args:
        tag: 可能是別名的標籤
    
    Returns:
        標準標籤名稱
    """
    return TAG_ALIASES.get(tag.lower(), tag)


# ============================================
# 使用範例
# ============================================

if __name__ == "__main__":
    from content_rating import classify_content_level, filter_tags_by_user_access
    
    # 測試分類映射
    print("Category Mapping:")
    print(f"  CHARACTER_RELATED → {map_category('CHARACTER_RELATED')}")
    print(f"  ENVIRONMENT → {map_category('ENVIRONMENT')}")
    print(f"  ACTION_POSE → {map_category('ACTION_POSE')}")
    
    # 測試規則分類
    print("\nRule-based Categorization:")
    test_tags = ["1girl", "long_hair", "kimono", "outdoors", "smile"]
    for tag in test_tags:
        cat = categorize_tag_by_rules(tag)
        print(f"  {tag:15} → {cat}")
    
    # 測試衝突檢測
    print("\nConflict Detection:")
    conflict_tags = ["long_hair", "short_hair", "1girl"]
    conflicts = detect_conflicts(conflict_tags)
    print(f"  Tags: {conflict_tags}")
    print(f"  Conflicts: {conflicts}")
    
    # 測試內容過濾
    print("\nContent Filtering:")
    mixed_tags = ["1girl", "smile", "breasts", "nipples", "loli"]
    
    print("\n  Free User:")
    allowed, removed, meta = filter_tags_by_user_access(mixed_tags, "all-ages")
    print(f"    Allowed: {allowed}")
    print(f"    Removed: {removed}")
    print(f"    Reasons: {meta['reasons']}")
    
    print("\n  Paid User (R18):")
    allowed, removed, meta = filter_tags_by_user_access(mixed_tags, "r18")
    print(f"    Allowed: {allowed}")
    print(f"    Removed: {removed}")
    print(f"    Blocked: {meta['blocked_count']}")

