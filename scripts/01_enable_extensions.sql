-- ============================================================================
-- Script 1: Enable Extensions
-- ============================================================================

-- Enable pgvector extension for vector search
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is enabled
SELECT extname, extversion 
FROM pg_extension 
WHERE extname = 'vector';

