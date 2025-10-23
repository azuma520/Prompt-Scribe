-- ============================================================================
-- Script 11: Add conversation tracking fields to inspire_sessions
-- 支持 Responses API 的對話狀態追蹤
-- ============================================================================

-- 添加對話相關欄位到 inspire_sessions
DO $$ 
BEGIN
    -- 添加 last_response_id 欄位
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'last_response_id'
    ) THEN
        ALTER TABLE inspire_sessions 
        ADD COLUMN last_response_id TEXT;
        
        COMMENT ON COLUMN inspire_sessions.last_response_id IS 
            'OpenAI Responses API 的最後一個 response ID (用於 previous_response_id)';
        
        RAISE NOTICE '✅ 已添加 last_response_id 欄位';
    ELSE
        RAISE NOTICE '⚠️ last_response_id 欄位已存在，跳過';
    END IF;

    -- 添加 last_user_message 欄位
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'last_user_message'
    ) THEN
        ALTER TABLE inspire_sessions 
        ADD COLUMN last_user_message TEXT;
        
        COMMENT ON COLUMN inspire_sessions.last_user_message IS 
            '用戶的最後一條訊息內容';
        
        RAISE NOTICE '✅ 已添加 last_user_message 欄位';
    ELSE
        RAISE NOTICE '⚠️ last_user_message 欄位已存在，跳過';
    END IF;

    -- 添加 last_agent_message 欄位
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'last_agent_message'
    ) THEN
        ALTER TABLE inspire_sessions 
        ADD COLUMN last_agent_message TEXT;
        
        COMMENT ON COLUMN inspire_sessions.last_agent_message IS 
            'Agent 的最後一條回應內容';
        
        RAISE NOTICE '✅ 已添加 last_agent_message 欄位';
    ELSE
        RAISE NOTICE '⚠️ last_agent_message 欄位已存在，跳過';
    END IF;

    -- 添加 turn_count 欄位
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'turn_count'
    ) THEN
        ALTER TABLE inspire_sessions 
        ADD COLUMN turn_count INTEGER DEFAULT 0;
        
        COMMENT ON COLUMN inspire_sessions.turn_count IS 
            '對話回合數（用於追蹤對話進度）';
        
        RAISE NOTICE '✅ 已添加 turn_count 欄位';
    ELSE
        RAISE NOTICE '⚠️ turn_count 欄位已存在，跳過';
    END IF;
END $$;

-- 創建索引（可選，用於查詢優化）
CREATE INDEX IF NOT EXISTS idx_sessions_last_response 
    ON inspire_sessions(last_response_id)
    WHERE last_response_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_sessions_turn_count 
    ON inspire_sessions(turn_count);

-- 驗證
DO $$
DECLARE
    last_response_id_exists BOOLEAN;
    last_user_message_exists BOOLEAN;
    last_agent_message_exists BOOLEAN;
    turn_count_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'last_response_id'
    ) INTO last_response_id_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'last_user_message'
    ) INTO last_user_message_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'last_agent_message'
    ) INTO last_agent_message_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inspire_sessions' 
        AND column_name = 'turn_count'
    ) INTO turn_count_exists;
    
    IF last_response_id_exists AND last_user_message_exists 
       AND last_agent_message_exists AND turn_count_exists THEN
        RAISE NOTICE '====================================';
        RAISE NOTICE '✅ Migration 完成';
        RAISE NOTICE '====================================';
        RAISE NOTICE 'inspire_sessions 新增欄位：';
        RAISE NOTICE '  - last_response_id (TEXT)';
        RAISE NOTICE '  - last_user_message (TEXT)';
        RAISE NOTICE '  - last_agent_message (TEXT)';
        RAISE NOTICE '  - turn_count (INTEGER)';
        RAISE NOTICE '====================================';
    ELSE
        RAISE EXCEPTION '❌ Migration 失敗: 部分欄位未創建成功';
    END IF;
END $$;

