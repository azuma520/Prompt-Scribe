# 規格文件：SQLite 資料遷移至 Supabase

**規格編號 (Spec ID):** SPEC-2025-002

**版本 (Version):** 1.0.0

**狀態 (Status):** Draft

**作者 (Author):** AI Assistant

**建立日期 (Created):** 2025-10-14

**最後更新 (Last Updated):** 2025-10-14

---

## 憲法符合性檢查 (Constitution Compliance Check)

- [x] 符合「兩階段混合式架構」原則（明確標示屬於階段二）
- [x] 符合「LLM 職責分離」原則（向量化使用資料層 API）
- [x] 符合「規格驅動開發」原則（本規格先於實作）
- [x] 符合「資料優先」原則（已定義資料模型與驗證邏輯）
- [x] 符合「模組化與可讀性」原則（設計清晰、職責單一）

---

## 1. 概述 (Overview)

### 1.1 目標 (Objective)

將階段一產出的本地 SQLite 資料庫（`tags.db`）完整遷移至 Supabase 雲端平台，實現從本地資料管線到雲端應用後端的無縫過渡。遷移後系統應支援 REST API 存取、語意搜尋功能，並為多使用者應用場景做好準備。

**核心價值：**
- 讓 Prompt 標籤資料可透過網路存取
- 提供語意搜尋能力，提升使用者體驗
- 保持資料完整性與可追溯性
- 為未來的協作功能奠定基礎

### 1.2 範圍 (Scope)

**包含 (In Scope):**
- 完整遷移 `tags.db` 中所有資料表與資料
- 遷移 140,782 個標籤及其分類資訊
- 建立向量嵌入以支援語意搜尋
- 設定資料庫索引以優化查詢效能
- 建立資料存取的安全策略
- 驗證遷移後資料的完整性與一致性
- 提供基本的查詢 API 端點
- 建立遷移過程的詳細記錄

**不包含 (Out of Scope):**
- 前端使用者介面開發
- 進階的使用者管理系統
- 即時協作功能
- 資料的持續同步機制
- 第三方整合（除了必要的向量化服務）
- 本地資料庫的刪除或修改（保持階段一產出不變）

### 1.3 架構階段定位 (Architecture Stage)

- [ ] 階段一：本地資料管線
- [x] 階段二：雲端應用後端
- [ ] 跨階段（需說明如何解耦）

**說明：** 此功能屬於階段二的起始項目，負責將階段一的產出（`tags.db`）遷移至雲端基礎設施。

---

## 2. 使用者場景 (User Scenarios)

### 2.1 主要場景：資料管理員執行遷移

**角色：** 資料管理員（Data Administrator）

**前置條件：**
- 已完成階段一資料處理，擁有 `tags.db` 檔案
- 已註冊 Supabase 帳號並建立專案
- 已取得必要的 API 金鑰

**操作流程：**
1. 管理員檢查本地 `tags.db` 的資料品質與完整性
2. 管理員配置 Supabase 連線資訊
3. 管理員執行遷移工具
4. 系統建立必要的資料表結構
5. 系統批次上傳標籤資料
6. 系統驗證遷移後的資料完整性
7. 管理員檢視遷移報告，確認成功

**預期結果：**
- 所有標籤資料成功遷移至 Supabase
- 資料完整性 100% 保持
- 遷移過程有完整記錄可供審計
- 管理員可透過 Supabase Dashboard 檢視資料

**異常處理：**
- 若連線失敗，系統應提供清楚的錯誤訊息並允許重試
- 若部分資料上傳失敗，系統應記錄失敗項目並提供補救方案
- 若資料驗證發現不一致，系統應停止並報告問題

### 2.2 次要場景：開發者透過 API 查詢標籤

**角色：** 應用開發者（Application Developer）

**前置條件：**
- 資料已成功遷移至 Supabase
- 開發者已取得 API 金鑰

**操作流程：**
1. 開發者透過 REST API 查詢特定分類的標籤
2. 系統返回符合條件的標籤清單
3. 開發者取得標籤的詳細資訊（名稱、分類、使用次數、信心度）

**預期結果：**
- API 回應時間 < 2 秒
- 返回的資料格式一致且完整
- 支援分頁與篩選功能

