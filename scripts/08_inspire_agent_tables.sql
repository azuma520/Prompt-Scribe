-- ============================================================================
-- Script 8: Inspire Agent Tables
-- 整合現有資料庫（tags_final）與新的 Inspire Agent 功能
-- ============================================================================

-- ============================================
-- Part 1: 擴展現有 tags_final 表
-- 添加 Inspire Agent 需要的欄位
-- ============================================

-- 檢查欄位是否存在，不存在才添加
DO $$ 
BEGIN
    -- 添加 category 欄位（Inspire 需要的類別系統）
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tags_final' AND column_name = 'category'
    ) THEN
        ALTER TABLE tags_final 
        ADD COLUMN category TEXT CHECK (category IN (
            'CHARACTER', 'APPEARANCE', 'CLOTHING', 
            'SCENE', 'STYLE', 'EFFECT', 'ACTION', 
            'MOOD', 'QUALITY', 'META', NULL
        ));
        
        COMMENT ON COLUMN tags_final.category IS 'Inspire Agent 使用的標籤類別';
    END IF;

    -- 添加 aliases 欄位
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tags_final' AND column_name = 'aliases'
    ) THEN
        ALTER TABLE tags_final 
        ADD COLUMN aliases TEXT[] DEFAULT '{}';
        
        COMMENT ON COLUMN tags_final.aliases IS '標籤別名列表';
    END IF;

    -- 添加 conflicts 欄位
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tags_final' AND column_name = 'conflicts'
    ) THEN
        ALTER TABLE tags_final 
        ADD COLUMN conflicts TEXT[] DEFAULT '{}';
        
        COMMENT ON COLUMN tags_final.conflicts IS '互斥標籤列表';
    END IF;

    -- 添加 nsfw_level 欄位（P0 安全需求）
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tags_final' AND column_name = 'nsfw_level'
    ) THEN
        ALTER TABLE tags_final 
        ADD COLUMN nsfw_level TEXT NOT NULL DEFAULT 'all-ages'
            CHECK (nsfw_level IN ('all-ages', 'r15', 'r18', 'blocked'));
        
        COMMENT ON COLUMN tags_final.nsfw_level IS '內容分級（P0 安全）';
    END IF;
END $$;

-- 創建索引（如果不存在）
CREATE INDEX IF NOT EXISTS idx_tags_category 
    ON tags_final(category);

CREATE INDEX IF NOT EXISTS idx_tags_nsfw_level 
    ON tags_final(nsfw_level);

CREATE INDEX IF NOT EXISTS idx_tags_aliases_gin 
    ON tags_final USING GIN(aliases);

-- ============================================
-- Part 2: 新表 - Tag 共現（用於推薦組合）
-- ============================================

CREATE TABLE IF NOT EXISTS tag_cooccur (
    tag TEXT NOT NULL,
    other_tag TEXT NOT NULL,
    cooccur_count INTEGER NOT NULL DEFAULT 0,
    confidence FLOAT DEFAULT 0.0,
    
    PRIMARY KEY (tag, other_tag),
    
    CONSTRAINT no_self_cooccur CHECK (tag != other_tag),
    CONSTRAINT check_cooccur_count CHECK (cooccur_count >= 0),
    CONSTRAINT check_confidence CHECK (confidence BETWEEN 0.0 AND 1.0)
);

COMMENT ON TABLE tag_cooccur IS '標籤共現統計（用於推薦常見組合）';

CREATE INDEX IF NOT EXISTS idx_cooccur_tag 
    ON tag_cooccur(tag, cooccur_count DESC);

CREATE INDEX IF NOT EXISTS idx_cooccur_other_tag 
    ON tag_cooccur(other_tag, cooccur_count DESC);

-- ============================================
-- Part 3: 新表 - Inspire Sessions（業務資料）
-- ============================================

CREATE TABLE IF NOT EXISTS inspire_sessions (
    -- 主鍵
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    
    -- 狀態機
    current_phase TEXT NOT NULL DEFAULT 'understanding'
        CHECK (current_phase IN (
            'understanding', 'exploring', 'refining', 
            'finalizing', 'completed', 'aborted'
        )),
    
    -- 提取的資料（從工具調用中）
    extracted_intent JSONB,
    generated_directions JSONB,
    selected_direction_index INTEGER,
    final_output JSONB,
    
    -- 追蹤與控制
    total_cost DECIMAL(10, 6) DEFAULT 0.0,
    total_tokens INTEGER DEFAULT 0,
    tool_call_count JSONB DEFAULT '{}'::jsonb,
    abort_reason TEXT,
    
    -- 品質與反饋
    quality_score INTEGER CHECK (quality_score BETWEEN 0 AND 100),
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    user_feedback TEXT,
    
    -- 時間戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- 約束
    CONSTRAINT valid_cost CHECK (total_cost >= 0),
    CONSTRAINT valid_tokens CHECK (total_tokens >= 0)
);

COMMENT ON TABLE inspire_sessions IS 'Inspire Agent 對話 Session 業務資料';

