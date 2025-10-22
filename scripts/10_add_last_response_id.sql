-- ============================================================================
-- Script 10: Add last_response_id to inspire_sessions
-- 支持 Responses API 的 previous_response_id 功能
-- ============================================================================

-- 添加 last_response_id 欄位到 inspire_sessions
DO $$ 
BEGIN
    -- 檢查欄位是否已存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'last_response_id'
    ) THEN
        -- 添加欄位
        ALTER TABLE inspire_sessions 
        ADD COLUMN last_response_id TEXT;
        
        -- 添加註解
        COMMENT ON COLUMN inspire_sessions.last_response_id IS 
            'OpenAI Responses API 的最後一個 response ID (用於 previous_response_id)';
        
        RAISE NOTICE '✅ 已添加 last_response_id 欄位到 inspire_sessions';
    ELSE
        RAISE NOTICE '⚠️ last_response_id 欄位已存在，跳過';
    END IF;
END $$;

-- 創建索引（可選，用於查詢優化）
CREATE INDEX IF NOT EXISTS idx_sessions_last_response 
    ON inspire_sessions(last_response_id)
    WHERE last_response_id IS NOT NULL;

-- 驗證
DO $$
DECLARE
    column_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'last_response_id'
    ) INTO column_exists;
    
    IF column_exists THEN
        RAISE NOTICE '====================================';
        RAISE NOTICE '✅ Migration 完成';
        RAISE NOTICE '====================================';
        RAISE NOTICE 'inspire_sessions.last_response_id 欄位已就緒';
        RAISE NOTICE '====================================';
    ELSE
        RAISE EXCEPTION '❌ Migration 失敗: last_response_id 欄位未創建';
    END IF;
END $$;

