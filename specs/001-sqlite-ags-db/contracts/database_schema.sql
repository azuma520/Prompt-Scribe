-- ============================================================================
-- Supabase 資料庫 Schema
-- 專案: SQLite 遷移至 Supabase (PLAN-2025-004)
-- 建立日期: 2025-10-14
-- 版本: 1.0.0
-- ============================================================================

-- 啟用 pgvector 擴展（向量搜尋）
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- 表1: tags_final （標籤主表）
-- ============================================================================

CREATE TABLE IF NOT EXISTS tags_final (
    -- 主鍵
    id TEXT PRIMARY KEY,
    
    -- 基本資訊
    name TEXT NOT NULL UNIQUE,
    danbooru_cat INTEGER NOT NULL,
    post_count INTEGER NOT NULL DEFAULT 0,
    
    -- 分類資訊
    main_category TEXT,
    sub_category TEXT,
    confidence REAL,
    classification_source TEXT,
    
    -- 時間戳記
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 約束條件
    CONSTRAINT check_danbooru_cat CHECK (danbooru_cat >= 0 AND danbooru_cat <= 5),
    CONSTRAINT check_post_count CHECK (post_count >= 0),
    CONSTRAINT check_confidence CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
    CONSTRAINT check_classification_source CHECK (classification_source IN ('rule', 'llm', 'manual', NULL))
);

-- tags_final 索引
CREATE INDEX idx_tags_main_category 
ON tags_final(main_category)
WHERE main_category IS NOT NULL;

CREATE INDEX idx_tags_sub_category 
ON tags_final(sub_category)
WHERE sub_category IS NOT NULL;

CREATE INDEX idx_tags_post_count 
ON tags_final(post_count DESC);

CREATE INDEX idx_tags_confidence 
ON tags_final(confidence DESC)
WHERE confidence IS NOT NULL;

CREATE INDEX idx_tags_danbooru_cat 
ON tags_final(danbooru_cat);

-- 複合索引（常見查詢模式）
CREATE INDEX idx_tags_category_count 
ON tags_final(main_category, post_count DESC)
WHERE main_category IS NOT NULL;

CREATE INDEX idx_tags_source_confidence 
ON tags_final(classification_source, confidence DESC)
WHERE classification_source IS NOT NULL;

-- 觸發器：自動更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tags_final_updated_at
    BEFORE UPDATE ON tags_final
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 表2: tag_embeddings （向量嵌入表）
-- ============================================================================

CREATE TABLE IF NOT EXISTS tag_embeddings (
    -- 主鍵
    id SERIAL PRIMARY KEY,
    
    -- 外鍵
    tag_name TEXT NOT NULL UNIQUE,
    
    -- 向量資料
    embedding VECTOR(1536) NOT NULL,
    model TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    
    -- 時間戳記
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 外鍵約束
    CONSTRAINT fk_tag_name 
        FOREIGN KEY (tag_name) 
        REFERENCES tags_final(name) 
        ON DELETE CASCADE,
    
    -- 檢查約束
    CONSTRAINT check_model CHECK (model IN ('text-embedding-3-small', 'text-embedding-3-large'))
);

-- tag_embeddings 向量索引
CREATE INDEX idx_tag_embeddings_vector 
ON tag_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================================================
-- 表3: migration_log （遷移日誌表）
-- ============================================================================

CREATE TABLE IF NOT EXISTS migration_log (
    -- 主鍵
    id SERIAL PRIMARY KEY,
    
    -- 遷移資訊
    migration_batch TEXT NOT NULL,
    operation TEXT NOT NULL,
    records_affected INTEGER NOT NULL DEFAULT 0,
    
    -- 狀態資訊
    status TEXT NOT NULL,
    error_message TEXT,
    
    -- 時間資訊
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds REAL,
    
    -- 約束條件
    CONSTRAINT check_status CHECK (status IN ('success', 'failed', 'pending')),
    CONSTRAINT check_records_affected CHECK (records_affected >= 0),
    CONSTRAINT check_duration CHECK (duration_seconds IS NULL OR duration_seconds >= 0)
);