CREATE INDEX IF NOT EXISTS idx_sessions_user 
    ON inspire_sessions(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sessions_phase 
    ON inspire_sessions(current_phase);

CREATE INDEX IF NOT EXISTS idx_sessions_quality 
    ON inspire_sessions(quality_score);

CREATE INDEX IF NOT EXISTS idx_sessions_created 
    ON inspire_sessions(created_at DESC);

-- ============================================
-- Part 4: 物化視圖 - 熱門標籤（加速查詢）
-- ============================================

CREATE MATERIALIZED VIEW IF NOT EXISTS popular_tags AS
SELECT 
    name AS tag,
    category,
    post_count,
    nsfw_level,
    main_category,
    sub_category
FROM tags_final
WHERE post_count >= 1000
  AND nsfw_level = 'all-ages'
ORDER BY post_count DESC;

COMMENT ON MATERIALIZED VIEW popular_tags IS '熱門標籤快取（post_count >= 1000, 僅 all-ages）';

CREATE INDEX IF NOT EXISTS idx_popular_tags_category 
    ON popular_tags(category);

CREATE INDEX IF NOT EXISTS idx_popular_tags_post_count 
    ON popular_tags(post_count DESC);

-- ============================================
-- Part 5: 物化視圖 - 衝突對（展開 conflicts）
-- ============================================

CREATE MATERIALIZED VIEW IF NOT EXISTS conflict_pairs AS
SELECT 
    name AS tag_a,
    UNNEST(conflicts) AS tag_b
FROM tags_final
WHERE conflicts IS NOT NULL 
  AND array_length(conflicts, 1) > 0;

COMMENT ON MATERIALIZED VIEW conflict_pairs IS '標籤衝突對（從 conflicts 陣列展開）';

CREATE INDEX IF NOT EXISTS idx_conflict_pairs_a 
    ON conflict_pairs(tag_a);

CREATE INDEX IF NOT EXISTS idx_conflict_pairs_b 
    ON conflict_pairs(tag_b);

-- ============================================
-- Part 6: 刷新函數（定期更新物化視圖）
-- ============================================

CREATE OR REPLACE FUNCTION refresh_inspire_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY popular_tags;
    REFRESH MATERIALIZED VIEW CONCURRENTLY conflict_pairs;
    
    RAISE NOTICE '物化視圖已刷新';
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_inspire_materialized_views() IS '刷新 Inspire Agent 使用的物化視圖';

-- ============================================
-- Part 7: 初始化封禁清單（P0 安全）
-- ============================================

-- 將封禁標籤標記為 blocked
UPDATE tags_final 
SET nsfw_level = 'blocked'
WHERE name IN (
    'loli', 'shota', 'child', 'kid', 'toddler', 'baby',
    'underage', 'young_girl', 'young_boy'
)
AND nsfw_level != 'blocked';

-- ============================================
-- Part 8: 初始化類別映射（基於 danbooru_cat）
-- ============================================

-- 基於現有的 danbooru_cat 和 main_category 設置 category
UPDATE tags_final
SET category = CASE
    -- 角色相關
    WHEN main_category IN ('CHARACTER', 'PERSON') OR name IN ('1girl', '1boy', '2girls', 'solo', 'multiple_girls') 
        THEN 'CHARACTER'
    
    -- 外觀相關
    WHEN main_category IN ('HAIR', 'EYES', 'BODY', 'FACE') OR name LIKE '%_hair' OR name LIKE '%_eyes'
        THEN 'APPEARANCE'
    
    -- 服裝相關
    WHEN main_category IN ('CLOTHING', 'OUTFIT') OR name LIKE '%_dress' OR name LIKE '%_uniform'
        THEN 'CLOTHING'
    
    -- 場景相關
    WHEN main_category IN ('SCENE', 'LOCATION', 'BACKGROUND') OR name IN ('outdoors', 'indoors', 'forest', 'beach', 'city')
        THEN 'SCENE'
    
    -- 風格相關
    WHEN main_category IN ('STYLE', 'ART') OR name LIKE '%_style' OR name LIKE 'anime%'
        THEN 'STYLE'
    
    -- 效果相關
    WHEN main_category IN ('EFFECT', 'LIGHTING') OR name LIKE '%_lighting' OR name LIKE '%_glow'
        THEN 'EFFECT'
    
    -- 動作相關
    WHEN main_category IN ('ACTION', 'POSE') OR name LIKE '%ing' OR name IN ('sitting', 'standing', 'walking', 'running')
        THEN 'ACTION'
    
    -- 情緒/氛圍相關
    WHEN name IN ('smile', 'happy', 'sad', 'angry', 'peaceful', 'dreamy', 'mysterious')
        THEN 'MOOD'
    
    -- 品質相關
    WHEN name IN ('masterpiece', 'best_quality', 'high_quality', 'highly_detailed', 'absurdres', 'highres')
        THEN 'QUALITY'
    
    -- 其他
    ELSE 'META'
END
WHERE category IS NULL;

-- ============================================
-- Part 9: 刷新物化視圖
-- ============================================

SELECT refresh_inspire_materialized_views();

-- ============================================
-- Part 10: 驗證安裝
-- ============================================

-- 檢查統計
DO $$
DECLARE
    total_tags INTEGER;
    safe_tags INTEGER;
    blocked_tags INTEGER;
    popular_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_tags FROM tags_final;
    SELECT COUNT(*) INTO safe_tags FROM tags_final WHERE nsfw_level = 'all-ages';
    SELECT COUNT(*) INTO blocked_tags FROM tags_final WHERE nsfw_level = 'blocked';
    SELECT COUNT(*) INTO popular_count FROM popular_tags;
    
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Inspire Agent 資料庫設置完成';
    RAISE NOTICE '====================================';
    RAISE NOTICE '總標籤數: %', total_tags;
    RAISE NOTICE '安全標籤數: %', safe_tags;
    RAISE NOTICE '封禁標籤數: %', blocked_tags;
    RAISE NOTICE '熱門標籤數: %', popular_count;
    RAISE NOTICE '====================================';
END $$;

