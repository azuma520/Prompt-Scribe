# 開發計畫：Prompt-Scribe API 優化與 LLM 友好設計

**計畫編號 (Plan ID):** PLAN-2025-005

**版本 (Version):** 1.0.0

**狀態 (Status):** Planning

**計畫負責人 (Owner):** AI Assistant

**建立日期 (Created):** 2025-01-14

**最後更新 (Last Updated):** 2025-01-14

**預計開始 (Start Date):** 2025-01-15

**預計完成 (Target Date):** 2025-02-15

---

## 憲法符合性檢查 (Constitution Compliance Check)

- [x] 計畫遵循「兩階段混合式架構」（專注於階段二：雲端應用後端）
- [x] 計畫遵循「LLM 職責分離」（API 層處理複雜性，LLM 僅需簡單調用）
- [x] 計畫遵循「規格驅動開發」（基於 SPEC-2025-002 和實際需求分析）
- [x] 計畫遵循「資料優先」（優先完成關鍵字搜尋，向量化延後）
- [x] 計畫考慮「模組化與可讀性」（API 分層設計，職責明確）

---

## 1. 計畫概述 (Overview)

### 1.1 目標 (Objectives)

基於已完成的 SQLite 到 Supabase 資料遷移（140,782 筆標籤），本計畫旨在設計和實作 LLM 友好的 API 系統，使 LLM 能夠高效、準確地協助使用者生成圖像 prompt。

**主要目標：**
1. 設計漸進式的 API 架構，優先實作關鍵字搜尋功能
2. 建立 LLM 專用的高層級 API 端點，簡化 LLM 的工作流程
3. 實作智能標籤推薦和品質驗證功能
4. 為未來的語意搜尋功能預留擴展空間
5. 確保 API 的易用性、效能和可維護性

**成功指標 (Success Metrics):**
- API 響應時間 < 500ms (P95)
- LLM 標籤推薦準確率 > 85%
- API 調用成功率 > 99%
- 關鍵字搜尋覆蓋率 > 80% 的用戶需求
- API 文檔完整度 100%

### 1.2 背景與動機 (Background and Motivation)

**背景：**
- 已成功遷移 140,782 筆 Danbooru 標籤到 Supabase
- 資料包含完整的分類系統（14 個主分類）和流行度資訊
- 目標是讓 LLM 協助使用者生成高品質的圖像 prompt

**關鍵挑戰：**
1. **LLM 工作流程複雜性**: 原設計需要 LLM 管理多個 API 調用（OpenAI Embedding + 向量搜尋）
2. **向量化成本**: 立即向量化 140,782 筆標籤需要時間和成本
3. **實際需求未明**: 不確定語意搜尋是否真的必要

**優化動機：**
- 透過高層級 API 簡化 LLM 的工作（從兩步變一步）
- 採用漸進式開發，先用關鍵字搜尋滿足 80% 需求
- 在伺服器端處理複雜性，而非讓 LLM 處理
- 建立可擴展的架構，未來可無縫升級到向量搜尋

### 1.3 範圍 (Scope)

**包含 (In Scope):**
- 設計三層級 API 架構（低層級、高層級、LLM 專用）
- 實作基於關鍵字的智能標籤推薦功能
- 建立標籤品質驗證機制
- 實作分類篩選和流行度排序
- 設計智能關鍵字擴展系統（同義詞字典）
- 建立 API 快取機制
- 完整的 API 文檔和使用範例
- API 測試套件

**不包含 (Out of Scope - 延後到 Phase 2):**
- 向量化所有標籤（延後至需求明確後）
- 語意搜尋 API 實作（延後至向量化完成後）
- 標籤關係分析（需要大量資料分析）
- 用戶管理和認證系統
- 前端應用開發
- 即時推薦和協作功能

---

## 2. API 架構設計 (API Architecture Design)

### 2.1 三層級 API 設計哲學

基於「簡單優於複雜」和「LLM 友好」的原則，我們設計三個層級的 API：

#### **Layer 1: 基礎 API（Foundation Layer）**
```yaml
目標用戶: 進階開發者、內部服務
特點: 低層級、高彈性、高效能
範例: /rpc/search_similar_tags (需要傳入向量)
```

#### **Layer 2: 業務 API（Business Layer）**
```yaml
目標用戶: 一般開發者
特點: RESTful、標準化、易於理解
範例: GET /api/v1/tags, POST /api/v1/search
```

#### **Layer 3: LLM 專用 API（LLM-Friendly Layer）** ⭐
```yaml
目標用戶: LLM (GPT-4, Claude, etc.)
特點: 一站式、容錯性高、回應結構化
範例: POST /api/llm/recommend-from-description
```