-- migration_log 索引
CREATE INDEX idx_migration_batch 
ON migration_log(migration_batch);

CREATE INDEX idx_migration_status 
ON migration_log(status);

CREATE INDEX idx_migration_time 
ON migration_log(started_at DESC);

-- ============================================================================
-- Row-Level Security (RLS) 策略
-- ============================================================================

-- 啟用 RLS
ALTER TABLE tags_final ENABLE ROW LEVEL SECURITY;
ALTER TABLE tag_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE migration_log ENABLE ROW LEVEL SECURITY;

-- tags_final 策略
CREATE POLICY "Allow anonymous read tags"
ON tags_final FOR SELECT
TO anon
USING (true);

CREATE POLICY "Allow service role full access to tags"
ON tags_final FOR ALL
TO service_role
USING (true);

-- tag_embeddings 策略
CREATE POLICY "Allow authenticated read embeddings"
ON tag_embeddings FOR SELECT
TO authenticated, anon
USING (true);

CREATE POLICY "Allow service role full access to embeddings"
ON tag_embeddings FOR ALL
TO service_role
USING (true);

-- migration_log 策略
CREATE POLICY "Allow service role full access to logs"
ON migration_log FOR ALL
TO service_role
USING (true);

-- ============================================================================
-- RPC 函式: 統計資訊
-- ============================================================================

-- 函式1: 取得分類統計
CREATE OR REPLACE FUNCTION get_category_statistics()
RETURNS TABLE (
    category TEXT,
    tag_count BIGINT,
    percentage NUMERIC,
    avg_confidence NUMERIC,
    total_usage BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        main_category AS category,
        COUNT(*)::BIGINT AS tag_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL), 2) AS percentage,
        ROUND(AVG(confidence)::NUMERIC, 3) AS avg_confidence,
        SUM(post_count)::BIGINT AS total_usage
    FROM tags_final
    WHERE main_category IS NOT NULL
    GROUP BY main_category
    ORDER BY tag_count DESC;
END;
$$ LANGUAGE plpgsql;

