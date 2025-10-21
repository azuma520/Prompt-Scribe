# 🎯 Inspire Agent 資料庫整合策略

**基於實際資料庫分析的最終規劃**

**日期**: 2025-10-21  
**版本**: Final v1.0

---

## 📊 實際發現總結

### 現有資料庫狀態（tags_final）

✅ **可直接使用的資料：**
```
- name: 標籤名稱（140,782 個）
- post_count: 使用次數（完整且可靠）
- main_category: 主分類（96.56% 已分類）
- sub_category: 子分類（部分填充）
- confidence: 分類信心度
```

✅ **資料品質：**
```
- 78,475 tags >= 1,000 posts (55.74%) ← 高品質！
- 15,620 tags >= 10,000 posts (11.10%) ← 超熱門
- 4,841 tags 未分類 (3.44%) ← 可接受
```

⚠️ **需要處理的問題：**
```
- NSFW 內容存在（TOP 100 中有 5 個）
- 封禁標籤存在（loli: 2.3M, child: 881K）
- 沒有 aliases, conflicts, nsfw_level 欄位
- tag_embeddings 是空的（語義搜尋不可用）
- 分類系統需要映射到 Inspire 類別
```

---

## 🎯 最終整合策略：**策略 A（最小改動）**

### 為什麼選擇策略 A？

**原因：**
1. ✅ **零風險** - 不修改生產表
2. ✅ **快速** - 立即可用現有資料
3. ✅ **靈活** - 程式碼層可隨時調整
4. ✅ **可測試** - 不影響現有系統

### 核心原則

```
充分利用現有欄位（name, post_count, main_category）
+
應用層邏輯（映射、規則、過濾）
+
最小新表（只建 inspire_sessions）
=
Week 1 可上線的 MVP
```

---

## 🗄️ 資料層設計

### Layer 1: 現有 tags_final（不改動）

**直接使用：**
```sql
SELECT 
    name,           -- 標籤名稱
    post_count,     -- 流行度
    main_category   -- 原始分類
FROM tags_final
WHERE post_count >= 1000  -- 只用高品質標籤
ORDER BY post_count DESC;
```

**不添加任何欄位！** ✅

---

### Layer 2: 應用層映射（程式碼）

**新檔案：** `src/api/config/database_mappings.py`