### 2.2 LLM 友好設計原則

#### **原則 1: 單一職責，一次調用**
```
❌ 錯誤設計: LLM 需要調用 2-3 個 API 才能完成任務
✅ 正確設計: LLM 調用 1 個 API 就能完成整個工作流程
```

#### **原則 2: 伺服器端處理複雜性**
```
❌ 錯誤: 讓 LLM 處理向量生成、資料轉換
✅ 正確: 伺服器端自動處理，LLM 只傳文字
```

#### **原則 3: 結構化且有解釋的回應**
```json
// ❌ 簡單但不友好
{
  "tags": ["1girl", "solo", "school_uniform"]
}

// ✅ LLM 友好
{
  "query": "a girl in school uniform",
  "recommendations": [
    {
      "tag": "1girl",
      "confidence": 0.95,
      "popularity": "very_popular",
      "reason": "直接對應'一個女孩'的核心概念",
      "usage_tip": "必備標籤，用於指定單一女性角色",
      "category": "CHARACTER"
    },
    {
      "tag": "school_uniform",
      "confidence": 0.92,
      "popularity": "popular",
      "reason": "直接匹配'校服'關鍵字",
      "usage_tip": "準確描述服裝類型",
      "category": "CLOTHING"
    }
  ],
  "metadata": {
    "total_candidates": 156,
    "processing_time_ms": 234
  }
}
```

### 2.3 漸進式開發策略

#### **Phase 1: 關鍵字搜尋（本計畫重點）**
```
技術: PostgreSQL 文字搜尋 + 智能排序
成本: 零（使用現有資源）
開發時間: 1 週
覆蓋需求: 80%
```

#### **Phase 2: 智能關鍵字擴展**
```
技術: 同義詞字典 + 分類關聯
成本: 零（手動建立字典）
開發時間: 3-5 天
覆蓋需求: 85-90%
```

#### **Phase 3: 語意搜尋（未來）**
```
技術: OpenAI Embeddings + pgvector
成本: $5 USD（一次性）
開發時間: 1-2 週
覆蓋需求: 95%+
```

---

## 3. 核心 API 設計

### 3.1 LLM 專用端點設計

#### **API 1: 智能標籤推薦（核心功能）**

```yaml
POST /api/llm/recommend-tags

描述: 
  LLM 專用的智能標籤推薦端點
  輸入用戶的自然語言描述，返回最適合的標籤組合

請求範例:
{
  "description": "a lonely girl in cyberpunk city at night",
  "max_tags": 10,
  "exclude_adult": true,
  "min_popularity": 100,
  "balance_categories": true
}

回應範例:
{
  "query": "a lonely girl in cyberpunk city at night",
  "recommended_tags": [
    {
      "tag": "1girl",
      "confidence": 0.98,
      "popularity_tier": "very_popular",
      "post_count": 5234567,
      "category": "CHARACTER",
      "match_reason": "對應'girl'關鍵字",
      "usage_context": "核心標籤，指定單一女性角色",
      "weight": 10
    },
    {
      "tag": "solo",
      "confidence": 0.95,
      "popularity_tier": "very_popular", 
      "post_count": 4123456,
      "category": "CHARACTER",
      "match_reason": "對應'lonely'孤獨概念",
      "usage_context": "表示單獨一人，增強孤獨感",
      "weight": 9
    },
    {
      "tag": "cyberpunk",
      "confidence": 0.92,
      "popularity_tier": "popular",
      "post_count": 234567,
      "category": "ART_STYLE",
      "match_reason": "直接匹配'cyberpunk'風格",
      "usage_context": "定義整體藝術風格",
      "weight": 9
    },
    {
      "tag": "city",
      "confidence": 0.88,
      "popularity_tier": "popular",
      "post_count": 456789,
      "category": "ENVIRONMENT",
      "match_reason": "對應'city'場景",
      "usage_context": "設定場景背景",
      "weight": 8
    },
    {
      "tag": "night",
      "confidence": 0.90,
      "popularity_tier": "popular",
      "post_count": 678901,
      "category": "ENVIRONMENT",
      "match_reason": "對應'at night'時間設定",
      "usage_context": "設定光線和氛圍",
      "weight": 8
    }
  ],
  "category_distribution": {
    "CHARACTER": 2,
    "ART_STYLE": 1,
    "ENVIRONMENT": 2
  },
  "quality_assessment": {
    "overall_score": 92,
    "balance_score": 88,
    "popularity_score": 95,
    "warnings": []
  },
  "suggested_prompt": "1girl, solo, cyberpunk, city, night",
  "metadata": {
    "processing_time_ms": 145,
    "total_candidates": 89,
    "algorithm": "keyword_matching_v1"
  }
}
```