-- 函式2: 取得覆蓋率統計
CREATE OR REPLACE FUNCTION get_coverage_stats()
RETURNS TABLE (
    total_tags BIGINT,
    classified_tags BIGINT,
    unclassified_tags BIGINT,
    vectorized_tags BIGINT,
    coverage_rate NUMERIC,
    vectorization_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT AS total_tags,
        COUNT(CASE WHEN main_category IS NOT NULL THEN 1 END)::BIGINT AS classified_tags,
        COUNT(CASE WHEN main_category IS NULL THEN 1 END)::BIGINT AS unclassified_tags,
        (SELECT COUNT(*)::BIGINT FROM tag_embeddings) AS vectorized_tags,
        ROUND(COUNT(CASE WHEN main_category IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) AS coverage_rate,
        ROUND((SELECT COUNT(*) FROM tag_embeddings) * 100.0 / COUNT(*), 2) AS vectorization_rate
    FROM tags_final;
END;
$$ LANGUAGE plpgsql;

-- 函式3: 取得熱門標籤
CREATE OR REPLACE FUNCTION get_top_tags(
    limit_count INTEGER DEFAULT 20,
    category_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    name TEXT,
    main_category TEXT,
    post_count INTEGER,
    confidence REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.name,
        t.main_category,
        t.post_count,
        t.confidence
    FROM tags_final t
    WHERE 
        CASE 
            WHEN category_filter IS NOT NULL THEN t.main_category = category_filter
            ELSE TRUE
        END
    ORDER BY t.post_count DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- RPC 函式: 語意搜尋
-- ============================================================================

-- 函式4: 語意相似度搜尋
CREATE OR REPLACE FUNCTION search_similar_tags(
    query_embedding VECTOR(1536),
    match_threshold REAL DEFAULT 0.7,
    match_count INTEGER DEFAULT 10,
    category_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    tag_name TEXT,
    similarity REAL,
    main_category TEXT,
    post_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.tag_name,
        (1 - (e.embedding <=> query_embedding))::REAL AS similarity,
        t.main_category,
        t.post_count
    FROM tag_embeddings e
    JOIN tags_final t ON e.tag_name = t.name
    WHERE 
        (1 - (e.embedding <=> query_embedding)) > match_threshold
        AND (
            CASE 
                WHEN category_filter IS NOT NULL THEN t.main_category = category_filter
                ELSE TRUE
            END
        )
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- 函式5: 文字轉向量搜尋（輔助函式，需要前端先呼叫 OpenAI API）
CREATE OR REPLACE FUNCTION search_tags_by_text(
    search_query TEXT,
    category_filter TEXT DEFAULT NULL,
    min_confidence REAL DEFAULT 0.0,
    limit_count INTEGER DEFAULT 20
)
RETURNS TABLE (
    name TEXT,
    main_category TEXT,
    sub_category TEXT,
    post_count INTEGER,
    confidence REAL
) AS $$
BEGIN
    -- 文字搜尋（模糊比對）
    RETURN QUERY
    SELECT 
        t.name,
        t.main_category,
        t.sub_category,
        t.post_count,
        t.confidence
    FROM tags_final t
    WHERE 
        t.name ILIKE '%' || search_query || '%'
        AND (
            CASE 
                WHEN category_filter IS NOT NULL THEN t.main_category = category_filter
                ELSE TRUE
            END
        )
        AND (
            CASE 
                WHEN t.confidence IS NOT NULL THEN t.confidence >= min_confidence
                ELSE TRUE
            END
        )
    ORDER BY t.post_count DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 資料驗證函式
-- ============================================================================

-- 函式6: 檢查資料完整性
CREATE OR REPLACE FUNCTION check_data_integrity()
RETURNS TABLE (
    check_name TEXT,
    result TEXT,
    details TEXT
) AS $$
DECLARE
    total_tags INTEGER;
    total_embeddings INTEGER;
    orphaned_embeddings INTEGER;
    null_categories INTEGER;
BEGIN
    -- 取得基本統計
    SELECT COUNT(*) INTO total_tags FROM tags_final;
    SELECT COUNT(*) INTO total_embeddings FROM tag_embeddings;
    
    -- 檢查孤立的嵌入
    SELECT COUNT(*) INTO orphaned_embeddings 
    FROM tag_embeddings e 
    LEFT JOIN tags_final t ON e.tag_name = t.name 
    WHERE t.name IS NULL;
    
    -- 檢查未分類的標籤
    SELECT COUNT(*) INTO null_categories 
    FROM tags_final 
    WHERE main_category IS NULL;
    
    -- 返回檢查結果
    RETURN QUERY
    SELECT 
        'Total Tags'::TEXT,
        CASE WHEN total_tags = 140782 THEN 'PASS' ELSE 'FAIL' END,
        total_tags::TEXT;
    
    RETURN QUERY
    SELECT 
        'Total Embeddings'::TEXT,
        CASE WHEN total_embeddings >= total_tags * 0.99 THEN 'PASS' ELSE 'WARN' END,
        total_embeddings::TEXT;
    
    RETURN QUERY
    SELECT 
        'Orphaned Embeddings'::TEXT,
        CASE WHEN orphaned_embeddings = 0 THEN 'PASS' ELSE 'FAIL' END,
        orphaned_embeddings::TEXT;
    
    RETURN QUERY
    SELECT 
        'Unclassified Tags'::TEXT,
        CASE WHEN null_categories < total_tags * 0.10 THEN 'PASS' ELSE 'WARN' END,
        null_categories::TEXT;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 初始化完成
-- ============================================================================

-- 插入初始化日誌
INSERT INTO migration_log (
    migration_batch,
    operation,
    records_affected,
    status,
    started_at,
    completed_at
) VALUES (
    'schema_setup',
    'create_schema',
    0,
    'success',
    NOW(),
    NOW()
);

-- 顯示版本資訊
SELECT 'Supabase Schema v1.0.0 initialized successfully' AS message;

