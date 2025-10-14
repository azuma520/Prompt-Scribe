-- ============================================================================
-- Script 2: Create Tables
-- ============================================================================

-- Table 1: tags_final (Main tags table)
CREATE TABLE IF NOT EXISTS tags_final (
    -- Primary key
    id TEXT PRIMARY KEY,
    
    -- Basic information
    name TEXT NOT NULL UNIQUE,
    danbooru_cat INTEGER NOT NULL,
    post_count INTEGER NOT NULL DEFAULT 0,
    
    -- Classification information
    main_category TEXT,
    sub_category TEXT,
    confidence REAL,
    classification_source TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_danbooru_cat CHECK (danbooru_cat >= 0 AND danbooru_cat <= 5),
    CONSTRAINT check_post_count CHECK (post_count >= 0),
    CONSTRAINT check_confidence CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
    CONSTRAINT check_classification_source CHECK (classification_source IN ('rule', 'llm', 'manual', NULL))
);

-- Table 2: tag_embeddings (Vector embeddings table)
CREATE TABLE IF NOT EXISTS tag_embeddings (
    -- Primary key
    id SERIAL PRIMARY KEY,
    
    -- Foreign key to tags_final
    tag_name TEXT NOT NULL UNIQUE,
    
    -- Vector embedding
    embedding VECTOR(1536) NOT NULL,
    
    -- Model information
    model TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_tag_embeddings_tag_name 
        FOREIGN KEY (tag_name) 
        REFERENCES tags_final(name) 
        ON DELETE CASCADE
);

-- Table 3: migration_log (Migration log table)
CREATE TABLE IF NOT EXISTS migration_log (
    -- Primary key
    id SERIAL PRIMARY KEY,
    
    -- Migration information
    migration_batch TEXT NOT NULL,
    operation TEXT NOT NULL,
    records_affected INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    error_message TEXT,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds REAL,
    
    -- Constraints
    CONSTRAINT check_status CHECK (status IN ('success', 'failed', 'pending')),
    CONSTRAINT check_records_affected CHECK (records_affected >= 0),
    CONSTRAINT check_duration CHECK (duration_seconds IS NULL OR duration_seconds >= 0)
);

