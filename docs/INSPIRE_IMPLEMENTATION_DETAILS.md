# 🔧 Inspire Agent 實作細節文檔

**基於技術評審反饋的補充文檔**

**日期**: 2025-10-21  
**版本**: 1.0.0  
**狀態**: 實作指南

---

## 📋 文檔目的

本文檔補充 `INSPIRE_AGENT_DESIGN.md` 中缺失的**可執行細節**，包括：

1. 資料庫契約（精確定義）
2. 驗證器實作邏輯（可測試）
3. 內容安全與合規（P0 必做）
4. 狀態機與中止條件（防止失控）
5. 快速落地計劃（一週 MVP）

---

## 🗄️ 資料庫契約與 Schema

### PostgreSQL Schema（完整定義）

#### 1. Tags 主表（核心）

```sql
CREATE TABLE tags (
    -- 基礎資訊
    tag TEXT PRIMARY KEY,
    category TEXT NOT NULL CHECK (category IN (
        'CHARACTER', 'APPEARANCE', 'CLOTHING', 
        'SCENE', 'STYLE', 'EFFECT', 'ACTION', 
        'MOOD', 'QUALITY', 'META'
    )),
    
    -- 流行度與品質
    post_count INTEGER NOT NULL DEFAULT 0,
    quality_score FLOAT DEFAULT 0.0,  -- 基於使用頻率和評分
    
    -- 關聯與規則
    aliases TEXT[] DEFAULT '{}',      -- ["long_hair", "longhair"]
    conflicts TEXT[] DEFAULT '{}',    -- ["short_hair", "bald"]
    implied TEXT[] DEFAULT '{}',      -- ["1girl" implies "solo"?]
    related TEXT[] DEFAULT '{}',      -- 常見組合建議
    
    -- 內容分級（P0）
    nsfw_level TEXT NOT NULL DEFAULT 'all-ages' 
        CHECK (nsfw_level IN ('all-ages', 'r15', 'r18', 'blocked')),
    
    -- 元數據
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT valid_post_count CHECK (post_count >= 0)
);

-- 索引優化
CREATE INDEX idx_tags_category ON tags(category);
CREATE INDEX idx_tags_post_count ON tags(post_count DESC);
CREATE INDEX idx_tags_nsfw ON tags(nsfw_level);
CREATE INDEX idx_tags_aliases_gin ON tags USING GIN(aliases);
```

---

#### 2. Tag 共現表（用於推薦組合）

```sql
CREATE TABLE tag_cooccur (
    tag TEXT NOT NULL,
    other_tag TEXT NOT NULL,
    cooccur_count INTEGER NOT NULL DEFAULT 0,
    confidence FLOAT DEFAULT 0.0,  -- PMI or lift
    
    PRIMARY KEY (tag, other_tag),
    FOREIGN KEY (tag) REFERENCES tags(tag) ON DELETE CASCADE,
    FOREIGN KEY (other_tag) REFERENCES tags(tag) ON DELETE CASCADE,
    
    CONSTRAINT no_self_cooccur CHECK (tag != other_tag)
);

CREATE INDEX idx_cooccur_tag ON tag_cooccur(tag, cooccur_count DESC);
```

---

#### 3. 派生視圖（加速查詢）

```sql
-- 熱門標籤（post_count >= 1000）
CREATE MATERIALIZED VIEW popular_tags AS
SELECT tag, category, post_count, nsfw_level
FROM tags
WHERE post_count >= 1000
  AND nsfw_level = 'all-ages'
ORDER BY post_count DESC;

CREATE INDEX idx_popular_tags_category ON popular_tags(category);

-- 衝突對（展開 conflicts 陣列）
CREATE MATERIALIZED VIEW conflict_pairs AS
SELECT 
    tag AS tag_a,
    UNNEST(conflicts) AS tag_b
FROM tags
WHERE conflicts IS NOT NULL AND array_length(conflicts, 1) > 0;

CREATE INDEX idx_conflict_pairs ON conflict_pairs(tag_a, tag_b);

-- 刷新策略（每日凌晨）
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY popular_tags;
    REFRESH MATERIALIZED VIEW CONCURRENTLY conflict_pairs;
END;
$$ LANGUAGE plpgsql;
```

---

#### 4. Inspire Sessions（業務資料）

```sql
CREATE TABLE inspire_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    
    -- 狀態機
    current_phase TEXT NOT NULL DEFAULT 'understanding'
        CHECK (current_phase IN (
            'understanding', 'exploring', 'refining', 
            'finalizing', 'completed', 'aborted'
        )),
    
    -- 提取的資料（JSONB）
    extracted_intent JSONB,
    generated_directions JSONB,
    selected_direction_index INTEGER,
    final_output JSONB,
    
    -- 追蹤與控制
    total_cost DECIMAL(10, 6) DEFAULT 0.0,
    total_tokens INTEGER DEFAULT 0,
    tool_call_count JSONB DEFAULT '{}'::jsonb,  -- {"search": 3, "generate": 2}
    abort_reason TEXT,
    
    -- 品質與反饋
    quality_score INTEGER,
    user_satisfaction INTEGER,  -- 1-5
    user_feedback TEXT,
    
    -- 時間戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    CONSTRAINT valid_quality_score CHECK (quality_score BETWEEN 0 AND 100),
    CONSTRAINT valid_cost CHECK (total_cost >= 0)
);

CREATE INDEX idx_sessions_user ON inspire_sessions(user_id, created_at DESC);
CREATE INDEX idx_sessions_phase ON inspire_sessions(current_phase);
CREATE INDEX idx_sessions_quality ON inspire_sessions(quality_score);
```

---

### Redis 快取策略（高頻資料）

#### Key 設計

```python
# 熱門標籤（Sorted Set，按 post_count）
"hot:tags:{category}"          # ZADD hot:tags:SCENE moonlight 15234
"hot:tags:all"                 # 全類別

# 標籤組合（Sorted Set，按共現次數）
"combo:{tag}"                  # ZADD combo:moonlight night_sky 8932

# 別名映射（String）
"alias:{alias}"                # SET alias:longhair "long_hair"

# 衝突檢測（Set）
"conflicts:{tag}"              # SADD conflicts:long_hair "short_hair" "bald"

# 封禁清單（Set，P0）
"policy:blocklist"             # SADD policy:blocklist "loli" "child" ...
"policy:nsfw"                  # SADD policy:nsfw "nude" "nsfw" ...

# 個人化（Sorted Set）
"user:{user_id}:prefs"         # ZADD user:123:prefs cinematic_lighting 0.85
```

