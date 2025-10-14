-- ============================================================================
-- 第一部分：建立基本表和擴展
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
    'create_tables',
    0,
    'success',
    NOW(),
    NOW()
);