**實作重點**:
1. 關鍵字提取和擴展
2. 分類平衡算法
3. 流行度加權排序
4. LLM 可讀的解釋生成

#### **API 2: 標籤品質驗證**

```yaml
POST /api/llm/validate-prompt

描述:
  驗證標籤組合的品質和合理性
  檢測衝突、冗餘、流行度問題

請求範例:
{
  "tags": ["1girl", "1boy", "solo", "school_uniform"],
  "strict_mode": false
}

回應範例:
{
  "overall_score": 65,
  "validation_result": "warning",
  "issues": [
    {
      "type": "conflict",
      "severity": "high",
      "tags_involved": ["solo", "1boy"],
      "message": "'solo'表示單獨一人，與'1boy'（表示有男孩）可能衝突",
      "suggestion": "如果是一男一女，建議移除'solo'，改用'1girl, 1boy'",
      "impact_score": -20
    },
    {
      "type": "ambiguity",
      "severity": "medium",
      "tags_involved": ["1girl", "1boy"],
      "message": "同時包含'1girl'和'1boy'，建議明確場景",
      "suggestion": "考慮添加'2people'或'couple'來明確關係",
      "impact_score": -10
    }
  ],
  "suggestions": {
    "recommended_fixes": [
      {
        "action": "remove",
        "tag": "solo",
        "reason": "與多人場景衝突"
      },
      {
        "action": "add",
        "tag": "2people",
        "reason": "明確表示兩人場景"
      }
    ],
    "improved_prompt": "1girl, 1boy, 2people, school_uniform"
  },
  "category_analysis": {
    "distribution": {
      "CHARACTER": 2,
      "CLOTHING": 1
    },
    "balance_score": 75,
    "recommendations": ["考慮添加環境或動作標籤以豐富畫面"]
  }
}
```

#### **API 3: 文字搜尋（簡化版）**

```yaml
POST /api/llm/search-by-keywords

描述:
  基於關鍵字的智能搜尋，無需向量化
  自動擴展同義詞和相關詞

請求範例:
{
  "keywords": "lonely cyberpunk",
  "max_results": 10,
  "category_hints": ["ART_STYLE", "CHARACTER"],
  "boost_popular": true
}

回應範例:
{
  "query": "lonely cyberpunk",
  "expanded_keywords": ["lonely", "solo", "alone", "cyberpunk", "neon", "futuristic"],
  "results": [
    {
      "tag": "solo",
      "relevance_score": 0.95,
      "match_type": "synonym_match",
      "matched_keyword": "lonely → solo"
    },
    {
      "tag": "cyberpunk",
      "relevance_score": 0.98,
      "match_type": "exact_match",
      "matched_keyword": "cyberpunk"
    }
  ]
}
```

### 3.2 資料庫函數設計

#### **函數 1: 智能關鍵字推薦**