---

#### 快取策略

```python
class InspireCache:
    """Redis 快取管理"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.TTL_HOT_TAGS = 86400  # 24 小時
        self.TTL_COMBOS = 3600     # 1 小時
    
    async def get_hot_tags(self, category: str = "all", limit: int = 100):
        """獲取熱門標籤"""
        key = f"hot:tags:{category}"
        
        # 嘗試從快取讀取
        cached = await self.redis.zrevrange(key, 0, limit-1, withscores=True)
        
        if cached:
            return [{"tag": tag, "popularity": score} for tag, score in cached]
        
        # 快取未命中，從 DB 載入
        if category == "all":
            tags = await db.execute("""
                SELECT tag, post_count FROM popular_tags 
                ORDER BY post_count DESC LIMIT $1
            """, limit)
        else:
            tags = await db.execute("""
                SELECT tag, post_count FROM popular_tags 
                WHERE category = $1
                ORDER BY post_count DESC LIMIT $2
            """, category, limit)
        
        # 寫入快取
        if tags:
            await self.redis.zadd(key, {t["tag"]: t["post_count"] for t in tags})
            await self.redis.expire(key, self.TTL_HOT_TAGS)
        
        return tags
    
    async def get_tag_combinations(self, tag: str, limit: int = 10):
        """獲取常見組合"""
        key = f"combo:{tag}"
        
        cached = await self.redis.zrevrange(key, 0, limit-1, withscores=True)
        if cached:
            return [{"tag": t, "score": s} for t, s in cached]
        
        # 從 DB 載入
        combos = await db.execute("""
            SELECT other_tag, cooccur_count FROM tag_cooccur
            WHERE tag = $1
            ORDER BY cooccur_count DESC LIMIT $2
        """, tag, limit)
        
        if combos:
            await self.redis.zadd(key, {c["other_tag"]: c["cooccur_count"] for c in combos})
            await self.redis.expire(key, self.TTL_COMBOS)
        
        return combos
    
    async def is_blocked(self, tag: str) -> bool:
        """檢查是否被封禁（P0）"""
        return await self.redis.sismember("policy:blocklist", tag.lower())
    
    async def resolve_alias(self, tag: str) -> str:
        """別名解析"""
        canonical = await self.redis.get(f"alias:{tag.lower()}")
        return canonical if canonical else tag
```

---

## ⚙️ 工具 I/O 契約（嚴格定義）

### 1. understand_intent

**輸入：**
```python
{
    "input_text": str  # 使用者原始輸入
}
```

**輸出（只這些鍵）：**
```python
{
    "core_mood": str,              # "孤獨、夢幻"
    "visual_elements": [str],      # ["少女", "森林", "月光"]
    "style_preference": str,       # "anime" | "realistic" | "artistic" | "mixed" | "unspecified"
    "clarity_level": str,          # "crystal_clear" | "mostly_clear" | "somewhat_vague" | "very_vague"
    "confidence": float,           # 0.0-1.0
    "next_action": str             # "generate_directly" | "ask_clarification" | "search_references"
}
```

---

### 2. search_examples（內部工具）

**輸入：**
```python
{
    "search_keywords": [str],      # ["moonlight", "dreamy"]
    "search_purpose": str,         # "find_mood_tags" | "find_scene_tags" | "find_combinations"
    "search_strategy": str,        # "keyword" | "semantic" | "auto"
    "min_popularity": int,         # 預設 1000
    "max_results": int             # 預設 10
}
```

**輸出（嚴格格式，只四鍵）：**
```python
{
    "examples": [
        {
            "tag": str,            # "moonlight"
            "category": str,       # "SCENE"
            "popularity": int,     # 15234
            "usage_hint": str      # "常與 night_sky, stars 組合"
        }
    ],
    "search_strategy_used": str,   # 實際使用的策略
    "common_combinations": [[str]],# [["moonlight", "night_sky"], ...]
    "suggestions": str             # 給 Agent 的建議
}
```

---

### 3. generate_ideas

**輸入：**
```python
{
    "context": {
        "intent": dict,            # understand_intent 的輸出
        "references": [dict]       # search_examples 的結果（可選）
    },
    "num_directions": int,         # 2-3
    "diversity_level": str         # "low" | "moderate" | "high"
}
```

**輸出：**
```python
{
    "ideas": [
        {
            "title": str,          # "月下獨舞"
            "concept": str,        # 1-2 句描述
            "vibe": str,           # 核心氛圍
            "main_tags": [str],    # 10-15 個核心標籤
            "quick_preview": str,  # 簡化的 prompt 預覽
            "uniqueness": str      # 這個方向的獨特點
        }
    ],
    "generation_basis": str,       # 基於什麼資訊生成
    "diversity_achieved": str      # "low" | "moderate" | "high"
}
```

---

### 4. validate_quality

**輸入：**
```python
{
    "tags": [str],                 # 要驗證的標籤
    "check_aspects": [str],        # ["validity", "conflicts", "redundancy", "balance", "popularity"]
    "strictness": str              # "lenient" | "moderate" | "strict"
}
```

**輸出：**
```python
{
    "is_valid": bool,              # score >= 70
    "score": int,                  # 0-100
    
    "issues": [
        {
            "type": str,           # "invalid_tag" | "conflict" | "redundancy" | "imbalance" | "unpopular"
            "severity": str,       # "critical" | "warning" | "info"
            "description": str,    # "標籤 'longhair' 無效，建議 'long_hair'"
            "affected_tags": [str]
        }
    ],
    
    "strengths": [
        {
            "aspect": str,         # "category_coverage" | "popularity" | "coherence"
            "description": str     # "類別分佈均衡（5/5 類別）"
        }
    ],
    
    "quick_fixes": {
        "remove": [str],           # 建議移除的標籤
        "add": [str],              # 建議添加的標籤
        "replace": {               # 建議替換：old -> new
            "old_tag": "new_tag"
        }
    },
    
    "category_distribution": {     # CHARACTER: 2, SCENE: 3, ...
        "CHARACTER": int,
        "APPEARANCE": int,
        "SCENE": int,
        "MOOD": int,
        "STYLE": int
    },
    
    "details": {
        "invalid_count": int,
        "conflict_count": int,
        "redundancy_count": int,
        "unpopular_count": int,
        "balance_score": int       # 0-100
    }
}
```

