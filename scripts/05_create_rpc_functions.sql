-- ============================================================================
-- Script 5: RPC Functions (Part 1: Statistics)
-- ============================================================================

-- Function 1: Get category statistics
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

-- Function 2: Get coverage statistics
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

-- Function 3: Get top tags
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