```python
"""
資料庫映射配置
將現有 main_category 映射到 Inspire 類別系統
"""

# ============================================
# 分類映射（main_category → Inspire category）
# ============================================

CATEGORY_MAPPING = {
    # 角色相關
    "CHARACTER_RELATED": "CHARACTER",
    "CHARACTER": "CHARACTER",
    
    # 外觀相關
    "HAIR": "APPEARANCE",
    "EYES": "APPEARANCE",
    "BODY": "APPEARANCE",
    "FACE": "APPEARANCE",
    
    # 服裝相關
    "CLOTHING": "CLOTHING",
    "OUTFIT": "CLOTHING",
    
    # 場景相關
    "ENVIRONMENT": "SCENE",
    "LOCATION": "SCENE",
    "BACKGROUND": "SCENE",
    
    # 風格相關
    "STYLE": "STYLE",
    "ART": "STYLE",
    "TECHNICAL": "STYLE",
    "THEME_CONCEPT": "STYLE",
    
    # 動作相關
    "ACTION_POSE": "ACTION",
    "POSE": "ACTION",
    
    # 組合相關
    "COMPOSITION": "META",
    
    # 預設
    None: "META"
}

def map_category(main_category: str) -> str:
    """映射分類"""
    return CATEGORY_MAPPING.get(main_category, "META")


# ============================================
# NSFW 檢測（關鍵字規則）
# ============================================

NSFW_KEYWORDS = [
    "nsfw", "nude", "naked", "sex", "penis", "vagina",
    "breasts", "large_breasts", "medium_breasts", "small_breasts",
    "nipples", "ass", "pussy", "porn", "hentai", "cum",
    "erect", "explicit", "r-18", "r18"
]

BLOCKED_KEYWORDS = [
    # 未成年人（P0 絕對封禁）
    "loli", "shota", "child", "kid", "kids", "toddler",
    "baby", "underage", "young_girl", "young_boy",
    "child_", "children"
]

def classify_nsfw_level(tag_name: str) -> str:
    """
    基於關鍵字檢測 NSFW 等級
    
    Returns:
        "blocked" | "r18" | "all-ages"
    """
    tag_lower = tag_name.lower()
    
    # 檢查封禁
    if any(kw in tag_lower for kw in BLOCKED_KEYWORDS):
        return "blocked"
    
    # 檢查 NSFW
    if any(kw in tag_lower for kw in NSFW_KEYWORDS):
        return "r18"
    
    return "all-ages"


# ============================================
# 衝突檢測（規則）
# ============================================

CONFLICT_PAIRS = [
    # 髮長
    ("long_hair", "short_hair"),
    ("long_hair", "bald"),
    ("short_hair", "very_long_hair"),
    
    # 角色數量
    ("solo", "multiple_girls"),
    ("solo", "2girls"),
    ("1girl", "no_humans"),
    ("1boy", "no_humans"),
    
    # 時間
    ("day", "night"),
    ("sunny", "cloudy"),
    ("sunrise", "sunset"),
    
    # 構圖
    ("close-up", "wide_shot"),
    ("portrait", "full_body"),
]

def detect_conflicts(tags: list[str]) -> list[tuple]:
    """
    檢測衝突標籤對
    
    Returns:
        [(tag_a, tag_b), ...]
    """
    conflicts = []
    tags_set = set(tags)
    
    for tag_a, tag_b in CONFLICT_PAIRS:
        if tag_a in tags_set and tag_b in tags_set:
            conflicts.append((tag_a, tag_b))
    
    return conflicts


# ============================================
# 別名映射（常見錯誤）
# ============================================

TAG_ALIASES_SIMPLE = {
    "longhair": "long_hair",
    "shorthair": "short_hair",
    "blueeyes": "blue_eyes",
    "1girls": "1girl",
    "2girl": "2girls",
    "anime": "anime_style",  # anime_style 不存在，用相似的
}

def resolve_alias(tag: str) -> str:
    """解析別名"""
    return TAG_ALIASES_SIMPLE.get(tag.lower(), tag)
```

---

### Layer 3: 新表 - inspire_sessions（最小必須）

**唯一需要創建的新表：**

```sql
CREATE TABLE inspire_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    current_phase TEXT DEFAULT 'understanding',
    
    -- 業務資料（JSONB 靈活存儲）
    extracted_intent JSONB,
    generated_directions JSONB,
    final_output JSONB,
    
    -- 追蹤資料
    total_cost DECIMAL(10, 6) DEFAULT 0.0,
    tool_call_count JSONB DEFAULT '{}'::jsonb,
    quality_score INTEGER,
    
    -- 時間戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**這是唯一的 Schema 變更！** ✅

---

## 🛠️ 實作方案

### 1. 資料庫服務（包裝現有查詢）

**新檔案：** `src/api/services/inspire_db_wrapper.py`

```python
"""
Inspire Agent 資料庫包裝
基於現有 SupabaseService，添加 Inspire 專用方法
"""

from services.supabase_client import get_supabase_service
from config.database_mappings import (
    map_category,
    classify_nsfw_level,
    detect_conflicts,
    resolve_alias
)