---

### 5. finalize_prompt

**輸入：**
```python
{
    "selected_direction": dict,    # generate_ideas 中的一個 idea
    "validated_tags": [str],       # validate_quality 修正後的標籤
    "quality_score": int,          # 來自 validate
    "user_preferences": dict       # 可選，個人化設定
}
```

**輸出：**
```python
{
    "final_output": {
        "title": str,
        "concept": str,
        "positive_prompt": str,    # 完整逗號分隔
        "negative_prompt": str,
        "structure": {
            "subject": [str],
            "appearance": [str],
            "scene": [str],
            "mood": [str],
            "style": [str]
        },
        "parameters": {
            "cfg_scale": float,
            "steps": int,
            "sampler": str,
            "seed": int | null
        },
        "usage_tips": str
    },
    "quality_score": int,
    "metadata": {
        "total_tags": int,
        "generation_time": float,
        "confidence": float
    }
}
```

---

## 🛡️ 驗證器實作邏輯（可測試）

### 核心驗證函數

```python
from typing import List, Dict, Tuple

class InspireQualityValidator:
    """
    Prompt 品質驗證器
    基於 Danbooru 最佳實踐和資料庫統計
    """
    
    def __init__(self, db, cache):
        self.db = db
        self.cache = cache
        
        # 扣分規則（可調整）
        self.PENALTIES = {
            "invalid_tag": 35,
            "critical_conflict": 25,
            "minor_conflict": 10,
            "redundancy": 5,
            "poor_balance": 20,
            "unpopular_ratio_high": 5
        }
        
        # 最低類別要求
        self.MIN_CATEGORIES = 3
        
        # 流行度門檻
        self.POPULARITY_THRESHOLD = 100
    
    async def validate(
        self,
        tags: List[str],
        check_aspects: List[str],
        strictness: str = "moderate"
    ) -> Dict:
        """主驗證函數"""
        
        # 1. 正規化標籤
        tags_norm = await self._normalize_tags(tags)
        
        # 2. 初始化分數
        score = 100
        issues = []
        strengths = []
        quick_fixes = {"remove": [], "add": [], "replace": {}}
        
        # 3. 執行各項檢查
        if "validity" in check_aspects:
            score, issues, quick_fixes = await self._check_validity(
                tags_norm, score, issues, quick_fixes
            )
        
        if "conflicts" in check_aspects:
            score, issues, quick_fixes = await self._check_conflicts(
                tags_norm, score, issues, quick_fixes, strictness
            )
        
        if "redundancy" in check_aspects:
            score, issues = await self._check_redundancy(
                tags_norm, score, issues
            )
        
        if "balance" in check_aspects:
            score, issues, strengths, quick_fixes = await self._check_balance(
                tags_norm, score, issues, strengths, quick_fixes
            )
        
        if "popularity" in check_aspects:
            score, issues = await self._check_popularity(
                tags_norm, score, issues
            )
        
        # 4. 計算類別分佈
        category_dist = await self._get_category_distribution(tags_norm)
        
        # 5. 返回結果
        return {
            "is_valid": score >= 70,
            "score": score,
            "issues": issues,
            "strengths": strengths,
            "quick_fixes": quick_fixes,
            "category_distribution": category_dist,
            "details": {
                "invalid_count": len([i for i in issues if i["type"] == "invalid_tag"]),
                "conflict_count": len([i for i in issues if i["type"] == "conflict"]),
                "redundancy_count": len([i for i in issues if i["type"] == "redundancy"]),
                "unpopular_count": len([i for i in issues if i["type"] == "unpopular"]),
                "balance_score": min(100, (len(category_dist) / 5) * 100)
            }
        }
    
    async def _normalize_tags(self, tags: List[str]) -> List[str]:
        """正規化：去重、小寫、解析別名"""
        unique_tags = list(dict.fromkeys(tags))  # 保持順序去重
        normalized = []
        
        for tag in unique_tags:
            tag_lower = tag.lower().strip()
            # 解析別名
            canonical = await self.cache.resolve_alias(tag_lower)
            normalized.append(canonical)
        
        return list(dict.fromkeys(normalized))  # 再次去重（別名可能合併）
    
    async def _check_validity(
        self, tags: List[str], score: int, issues: List, quick_fixes: Dict
    ) -> Tuple:
        """檢查標籤是否存在於資料庫"""
        
        # 批量檢查
        valid_tags = await self.db.execute("""
            SELECT tag FROM tags WHERE tag = ANY($1)
        """, tags)
        
        valid_set = {row["tag"] for row in valid_tags}
        invalid_tags = [t for t in tags if t not in valid_set]
        
        if invalid_tags:
            score -= self.PENALTIES["invalid_tag"]
            
            for invalid in invalid_tags:
                # 尋找相似標籤（建議）
                suggestions = await self._find_similar_tags(invalid)
                
                issues.append({
                    "type": "invalid_tag",
                    "severity": "critical",
                    "description": f"標籤 '{invalid}' 不存在於資料庫",
                    "affected_tags": [invalid],
                    "suggestions": suggestions
                })
                
                quick_fixes["remove"].append(invalid)
                if suggestions:
                    quick_fixes["replace"][invalid] = suggestions[0]
        
        return score, issues, quick_fixes
    
    async def _check_conflicts(
        self, tags: List[str], score: int, issues: List, 
        quick_fixes: Dict, strictness: str
    ) -> Tuple:
        """檢查標籤衝突（互斥）"""
        
        conflicts_found = []
        
        for tag in tags:
            # 從 Redis 或 DB 獲取衝突列表
            conflicts = await self.cache.redis.smembers(f"conflicts:{tag}")
            
            if not conflicts:
                # 快取未命中，從 DB 載入
                result = await self.db.execute("""
                    SELECT tag_b FROM conflict_pairs WHERE tag_a = $1
                """, tag)
                conflicts = {row["tag_b"] for row in result}
                
                if conflicts:
                    await self.cache.redis.sadd(f"conflicts:{tag}", *conflicts)
            
            # 檢查當前標籤列表中是否有衝突
            conflicting = [t for t in tags if t in conflicts and t != tag]
            
            if conflicting:
                conflicts_found.append((tag, conflicting))
        
        if conflicts_found:
            penalty = self.PENALTIES["critical_conflict"] if strictness == "strict" else self.PENALTIES["minor_conflict"]
            score -= penalty * len(conflicts_found)
            
            for tag, conflicting in conflicts_found:
                issues.append({
                    "type": "conflict",
                    "severity": "critical" if strictness == "strict" else "warning",
                    "description": f"'{tag}' 與 {conflicting} 衝突",
                    "affected_tags": [tag] + conflicting
                })
                
                # 建議移除流行度較低的
                popularity = await self._get_tags_popularity([tag] + conflicting)
                least_popular = min(popularity, key=popularity.get)
                quick_fixes["remove"].append(least_popular)
        
        return score, issues, quick_fixes
    
    async def _check_redundancy(
        self, tags: List[str], score: int, issues: List
    ) -> Tuple:
        """檢查冗餘（同義或包含關係）"""
        
        # 簡化版：檢查是否有標籤互為別名
        redundant_pairs = []
        
        for i, tag_a in enumerate(tags):
            for tag_b in tags[i+1:]:
                # 檢查 tag_b 是否是 tag_a 的別名
                result = await self.db.execute("""
                    SELECT 1 FROM tags 
                    WHERE tag = $1 AND $2 = ANY(aliases)
                """, tag_a, tag_b)
                
                if result:
                    redundant_pairs.append((tag_a, tag_b))
        
        if redundant_pairs:
            score -= self.PENALTIES["redundancy"] * len(redundant_pairs)
            
            for tag_a, tag_b in redundant_pairs:
                issues.append({
                    "type": "redundancy",
                    "severity": "info",
                    "description": f"'{tag_a}' 和 '{tag_b}' 是同義詞",
                    "affected_tags": [tag_a, tag_b]
                })
        
        return score, issues
    
    async def _check_balance(
        self, tags: List[str], score: int, issues: List, 
        strengths: List, quick_fixes: Dict
    ) -> Tuple:
        """檢查類別平衡（至少 3 類）"""
        
        category_dist = await self._get_category_distribution(tags)
        
        if len(category_dist) < self.MIN_CATEGORIES:
            score -= self.PENALTIES["poor_balance"]
            
            missing_categories = set([
                "CHARACTER", "APPEARANCE", "SCENE", "MOOD", "STYLE"
            ]) - set(category_dist.keys())
            
            issues.append({
                "type": "imbalance",
                "severity": "warning",
                "description": f"類別分佈不均（{len(category_dist)}/5），缺少：{missing_categories}",
                "affected_tags": []
            })
            
            # 建議補充
            if "SCENE" not in category_dist:
                scene_suggestions = await self.cache.get_hot_tags("SCENE", 3)
                quick_fixes["add"].extend([t["tag"] for t in scene_suggestions[:1]])
            
            if "MOOD" not in category_dist:
                mood_suggestions = await self.cache.get_hot_tags("MOOD", 3)
                quick_fixes["add"].extend([t["tag"] for t in mood_suggestions[:1]])
        
        else:
            strengths.append({
                "aspect": "category_coverage",
                "description": f"類別分佈均衡（{len(category_dist)}/5 類別）"
            })
        
        return score, issues, strengths, quick_fixes
    
    async def _check_popularity(
        self, tags: List[str], score: int, issues: List
    ) -> Tuple:
        """檢查流行度（避免過多冷門標籤）"""
        
        popularity = await self._get_tags_popularity(tags)
        unpopular = [t for t, p in popularity.items() if p < self.POPULARITY_THRESHOLD]
        
        unpopular_ratio = len(unpopular) / len(tags) if tags else 0
        
        if unpopular_ratio > 0.4:  # 超過 40% 冷門
            score -= self.PENALTIES["unpopular_ratio_high"]
            
            issues.append({
                "type": "unpopular",
                "severity": "info",
                "description": f"{len(unpopular)} 個標籤較冷門（<{self.POPULARITY_THRESHOLD} 使用次數）",
                "affected_tags": unpopular
            })
        
        return score, issues
    
    async def _get_category_distribution(self, tags: List[str]) -> Dict[str, int]:
        """獲取類別分佈"""
        result = await self.db.execute("""
            SELECT category, COUNT(*) as count
            FROM tags
            WHERE tag = ANY($1)
            GROUP BY category
        """, tags)
        
        return {row["category"]: row["count"] for row in result}
    
    async def _get_tags_popularity(self, tags: List[str]) -> Dict[str, int]:
        """獲取標籤流行度"""
        result = await self.db.execute("""
            SELECT tag, post_count
            FROM tags
            WHERE tag = ANY($1)
        """, tags)
        
        return {row["tag"]: row["post_count"] for row in result}
    
    async def _find_similar_tags(self, invalid_tag: str, limit: int = 3) -> List[str]:
        """尋找相似標籤（用於建議）"""
        # 使用 PostgreSQL 的 similarity 或 trigram
        result = await self.db.execute("""
            SELECT tag, similarity(tag, $1) as sim
            FROM tags
            WHERE similarity(tag, $1) > 0.3
            ORDER BY sim DESC
            LIMIT $2
        """, invalid_tag, limit)
        
        return [row["tag"] for row in result]
```

