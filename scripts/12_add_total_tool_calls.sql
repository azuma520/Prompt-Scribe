-- ============================================================================
-- Script 12: Add total_tool_calls to inspire_sessions (schema alignment)
-- 將資料庫 schema 與程式欄位對齊，避免 PGRST204（欄位不存在）
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'inspire_sessions' AND column_name = 'total_tool_calls'
    ) THEN
        ALTER TABLE inspire_sessions
        ADD COLUMN total_tool_calls INTEGER NOT NULL DEFAULT 0;

        COMMENT ON COLUMN inspire_sessions.total_tool_calls IS '工具呼叫總次數（對齊程式的寫入欄位）';
        RAISE NOTICE '✅ 已添加 total_tool_calls 欄位到 inspire_sessions';
    ELSE
        RAISE NOTICE '⚠️ total_tool_calls 已存在，跳過';
    END IF;
END $$;