class InspireDbWrapper:
    """
    Inspire 資料庫包裝
    不修改資料庫，只在應用層處理
    """
    
    def __init__(self):
        self.supabase = get_supabase_service()
    
    def get_tags_with_inspire_metadata(self, tag_names: list[str]) -> list[dict]:
        """
        獲取標籤並添加 Inspire 元數據
        
        Returns:
            [{
                "tag": str,
                "category": str,          # 映射後的 Inspire 類別
                "popularity": int,
                "nsfw_level": str,        # 應用層檢測
                "usage_hint": str
            }]
        """
        import asyncio
        
        # 查詢現有資料
        raw_data = asyncio.run(
            self.supabase.get_tags_by_names(tag_names)
        )
        
        # 添加 Inspire 元數據（應用層）
        result = []
        for tag_name in tag_names:
            tag = raw_data.get(tag_name)
            
            if not tag:
                continue
            
            result.append({
                "tag": tag["name"],
                "category": map_category(tag.get("main_category")),  # 映射
                "popularity": tag["post_count"],
                "nsfw_level": classify_nsfw_level(tag["name"]),      # 檢測
                "usage_hint": self._generate_usage_hint(tag)
            })
        
        return result
    
    def search_safe_tags(
        self,
        keywords: list[str],
        min_popularity: int = 1000,
        limit: int = 20
    ) -> list[dict]:
        """
        搜尋安全標籤（自動過濾 NSFW）
        
        Returns:
            嚴格格式的標籤列表
        """
        import asyncio
        
        # 使用現有搜尋
        raw_results = asyncio.run(
            self.supabase.search_tags_by_keywords(
                keywords=keywords,
                limit=limit * 2,  # 多查一些，過濾後可能不夠
                min_popularity=min_popularity
            )
        )
        
        # 過濾 NSFW 和 Blocked
        safe_results = []
        for tag in raw_results:
            nsfw_level = classify_nsfw_level(tag["name"])
            
            if nsfw_level == "blocked":
                continue  # 跳過封禁標籤
            
            if nsfw_level == "r18":
                continue  # MVP 階段全部過濾
            
            safe_results.append({
                "tag": tag["name"],
                "category": map_category(tag.get("main_category")),
                "popularity": tag["post_count"],
                "usage_hint": ""
            })
            
            if len(safe_results) >= limit:
                break
        
        return safe_results
    
    def validate_tags(self, tags: list[str]) -> dict:
        """
        驗證標籤（基於現有資料 + 應用層規則）
        
        Returns:
            {
                "valid": [str],
                "invalid": [str],
                "blocked": [str],
                "nsfw": [str]
            }
        """
        import asyncio
        
        # 解析別名
        resolved_tags = [resolve_alias(t) for t in tags]
        
        # 查詢資料庫
        tag_data = asyncio.run(
            self.supabase.get_tags_by_names(resolved_tags)
        )
        
        valid = []
        invalid = []
        blocked = []
        nsfw = []
        
        for tag in resolved_tags:
            if tag not in tag_data or tag_data[tag] is None:
                invalid.append(tag)
                continue
            
            nsfw_level = classify_nsfw_level(tag)
            
            if nsfw_level == "blocked":
                blocked.append(tag)
            elif nsfw_level == "r18":
                nsfw.append(tag)
            else:
                valid.append(tag)
        
        return {
            "valid": valid,
            "invalid": invalid,
            "blocked": blocked,
            "nsfw": nsfw
        }
    
    def check_conflicts_rule_based(self, tags: list[str]) -> list[tuple]:
        """基於規則檢測衝突"""
        return detect_conflicts(tags)
    
    def _generate_usage_hint(self, tag: dict) -> str:
        """生成使用提示"""
        popularity = tag.get("post_count", 0)
        
        if popularity >= 10_000_000:
            return "超熱門標籤"
        elif popularity >= 1_000_000:
            return "常用標籤"
        elif popularity >= 100_000:
            return "流行標籤"
        else:
            return "一般標籤"
```

---

### 2. 最小 SQL Migration

**只需要創建 inspire_sessions 表：**

```sql
-- scripts/09_inspire_minimal_migration.sql

-- 唯一的新表：Session 元數據
CREATE TABLE IF NOT EXISTS inspire_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    current_phase TEXT DEFAULT 'understanding',
    
    -- 業務資料（JSONB 靈活）
    extracted_intent JSONB,
    generated_directions JSONB,
    final_output JSONB,
    
    -- 追蹤
    total_cost DECIMAL(10, 6) DEFAULT 0.0,
    tool_call_count JSONB DEFAULT '{}'::jsonb,
    quality_score INTEGER,
    
    -- 時間
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 約束
    CHECK (total_cost >= 0),
    CHECK (quality_score IS NULL OR (quality_score BETWEEN 0 AND 100))
);