```sql
CREATE OR REPLACE FUNCTION llm_recommend_tags(
    user_description TEXT,
    max_results INTEGER DEFAULT 10,
    exclude_adult BOOLEAN DEFAULT TRUE,
    min_popularity INTEGER DEFAULT 100,
    balance_categories BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    tag_name TEXT,
    confidence_score REAL,
    popularity_tier TEXT,
    post_count INTEGER,
    main_category TEXT,
    sub_category TEXT,
    match_reason TEXT,
    usage_context TEXT,
    weight INTEGER
) AS $$
DECLARE
    keywords TEXT[];
    keyword TEXT;
BEGIN
    -- 1. 提取關鍵字（簡化版：用空格分割）
    keywords := string_to_array(lower(user_description), ' ');
    
    -- 2. 查詢匹配的標籤
    RETURN QUERY
    WITH matched_tags AS (
        SELECT 
            t.name,
            t.post_count,
            t.main_category,
            t.sub_category,
            t.confidence,
            -- 計算相關性分數
            CASE 
                -- 完全匹配
                WHEN t.name = ANY(keywords) THEN 1.0
                -- 前綴匹配
                WHEN EXISTS (
                    SELECT 1 FROM unnest(keywords) k 
                    WHERE t.name LIKE k || '%'
                ) THEN 0.9
                -- 包含匹配
                WHEN EXISTS (
                    SELECT 1 FROM unnest(keywords) k 
                    WHERE t.name LIKE '%' || k || '%'
                ) THEN 0.7
                -- 分類匹配
                WHEN EXISTS (
                    SELECT 1 FROM unnest(keywords) k 
                    WHERE t.main_category ILIKE '%' || k || '%'
                ) THEN 0.5
                ELSE 0.3
            END as relevance_score,
            -- 匹配原因
            CASE 
                WHEN t.name = ANY(keywords) THEN '完全匹配關鍵字: ' || t.name
                WHEN EXISTS (SELECT 1 FROM unnest(keywords) k WHERE t.name LIKE '%' || k || '%') 
                    THEN '包含關鍵字: ' || (SELECT k FROM unnest(keywords) k WHERE t.name LIKE '%' || k || '%' LIMIT 1)
                ELSE '分類相關'
            END as reason
        FROM tags_final t
        WHERE 
            -- 基本篩選
            t.post_count >= min_popularity
            AND (NOT exclude_adult OR t.main_category != 'ADULT_CONTENT')
            AND (t.confidence IS NULL OR t.confidence >= 0.6)
            -- 至少有一個條件匹配
            AND (
                t.name ILIKE ANY(SELECT '%' || k || '%' FROM unnest(keywords) k)
                OR t.main_category ILIKE ANY(SELECT '%' || k || '%' FROM unnest(keywords) k)
            )
    ),
    ranked_tags AS (
        SELECT 
            mt.*,
            -- 綜合分數：相關性 70% + 流行度 30%
            (mt.relevance_score * 0.7 + 
             (ln(mt.post_count + 1) / 20.0) * 0.3) as combined_score,
            -- 權重（用於排序）
            (mt.relevance_score * 10)::INTEGER as tag_weight
        FROM matched_tags mt
    )
    SELECT 
        rt.name as tag_name,
        rt.relevance_score as confidence_score,
        CASE 
            WHEN rt.post_count > 100000 THEN 'very_popular'
            WHEN rt.post_count > 10000 THEN 'popular'
            WHEN rt.post_count > 1000 THEN 'moderate'
            ELSE 'niche'
        END as popularity_tier,
        rt.post_count,
        rt.main_category,
        rt.sub_category,
        rt.reason as match_reason,
        CASE rt.main_category
            WHEN 'CHARACTER' THEN '角色核心標籤，影響人物基本特徵'
            WHEN 'CHARACTER_RELATED' THEN '角色相關標籤，描述外觀細節'
            WHEN 'ACTION_POSE' THEN '動作姿態標籤，影響人物動作和表情'
            WHEN 'ENVIRONMENT' THEN '環境標籤，設定場景背景'
            WHEN 'ART_STYLE' THEN '藝術風格標籤，影響整體畫風'
            WHEN 'OBJECTS' THEN '物件標籤，添加場景元素'
            ELSE '通用標籤'
        END as usage_context,
        rt.tag_weight as weight
    FROM ranked_tags rt
    ORDER BY 
        rt.combined_score DESC,
        rt.post_count DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;
```

#### **函數 2: 標籤驗證**

```sql
CREATE OR REPLACE FUNCTION llm_validate_tags(
    input_tags TEXT[],
    strict_mode BOOLEAN DEFAULT FALSE
)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    issues JSONB[] := '{}';
    overall_score INTEGER := 100;
    tag_info RECORD;
    category_counts JSONB;
BEGIN
    -- 檢查每個標籤
    FOR tag_info IN 
        SELECT name, post_count, main_category, sub_category, confidence
        FROM tags_final 
        WHERE name = ANY(input_tags)
    LOOP
        -- 流行度檢查
        IF tag_info.post_count < 100 THEN
            issues := issues || jsonb_build_object(
                'type', 'low_popularity',
                'severity', 'medium',
                'tags_involved', ARRAY[tag_info.name],
                'message', format('標籤 "%s" 使用次數較少 (%s)，可能影響生圖品質', 
                                tag_info.name, tag_info.post_count),
                'suggestion', '考慮使用更流行的相似標籤',
                'impact_score', -10
            );
            overall_score := overall_score - 10;
        END IF;
    END LOOP;
    
    -- 衝突檢測
    IF '1girl' = ANY(input_tags) AND '1boy' = ANY(input_tags) AND 'solo' = ANY(input_tags) THEN
        issues := issues || jsonb_build_object(
            'type', 'conflict',
            'severity', 'high',
            'tags_involved', ARRAY['solo', '1girl', '1boy'],
            'message', '''solo''表示單人，但同時有''1girl''和''1boy''',
            'suggestion', '移除''solo''或改用''1girl, 1boy, 2people''',
            'impact_score', -25
        );
        overall_score := overall_score - 25;
    END IF;
    
    -- 分類分佈分析
    SELECT jsonb_object_agg(main_category, cnt)
    INTO category_counts
    FROM (
        SELECT main_category, COUNT(*) as cnt
        FROM tags_final
        WHERE name = ANY(input_tags)
        GROUP BY main_category
    ) sub;
    
    -- 構建結果
    result := jsonb_build_object(
        'overall_score', GREATEST(overall_score, 0),
        'validation_result', 
            CASE 
                WHEN overall_score >= 80 THEN 'good'
                WHEN overall_score >= 60 THEN 'warning'
                ELSE 'poor'
            END,
        'issues', array_to_json(issues),
        'category_analysis', jsonb_build_object(
            'distribution', category_counts,
            'balance_score', 
                CASE 
                    WHEN jsonb_array_length(jsonb_object_keys(category_counts)::jsonb) >= 3 THEN 85
                    WHEN jsonb_array_length(jsonb_object_keys(category_counts)::jsonb) = 2 THEN 70
                    ELSE 50
                END
        )
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
```

