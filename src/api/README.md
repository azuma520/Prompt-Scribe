# Prompt-Scribe API

🤖 **LLM 友好的標籤推薦 API**

## 專案資訊

- **版本**: 2.0.0
- **計畫編號**: PLAN-2025-005
- **核心理念**: 讓 API 承擔複雜性，讓 LLM 保持簡單

## 快速開始

### 1. 安裝依賴

```bash
cd src/api
pip install -r requirements.txt
```

### 2. 配置環境

複製 `.env.example` 為 `.env` 並填入你的 Supabase 憑證：

```bash
cp .env.example .env
```

編輯 `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

### 3. 啟動服務

```bash
# 開發模式
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --port 8000
```

### 4. 訪問文檔

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API 端點概覽

### 🎯 LLM 專用端點

#### POST /api/llm/recommend-tags
智能標籤推薦 - LLM 最常用的端點

**請求範例**:
```json
{
  "description": "a lonely girl in cyberpunk city at night",
  "max_tags": 10,
  "exclude_adult": true
}
```

**回應**: 包含推薦標籤、分類分佈、品質評估、使用建議等

#### POST /api/llm/validate-prompt
標籤品質驗證

**請求範例**:
```json
{
  "tags": ["1girl", "solo", "school_uniform"],
  "strict_mode": false
}
```

**回應**: 驗證結果、問題列表、改進建議

#### POST /api/llm/search-by-keywords
智能關鍵字搜尋

**請求範例**:
```json
{
  "keywords": "lonely cyberpunk girl",
  "max_results": 10
}
```

#### GET /api/llm/popular-by-category
分類熱門標籤

**參數**:
- `category`: 分類名稱 (可選)
- `limit`: 返回數量 (預設 20)

### 📚 基礎端點

#### GET /api/v1/tags
查詢標籤列表（支援分頁和篩選）

#### GET /api/v1/tags/{tag_name}
查詢單一標籤詳情

#### POST /api/v1/search
簡單文字搜尋

#### GET /api/v1/stats
獲取統計資訊

## 專案結構

```
src/api/
├── main.py                     # FastAPI 主應用
├── config.py                   # 配置管理
├── requirements.txt            # Python 依賴
│
├── routers/                    # API 路由
│   ├── v1/                     # 基礎 API
│   │   ├── tags.py
│   │   ├── search.py
│   │   └── statistics.py
│   └── llm/                    # LLM 專用 API
│       ├── recommendations.py
│       ├── validation.py
│       └── helpers.py
│
├── services/                   # 業務服務
│   ├── supabase_client.py     # 資料庫連接
│   ├── keyword_expander.py    # 關鍵字擴展
│   └── cache_manager.py       # 快取管理
│
├── models/                     # 資料模型
│   ├── requests.py            # 請求模型
│   └── responses.py           # 回應模型
│
├── data/                       # 資料檔案
│   └── keyword_synonyms.yaml  # 同義詞字典
│
└── tests/                      # 測試檔案
```

## 核心特性

### 1. 漸進式設計
- ✅ **Phase 1**: 關鍵字搜尋（已實作）
- 🔄 **Phase 2**: 向量搜尋（延後，根據需求決定）

### 2. 智能關鍵字擴展
使用同義詞字典自動擴展關鍵字：
```
"lonely girl" → ["lonely", "solo", "alone", "girl", "1girl", "female"]
```

### 3. 快取機制
- 記憶體快取（LRU）
- TTL 過期策略
- 自動快取統計

### 4. LLM 友好設計
- 一次 API 調用完成所有工作
- 結構化回應，包含詳細解釋
- 容錯性高，錯誤訊息清晰

## 效能指標

- API 響應時間: < 500ms (P95)
- 快取命中率: > 40%
- 支援併發: > 50 同時用戶

## 已知限制

### 效能特性

#### 標籤驗證端點
- **N+1 查詢模式**: 當前實作對每個標籤執行單獨的資料庫查詢
  - 5 個標籤: ~1.6 秒
  - 10 個標籤: ~3.2 秒
  - 20 個標籤: ~6.4 秒
- **適用場景**: 單次驗證 ≤10 個標籤
- **優化計畫**: 批量查詢實作（生產環境部署前）

#### 快取機制
- **當前狀態**: 記憶體快取已配置但未完全啟用
- **影響**: 重複查詢仍會訪問資料庫
- **優化計畫**: LRU 快取啟用與測試

#### 跨區域延遲
- **基礎延遲**: 300-500ms（Supabase 資料庫位於不同地理區域）
- **影響**: 每次資料庫查詢的基礎延遲
- **建議**: 生產環境考慮區域部署或 CDN

### 建議使用場景

**✅ 當前適合**:
- 開發與測試環境
- 低流量應用 (<10 req/s)
- 單次標籤驗證 ≤10 個
- 非即時應用

**⚠️ 需優化後使用**:
- 高流量生產環境 (>50 req/s)
- 批量標籤驗證 (>20 個)
- 即時應用 (要求 <500ms)
- 高併發場景

### 生產環境檢查清單

在部署至生產環境前，建議完成以下項目：

- [ ] 實作批量查詢優化（validate-prompt 端點）
- [ ] 啟用並測試快取機制
- [ ] 執行負載測試
- [ ] 調整 `SLOW_REQUEST_THRESHOLD` 設定
- [ ] 檢視資料庫連接池配置
- [ ] 考慮區域部署以降低延遲
- [ ] 設置監控與警報

詳細效能說明請參考: [Performance Notes](../../docs/api/PERFORMANCE_NOTES.md)

## 開發指南

### 執行測試

```bash
pytest tests/ -v --cov=.
```

### 代碼格式化

```bash
black .
flake8 .
```

### 檢查 Linter

```bash
mypy .
```

## 文檔

- 📖 [LLM 整合指南](../docs/LLM_INTEGRATION_GUIDE.md)
- 📖 [API 參考文檔](../docs/API_REFERENCE.md)
- 📖 [部署指南](../docs/DEPLOYMENT_GUIDE.md)

## 授權

MIT License

## 貢獻者

- AI Assistant (Initial Implementation)

---

**建立日期**: 2025-01-14  
**最後更新**: 2025-01-14  
**狀態**: ✅ Phase 1-2 完成