### 2.3 次要場景：使用者進行語意搜尋

**角色：** 終端使用者（End User）

**前置條件：**
- 資料已遷移且向量嵌入已生成
- 使用者透過應用程式存取系統

**操作流程：**
1. 使用者輸入自然語言查詢（例如："找到所有與學生制服相關的標籤"）
2. 系統將查詢轉換為向量
3. 系統執行向量相似度搜尋
4. 系統返回最相關的標籤清單

**預期結果：**
- 搜尋結果在 3 秒內返回
- 結果按相關性排序
- 返回的標籤與查詢語意相關

---

## 3. 需求 (Requirements)

### 3.1 功能需求 (Functional Requirements)

| ID | 需求描述 | 優先級 | 驗收標準 |
|----|----------|--------|----------|
| FR-01 | 系統應完整遷移 tags_final 表中的所有資料 | High | 遷移後記錄數 = 140,782；欄位資料無遺失 |
| FR-02 | 系統應保持資料的分類資訊（主分類、副分類、信心度） | High | 100% 資料的分類資訊保持一致 |
| FR-03 | 系統應為每個標籤生成向量嵌入 | High | 所有標籤都有對應的 1536 維向量 |
| FR-04 | 系統應提供基本的查詢 API（按名稱、分類、頻率） | High | API 能正確返回查詢結果 |
| FR-05 | 系統應提供語意搜尋功能 | Medium | 語意搜尋能返回相關標籤（相似度 > 0.7） |
| FR-06 | 系統應驗證遷移後的資料完整性 | High | 自動比對本地與雲端資料，差異為 0 |
| FR-07 | 系統應記錄遷移過程的所有關鍵步驟 | Medium | 產生包含時間戳、操作、結果的遷移日誌 |
| FR-08 | 系統應支援批次處理大量資料 | High | 能處理 100,000+ 記錄而不失敗 |
| FR-09 | 系統應提供遷移狀態查詢功能 | Low | 管理員可隨時查看遷移進度 |
| FR-10 | 系統應提供回滾機制 | Medium | 遷移失敗時能清除部分資料並重新開始 |

### 3.2 非功能需求 (Non-Functional Requirements)

| ID | 類別 | 需求描述 | 標準 |
|----|------|----------|------|
| NFR-01 | 效能 (Performance) | 遷移過程應在合理時間內完成 | 140,782 筆資料在 30 分鐘內完成遷移 |
| NFR-02 | 效能 (Performance) | API 查詢回應時間應快速 | 90% 查詢在 2 秒內回應 |
| NFR-03 | 效能 (Performance) | 語意搜尋應有可接受的延遲 | 90% 語意搜尋在 3 秒內完成 |
| NFR-04 | 可靠性 (Reliability) | 資料遷移應確保完整性 | 資料完整性驗證通過率 100% |
| NFR-05 | 可靠性 (Reliability) | 系統應能從中斷中恢復 | 支援從任意檢查點重新開始遷移 |
| NFR-06 | 安全性 (Security) | API 存取應有適當的權限控制 | 匿名使用者僅能讀取，管理操作需認證 |
| NFR-07 | 可維護性 (Maintainability) | 遷移過程應有清楚的日誌 | 每個關鍵步驟都有時間戳和狀態記錄 |
| NFR-08 | 可擴展性 (Scalability) | 系統應支援未來資料量成長 | 資料庫設計支援 1,000,000+ 標籤 |
| NFR-09 | 成本效益 (Cost) | 向量生成成本應控制在預算內 | 總成本 < $10 USD（基於 OpenAI Embeddings 定價） |

---

## 4. 資料模型 (Data Model)

### 4.1 核心資料表結構

#### 4.1.1 tags_final 表（主要標籤資料）

```sql
-- 標籤資料表（遷移自 SQLite）
CREATE TABLE tags_final (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    danbooru_cat INTEGER NOT NULL,
    post_count INTEGER DEFAULT 0,
    main_category TEXT,
    sub_category TEXT,
    confidence REAL,
    classification_source TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引設計
CREATE INDEX idx_tags_main_category ON tags_final(main_category);
CREATE INDEX idx_tags_sub_category ON tags_final(sub_category);
CREATE INDEX idx_tags_post_count ON tags_final(post_count DESC);
CREATE INDEX idx_tags_confidence ON tags_final(confidence);
CREATE INDEX idx_tags_danbooru_cat ON tags_final(danbooru_cat);
```