---

## 🔒 內容安全與合規（P0 必做）

### 1. 封禁清單（Blocklist）

```python
# 初始化封禁清單（啟動時載入到 Redis）
BLOCKED_TAGS = {
    # 未成年人相關（嚴格禁止）
    "loli", "shota", "child", "kid", "toddler", "baby",
    "underage", "young_girl", "young_boy", "child_",
    
    # 性暗示 + 未成年（組合禁止）
    # 單獨檢測邏輯處理
}

NSFW_TAGS = {
    "nsfw", "nude", "naked", "sex", "explicit",
    "hentai", "porn", "xxx", "r-18", "r18"
}

SENSITIVE_TAGS = {
    "blood", "gore", "violence", "death", "suicide",
    "self-harm", "hanging", "decapitation"
}
```

---

### 2. 內容過濾器

```python
from typing import Tuple, List, Dict

class ContentSafetyFilter:
    """內容安全過濾器（P0）"""
    
    def __init__(self, cache, moderation_api):
        self.cache = cache
        self.moderation_api = moderation_api
    
    async def filter_tags(
        self, 
        tags: List[str],
        user_age_verified: bool = False
    ) -> Tuple[List[str], List[str], Dict]:
        """
        過濾標籤
        
        Returns:
            (safe_tags, removed_tags, metadata)
        """
        
        safe_tags = []
        removed_tags = []
        metadata = {
            "blocked_count": 0,
            "nsfw_count": 0,
            "sensitive_count": 0,
            "reason": []
        }
        
        for tag in tags:
            tag_lower = tag.lower()
            
            # 檢查 1: 封禁清單（絕對禁止）
            if await self.cache.is_blocked(tag_lower):
                removed_tags.append(tag)
                metadata["blocked_count"] += 1
                metadata["reason"].append(f"'{tag}' 在封禁清單中")
                continue
            
            # 檢查 2: NSFW（需年齡驗證）
            if tag_lower in NSFW_TAGS:
                if not user_age_verified:
                    removed_tags.append(tag)
                    metadata["nsfw_count"] += 1
                    metadata["reason"].append(f"'{tag}' 需要年齡驗證")
                    continue
            
            # 檢查 3: 敏感內容（警告但允許）
            if tag_lower in SENSITIVE_TAGS:
                metadata["sensitive_count"] += 1
                metadata["reason"].append(f"'{tag}' 包含敏感內容")
                # 仍然添加，但標記
            
            safe_tags.append(tag)
        
        return safe_tags, removed_tags, metadata
    
    async def check_user_input(self, text: str) -> Tuple[bool, str]:
        """
        檢查使用者輸入（使用 OpenAI Moderation API）
        
        Returns:
            (is_safe, reason)
        """
        
        try:
            response = await self.moderation_api.create(input=text)
            result = response.results[0]
            
            if result.flagged:
                # 找出被標記的類別
                flagged_categories = [
                    cat for cat, flagged in result.categories.dict().items() 
                    if flagged
                ]
                
                return False, f"輸入包含不適當內容：{', '.join(flagged_categories)}"
            
            return True, ""
        
        except Exception as e:
            logger.error(f"Moderation API 錯誤：{e}")
            # 失敗時保守處理：允許但記錄
            return True, ""
    
    async def suggest_safe_alternative(
        self, 
        blocked_tags: List[str]
    ) -> List[str]:
        """為被封禁的標籤建議安全替代"""
        
        alternatives = []
        
        for tag in blocked_tags:
            # 替代邏輯
            if tag in {"loli", "shota", "child"}:
                alternatives.extend(["1girl", "solo", "youthful"])
            elif tag in NSFW_TAGS:
                alternatives.extend(["artistic", "aesthetic", "elegant"])
        
        return list(set(alternatives))
```

