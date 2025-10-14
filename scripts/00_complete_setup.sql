-- ============================================================================
-- Complete Database Setup Script
-- Optimized for Supabase Dashboard SQL Editor
-- Project: SQLite Migration to Supabase (PLAN-2025-004)
-- ============================================================================

-- Step 1: Enable Extensions
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create Tables
-- ============================================================================

-- Table 1: tags_final
CREATE TABLE IF NOT EXISTS tags_final (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    danbooru_cat INTEGER NOT NULL,
    post_count INTEGER NOT NULL DEFAULT 0,
    main_category TEXT,
    sub_category TEXT,
    confidence REAL,
    classification_source TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_danbooru_cat CHECK (danbooru_cat >= 0 AND danbooru_cat <= 5),
    CONSTRAINT check_post_count CHECK (post_count >= 0),
    CONSTRAINT check_confidence CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
    CONSTRAINT check_classification_source CHECK (classification_source IN ('rule', 'llm', 'manual', NULL))
);

-- Table 2: tag_embeddings
CREATE TABLE IF NOT EXISTS tag_embeddings (
    id SERIAL PRIMARY KEY,
    tag_name TEXT NOT NULL UNIQUE,
    embedding VECTOR(1536) NOT NULL,
    model TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_tag_embeddings_tag_name 
        FOREIGN KEY (tag_name) 
        REFERENCES tags_final(name) 
        ON DELETE CASCADE
);

-- Table 3: migration_log
CREATE TABLE IF NOT EXISTS migration_log (
    id SERIAL PRIMARY KEY,
    migration_batch TEXT NOT NULL,
    operation TEXT NOT NULL,
    records_affected INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds REAL,
    CONSTRAINT check_status CHECK (status IN ('success', 'failed', 'pending')),
    CONSTRAINT check_records_affected CHECK (records_affected >= 0),
    CONSTRAINT check_duration CHECK (duration_seconds IS NULL OR duration_seconds >= 0)
);

-- Step 3: Create Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_tags_main_category ON tags_final(main_category) WHERE main_category IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tags_sub_category ON tags_final(sub_category) WHERE sub_category IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tags_post_count ON tags_final(post_count DESC);
CREATE INDEX IF NOT EXISTS idx_tags_confidence ON tags_final(confidence DESC) WHERE confidence IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tags_danbooru_cat ON tags_final(danbooru_cat);
CREATE INDEX IF NOT EXISTS idx_tags_category_count ON tags_final(main_category, post_count DESC) WHERE main_category IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tags_source_confidence ON tags_final(classification_source, confidence DESC) WHERE classification_source IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tag_embeddings_vector ON tag_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_migration_batch ON migration_log(migration_batch);
CREATE INDEX IF NOT EXISTS idx_migration_status ON migration_log(status);
CREATE INDEX IF NOT EXISTS idx_migration_time ON migration_log(started_at DESC);

-- Step 4: Enable RLS and Create Policies
-- ============================================================================

ALTER TABLE tags_final ENABLE ROW LEVEL SECURITY;
ALTER TABLE tag_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE migration_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous read tags" ON tags_final FOR SELECT TO anon USING (true);
CREATE POLICY "Allow service role full access to tags" ON tags_final FOR ALL TO service_role USING (true);
CREATE POLICY "Allow authenticated read embeddings" ON tag_embeddings FOR SELECT TO authenticated, anon USING (true);
CREATE POLICY "Allow service role full access to embeddings" ON tag_embeddings FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access to logs" ON migration_log FOR ALL TO service_role USING (true);

-- Step 5: Create RPC Functions
-- ============================================================================

-- Success message
SELECT 'Database setup completed successfully!' AS message;

