-- =====================================================
-- Prompt-Scribe Inspire 資料庫 Schema
-- 版本: 1.0.0
-- 更新日期: 2025-10-17
-- 描述: Inspire 功能所需的資料表結構
-- =====================================================

-- =====================================================
-- 1. 啟用必要的擴展
-- =====================================================

-- UUID 支援
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 時間戳支援
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- 2. 核心資料表
-- =====================================================

-- -----------------------------------------------------
-- 2.1 inspire_sessions（Session 管理）
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS inspire_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID UNIQUE NOT NULL,
    
    -- Session 狀態
    mode VARCHAR(20) CHECK (mode IN ('emotion', 'theme')),
    current_round INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    
    -- 統計資訊
    total_rounds INTEGER DEFAULT 0,
    total_cards_generated INTEGER DEFAULT 0,
    total_feedbacks INTEGER DEFAULT 0,
    finalized BOOLEAN DEFAULT FALSE,
    
    -- 使用者資訊（匿名）
    client_id VARCHAR(100),
    user_agent TEXT,
    viewport_width INTEGER,
    
    -- 時間戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- 計算欄位
    duration_seconds INTEGER,
    
    -- 索引提示
    CONSTRAINT valid_round CHECK (current_round >= 1),
    CONSTRAINT valid_stats CHECK (
        total_rounds >= 0 AND 
        total_cards_generated >= 0 AND 
        total_feedbacks >= 0
    )
);

-- 索引
CREATE INDEX idx_inspire_sessions_session_id ON inspire_sessions(session_id);
CREATE INDEX idx_inspire_sessions_status ON inspire_sessions(status);
CREATE INDEX idx_inspire_sessions_created_at ON inspire_sessions(created_at DESC);
CREATE INDEX idx_inspire_sessions_client_id ON inspire_sessions(client_id);

-- -----------------------------------------------------
-- 2.2 inspire_rounds（對話輪次記錄）
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS inspire_rounds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES inspire_sessions(session_id) ON DELETE CASCADE,
    
    -- 輪次資訊
    round_number INTEGER NOT NULL,
    mode VARCHAR(20) CHECK (mode IN ('emotion', 'theme')),
    
    -- 輸入
    user_input TEXT NOT NULL,
    
    -- 輸出
    cards_generated JSONB NOT NULL,  -- 儲存為 JSON 陣列
    cards_count INTEGER DEFAULT 3,
    
    -- 使用者互動
    selected_card_index INTEGER,
    selected_card JSONB,
    feedback_text TEXT,
    
    -- 技術指標
    model_used VARCHAR(100),
    latency_ms INTEGER,
    cost_usd DECIMAL(10, 6),
    
    -- SQL 查詢資訊
    sql_queries_count INTEGER DEFAULT 0,
    tags_used TEXT[],
    
    -- 時間戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 約束
    CONSTRAINT valid_round_number CHECK (round_number >= 1),
    CONSTRAINT valid_cards_count CHECK (cards_count >= 1 AND cards_count <= 5),
    CONSTRAINT valid_selected_index CHECK (
        selected_card_index IS NULL OR 
        (selected_card_index >= 0 AND selected_card_index < cards_count)
    )
);

-- 索引
CREATE INDEX idx_inspire_rounds_session_id ON inspire_rounds(session_id);
CREATE INDEX idx_inspire_rounds_round_number ON inspire_rounds(round_number);
CREATE INDEX idx_inspire_rounds_created_at ON inspire_rounds(created_at DESC);
CREATE INDEX idx_inspire_rounds_tags_used ON inspire_rounds USING GIN (tags_used);