#### 4.1.2 tag_embeddings 表（向量嵌入）

```sql
-- 向量嵌入表（用於語意搜尋）
CREATE TABLE tag_embeddings (
    id SERIAL PRIMARY KEY,
    tag_name TEXT NOT NULL REFERENCES tags_final(name),
    embedding VECTOR(1536),
    model TEXT DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tag_name)
);

-- 向量相似度索引
CREATE INDEX idx_tag_embeddings_vector ON tag_embeddings 
USING ivfflat (embedding vector_cosine_ops);
```

#### 4.1.3 migration_log 表（遷移記錄）

```sql
-- 遷移日誌表
CREATE TABLE migration_log (
    id SERIAL PRIMARY KEY,
    migration_batch TEXT NOT NULL,
    operation TEXT NOT NULL,
    records_affected INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    error_message TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds REAL
);
```

### 4.2 資料流向

```
階段一產出 (tags.db)
    ↓
[讀取與驗證]
    ↓
[批次轉換] → 資料格式轉換、ID 生成
    ↓
[上傳至 Supabase] → tags_final 表
    ↓
[生成向量嵌入] → 呼叫嵌入 API
    ↓
[儲存向量] → tag_embeddings 表
    ↓
[驗證完整性] → 比對記錄數與抽樣檢查
    ↓
[產生報告] → 遷移成功報告
```

### 4.3 資料驗證規則

**輸入驗證（從 SQLite 讀取時）：**
- 必填欄位：name, danbooru_cat, post_count
- 資料型別檢查：post_count 必須為非負整數
- confidence 值必須在 0.0-1.0 之間（若存在）
- name 不可包含空字串或 NULL

**輸出驗證（寫入 Supabase 後）：**
- 記錄總數必須等於本地資料庫
- 每個標籤的 name 欄位必須唯一
- main_category 值必須在預定義的分類清單中
- 向量嵌入維度必須為 1536

**一致性檢查：**
- 抽樣檢查 100 筆資料，逐欄位比對
- 統計資訊檢查（總數、分類分佈）必須一致
- 檢查是否有孤立的向量（tag_name 不存在於 tags_final）

---

## 5. 成功標準 (Success Criteria)

### 5.1 資料遷移成功標準

| 標準 | 測量方式 | 目標值 |
|------|----------|--------|
| 資料完整性 | 比對遷移前後的記錄總數 | 100% 一致（140,782 筆） |
| 資料正確性 | 抽樣檢查 100 筆資料的欄位值 | 100% 相符 |
| 遷移速度 | 測量從開始到完成的總時間 | < 30 分鐘 |
| 向量生成率 | 計算成功生成向量的標籤比例 | ≥ 99% |
| 錯誤率 | 記錄遷移過程中的失敗次數 | < 1% |

### 5.2 功能可用性標準

| 標準 | 測量方式 | 目標值 |
|------|----------|--------|
| 查詢功能 | 執行 10 種不同查詢模式 | 100% 返回正確結果 |
| API 回應時間 | 測量 100 次查詢的平均回應時間 | < 2 秒 |
| 語意搜尋準確度 | 測試 20 個查詢案例的結果相關性 | ≥ 80% 使用者滿意度 |
| 並發處理能力 | 模擬 10 個並發查詢 | 全部成功回應 |

### 5.3 營運就緒標準

| 標準 | 測量方式 | 目標值 |
|------|----------|--------|
| 文件完整性 | 檢查是否包含所有必要文件 | API 文件、遷移報告、故障排除指南齊全 |
| 監控能力 | 驗證是否能查看系統狀態 | 可透過 Dashboard 查看關鍵指標 |
| 安全性設定 | 檢查存取控制策略 | Row-Level Security 正確設定 |
| 備份機制 | 驗證資料備份功能 | Supabase 自動備份已啟用 |

---

## 6. 介面定義 (Interface Definition)

### 6.1 遷移工具介面

**命令列介面（CLI）：**