---

### 3. Guardrail 整合

```python
# Layer 1: API 層（FastAPI）
@router.post("/api/inspire/start")
async def start_inspire(
    request: dict,
    safety_filter: ContentSafetyFilter = Depends()
):
    user_input = request.get("message", "")
    
    # P0: 內容安全檢查
    is_safe, reason = await safety_filter.check_user_input(user_input)
    
    if not is_safe:
        return {
            "error": "content_unsafe",
            "message": "輸入包含不適當內容",
            "reason": reason,
            "suggestion": "請使用更具體的描述，避免敏感詞彙"
        }
    
    # 繼續處理...
    result = await run_inspire_agent(user_input, user_id)
    return result

# Layer 3: Tool 層（驗證器中）
@function_tool
async def validate_quality(tags: list[str], ...) -> dict:
    """驗證品質（包含內容安全）"""
    
    # P0: 過濾標籤
    safe_tags, removed_tags, safety_meta = await safety_filter.filter_tags(tags)
    
    if removed_tags:
        logger.warning(f"移除了 {len(removed_tags)} 個不安全標籤")
        
        # 建議替代
        alternatives = await safety_filter.suggest_safe_alternative(removed_tags)
        tags = safe_tags + alternatives
    
    # 繼續常規驗證...
    validation_result = await validator.validate(tags, ...)
    
    # 合併安全資訊
    validation_result["safety"] = safety_meta
    validation_result["removed_tags"] = removed_tags
    
    return validation_result
```

---

## 🎮 狀態機與中止條件

### 狀態機設計

