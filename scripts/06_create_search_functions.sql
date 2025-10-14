-- ============================================================================
-- Script 6: RPC Functions (Part 2: Search Functions)
-- ============================================================================

-- Function 4: Semantic similarity search
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
        AND (category_filter IS NULL OR t.main_category = category_filter)
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Function 5: Text search tags
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
        AND (category_filter IS NULL OR t.main_category = category_filter)
        AND (t.confidence IS NULL OR t.confidence >= min_confidence)
    ORDER BY t.post_count DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function 6: Check data integrity
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
    -- Get basic statistics
    SELECT COUNT(*) INTO total_tags FROM tags_final;
    SELECT COUNT(*) INTO total_embeddings FROM tag_embeddings;
    
    -- Check orphaned embeddings
    SELECT COUNT(*) INTO orphaned_embeddings 
    FROM tag_embeddings e 
    LEFT JOIN tags_final t ON e.tag_name = t.name 
    WHERE t.name IS NULL;
    
    -- Check unclassified tags
    SELECT COUNT(*) INTO null_categories 
    FROM tags_final 
    WHERE main_category IS NULL;
    
    -- Return check results
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