```bash
# 基本遷移命令
migrate-to-supabase --source <sqlite_path> --validate-only

# 完整遷移
migrate-to-supabase --source <sqlite_path> --generate-embeddings

# 僅生成向量
migrate-to-supabase --embeddings-only --batch-size 1000

# 驗證遷移結果
migrate-to-supabase --verify --sample-size 100
```

**配置檔案格式：**

```yaml
# migration-config.yaml
source:
  type: sqlite
  path: ./stage1/output/tags.db
  
target:
  platform: supabase
  url: ${SUPABASE_URL}
  anon_key: ${SUPABASE_ANON_KEY}
  service_role_key: ${SUPABASE_SERVICE_ROLE_KEY}
  
embeddings:
  enabled: true
  provider: openai
  api_key: ${OPENAI_API_KEY}
  model: text-embedding-3-small
  batch_size: 1000
  
options:
  validate_before_upload: true
  create_backup: true
  batch_size: 500
  max_retries: 3
  log_level: INFO
```

### 6.2 API 端點定義

#### 6.2.1 查詢標籤

**端點：** `GET /rest/v1/tags_final`

**參數：**
- `name` (string, optional): 標籤名稱（支援模糊搜尋）
- `main_category` (string, optional): 主分類篩選
- `min_post_count` (integer, optional): 最低使用次數
- `limit` (integer, default: 20): 返回數量
- `offset` (integer, default: 0): 分頁偏移

**回應範例：**
```json
[
  {
    "id": "tag_001",
    "name": "school_uniform",
    "danbooru_cat": 0,
    "post_count": 15234,
    "main_category": "CHARACTER_RELATED",
    "sub_category": "CLOTHING",
    "confidence": 0.95
  }
]
```

#### 6.2.2 語意搜尋

**端點：** `POST /rest/v1/rpc/search_similar_tags`

**請求體：**
```json
{
  "query_text": "student clothing",
  "match_threshold": 0.7,
  "match_count": 10,
  "category_filter": "CHARACTER_RELATED"
}
```

**回應範例：**
```json
[
  {
    "tag_name": "school_uniform",
    "similarity": 0.89,
    "post_count": 15234
  },
  {
    "tag_name": "student",
    "similarity": 0.85,
    "post_count": 8921
  }
]
```

#### 6.2.3 統計資訊

**端點：** `GET /rest/v1/rpc/get_category_statistics`

**回應範例：**
```json
{
  "total_tags": 140782,
  "classified_tags": 135941,
  "coverage_rate": 0.9656,
  "categories": [
    {
      "name": "CHARACTER_RELATED",
      "count": 45231,
      "percentage": 0.32
    }
  ]
}
```

### 6.3 相依性 (Dependencies)

**外部服務相依：**
- Supabase 平台（PostgreSQL 15+, pgvector extension）
- OpenAI Embeddings API 或相容服務
- 網路連線（用於上傳資料和 API 呼叫）

**內部模組相依：**
- 階段一產出：`tags.db`（必須）
- 階段一分類定義：用於驗證分類值的有效性

---

## 7. LLM 使用聲明 (LLM Usage Declaration)

### 7.1 IDE LLM 使用

- [x] 用於程式碼生成輔助
- [x] 用於文件撰寫輔助
- [ ] 用於測試案例生成

### 7.2 資料層 LLM 使用

- [x] 使用（必須填寫以下資訊）

**使用資訊：**

- **用途：** 生成標籤的向量嵌入（embeddings），用於語意搜尋功能
- **模型選擇：** OpenAI text-embedding-3-small（或相容的嵌入模型）
- **輸入格式：** 
  ```json
  {
    "input": ["tag1", "tag2", "tag3"],
    "model": "text-embedding-3-small"
  }
  ```
- **輸出格式：** 
  ```json
  {
    "data": [
      {
        "embedding": [0.001, 0.002, ...],  // 1536 維向量
        "index": 0
      }
    ]
  }
  ```
- **記錄機制：** 
  - 每次 API 呼叫記錄至 `migration_log` 表
  - 記錄內容：時間戳、處理的標籤數、API 延遲、成本估算
  - 失敗的標籤記錄至單獨的錯誤日誌