#### **函數 3: 分類熱門標籤**

```sql
CREATE OR REPLACE FUNCTION llm_get_popular_by_category(
    category_name TEXT DEFAULT NULL,
    limit_count INTEGER DEFAULT 20,
    min_popularity INTEGER DEFAULT 1000
)
RETURNS TABLE (
    tag_name TEXT,
    category TEXT,
    popularity_score INTEGER,
    tier TEXT,
    usage_tip TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.name as tag_name,
        t.main_category as category,
        t.post_count as popularity_score,
        CASE 
            WHEN t.post_count > 100000 THEN 'very_popular'
            WHEN t.post_count > 10000 THEN 'popular'
            WHEN t.post_count > 1000 THEN 'moderate'
            ELSE 'niche'
        END as tier,
        CASE t.main_category
            WHEN 'CHARACTER' THEN '用於描述角色類型和數量'
            WHEN 'CHARACTER_RELATED' THEN '用於描述角色外觀和特徵'
            WHEN 'ACTION_POSE' THEN '用於描述動作和姿態'
            WHEN 'ENVIRONMENT' THEN '用於設定場景和環境'
            WHEN 'ART_STYLE' THEN '用於定義整體藝術風格'
            WHEN 'OBJECTS' THEN '用於添加場景物件'
            ELSE '通用標籤'
        END as usage_tip
    FROM tags_final t
    WHERE 
        (category_name IS NULL OR t.main_category = category_name)
        AND t.post_count >= min_popularity
        AND t.main_category IS NOT NULL
    ORDER BY t.post_count DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;
```

### 3.3 智能關鍵字擴展字典

```yaml
# 儲存在資料庫或配置檔中
keyword_synonyms:
  # 角色相關
  girl: [1girl, female, woman, lady]
  boy: [1boy, male, man]
  alone: [solo, single, one_person]
  
  # 風格相關  
  cyberpunk: [neon, futuristic, sci-fi, technology, cyber]
  anime: [manga, japanese_style, illustration]
  realistic: [photorealistic, photo, real]
  
  # 情緒相關
  happy: [smile, smiling, cheerful, joyful]
  sad: [crying, tears, melancholy, depressed]
  lonely: [solo, alone, isolated, solitary]
  
  # 環境相關
  city: [urban, cityscape, street, buildings]
  nature: [forest, mountain, outdoor, landscape]
  room: [bedroom, living_room, indoor, interior]
  
  # 時間相關
  night: [nighttime, evening, dark, moonlight]
  day: [daytime, sunlight, bright, sunny]
  
  # 服裝相關
  uniform: [school_uniform, military_uniform, outfit]
  dress: [gown, skirt, clothing]
  
  # 動作相關
  sitting: [seated, sit, sitting_down]
  standing: [stand, standing_up, upright]
  running: [run, sprint, jogging]
```

---

## 4. 開發階段規劃

### 4.1 Phase 1: 基礎 API 實作（Week 1）

#### **任務 1.1: 設置 API 專案結構**
```
□ 建立 FastAPI 專案
□ 配置 Supabase 連接
□ 設置環境變數管理
□ 建立基本路由結構
□ 配置 CORS 和中間件
```

**產出物**: 
- `api/main.py`
- `api/config.py`
- `api/requirements.txt`

#### **任務 1.2: 實作基礎端點**
```
□ GET /api/v1/tags (分頁查詢)
□ GET /api/v1/tags/{name} (單一標籤)
□ GET /api/v1/categories (分類列表)
□ GET /api/v1/stats (基本統計)
```

**產出物**:
- `api/routers/v1/tags.py`
- `api/routers/v1/statistics.py`

#### **任務 1.3: 實作關鍵字搜尋**
```
□ 建立關鍵字提取邏輯
□ 實作同義詞擴展系統
□ 建立 POST /api/v1/search endpoint
□ 實作流行度加權排序
```

