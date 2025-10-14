-- ============================================================================
-- Script 4: Row-Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE tags_final ENABLE ROW LEVEL SECURITY;
ALTER TABLE tag_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE migration_log ENABLE ROW LEVEL SECURITY;

-- Policies for tags_final table
CREATE POLICY "Allow anonymous read tags"
ON tags_final FOR SELECT
TO anon
USING (true);

CREATE POLICY "Allow service role full access to tags"
ON tags_final FOR ALL
TO service_role
USING (true);

-- Policies for tag_embeddings table
CREATE POLICY "Allow authenticated read embeddings"
ON tag_embeddings FOR SELECT
TO authenticated, anon
USING (true);

CREATE POLICY "Allow service role full access to embeddings"
ON tag_embeddings FOR ALL
TO service_role
USING (true);

-- Policies for migration_log table
CREATE POLICY "Allow service role full access to logs"
ON migration_log FOR ALL
TO service_role
USING (true);