- **失敗處理：** 
  - 單次 API 呼叫失敗：重試最多 3 次（指數退避）
  - 批次失敗：記錄失敗的標籤，繼續處理其他批次
  - 全部失敗：系統仍可運作，但語意搜尋功能不可用
  - 降級方案：僅使用基本的文字搜尋功能

---

## 8. 測試策略 (Testing Strategy)

### 8.1 單元測試

**測試覆蓋率目標：** ≥ 80%

**關鍵測試案例：**
- 資料讀取模組：測試從 SQLite 正確讀取各種資料類型
- 資料轉換模組：測試資料格式轉換的正確性
- 批次處理模組：測試批次分割與上傳邏輯
- 驗證模組：測試各種驗證規則
- 錯誤處理：測試各種異常情況的處理

### 8.2 整合測試

**測試範圍：**
- 完整遷移流程：從讀取 SQLite 到寫入 Supabase
- API 端點：測試所有定義的 API 功能
- 向量搜尋：測試嵌入生成和相似度搜尋
- 資料一致性：測試遷移前後資料的一致性

**測試資料集：**
- 使用實際的 `tags.db` 的子集（1,000 筆）進行測試
- 包含各種邊界情況（空值、極端值、特殊字元）

### 8.3 效能測試

**測試項目：**
- 大量資料上傳：測試 140,782 筆資料的上傳時間
- API 回應時間：測試不同查詢模式的回應時間
- 並發處理：測試多個同時查詢的處理能力
- 記憶體使用：監控遷移過程的記憶體消耗

**效能基準：**
- 遷移速度：≥ 4,500 筆/分鐘
- API 延遲：P95 < 2 秒
- 語意搜尋：P95 < 3 秒

### 8.4 驗收測試

**測試場景：**
1. 完整遷移流程測試：執行完整遷移並驗證所有資料
2. API 功能測試：測試所有 API 端點的正確性
3. 語意搜尋測試：測試 20 個實際使用案例
4. 故障恢復測試：測試中斷後的恢復能力
5. 效能測試：驗證是否符合效能要求

**驗收標準：**
- 所有測試案例通過率 100%
- 資料完整性驗證通過
- 效能指標符合要求
- 使用者文件完整

---

## 9. 風險與對策 (Risks and Mitigation)

### 9.1 技術風險

| 風險 | 可能性 | 影響程度 | 對策 |
|------|--------|----------|------|
| API 速率限制導致遷移中斷 | Medium | Medium | 實作速率限制控制；使用批次處理；支援從中斷點恢復 |
| 大量資料上傳超時 | Medium | High | 分批上傳；實作進度檢查點；支援斷點續傳 |
| 向量生成成本超出預算 | Low | Medium | 預先估算成本；設定預算上限；提供不生成向量的選項 |
| 資料格式不相容 | Low | High | 遷移前進行完整驗證；提供資料清理工具 |
| 網路不穩定導致上傳失敗 | Medium | Medium | 實作自動重試機制；記錄失敗項目以便補救 |

### 9.2 營運風險

| 風險 | 可能性 | 影響程度 | 對策 |
|------|--------|----------|------|
| Supabase 服務中斷 | Low | High | 選擇服務穩定的時段進行遷移；保留本地資料作為備份 |
| 存取權限配置錯誤 | Medium | High | 提供權限配置檢查清單；自動化驗證腳本 |
| 遷移後發現資料錯誤 | Low | High | 實作完整的驗證流程；支援回滾機制 |
| 文件不完整導致無法維護 | Medium | Medium | 建立詳細的操作手冊；記錄所有決策 |

---

## 10. 假設與依賴 (Assumptions and Dependencies)

### 10.1 假設 (Assumptions)

- Supabase 專案已建立且可正常存取
- 網路頻寬足夠支援大量資料傳輸
- OpenAI API 金鑰有效且配額充足
- `tags.db` 檔案未損壞且資料結構符合預期
- 管理員具備基本的命令列操作能力
- 遷移過程中 Supabase 服務保持穩定

### 10.2 依賴 (Dependencies)

**前置依賴：**
- 階段一必須完成，產出 `tags.db` 檔案
- Supabase 專案已建立並取得 API 金鑰
- OpenAI API 金鑰（若需要向量搜尋功能）