**產出物**:
- `api/services/keyword_expander.py`
- `api/routers/v1/search.py`

### 4.2 Phase 2: LLM 專用端點（Week 2）

#### **任務 2.1: 智能推薦功能**
```
□ 實作關鍵字提取算法
□ 建立分類平衡邏輯
□ 實作 POST /api/llm/recommend-tags
□ 添加解釋生成邏輯
□ 建立資料庫函數 llm_recommend_tags
```

**產出物**:
- `api/routers/llm/recommendations.py`
- `scripts/07_create_llm_functions.sql`

#### **任務 2.2: 品質驗證功能**
```
□ 建立衝突檢測規則
□ 實作冗餘檢測邏輯
□ 實作 POST /api/llm/validate-prompt
□ 建立資料庫函數 llm_validate_tags
□ 設計改進建議生成器
```

**產出物**:
- `api/routers/llm/validation.py`
- `api/services/conflict_detector.py`

#### **任務 2.3: 輔助功能**
```
□ 實作 GET /api/llm/popular-by-category
□ 實作 POST /api/llm/search-by-keywords
□ 建立快取機制（常用查詢）
□ 實作批次查詢支援
```

**產出物**:
- `api/routers/llm/helpers.py`
- `api/middleware/cache.py`

### 4.3 Phase 3: 測試和文檔（Week 3）

#### **任務 3.1: API 測試**
```
□ 單元測試（所有端點）
□ 整合測試（LLM 工作流程）
□ 效能測試（響應時間）
□ 負載測試（併發處理）
```

**產出物**:
- `api/tests/test_endpoints.py`
- `api/tests/test_llm_workflow.py`

#### **任務 3.2: 文檔和範例**
```
□ 更新 OpenAPI 規格
□ 編寫 LLM 使用指南
□ 建立 Postman Collection
□ 編寫 Python SDK 範例
□ 建立 LLM Tool Definition (for GPT/Claude)
```

**產出物**:
- `docs/API_GUIDE.md`
- `docs/LLM_INTEGRATION.md`
- `examples/llm_usage.py`

### 4.4 Phase 4: 部署和監控（Week 4）

#### **任務 4.1: 部署準備**
```
□ 設置 Docker 容器
□ 配置環境變數
□ 設置 CI/CD 流程
□ 準備部署文檔
```

#### **任務 4.2: 監控和日誌**
```
□ 實作 API 使用量追蹤
□ 設置錯誤日誌
□ 建立效能監控
□ 設置告警機制
```

---

## 5. 未來擴展規劃（Phase 2 - 延後）

### 5.1 語意搜尋準備（Month 2）

當基礎 API 穩定且收集到真實使用需求後，再考慮實作：

#### **任務 X.1: 向量化評估**
```
□ 分析關鍵字搜尋的覆蓋率
□ 識別無法滿足的查詢類型
□ 評估向量搜尋的投資報酬率
□ 決定是否需要向量化
```

#### **任務 X.2: Embedding 生成（如果需要）**
```
□ 選擇 embedding 模型
□ 建立批次處理腳本
□ 生成所有標籤的 embeddings
□ 驗證向量品質
```

#### **任務 X.3: 語意搜尋 API**
```
□ 實作 POST /api/llm/semantic-search-by-text
□ 建立 Edge Function 處理 embedding 生成
□ 實作快取機制
□ 整合到現有 API
```

---

## 6. 技術規格

### 6.1 技術棧

**後端 API:**
- FastAPI 0.109+ (Python 3.9+)
- Supabase Python Client 2.x
- Pydantic 2.x (資料驗證)
- python-dotenv (環境管理)

**資料庫:**
- PostgreSQL 15+ (via Supabase)
- pgvector 0.5+ (向量擴展，預留)
- 現有的索引和函數

**部署:**
- Docker (容器化)
- Vercel/Railway/Render (平台選擇)
- GitHub Actions (CI/CD)

**可選依賴（未來）:**
- OpenAI Python SDK (embedding 生成)
- Redis (快取層)

### 6.2 效能目標

```
API 響應時間:
- 簡單查詢: < 200ms (P95)
- 複雜查詢: < 500ms (P95)
- LLM 推薦: < 300ms (P95)

吞吐量:
- QPS: > 100 (簡單查詢)
- 併發: > 50 同時用戶

可用性:
- Uptime: > 99.5%
- 錯誤率: < 0.5%
```

### 6.3 安全性設計

```
認證:
- Supabase Anonymous Key (公開查詢)
- Service Role Key (管理功能)
- 未來: JWT 用戶認證

授權:
- RLS 政策控制資料存取
- API Rate Limiting
- CORS 配置

資料保護:
- API Key 不暴露給客戶端
- 敏感操作需要 Service Role Key
- 輸入驗證和清理
```