-- -----------------------------------------------------
-- 2.3 inspire_generation_logs（生成日誌）
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS inspire_generation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES inspire_sessions(session_id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL,
    
    -- 輸入資訊
    user_input TEXT NOT NULL,
    mode VARCHAR(20),
    
    -- 生成結果
    cards_count INTEGER,
    cards_data JSONB,
    
    -- 技術指標
    model VARCHAR(100),
    latency_ms INTEGER,
    cost_usd DECIMAL(10, 6),
    
    -- SQL 相關
    sql_queries INTEGER DEFAULT 0,
    tags_used TEXT[],
    
    -- 錯誤資訊（如有）
    error_occurred BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_generation_logs_session_id ON inspire_generation_logs(session_id);
CREATE INDEX idx_generation_logs_created_at ON inspire_generation_logs(created_at DESC);
CREATE INDEX idx_generation_logs_model ON inspire_generation_logs(model);

-- -----------------------------------------------------
-- 2.4 inspire_usage_logs（使用日誌）
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS inspire_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id VARCHAR(100) NOT NULL,
    session_id UUID NOT NULL,
    
    -- 行為統計
    total_rounds INTEGER DEFAULT 0,
    total_cards_generated INTEGER DEFAULT 0,
    total_feedbacks INTEGER DEFAULT 0,
    finalized BOOLEAN DEFAULT FALSE,
    
    -- 時間分析
    session_duration_seconds INTEGER,
    time_to_first_card_seconds INTEGER,
    time_to_finalize_seconds INTEGER,
    
    -- 裝置資訊
    user_agent TEXT,
    viewport_width INTEGER,
    device_type VARCHAR(20),  -- 'desktop', 'tablet', 'mobile'
    
    -- 地理資訊（可選）
    country_code VARCHAR(2),
    timezone VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_usage_logs_client_id ON inspire_usage_logs(client_id);
CREATE INDEX idx_usage_logs_session_id ON inspire_usage_logs(session_id);
CREATE INDEX idx_usage_logs_created_at ON inspire_usage_logs(created_at DESC);
CREATE INDEX idx_usage_logs_finalized ON inspire_usage_logs(finalized);

-- -----------------------------------------------------
-- 2.5 inspire_feedback_logs（反饋日誌）
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS inspire_feedback_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES inspire_sessions(session_id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL,
    
    -- 選擇資訊
    selected_card_index INTEGER,
    selected_scene TEXT,
    selected_style TEXT,
    selected_card JSONB,
    
    -- 反饋內容
    feedback_text TEXT NOT NULL,
    feedback_type VARCHAR(20) CHECK (feedback_type IN ('refine', 'regenerate', 'positive')),
    
    -- 評分（可選）
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    rating_reason TEXT,
    
    -- 結果
    refined_cards JSONB,
    refinement_success BOOLEAN,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_feedback_logs_session_id ON inspire_feedback_logs(session_id);
CREATE INDEX idx_feedback_logs_created_at ON inspire_feedback_logs(created_at DESC);
CREATE INDEX idx_feedback_logs_rating ON inspire_feedback_logs(rating);
CREATE INDEX idx_feedback_logs_feedback_type ON inspire_feedback_logs(feedback_type);

-- =====================================================
-- 3. 視圖（Views）
-- =====================================================

-- -----------------------------------------------------
-- 3.1 活躍 Session 統計視圖
-- -----------------------------------------------------
CREATE OR REPLACE VIEW inspire_active_sessions AS
SELECT 
    COUNT(*) as active_count,
    COUNT(*) FILTER (WHERE mode = 'emotion') as emotion_mode_count,
    COUNT(*) FILTER (WHERE mode = 'theme') as theme_mode_count,
    AVG(current_round) as avg_rounds,
    AVG(total_cards_generated) as avg_cards_per_session
FROM inspire_sessions
WHERE status = 'active'
  AND created_at >= NOW() - INTERVAL '24 hours';

-- -----------------------------------------------------
-- 3.2 反饋統計視圖
-- -----------------------------------------------------
CREATE OR REPLACE VIEW inspire_feedback_stats AS
SELECT 
    feedback_type,
    COUNT(*) as count,
    AVG(rating) as avg_rating,
    COUNT(*) FILTER (WHERE refinement_success = TRUE) as success_count
FROM inspire_feedback_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY feedback_type;

-- =====================================================
-- 4. RPC 函數（Remote Procedure Calls）
-- =====================================================

-- -----------------------------------------------------
-- 4.1 創建或獲取 Session
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION get_or_create_inspire_session(
    p_session_id UUID,
    p_client_id VARCHAR(100) DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_viewport_width INTEGER DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_session_id UUID;
BEGIN
    -- 嘗試獲取現有 Session
    SELECT id INTO v_session_id
    FROM inspire_sessions
    WHERE session_id = p_session_id;
    
    -- 如果不存在，創建新的
    IF v_session_id IS NULL THEN
        INSERT INTO inspire_sessions (
            session_id,
            client_id,
            user_agent,
            viewport_width
        ) VALUES (
            p_session_id,
            p_client_id,
            p_user_agent,
            p_viewport_width
        )
        RETURNING id INTO v_session_id;
    END IF;
    
    RETURN v_session_id;
END;
$$;

-- -----------------------------------------------------
-- 4.2 記錄生成事件
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION log_inspire_generation(
    p_session_id UUID,
    p_round INTEGER,
    p_input TEXT,
    p_mode VARCHAR(20),
    p_cards JSONB,
    p_model VARCHAR(100),
    p_latency_ms INTEGER,
    p_cost_usd DECIMAL(10, 6),
    p_tags_used TEXT[]
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_log_id UUID;
BEGIN
    -- 插入生成日誌
    INSERT INTO inspire_generation_logs (
        session_id,
        round_number,
        user_input,
        mode,
        cards_count,
        cards_data,
        model,
        latency_ms,
        cost_usd,
        tags_used
    ) VALUES (
        p_session_id,
        p_round,
        p_input,
        p_mode,
        jsonb_array_length(p_cards),
        p_cards,
        p_model,
        p_latency_ms,
        p_cost_usd,
        p_tags_used
    )
    RETURNING id INTO v_log_id;
    
    -- 更新 Session 統計
    UPDATE inspire_sessions
    SET 
        total_rounds = total_rounds + 1,
        total_cards_generated = total_cards_generated + jsonb_array_length(p_cards),
        current_round = p_round,
        updated_at = NOW()
    WHERE session_id = p_session_id;
    
    RETURN v_log_id;
END;
$$;

-- -----------------------------------------------------
-- 4.3 獲取 Session 完整歷史
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION get_inspire_session_history(p_session_id UUID)
RETURNS TABLE (
    round_number INTEGER,
    user_input TEXT,
    cards JSONB,
    selected_card JSONB,
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.round_number,
        r.user_input,
        r.cards_generated,
        r.selected_card,
        r.feedback_text,
        r.created_at
    FROM inspire_rounds r
    WHERE r.session_id = p_session_id
    ORDER BY r.round_number ASC;
END;
$$;

-- =====================================================
-- 5. RLS（Row Level Security）策略
-- =====================================================

-- 啟用 RLS
ALTER TABLE inspire_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspire_rounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspire_generation_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspire_usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspire_feedback_logs ENABLE ROW LEVEL SECURITY;

-- -----------------------------------------------------
-- 匿名使用者可以創建和讀取自己的 Session
-- -----------------------------------------------------
CREATE POLICY "Allow anonymous to create sessions"
ON inspire_sessions FOR INSERT
TO anon
WITH CHECK (true);

CREATE POLICY "Allow anonymous to read own sessions"
ON inspire_sessions FOR SELECT
TO anon
USING (true);

CREATE POLICY "Allow anonymous to update own sessions"
ON inspire_sessions FOR UPDATE
TO anon
USING (true);

-- -----------------------------------------------------
-- Rounds 資料表策略
-- -----------------------------------------------------
CREATE POLICY "Allow anonymous to create rounds"
ON inspire_rounds FOR INSERT
TO anon
WITH CHECK (true);

CREATE POLICY "Allow anonymous to read rounds"
ON inspire_rounds FOR SELECT
TO anon
USING (true);

-- -----------------------------------------------------
-- Logs 資料表策略（允許寫入，服務角色可讀）
-- -----------------------------------------------------
CREATE POLICY "Allow anonymous to insert generation logs"
ON inspire_generation_logs FOR INSERT
TO anon
WITH CHECK (true);

CREATE POLICY "Allow service role to read generation logs"
ON inspire_generation_logs FOR SELECT
TO service_role
USING (true);

CREATE POLICY "Allow anonymous to insert usage logs"
ON inspire_usage_logs FOR INSERT
TO anon
WITH CHECK (true);

CREATE POLICY "Allow anonymous to insert feedback logs"
ON inspire_feedback_logs FOR INSERT
TO anon
WITH CHECK (true);

-- =====================================================
-- 6. 觸發器（Triggers）
-- =====================================================

-- -----------------------------------------------------
-- 6.1 自動更新 updated_at 時間戳
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_inspire_sessions_updated_at
    BEFORE UPDATE ON inspire_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- -----------------------------------------------------
-- 6.2 自動計算 Session 持續時間
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_session_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' OR NEW.status = 'abandoned' THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.created_at));
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_inspire_session_duration
    BEFORE UPDATE ON inspire_sessions
    FOR EACH ROW
    WHEN (OLD.status = 'active' AND NEW.status IN ('completed', 'abandoned'))
    EXECUTE FUNCTION calculate_session_duration();

-- =====================================================
-- 7. 統計查詢函數
-- =====================================================

-- -----------------------------------------------------
-- 7.1 獲取每日統計
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION get_inspire_daily_stats(p_days INTEGER DEFAULT 7)
RETURNS TABLE (
    date DATE,
    total_sessions BIGINT,
    completed_sessions BIGINT,
    total_cards_generated BIGINT,
    avg_rounds_per_session NUMERIC,
    avg_duration_seconds NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(created_at) as date,
        COUNT(*) as total_sessions,
        COUNT(*) FILTER (WHERE status = 'completed') as completed_sessions,
        SUM(total_cards_generated) as total_cards_generated,
        AVG(total_rounds) as avg_rounds_per_session,
        AVG(duration_seconds) as avg_duration_seconds
    FROM inspire_sessions
    WHERE created_at >= NOW() - (p_days || ' days')::INTERVAL
    GROUP BY DATE(created_at)
    ORDER BY date DESC;
END;
$$;

-- -----------------------------------------------------
-- 7.2 獲取熱門標籤
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION get_inspire_popular_tags(p_limit INTEGER DEFAULT 20)
RETURNS TABLE (
    tag TEXT,
    usage_count BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        unnest(tags_used) as tag,
        COUNT(*) as usage_count
    FROM inspire_generation_logs
    WHERE created_at >= NOW() - INTERVAL '30 days'
      AND tags_used IS NOT NULL
    GROUP BY tag
    ORDER BY usage_count DESC
    LIMIT p_limit;
END;
$$;

-- -----------------------------------------------------
-- 7.3 獲取模式分佈
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION get_inspire_mode_distribution()
RETURNS TABLE (
    mode VARCHAR(20),
    count BIGINT,
    percentage NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH mode_counts AS (
        SELECT 
            mode,
            COUNT(*) as cnt
        FROM inspire_sessions
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY mode
    ),
    total AS (
        SELECT SUM(cnt) as total_count FROM mode_counts
    )
    SELECT 
        mc.mode,
        mc.cnt as count,
        ROUND((mc.cnt::NUMERIC / t.total_count * 100), 2) as percentage
    FROM mode_counts mc, total t
    ORDER BY mc.cnt DESC;
END;
$$;

-- =====================================================
-- 8. 資料保留政策（可選）
-- =====================================================

-- 自動清理 30 天前的已完成 Session
CREATE OR REPLACE FUNCTION cleanup_old_inspire_sessions()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM inspire_sessions
    WHERE status IN ('completed', 'abandoned')
      AND updated_at < NOW() - INTERVAL '30 days';
END;
$$;

-- 可以設置定時任務（pg_cron）或手動執行
-- SELECT cleanup_old_inspire_sessions();

-- =====================================================
-- 9. 初始資料（可選）
-- =====================================================

-- 可以預先插入一些範例資料用於測試

-- =====================================================
-- 10. 權限設置
-- =====================================================

-- 授予 anon 角色必要的權限
GRANT SELECT, INSERT, UPDATE ON inspire_sessions TO anon;
GRANT SELECT, INSERT ON inspire_rounds TO anon;
GRANT INSERT ON inspire_generation_logs TO anon;
GRANT INSERT ON inspire_usage_logs TO anon;
GRANT INSERT ON inspire_feedback_logs TO anon;

-- 授予 service_role 完整權限
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =====================================================
-- Schema 創建完成
-- =====================================================

-- 驗證腳本
DO $$
BEGIN
    RAISE NOTICE 'Inspire Schema 創建完成！';
    RAISE NOTICE '資料表: 5 個';
    RAISE NOTICE '視圖: 2 個';
    RAISE NOTICE 'RPC 函數: 6 個';
    RAISE NOTICE 'RLS 策略: 8 個';
END $$;