**技術依賴：**
- Supabase 支援 PostgreSQL 15+ 和 pgvector 擴展
- 網路連線穩定性
- 本地環境支援執行遷移工具

**資源依賴：**
- 足夠的 Supabase 儲存空間（建議 > 1 GB）
- 足夠的 API 配額（OpenAI Embeddings）
- 遷移期間的執行環境（不中斷）

---

## 11. 實作計畫 (Implementation Plan)

### 11.1 階段劃分

| 階段 | 任務 | 預估時間 | 優先級 | 交付物 |
|------|------|----------|--------|--------|
| 階段 1 | 環境準備與驗證 | 4 小時 | High | 環境設定文件、連線測試報告 |
| 階段 2 | 資料庫結構建立 | 4 小時 | High | SQL 遷移腳本、表結構文件 |
| 階段 3 | 基本資料遷移 | 8 小時 | High | 遷移工具、初步遷移報告 |
| 階段 4 | 向量嵌入生成 | 8 小時 | Medium | 嵌入生成工具、向量資料 |
| 階段 5 | API 端點設定 | 6 小時 | High | API 文件、測試案例 |
| 階段 6 | 驗證與測試 | 8 小時 | High | 測試報告、驗證結果 |
| 階段 7 | 文件與部署 | 4 小時 | Medium | 操作手冊、部署指南 |

**總預估時間：** 42 小時（約 5-6 工作天）

### 11.2 里程碑 (Milestones)

**M1: 環境就緒（Day 1）**
- Supabase 專案設定完成
- 連線測試通過
- 所有必要的 API 金鑰取得

**M2: 資料結構就緒（Day 2）**
- 所有資料表建立完成
- 索引設定完成
- 權限策略設定完成

**M3: 資料遷移完成（Day 3-4）**
- 140,782 筆標籤資料上傳完成
- 資料完整性驗證通過
- 遷移日誌完整記錄

**M4: 功能完整（Day 5）**
- 向量嵌入生成完成
- API 端點測試通過
- 語意搜尋功能可用

**M5: 上線就緒（Day 6）**
- 所有測試通過
- 文件完成
- 系統穩定運行

---

## 12. 驗收標準 (Acceptance Criteria)

### 12.1 必要驗收項目

- [ ] 所有 140,782 筆標籤成功遷移至 Supabase
- [ ] 資料完整性驗證通過（100% 一致）
- [ ] 至少 99% 的標籤成功生成向量嵌入
- [ ] 所有定義的 API 端點正常運作
- [ ] 語意搜尋功能測試通過（20 個測試案例）
- [ ] API 回應時間符合要求（P95 < 2 秒）
- [ ] 資料庫索引正確建立
- [ ] Row-Level Security 策略正確設定
- [ ] 遷移日誌完整且可讀
- [ ] 操作文件完整（包含故障排除）

### 12.2 選擇性驗收項目

- [ ] 遷移時間 < 30 分鐘（實際可能因網路而異）
- [ ] 向量生成成本 < $10 USD
- [ ] 提供遷移狀態監控介面
- [ ] 提供資料品質檢查工具

### 12.3 文件驗收標準

- [ ] API 文件包含所有端點的說明和範例
- [ ] 遷移操作手冊包含完整步驟
- [ ] 故障排除指南包含常見問題解決方案
- [ ] 架構文件說明資料庫設計
- [ ] 測試報告包含所有測試結果

---

## 13. 變更記錄 (Change Log)

| 版本 | 日期 | 變更內容 | 作者 |
|------|------|----------|------|
| 1.0.0 | 2025-10-14 | 初始版本 | AI Assistant |

---

## 14. 參考資料 (References)

- [專案開發憲法](../../.specify/memory/constitution.md)
- [階段二策略規劃 - PLAN-2025-002](../../.specify/plans/PLAN-2025-002-PHASE2-STRATEGY.md)
- [Plan C 最終完成報告](../../stage1/docs/PLAN_C_FINAL_COMPLETION_REPORT.md)
- [Supabase 部署指南](../../stage1/supabase_tools/SUPABASE_DEPLOYMENT_GUIDE.md)
- [Supabase 官方文件](https://supabase.com/docs)
- [pgvector 文件](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)

---

**規格結束 (End of Specification)**
