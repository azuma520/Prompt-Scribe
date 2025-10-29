-- ============================================================================
-- Setup Vector Extensions and Embedding Column
-- 設定向量擴充套件和嵌入欄位
-- ============================================================================

-- 1. Enable pgvector extension for vector search
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Enable pg_trgm extension for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 3. Add embedding column to tags_final table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tags_final' AND column_name = 'embedding'
    ) THEN
        ALTER TABLE tags_final
        ADD COLUMN embedding vector(1536); -- OpenAI text-embedding-3-small has 1536 dimensions
        
        COMMENT ON COLUMN tags_final.embedding IS 'OpenAI text-embedding-3-small vector representation';
        RAISE NOTICE 'Added embedding column to tags_final table';
    ELSE
        RAISE NOTICE 'embedding column already exists, skipping';
    END IF;
END $$;

-- 4. Create GIN index on name column for fuzzy search (two-stage search stage 1)
CREATE INDEX IF NOT EXISTS idx_tags_name_gin 
ON tags_final 
USING gin(name gin_trgm_ops);

-- 5. Create vector index for embedding similarity search
CREATE INDEX IF NOT EXISTS idx_tags_embedding_vector 
ON tags_final 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 6. Verify extensions are enabled
SELECT extname, extversion 
FROM pg_extension 
WHERE extname IN ('vector', 'pg_trgm');

-- 7. Show table structure
\d tags_final;