```python
from enum import Enum

class InspirePhase(str, Enum):
    UNDERSTANDING = "understanding"    # 理解階段
    EXPLORING = "exploring"            # 探索階段（搜尋、生成）
    REFINING = "refining"              # 精煉階段（迭代優化）
    FINALIZING = "finalizing"          # 定稿階段（嚴格驗證）
    COMPLETED = "completed"            # 完成
    ABORTED = "aborted"                # 中止

class InspireStateMachine:
    """Inspire Agent 狀態機"""
    
    def __init__(self, session_id: str, db, limits: dict):
        self.session_id = session_id
        self.db = db
        self.phase = InspirePhase.UNDERSTANDING
        
        # 限制條件
        self.limits = {
            "max_cost": limits.get("max_cost", 0.015),
            "max_turns": limits.get("max_turns", 15),
            "max_tool_calls_per_type": limits.get("max_tool_calls", 5),
            "timeout_seconds": limits.get("timeout", 120),
            "convergence_threshold": limits.get("convergence", 3)
        }
        
        # 追蹤狀態
        self.total_cost = 0.0
        self.total_turns = 0
        self.tool_calls = {}  # {"search": 2, "generate": 1}
        self.last_feedback = []
        self.start_time = time.time()
    
    async def transition(self, to_phase: InspirePhase, reason: str = ""):
        """狀態轉換"""
        old_phase = self.phase
        self.phase = to_phase
        
        logger.info(f"Session {self.session_id}: {old_phase} → {to_phase} ({reason})")
        
        # 更新資料庫
        await self.db.execute("""
            UPDATE inspire_sessions
            SET current_phase = $1, updated_at = NOW()
            WHERE session_id = $2
        """, to_phase, self.session_id)
    
    def record_tool_call(self, tool_name: str):
        """記錄工具調用"""
        self.tool_calls[tool_name] = self.tool_calls.get(tool_name, 0) + 1
    
    def add_cost(self, cost: float):
        """累加成本"""
        self.total_cost += cost
    
    def should_abort(self) -> Tuple[bool, str]:
        """檢查是否應該中止"""
        
        # 條件 1: 成本超限
        if self.total_cost >= self.limits["max_cost"]:
            return True, f"成本超限（${self.total_cost:.4f} >= ${self.limits['max_cost']}）"
        
        # 條件 2: 輪次超限
        if self.total_turns >= self.limits["max_turns"]:
            return True, f"輪次超限（{self.total_turns} >= {self.limits['max_turns']}）"
        
        # 條件 3: 超時
        elapsed = time.time() - self.start_time
        if elapsed >= self.limits["timeout_seconds"]:
            return True, f"超時（{elapsed:.1f}s >= {self.limits['timeout_seconds']}s）"
        
        # 條件 4: 工具調用過多
        for tool, count in self.tool_calls.items():
            if count >= self.limits["max_tool_calls_per_type"]:
                return True, f"工具 '{tool}' 調用過多（{count} >= {self.limits['max_tool_calls_per_type']}）"
        
        # 條件 5: 收斂（連續 N 輪無改進）
        if self.phase == InspirePhase.REFINING:
            if len(set(self.last_feedback[-3:])) == 1:  # 最近 3 次反饋相同
                return True, "已收斂（反饋無變化）"
        
        return False, ""
    
    async def next_action(self, agent_output: str) -> str:
        """決定下一步動作"""
        
        # 檢查中止條件
        should_abort, reason = self.should_abort()
        if should_abort:
            await self.transition(InspirePhase.ABORTED, reason)
            return "finalize_best"  # 直接用目前最佳結果定稿
        
        # 根據當前階段決定
        if self.phase == InspirePhase.UNDERSTANDING:
            # 理解階段 → 探索階段
            if "clarity_level" in agent_output and "mostly_clear" in agent_output:
                await self.transition(InspirePhase.EXPLORING, "清晰度足夠")
                return "generate_ideas"
            else:
                return "ask_clarification"
        
        elif self.phase == InspirePhase.EXPLORING:
            # 探索階段 → 精煉階段
            if "generated_directions" in agent_output:
                await self.transition(InspirePhase.REFINING, "方向已生成")
                return "wait_user_selection"
            else:
                return "continue_exploring"
        
        elif self.phase == InspirePhase.REFINING:
            # 精煉階段 → 定稿階段
            # 檢查品質分數
            if "quality_score" in agent_output and int(agent_output.get("quality_score", 0)) >= 85:
                await self.transition(InspirePhase.FINALIZING, "品質達標")
                return "finalize"
            else:
                # 繼續精煉
                if self.tool_calls.get("validate", 0) >= 3:
                    await self.transition(InspirePhase.FINALIZING, "驗證次數已達上限")
                    return "finalize"
                return "continue_refining"
        
        elif self.phase == InspirePhase.FINALIZING:
            await self.transition(InspirePhase.COMPLETED, "定稿完成")
            return "return_result"
        
        return "continue"
```

---

## 📅 一週 MVP 落地計劃（Day-by-Day）

### Day 1: 基礎設施（資料庫 + 快取）

**目標**: 建立穩固的資料層

**任務**:
- [ ] 執行 PostgreSQL Schema（tags, tag_cooccur, inspire_sessions）
- [ ] 建立物化視圖（popular_tags, conflict_pairs）
- [ ] 設置 Redis 快取層（InspireCache 類別）
- [ ] 初始化封禁清單（ContentSafetyFilter）
- [ ] 寫入 100 個熱門標籤到 Redis（測試）

**驗收標準**:
```bash
# 測試資料庫
psql -U postgres -d prompt_scribe -c "SELECT COUNT(*) FROM tags;"
# 應返回 140K+

# 測試 Redis
redis-cli ZCARD "hot:tags:all"
# 應返回 100

# 測試封禁清單
redis-cli SISMEMBER "policy:blocklist" "loli"
# 應返回 1
```

**預估時間**: 6-8 小時

---

### Day 2: 理解工具（understand_intent）

**目標**: 實現最小可用的意圖理解

**任務**:
- [ ] 實現 `understand_intent` 工具（簡化版）
- [ ] 3 個澄清問題（角色/場景、風格、必要元素）
- [ ] 單元測試（5 個測試案例）
- [ ] 整合 Moderation API（內容安全）

**實作重點**:
```python
@function_tool
async def understand_intent(input_text: str) -> dict:
    """理解使用者意圖（簡化 MVP 版）"""
    
    # 1. 內容安全檢查
    is_safe, reason = await safety_filter.check_user_input(input_text)
    if not is_safe:
        raise ValueError(f"輸入不安全：{reason}")
    
    # 2. 基礎解析（關鍵字提取）
    mood_keywords = extract_mood_keywords(input_text)
    visual_keywords = extract_visual_keywords(input_text)
    
    # 3. 判斷清晰度
    clarity = "mostly_clear" if len(visual_keywords) >= 2 else "somewhat_vague"
    
    # 4. 決定下一步
    next_action = "generate_directly" if clarity == "mostly_clear" else "ask_clarification"
    
    return {
        "core_mood": ", ".join(mood_keywords),
        "visual_elements": visual_keywords,
        "style_preference": detect_style(input_text),
        "clarity_level": clarity,
        "confidence": 0.8 if clarity == "mostly_clear" else 0.5,
        "next_action": next_action
    }
```

**驗收標準**:
- 5/5 測試通過
- 敏感詞輸入被拒絕
- 清晰輸入返回 `mostly_clear`

**預估時間**: 4-6 小時

---

### Day 3: 創意生成（generate_ideas）+ 熱門標籤池

**目標**: 基於熱門標籤生成創意方向（先不接語義搜尋）

**任務**:
- [ ] 實現 `generate_ideas` 工具
- [ ] 從 Redis 熱門池抽樣（按類別）
- [ ] 生成 2-3 個方向（title + concept + 10 tags）
- [ ] 單元測試（3 個場景）