---

## 7. 風險評估與緩解

### 7.1 技術風險

| 風險 | 機率 | 影響 | 緩解策略 |
|------|------|------|----------|
| 關鍵字搜尋準確率不足 | 中 | 中 | 建立完整的同義詞字典，收集回饋優化 |
| API 效能不符預期 | 低 | 高 | 使用快取、優化查詢、增加索引 |
| Supabase 配額限制 | 低 | 中 | 監控使用量，必要時升級方案 |
| LLM 集成複雜度 | 低 | 低 | 提供詳細文檔和範例 |

### 7.2 業務風險

| 風險 | 機率 | 影響 | 緩解策略 |
|------|------|------|----------|
| 用戶需求與設計不符 | 中 | 高 | 快速原型，早期測試，收集回饋 |
| 向量搜尋延後導致功能不完整 | 低 | 中 | 確保關鍵字搜尋足夠強大 |
| 開發時間超出預期 | 中 | 中 | 採用 MVP 方式，優先核心功能 |

---

## 8. 資源規劃

### 8.1 開發資源

```
Week 1: 基礎 API
- 開發時間: 3-4 天
- 測試時間: 1-2 天

Week 2: LLM 端點
- 開發時間: 3-4 天
- 測試時間: 1-2 天

Week 3: 文檔和優化
- 文檔編寫: 2 天
- 優化調整: 2-3 天

Week 4: 部署和上線
- 部署配置: 1-2 天
- 監控設置: 1 天
- 上線測試: 1-2 天
```

### 8.2 成本估算

```
開發成本: 
- 人力: 4 週 × 1 開發者 = 4 人週

基礎設施成本:
- Supabase Free Tier: $0/月 (500MB DB, 50k+ requests)
- 升級 Pro (如需): $25/月

未來成本（可選）:
- OpenAI Embedding (一次性): $5 USD
- Redis 快取 (如需): $5-10/月
```

---

## 9. 交付物清單 (Deliverables)

### 9.1 程式碼交付物

```
api/
├── main.py                          # FastAPI 主應用
├── config.py                        # 配置管理
├── requirements.txt                 # Python 依賴
├── routers/
│   ├── v1/
│   │   ├── tags.py                 # 基礎標籤 API
│   │   ├── search.py               # 搜尋 API
│   │   └── statistics.py           # 統計 API
│   ├── llm/
│   │   ├── recommendations.py      # LLM 推薦 API ⭐
│   │   ├── validation.py           # LLM 驗證 API ⭐
│   │   └── helpers.py              # LLM 輔助 API
│   └── admin/
│       └── management.py           # 管理 API
├── services/
│   ├── supabase_client.py          # Supabase 連接
│   ├── keyword_expander.py         # 關鍵字擴展 ⭐
│   ├── conflict_detector.py        # 衝突檢測 ⭐
│   └── cache_manager.py            # 快取管理
├── models/
│   ├── requests.py                 # 請求模型
│   └── responses.py                # 回應模型
└── tests/
    ├── test_basic_api.py
    ├── test_llm_endpoints.py       # LLM 端點測試 ⭐
    └── test_integration.py

scripts/
└── 07_create_llm_functions.sql     # LLM 專用資料庫函數 ⭐

data/
└── keyword_synonyms.yaml            # 同義詞字典 ⭐
```

### 9.2 文檔交付物

```
docs/
├── API_REFERENCE.md                 # API 完整參考
├── LLM_INTEGRATION_GUIDE.md        # LLM 整合指南 ⭐
├── QUICK_START.md                   # 快速開始
└── DEPLOYMENT_GUIDE.md             # 部署指南

examples/
├── llm_tool_definitions/
│   ├── gpt4_function_calling.json  # GPT-4 Function Calling 定義 ⭐
│   ├── claude_tools.json           # Claude Tools 定義 ⭐
│   └── openai_assistants.json      # OpenAI Assistants 定義
└── python_examples/
    ├── basic_usage.py
    └── llm_integration.py           # LLM 整合範例 ⭐
```

---

## 10. 成功標準

### 10.1 功能完整性

- [x] 資料遷移完成（140,782 筆標籤）
- [ ] 基礎 API 全部實作並測試通過
- [ ] LLM 專用端點全部實作並測試通過
- [ ] API 文檔完整且準確
- [ ] 所有測試通過率 > 95%

### 10.2 效能標準

- [ ] API 響應時間符合目標（< 500ms P95）
- [ ] 支援 50+ 併發用戶
- [ ] 關鍵字搜尋準確率 > 80%
- [ ] LLM 推薦滿意度 > 85%

