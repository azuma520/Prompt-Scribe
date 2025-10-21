-- ============================================================================
-- Inspire Agent Minimal Migration
-- 策略 A：最小改動，只創建必要的新表
-- 
-- 原則：
-- 1. 不修改現有 tags_final 表（零風險）
-- 2. 只創建 inspire_sessions 表（業務資料）
-- 3. 所有映射和規則在應用層（程式碼）
-- ============================================================================

-- ============================================
-- 新表：inspire_sessions（唯一的 Schema 變更）
-- ============================================

CREATE TABLE IF NOT EXISTS inspire_sessions (
    -- 主鍵
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    
    -- 狀態機
    current_phase TEXT NOT NULL DEFAULT 'understanding'
        CHECK (current_phase IN (
            'understanding', 'exploring', 'refining', 
            'finalizing', 'completed', 'aborted'
        )),
    
    -- 使用者權限（支援付費分級）
    user_access_level TEXT NOT NULL DEFAULT 'all-ages'
        CHECK (user_access_level IN (
            'all-ages',  -- 免費用戶
            'r15',       -- 年齡驗證
            'r18'        -- 付費 + 年齡驗證
        )),
    
    -- 業務資料（JSONB 靈活存儲）
    extracted_intent JSONB,
    generated_directions JSONB,
    selected_direction_index INTEGER,
    final_output JSONB,
    
    -- 追蹤與控制
    total_cost DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    tool_call_count JSONB NOT NULL DEFAULT '{}'::jsonb,
    abort_reason TEXT,
    
    -- 品質與反饋
    quality_score INTEGER,
    user_satisfaction INTEGER,
    user_feedback TEXT,
    
    -- 時間戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- 約束
    CONSTRAINT check_quality_score CHECK (quality_score IS NULL OR (quality_score BETWEEN 0 AND 100)),
    CONSTRAINT check_satisfaction CHECK (user_satisfaction IS NULL OR (user_satisfaction BETWEEN 1 AND 5)),
    CONSTRAINT check_cost CHECK (total_cost >= 0),
    CONSTRAINT check_tokens CHECK (total_tokens >= 0)
);

COMMENT ON TABLE inspire_sessions IS 'Inspire Agent 對話 Session 業務資料（支援付費分級）';
COMMENT ON COLUMN inspire_sessions.user_access_level IS '使用者內容權限：all-ages(免費) | r15(年齡驗證) | r18(付費)';

-- 索引
CREATE INDEX IF NOT EXISTS idx_inspire_sessions_user 
    ON inspire_sessions(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_inspire_sessions_phase 
    ON inspire_sessions(current_phase);

CREATE INDEX IF NOT EXISTS idx_inspire_sessions_quality 
    ON inspire_sessions(quality_score);

CREATE INDEX IF NOT EXISTS idx_inspire_sessions_created 
    ON inspire_sessions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_inspire_sessions_access_level 
    ON inspire_sessions(user_access_level);

-- ============================================
-- 完成！沒有其他 Schema 變更
-- ============================================

-- 驗證安裝
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Inspire Agent Minimal Migration Complete';
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Created tables:';
    RAISE NOTICE '  - inspire_sessions';
    RAISE NOTICE '';
    RAISE NOTICE 'Existing tables unchanged:';
    RAISE NOTICE '  - tags_final (140K+ tags)';
    RAISE NOTICE '  - tag_embeddings';
    RAISE NOTICE '';
    RAISE NOTICE 'All mapping and rules in app layer (Python code)';
    RAISE NOTICE '====================================';
END $$;