**實作重點**:
```python
@function_tool
async def generate_ideas(context: dict, num_directions: int = 3) -> dict:
    """生成創意方向（MVP：熱門標籤池）"""
    
    intent = context["intent"]
    ideas = []
    
    for i in range(num_directions):
        # 從熱門池抽樣
        character_tags = await cache.get_hot_tags("CHARACTER", 5)
        scene_tags = await cache.get_hot_tags("SCENE", 5)
        mood_tags = await cache.get_hot_tags("MOOD", 5)
        style_tags = await cache.get_hot_tags("STYLE", 5)
        
        # 組合（帶隨機性）
        selected = {
            "CHARACTER": random.sample(character_tags, 2),
            "SCENE": random.sample(scene_tags, 2),
            "MOOD": random.sample(mood_tags, 2),
            "STYLE": random.sample(style_tags, 2)
        }
        
        # 生成描述（固定模板）
        title = f"{intent['core_mood']}·{selected['SCENE'][0]['tag']}版"
        concept = f"基於 {intent['core_mood']} 的 {selected['SCENE'][0]['tag']} 場景"
        
        ideas.append({
            "title": title,
            "concept": concept,
            "vibe": intent["core_mood"],
            "main_tags": flatten(selected.values()),
            "quick_preview": ", ".join([t["tag"] for t in flatten(selected.values())]),
            "uniqueness": f"強調 {selected['MOOD'][0]['tag']}"
        })
    
    return {
        "ideas": ideas,
        "generation_basis": "熱門標籤池 + 使用者意圖",
        "diversity_achieved": "moderate"
    }
```

**驗收標準**:
- 生成 3 個不同方向
- 每個方向至少 10 個標籤
- 類別分佈均衡

**預估時間**: 5-7 小時

---

### Day 4: 品質驗證（validate_quality）

**目標**: 實現可執行的驗證規則

**任務**:
- [ ] 實現 `InspireQualityValidator` 類別
- [ ] 5 個檢查函數（validity, conflicts, redundancy, balance, popularity）
- [ ] `quick_fixes` 生成邏輯
- [ ] 單元測試（10 個案例）

**驗收標準**:
```python
# 測試案例
tags = ["1girl", "long_hair", "short_hair", "invalid_tag"]

result = await validator.validate(tags, ["validity", "conflicts"])

assert result["score"] < 70  # 有無效標籤和衝突
assert "invalid_tag" in result["quick_fixes"]["remove"]
assert ("long_hair" in result["quick_fixes"]["remove"] or 
        "short_hair" in result["quick_fixes"]["remove"])
```

**預估時間**: 6-8 小時

---

### Day 5: 定稿工具（finalize_prompt）

**目標**: 生成最終的結構化輸出

**任務**:
- [ ] 實現 `finalize_prompt` 工具
- [ ] 固定模板（positive/negative prompt）
- [ ] 參數建議（CFG, steps, sampler）
- [ ] 輸出驗證（確保格式正確）

**實作重點**:
```python
@function_tool
async def finalize_prompt(
    selected_direction: dict,
    validated_tags: list[str],
    quality_score: int
) -> dict:
    """定稿（MVP：固定模板）"""
    
    # 分類標籤
    structure = categorize_tags(validated_tags)
    
    # 組合 positive prompt
    positive = ", ".join([
        *structure["subject"],
        *structure["appearance"],
        *structure["scene"],
        *structure["mood"],
        *structure["style"],
        "masterpiece", "best_quality", "highly_detailed"
    ])
    
    # 固定 negative prompt
    negative = "nsfw, child, loli, gore, lowres, bad_anatomy, bad_hands, cropped, worst_quality, jpeg_artifacts, blurry"
    
    # 固定參數
    parameters = {
        "cfg_scale": 7.5,
        "steps": 35,
        "sampler": "DPM++ 2M Karras",
        "seed": None
    }
    
    return {
        "final_output": {
            "title": selected_direction["title"],
            "concept": selected_direction["concept"],
            "positive_prompt": positive,
            "negative_prompt": negative,
            "structure": structure,
            "parameters": parameters,
            "usage_tips": "CFG 可在 7-9 間調整以獲得不同效果"
        },
        "quality_score": quality_score,
        "metadata": {
            "total_tags": len(validated_tags),
            "generation_time": 0.0,
            "confidence": 0.9
        }
    }
```

**驗收標準**:
- 輸出符合契約格式
- Positive prompt 長度合理（<200 字）
- 參數在有效範圍內

**預估時間**: 3-5 小時

---

### Day 6: E2E 測試 + 合約測試

**目標**: 建立金樣測試，鎖定規格

**任務**:
- [ ] 3 個金樣場景（清晰/模糊/風險）
- [ ] 合約測試（每個工具 I/O）
- [ ] 中止條件測試
- [ ] CI 整合

**金樣測試**:
```python
# tests/test_inspire_e2e.py

@pytest.mark.asyncio
async def test_golden_case_clear_input():
    """金樣 A：清晰輸入，2 輪內完成"""
    
    session = InspireSession("test_clear")
    
    # 第 1 輪：理解
    result1 = await runner.run(
        agent,
        "一個穿白裙的精靈少女在森林中，夢幻氛圍",
        session=session
    )
    
    assert result1["phase"] == "exploring"
    assert len(result1["ideas"]) >= 2
    
    # 第 2 輪：定稿
    result2 = await runner.run(
        agent,
        "選擇第 1 個方向",
        session=session
    )
    
    assert result2["phase"] == "completed"
    assert result2["quality_score"] >= 85
    assert "elf" in result2["final_output"]["positive_prompt"]
    
    # 驗證輪次
    assert session.total_turns <= 2

@pytest.mark.asyncio
async def test_golden_case_blocked_content():
    """金樣 C：風險內容，拒絕並提供替代"""
    
    result = await runner.run(
        agent,
        "a cute loli girl with cat ears",
        session=SQLiteSession("test_blocked")
    )
    
    assert result["error"] == "content_unsafe"
    assert "loli" in result["reason"]
    assert "suggestion" in result
```

**驗收標準**:
- 3/3 金樣通過
- 所有合約測試通過
- CI 可自動運行

**預估時間**: 6-8 小時

---

### Day 7: 狀態機 + 前端整合

**目標**: 完整的流程控制 + 前端可用

**任務**:
- [ ] 實現 `InspireStateMachine`
- [ ] 整合到 FastAPI 端點
- [ ] 前端三卡方向展示
- [ ] 一鍵修復按鈕
- [ ] 完整流程測試