CREATE INDEX idx_sessions_user ON inspire_sessions(user_id, created_at DESC);
CREATE INDEX idx_sessions_phase ON inspire_sessions(current_phase);

-- 完成！沒有其他 Schema 變更
```

**這是唯一的 SQL 執行！** ✅

---

## 📋 分類映射規劃

### 現有分類（需要完整查詢）

**已知分類：**
```
CHARACTER_RELATED  → Inspire: CHARACTER
ENVIRONMENT        → Inspire: SCENE
ACTION_POSE        → Inspire: ACTION
THEME_CONCEPT      → Inspire: STYLE
TECHNICAL          → Inspire: STYLE
COMPOSITION        → Inspire: META
```

**需要建立完整映射表**（查詢所有 main_category 值後補充）

---

### Inspire 類別系統

**9 個類別：**
```
1. CHARACTER    - 角色（1girl, solo, ...）
2. APPEARANCE   - 外觀（long_hair, blue_eyes, ...）
3. CLOTHING     - 服裝（dress, uniform, ...）
4. SCENE        - 場景（outdoors, forest, ...）
5. STYLE        - 風格（anime, realistic, ...）
6. EFFECT       - 效果（glow, particles, ...）
7. ACTION       - 動作（sitting, standing, ...）
8. MOOD         - 情緒（smile, sad, peaceful, ...）
9. QUALITY      - 品質（masterpiece, highres, ...）
```

**映射邏輯：**
```python
def map_to_inspire_category(tag: dict) -> str:
    """
    映射到 Inspire 類別
    
    優先級：
    1. main_category 映射
    2. tag name 規則（如 *_hair → APPEARANCE）
    3. 預設 META
    """
    
    # 優先使用 main_category
    if tag.get("main_category"):
        inspire_cat = CATEGORY_MAPPING.get(tag["main_category"])
        if inspire_cat:
            return inspire_cat
    
    # 規則匹配
    tag_name = tag["name"]
    
    if tag_name in ["1girl", "1boy", "solo", "2girls", "multiple_girls"]:
        return "CHARACTER"
    
    if tag_name.endswith("_hair") or tag_name.endswith("_eyes"):
        return "APPEARANCE"
    
    if tag_name.endswith("_dress") or tag_name.endswith("_uniform"):
        return "CLOTHING"
    
    if tag_name in ["outdoors", "indoors", "forest", "beach", "city", "sky"]:
        return "SCENE"
    
    if tag_name.endswith("_style") or tag_name in ["realistic", "anime", "photorealistic"]:
        return "STYLE"
    
    if tag_name.endswith("ing") or tag_name in ["sitting", "standing", "walking"]:
        return "ACTION"
    
    if tag_name in ["smile", "sad", "happy", "angry", "peaceful", "dreamy"]:
        return "MOOD"
    
    if tag_name in ["masterpiece", "best_quality", "highres", "absurdres"]:
        return "QUALITY"
    
    return "META"
```

---

## 🔒 NSFW 處理方案

### 基於實際發現

**TOP 100 中的 NSFW 標籤：**
```
- breasts (55M)
- large_breasts (25M)
- medium_breasts (14M)
- nipples (13M)
- ass (9M)
```

**封禁標籤（存在於資料庫）：**
```
- loli (2.3M posts) ← P0 必須封禁
- child (881K posts) ← P0 必須封禁
- shota (339K posts) ← P0 必須封禁
```

### 過濾策略

**在所有工具中應用：**

```python
@function_tool
def search_examples(...) -> dict:
    """搜尋標籤（自動過濾 NSFW）"""
    
    # 搜尋
    results = db.search_safe_tags(keywords, ...)
    
    # 自動過濾已在 search_safe_tags 中完成
    # 返回的都是 all-ages 標籤
    
    return {"examples": results}


@function_tool
def validate_quality(tags: list[str], ...) -> dict:
    """驗證品質（包含 NSFW 檢查）"""
    
    validation = db.validate_tags(tags)
    
    # 移除 blocked 和 nsfw
    safe_tags = validation["valid"]
    removed = validation["blocked"] + validation["nsfw"]
    
    if removed:
        logger.warning(f"Removed {len(removed)} unsafe tags")
    
    # 繼續驗證 safe_tags...
    
    return {
        "is_valid": ...,
        "removed_tags": removed,  # 告知使用者
        "quick_fixes": {
            "remove": removed,
            ...
        }
    }
