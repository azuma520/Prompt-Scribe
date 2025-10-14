-- ============================================================================
-- 第二部分：建立索引
-- ============================================================================

-- tags_final 索引
CREATE INDEX IF NOT EXISTS idx_tags_main_category 
ON tags_final(main_category)
WHERE main_category IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tags_sub_category 
ON tags_final(sub_category)
WHERE sub_category IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tags_post_count 
ON tags_final(post_count DESC);

CREATE INDEX IF NOT EXISTS idx_tags_confidence 
ON tags_final(confidence DESC)
WHERE confidence IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tags_danbooru_cat 
ON tags_final(danbooru_cat);

-- 複合索引（常見查詢模式）
CREATE INDEX IF NOT EXISTS idx_tags_category_count 
ON tags_final(main_category, post_count DESC)
WHERE main_category IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tags_source_confidence 
ON tags_final(classification_source, confidence DESC)
WHERE classification_source IS NOT NULL;

-- tag_embeddings 向量索引
CREATE INDEX IF NOT EXISTS idx_tag_embeddings_vector 
ON tag_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- migration_log 索引
CREATE INDEX IF NOT EXISTS idx_migration_batch 
ON migration_log(migration_batch);

CREATE INDEX IF NOT EXISTS idx_migration_status 
ON migration_log(status);

CREATE INDEX IF NOT EXISTS idx_migration_time 
ON migration_log(started_at DESC);