### 10.3 可用性標準

- [ ] API 文檔清晰易懂
- [ ] LLM 整合範例完整可用
- [ ] 錯誤訊息友好且有幫助
- [ ] 上線後可用性 > 99%

---

## 11. 下一步行動 (Next Steps)

### 11.1 立即行動（本週）

1. **建立 API 專案結構**
   ```bash
   mkdir -p api/{routers/{v1,llm,admin},services,models,tests}
   touch api/main.py api/config.py api/requirements.txt
   ```

2. **實作第一個端點**
   - GET /api/v1/tags
   - 測試 Supabase 連接
   - 驗證基本功能

3. **建立同義詞字典**
   - 收集常見關鍵字
   - 建立擴展規則
   - 測試擴展效果

### 11.2 本週目標

- ✅ 完成 API 專案設置
- ✅ 實作 3-4 個基礎端點
- ✅ 建立關鍵字擴展系統
- ✅ 完成基本測試

### 11.3 決策點

**Week 2 結束時評估**:
- 關鍵字搜尋是否滿足需求？
- 是否需要立即實作向量搜尋？
- API 效能是否符合預期？
- 需要哪些額外功能？

---

## 附錄 A: API 設計對比

### A.1 設計演進

#### **原始設計（SPEC-2025-002）**
```yaml
優點:
- 完整的語意搜尋支援
- 技術上先進

缺點:
- LLM 需要管理多個 API 調用
- 需要立即向量化（成本和時間）
- 複雜度高
```

#### **優化設計（PLAN-2025-005）** ⭐
```yaml
優點:
- LLM 工作流程簡化（一次 API 調用）
- 漸進式開發（先關鍵字，後向量）
- 快速上線（1 週內可用）
- 成本最佳化（延後向量化）

改進:
- 新增高層級 LLM 專用端點
- 伺服器端處理複雜性
- 智能關鍵字擴展系統
- 完整的品質驗證機制
```

### A.2 核心改進點

| 面向 | 原設計 | 優化設計 | 改進幅度 |
|------|--------|----------|----------|
| LLM API 調用次數 | 2-3 次 | 1 次 | -60% |
| 開發時間 | 2-3 週 | 1 週（基礎功能） | -50% |
| 上線時間 | 3-4 週 | 1-2 週 | -60% |
| 初期成本 | $5 | $0 | -100% |
| LLM 錯誤率 | 15-20% | 5-10% | -50% |
| API 複雜度 | 高 | 低 | -70% |

---

## 附錄 B: LLM Tool Definition 範例

### B.1 GPT-4 Function Calling

```json
{
  "name": "recommend_tags_for_image",
  "description": "根據用戶的圖像描述，推薦最適合的 Danbooru 標籤組合",
  "parameters": {
    "type": "object",
    "properties": {
      "description": {
        "type": "string",
        "description": "用戶對想要生成的圖像的描述，例如：'a cute girl in school uniform'"
      },
      "max_tags": {
        "type": "integer",
        "description": "最多返回的標籤數量",
        "default": 10
      },
      "exclude_adult": {
        "type": "boolean",
        "description": "是否排除成人內容標籤",
        "default": true
      }
    },
    "required": ["description"]
  }
}
```

### B.2 使用範例

```python
# LLM 如何使用這個 API
import openai
import requests

# 1. 用戶輸入
user_input = "我想要一張孤獨的女孩在賽博龐克城市的圖片"

# 2. LLM 調用工具
function_call = {
    "name": "recommend_tags_for_image",
    "arguments": {
        "description": user_input,
        "max_tags": 8,
        "exclude_adult": True
    }
}

# 3. 呼叫 API（僅一次！）
response = requests.post(
    "https://your-api.com/api/llm/recommend-tags",
    json={
        "description": user_input,
        "max_tags": 8,
        "exclude_adult": True
    }
)

# 4. 獲得結構化建議
tags = response.json()

# 5. LLM 生成最終 prompt
final_prompt = ", ".join([t["tag"] for t in tags["recommended_tags"]])
# 結果: "1girl, solo, cyberpunk, city, night, neon_lights, ..."
```

---

## 結論

本計畫採用「簡單優先、漸進優化」的策略，通過以下方式優化 API 設計：

1. **簡化 LLM 工作流程**: 從兩步變一步
2. **降低開發成本**: 延後向量化，先用關鍵字
3. **加快上線速度**: 1 週內可提供基礎功能
4. **保持擴展性**: 架構設計支援未來升級

**核心理念**: 讓 API 承擔複雜性，讓 LLM 保持簡單。

**下一步**: 開始實作基礎 API 和 LLM 專用端點。
