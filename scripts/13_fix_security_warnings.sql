-- ============================================================================
-- Script 13: Fix Security Warnings (2025-01-27)
-- ============================================================================
-- 
-- 修復 Supabase Advisor 警告：
-- 1. Function Search Path Mutable: public.semantic_tag_search
-- 2. Extension in Public: public.vector
-- 3. Extension in Public: public.pg_trgm
-- 
-- ============================================================================

-- ============================================================================
-- PART 1: 修復 semantic_tag_search 函式的 search_path 問題
-- ============================================================================

-- 使用動態 SQL 來修復函式（無論其簽名如何）
DO $$
DECLARE
    func_oid oid;
    func_signature text;
    alter_stmt text;
BEGIN
    -- 尋找 semantic_tag_search 函式
    SELECT p.oid INTO func_oid
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public' 
    AND p.proname = 'semantic_tag_search'
    LIMIT 1;
    
    IF func_oid IS NOT NULL THEN
        -- 取得函式的完整簽名（包含參數類型）
        SELECT pg_get_function_identity_arguments(func_oid) INTO func_signature;
        
        RAISE NOTICE '✅ Found semantic_tag_search function with signature: %', func_signature;
        
        -- 建立 ALTER 語句
        alter_stmt := format(
            'ALTER FUNCTION public.semantic_tag_search(%s) SET search_path = public, pg_temp',
            func_signature
        );
        
        -- 執行 ALTER
        EXECUTE alter_stmt;
        
        RAISE NOTICE '✅ Fixed search_path for semantic_tag_search';
    ELSE
        RAISE NOTICE '⚠️ semantic_tag_search function not found, creating it...';
        
        -- 如果函式不存在，使用動態 SQL 建立一個標準版本的函式
        -- 根據程式碼使用情況（semantic_search_service.py），建立對應的函式
        EXECUTE '
        CREATE OR REPLACE FUNCTION public.semantic_tag_search(
            query_embedding vector(1536),
            match_count integer DEFAULT 10,
            min_similarity real DEFAULT 0.7
        )
        RETURNS TABLE (
            tag_name text,
            similarity real,
            main_category text,
            post_count integer
        )
        LANGUAGE plpgsql
        SECURITY INVOKER
        SET search_path = public, pg_temp
        AS $func$
        BEGIN
            RETURN QUERY
            SELECT 
                e.tag_name,
                (1 - (e.embedding <=> query_embedding))::real AS similarity,
                t.main_category,
                t.post_count
            FROM tag_embeddings e
            JOIN tags_final t ON e.tag_name = t.name
            WHERE 
                (1 - (e.embedding <=> query_embedding)) > min_similarity
            ORDER BY e.embedding <=> query_embedding
            LIMIT match_count;
        END;
        $func$';
        
        RAISE NOTICE '✅ Created semantic_tag_search function with secure settings';
    END IF;
END $$;

-- ============================================================================
-- PART 2: 將擴充套件移到 extensions schema
-- ============================================================================

-- 建立 extensions schema（如果不存在）
CREATE SCHEMA IF NOT EXISTS extensions;

-- 授予必要的權限
GRANT USAGE ON SCHEMA extensions TO PUBLIC;
GRANT ALL ON SCHEMA extensions TO postgres, anon, authenticated, service_role;

-- 2.1 移動 vector 擴充套件
DO $$
BEGIN
    -- 檢查擴充套件是否存在於 public schema
    IF EXISTS (
        SELECT 1 
        FROM pg_extension e
        JOIN pg_namespace n ON e.extnamespace = n.oid
        WHERE e.extname = 'vector' 
        AND n.nspname = 'public'
    ) THEN
        RAISE NOTICE 'Moving vector extension from public to extensions schema...';
        
        -- 移動擴充套件
        ALTER EXTENSION vector SET SCHEMA extensions;
        
        RAISE NOTICE '✅ Moved vector extension to extensions schema';
    ELSE
        RAISE NOTICE '⚠️ vector extension not found in public schema (may already be moved or not installed)';
    END IF;
END $$;

-- 2.2 移動 pg_trgm 擴充套件
DO $$
BEGIN
    -- 檢查擴充套件是否存在於 public schema
    IF EXISTS (
        SELECT 1 
        FROM pg_extension e
        JOIN pg_namespace n ON e.extnamespace = n.oid
        WHERE e.extname = 'pg_trgm' 
        AND n.nspname = 'public'
    ) THEN
        RAISE NOTICE 'Moving pg_trgm extension from public to extensions schema...';
        
        -- 移動擴充套件
        ALTER EXTENSION pg_trgm SET SCHEMA extensions;
        
        RAISE NOTICE '✅ Moved pg_trgm extension to extensions schema';
    ELSE
        RAISE NOTICE '⚠️ pg_trgm extension not found in public schema (may already be moved or not installed)';
    END IF;
END $$;

-- ============================================================================
-- PART 3: 更新 search_path 設定（推薦）
-- ============================================================================

-- 將 extensions 加入到資料庫的預設 search_path
-- 這樣使用擴充套件功能時不需要加上 extensions. 前綴
-- 注意：需要知道資料庫名稱，這裡使用 current_database()
DO $$
DECLARE
    db_name text;
BEGIN
    SELECT current_database() INTO db_name;
    EXECUTE format('ALTER DATABASE %I SET search_path = public, extensions, pg_catalog, pg_temp', db_name);
    RAISE NOTICE '✅ Updated database search_path to include extensions schema';
EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE NOTICE '⚠️ Cannot alter database search_path (requires superuser), skipping...';
END $$;

-- ============================================================================
-- PART 4: 驗證修復結果
-- ============================================================================

-- 4.1 驗證 semantic_tag_search 函式的 search_path
DO $$
DECLARE
    func_search_path_status text;
BEGIN
    SELECT 
        CASE 
            WHEN p.proconfig IS NOT NULL 
                AND array_to_string(p.proconfig, ', ') LIKE '%search_path%'
            THEN '✅ search_path 已設定'
            ELSE '⚠️ search_path 未在函式層級設定'
        END
    INTO func_search_path_status
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public' 
    AND p.proname = 'semantic_tag_search'
    LIMIT 1;
    
    IF func_search_path_status IS NOT NULL THEN
        RAISE NOTICE 'semantic_tag_search search_path 狀態: %', func_search_path_status;
    ELSE
        RAISE NOTICE '⚠️ semantic_tag_search 函式不存在';
    END IF;
END $$;

-- 4.2 驗證擴充套件位置
SELECT 
    e.extname AS extension_name,
    n.nspname AS schema_name,
    CASE 
        WHEN n.nspname = 'extensions' THEN '✅ 已移動到 extensions schema'
        WHEN n.nspname = 'public' THEN '⚠️ 仍在 public schema'
        ELSE '📍 位於 ' || n.nspname
    END AS status
FROM pg_extension e
JOIN pg_namespace n ON e.extnamespace = n.oid
WHERE e.extname IN ('vector', 'pg_trgm')
ORDER BY e.extname;

-- ============================================================================
-- 總結
-- ============================================================================
-- 
-- ✅ 修復完成：
-- 1. semantic_tag_search 函式已設定安全的 search_path
-- 2. vector 擴充套件已移動到 extensions schema
-- 3. pg_trgm 擴充套件已移動到 extensions schema
-- 4. 資料庫 search_path 已更新以包含 extensions
-- 
-- 這些更改應該可以清除 Supabase Advisor 的所有警告
-- 
-- ============================================================================