```

---

## 📊 資料品質評估

### 可直接使用（高品質）

```
✅ 78,475 tags >= 1,000 posts (55%)
   → 足夠 MVP 的「熱門池」策略

✅ 流行度資料完整
   → 可靠排序和過濾

✅ 分類覆蓋 96.56%
   → 映射後可用
```

### 需要補充（應用層）

```
⚠️ 別名：手動維護小清單（10-20 個常見錯誤）
⚠️ 衝突：規則檢測（10-20 對明顯衝突）
⚠️ NSFW：關鍵字檢測（30-50 個關鍵詞）
```

### 暫時不可用（Week 2）

```
❌ 語義搜尋（embeddings 是空的）
   → Week 1 用關鍵字搜尋
   → Week 2-3 離線生成 embeddings
```

---

## 🎯 整合時程（修正版）

### Week 1 MVP（基於策略 A）

**Day 1（6h）：資料層準備**
```bash
# 1. 執行最小 migration
psql ... -f scripts/09_inspire_minimal_migration.sql

# 2. 創建映射配置
src/api/config/database_mappings.py

# 3. 創建資料庫包裝
src/api/services/inspire_db_wrapper.py

# 4. 測試查詢和過濾
python test_inspire_db_wrapper.py
```

**Day 2-7：** 按原計劃（工具實作）

**關鍵差異：**
- ✅ 不執行複雜的 ALTER TABLE
- ✅ 不建立 tag_cooccur, popular_tags 等（先不需要）
- ✅ 全部用應用層邏輯

---

## 💡 關鍵決策

### 決策 1: 不修改 tags_final ✅

**原因：**
1. 現有資料已足夠（name, post_count）
2. 降低風險（不動生產表）
3. 快速迭代（程式碼層調整快）

---

### 決策 2: NSFW 過濾在應用層 ✅

**原因：**
1. 不需要資料庫欄位
2. 關鍵字規則夠用（TOP 100 只有 5 個 NSFW）
3. 可快速調整（增減關鍵字）

---

### 決策 3: 語義搜尋延後 ✅

**原因：**
1. embeddings 是空的（需要離線生成）
2. Week 1 用關鍵字搜尋夠用
3. 55% 標籤 >= 1K posts（關鍵字搜尋已很準確）

---

### 決策 4: 分類映射在程式碼 ✅

**原因：**
1. 不確定所有 main_category 值
2. 映射邏輯可能需要調整
3. 程式碼比資料庫更靈活

---

## 📝 待辦清單（優先級）

### P0（今晚/明天，2-3h）

- [ ] 創建 `config/database_mappings.py`（分類映射、NSFW 規則）
- [ ] 創建 `services/inspire_db_wrapper.py`（資料庫包裝）
- [ ] 創建 `scripts/09_inspire_minimal_migration.sql`（只建 inspire_sessions）
- [ ] 執行 migration
- [ ] 測試查詢和過濾

### P1（Day 2-3，8-10h）

- [ ] 實作 5 個工具（使用 InspireDbWrapper）
- [ ] 測試工具（單元測試）

### P2（Week 2-3）

- [ ] 離線生成 tag_embeddings
- [ ] 實作語義搜尋
- [ ] 統計 tag_cooccur（基於現有 posts）

---

## 🎯 最終方案：最小可行整合

### 資料層

```
現有 tags_final（不動）
    ↓ 查詢
應用層映射（程式碼）
    ↓ 過濾
安全標籤列表
    ↓ 使用
Inspire Agent 工具
```

### Schema 變更

```
只創建 1 個表：inspire_sessions
零風險 ✅
可回退 ✅
```

### 實作時間

```
原計劃 Day 1: 8h（複雜 migration）
新計劃 Day 1: 3h（最小 migration + 映射）
節省 5 小時 ✅
```

---

**要我現在創建這些檔案嗎？（映射、包裝、migration）** 🚀