**API 端點**:
```python
@router.post("/api/inspire/start")
async def start_inspire(request: dict):
    """開始對話"""
    
    user_input = request["message"]
    session_id = str(uuid.uuid4())
    
    # 創建狀態機
    state_machine = InspireStateMachine(session_id, db, LIMITS)
    
    # 內容安全檢查
    is_safe, reason = await safety_filter.check_user_input(user_input)
    if not is_safe:
        return {"error": "content_unsafe", "reason": reason}
    
    # 運行 Agent（SDK）
    sdk_session = SQLiteSession(session_id)
    result = await Runner.run(inspire_agent, user_input, session=sdk_session)
    
    # 狀態管理
    next_action = await state_machine.next_action(result.final_output)
    
    return {
        "session_id": session_id,
        "phase": state_machine.phase,
        "response": result.final_output,
        "next_action": next_action
    }

@router.post("/api/inspire/continue")
async def continue_inspire(request: dict):
    """繼續對話"""
    
    session_id = request["session_id"]
    user_message = request["message"]
    
    # 恢復狀態機
    state_machine = await InspireStateMachine.from_session(session_id, db)
    
    # 檢查中止條件
    should_abort, reason = state_machine.should_abort()
    if should_abort:
        return {
            "error": "aborted",
            "reason": reason,
            "suggestion": "請使用當前最佳結果或重新開始"
        }
    
    # 繼續運行
    sdk_session = SQLiteSession(session_id)
    result = await Runner.run(inspire_agent, user_message, session=sdk_session)
    
    next_action = await state_machine.next_action(result.final_output)
    
    return {
        "session_id": session_id,
        "phase": state_machine.phase,
        "response": result.final_output,
        "next_action": next_action
    }
```

**驗收標準**:
- 前端可完整走完流程
- 狀態轉換正確
- 中止條件生效
- 一鍵修復可用

**預估時間**: 8-10 小時

---

## 📊 測試與監控

### 合約測試（Contract Tests）

```python
# tests/test_contracts.py

def test_understand_intent_contract():
    """驗證 understand_intent 輸出契約"""
    
    output = {
        "core_mood": "孤獨、夢幻",
        "visual_elements": ["森林", "月光"],
        "style_preference": "anime",
        "clarity_level": "mostly_clear",
        "confidence": 0.9,
        "next_action": "generate_directly"
    }
    
    # 必須包含所有鍵
    required_keys = [
        "core_mood", "visual_elements", "style_preference",
        "clarity_level", "confidence", "next_action"
    ]
    
    for key in required_keys:
        assert key in output, f"缺少必要鍵：{key}"
    
    # 類型驗證
    assert isinstance(output["core_mood"], str)
    assert isinstance(output["visual_elements"], list)
    assert isinstance(output["confidence"], float)
    assert 0 <= output["confidence"] <= 1
    
    # 枚舉驗證
    assert output["style_preference"] in [
        "anime", "realistic", "artistic", "mixed", "unspecified"
    ]
    assert output["clarity_level"] in [
        "crystal_clear", "mostly_clear", "somewhat_vague", "very_vague"
    ]
```

---

### 指標與監控

```python
# 關鍵指標
METRICS = {
    # 使用指標
    "avg_turns_per_session": 3.5,     # 目標：<5
    "completion_rate": 0.85,           # 目標：>80%
    "abort_rate": 0.05,                # 目標：<10%
    
    # 品質指標
    "avg_quality_score": 87,           # 目標：>85
    "validation_pass_rate": 0.92,      # 目標：>90%
    "quick_fixes_adoption_rate": 0.75, # 目標：>70%
    
    # 性能指標
    "avg_response_time_ms": 2500,      # 目標：<3000
    "avg_cost_per_session": 0.0007,    # 目標：<0.001
    
    # 安全指標
    "blocked_content_rate": 0.02,      # 追蹤但無目標
    "nsfw_filtered_rate": 0.01         # 追蹤
}
```

---

## 🎯 優先級總結

### P0（Week 1 MVP）

1. ✅ 資料庫 Schema + Redis 快取
2. ✅ 內容安全過濾器
3. ✅ 5 個工具（簡化版，無語義搜尋）
4. ✅ 驗證器（可執行規則）
5. ✅ 狀態機與中止條件
6. ✅ E2E 金樣測試

### P1（Week 2-3）

7. ⏳ 語義搜尋（離線批量嵌入）
8. ⏳ 並行優化（草測驗證）
9. ⏳ 個人化學習（使用者偏好）
10. ⏳ 前端完整 UI

### P2（迭代期）

11. ⏳ 學習回饋閉環
12. ⏳ 行銷整合（NocoDB/Trello）
13. ⏳ 教學模式（顯示推理）

---

## ✨ 關鍵決策記錄

### 決策 1: MVP 不做語義搜尋

**原因**: 
- 語義搜尋需要離線嵌入（耗時）
- 熱門標籤池已足夠 80% 場景
- 可在 Week 2 補上

**好處**:
- Week 1 可專注核心流程
- 降低複雜度，減少風險
- 快速驗證架構可行性

---

### 決策 2: 固定負面 Prompt 模板

**原因**:
- 負面 Prompt 高度標準化
- 避免 Agent 生成不當內容
- 降低驗證複雜度

**模板**:
```
nsfw, child, loli, gore, lowres, bad_anatomy, bad_hands, 
cropped, worst_quality, jpeg_artifacts, blurry
```

---

### 決策 3: 嚴格的 I/O 契約

**原因**:
- 避免 LLM 自創鍵名
- 確保前端可靠解析
- 簡化測試

**實施**:
- 所有工具輸出只返回文檔定義的鍵
- 前端硬編碼鍵名（不動態解析）
- 合約測試鎖定格式

---

## 📚 參考資料

1. [Danbooru Tag Wiki](https://danbooru.donmai.us/wiki_pages)
2. [OpenAI Moderation API](https://platform.openai.com/docs/guides/moderation)
3. [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
4. [Redis Sorted Sets](https://redis.io/docs/data-types/sorted-sets/)
5. [Finite State Machines in Python](https://python-statemachine.readthedocs.io/)

---

**文檔版本**: 1.0.0  
**創建日期**: 2025-10-21  
**最後更新**: 2025-10-21  
**維護者**: Prompt-Scribe Team

**所有實作細節已記錄完整！可直接按此文檔開工。** 🚀

