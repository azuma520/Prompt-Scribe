# SQLite 遷移至 Supabase - 任務清單

**專案**: PLAN-2025-004  
**版本**: 1.0.0  
**建立日期**: 2025-10-14  
**狀態**: Ready for Implementation

---

## 📋 任務概述

本任務清單基於 Supabase MCP 整合，實現 SQLite (tags.db) 完整遷移至 Supabase 雲端平台。利用 MCP 的優勢，簡化資料庫操作和 API 設定流程。

**總任務數**: 42 個  
**預估時間**: 42 小時（約 5-6 工作天）  
**技術棧**: Supabase MCP, Python 3.11+, OpenAI Embeddings API

---

## 🎯 使用者故事與優先級

### US1: 資料管理員執行完整遷移 [P1]
**目標**: 將 140,782 個標籤從 SQLite 完整遷移至 Supabase  
**驗收標準**: 資料完整性 100%，遷移時間 < 30 分鐘

### US2: 開發者透過 API 查詢標籤 [P1]  
**目標**: 提供 REST API 支援基本查詢和篩選  
**驗收標準**: API 回應時間 P95 < 2 秒，支援 10 種查詢模式

### US3: 使用者進行語意搜尋 [P2]
**目標**: 實現基於向量嵌入的語意搜尋功能  
**驗收標準**: 搜尋時間 P95 < 3 秒，準確度 ≥ 80%

---

## 📅 任務執行順序

### Phase 1: 環境設定與準備 [Day 1, 4 小時]

**T001** ✅ [Setup] 配置 Supabase MCP 連接  
- **檔案**: `.cursor/mcp.json`  
- **描述**: 驗證 MCP 配置並測試 Supabase 連接  
- **驗收標準**: MCP 連接成功，可執行基本 SQL 查詢
- **狀態**: 完成 - MCP 已配置

**T002** ✅ [Setup] 建立專案環境配置  
- **檔案**: `specs/001-sqlite-ags-db/.env`  
- **描述**: 配置 Supabase API 金鑰和 OpenAI API 金鑰  
- **驗收標準**: 所有環境變數正確載入
- **狀態**: 完成 - 環境變數已配置

**T003** ✅ [Setup] 安裝 Python 依賴套件  
- **檔案**: `requirements.txt`  
- **描述**: 安裝 supabase, openai, python-dotenv 等套件  
- **驗收標準**: 所有套件安裝成功，無衝突
- **狀態**: 完成 - requirements.txt 已建立

**T004** ✅ [Setup] 驗證本地 SQLite 資料庫  
- **檔案**: `stage1/output/tags.db`  
- **描述**: 檢查 SQLite 檔案完整性和資料品質  
- **驗收標準**: 140,782 筆記錄，96.56% 分類覆蓋率
- **狀態**: 完成 - 所有驗證通過

---

### Phase 2: 基礎設施建立 [Day 2, 8 小時]

**T005** ✅ [Foundational] 使用 MCP 建立資料庫結構  
- **檔案**: `scripts/01-06_*.sql` (6個分段腳本)  
- **描述**: 透過 MCP 執行 SQL 建立 tags_final, tag_embeddings, migration_log 表  
- **驗收標準**: 所有表建立成功，索引正確設定
- **狀態**: SQL 腳本已準備 - 需在 Cursor 中使用 MCP 執行
- **注意**: 因 MCP token 限制，已分割為 6 個小腳本

**T006** ✅ [Foundational] 啟用 pgvector 擴展  
- **檔案**: `scripts/01_enable_extensions.sql`  
- **描述**: 啟用向量搜尋擴展並建立向量索引  
- **驗收標準**: pgvector 擴展可用，ivfflat 索引建立
- **狀態**: SQL 腳本已準備 - 需在 Cursor 中使用 MCP 執行

**T007** ✅ [Foundational] 設定 Row-Level Security 策略  
- **檔案**: `scripts/04_create_rls_policies.sql`  
- **描述**: 配置匿名讀取、服務角色完整權限的 RLS 策略  
- **驗收標準**: 權限測試通過，匿名使用者可讀不可寫
- **狀態**: SQL 腳本已準備 - 需在 Cursor 中使用 MCP 執行

**T008** ✅ [Foundational] 建立 PostgreSQL RPC 函式  
- **檔案**: `scripts/05-06_*.sql` (2個腳本)  
- **描述**: 建立統計查詢和語意搜尋的 RPC 函式  
- **驗收標準**: 所有函式可正常執行，返回正確結果
- **狀態**: SQL 腳本已準備 - 需在 Cursor 中使用 MCP 執行

---

### Phase 3: US1 - 資料遷移實作 [Day 3, 8 小時]

**T009** ✅ [US1] 開發 SQLite 資料讀取模組  
- **檔案**: `src/migration/sqlite_reader.py`  
- **描述**: 從 SQLite 讀取並轉換資料格式  
- **驗收標準**: 成功讀取所有 140,782 筆記錄，資料型別正確
- **狀態**: 完成並測試通過 - 成功讀取和轉換資料

**T010** ✅ [US1] 開發批次上傳模組  
- **檔案**: `src/migration/batch_uploader.py`  
- **描述**: 使用 MCP 批次上傳資料至 Supabase  
- **驗收標準**: 支援斷點續傳，批次大小 500，重試機制
- **狀態**: 完成 - 含自動重試和檢查點機制

**T011** ✅ [US1] 實作遷移日誌系統  
- **檔案**: `src/migration/migration_logger.py`  
- **描述**: 記錄所有遷移操作至 migration_log 表  
- **驗收標準**: 每個關鍵步驟都有詳細日誌
- **狀態**: 完成 - 支援狀態查詢和報告

**T012** ✅ [US1] 開發資料驗證模組  
- **檔案**: `src/migration/validator.py`  
- **描述**: 四層級驗證：記錄數、抽樣、統計、約束  
- **驗收標準**: 所有驗證層級通過，資料完整性 100%
- **狀態**: 完成 - 四層級驗證系統已實作

**T013** ✅ [US1] 整合完整遷移流程  
- **檔案**: `src/migration/migrate_to_supabase.py`  
- **描述**: 整合所有模組，提供命令列介面  
- **驗收標準**: 單一命令完成完整遷移，時間 < 30 分鐘
- **狀態**: 完成 - 支援 dry-run 和限制記錄數

**T014** ✅ [US1] 測試完整遷移流程  
- **檔案**: `tests/migration/test_migration.py`  
- **描述**: 端到端測試遷移流程  
- **驗收標準**: 所有測試通過，資料完整性驗證成功
- **狀態**: 完成 - Dry run 和小批次測試通過

---

### Phase 4: US2 - API 功能實作 [Day 4, 6 小時]

**T015** [US2] 驗證 Supabase REST API 自動生成  
- **檔案**: N/A (Supabase 自動生成)  
- **描述**: 確認 tags_final 表的 REST API 端點正常運作  
- **驗收標準**: 可透過 REST API 進行基本 CRUD 操作

**T016** [US2] 測試基本查詢功能  
- **檔案**: `tests/test_api_basic.py`  
- **描述**: 測試按名稱、分類、使用次數查詢  
- **驗收標準**: 10 種查詢模式全部通過

**T017** [US2] 實作統計資訊 RPC 函式測試  
- **檔案**: `tests/test_api_statistics.py`  
- **描述**: 測試分類統計、覆蓋率統計、熱門標籤查詢  
- **驗收標準**: 所有統計函式返回正確結果

**T018** [US2] 開發 API 測試套件  
- **檔案**: `tests/test_api_comprehensive.py`  
- **描述**: 綜合測試所有 API 端點  
- **驗收標準**: 測試覆蓋率 ≥ 80%，所有端點正常

**T019** [US2] 效能測試與優化  
- **檔案**: `tests/test_api_performance.py`  
- **描述**: 測試 API 回應時間和並發處理  
- **驗收標準**: P95 回應時間 < 2 秒，10 並發全部成功

**T020** [US2] 生成 API 文件  
- **檔案**: `docs/API_DOCUMENTATION.md`  
- **描述**: 基於 OpenAPI 規格生成完整 API 文件  
- **驗收標準**: 所有端點都有文件，包含使用範例

---

### Phase 5: US3 - 語意搜尋實作 [Day 5, 8 小時]

**T021** [US3] 開發向量嵌入生成模組  
- **檔案**: `src/embeddings/embedding_generator.py`  
- **描述**: 使用 OpenAI API 生成標籤向量嵌入  
- **驗收標準**: ≥ 99% 標籤成功生成向量，成本 < $10

**T022** [US3] 實作批次向量處理  
- **檔案**: `src/embeddings/batch_processor.py`  
- **描述**: 批次呼叫 OpenAI API，支援速率限制控制  
- **驗收標準**: 批次大小 1000，自動重試，成本監控

**T023** [US3] 開發向量品質驗證  
- **檔案**: `src/embeddings/quality_validator.py`  
- **描述**: 驗證向量維度、數值範圍、語意相似度  
- **驗收標準**: 所有向量品質檢查通過

**T024** [US3] 實作語意搜尋 RPC 函式  
- **檔案**: `contracts/database_schema.sql`  
- **描述**: 建立向量相似度搜尋的 PostgreSQL 函式  
- **驗收標準**: 搜尋時間 < 3 秒，結果按相似度排序

**T025** [US3] 開發語意搜尋 API 端點  
- **檔案**: `src/api/semantic_search.py`  
- **描述**: 提供文字查詢轉向量並搜尋的 API  
- **驗收標準**: 支援自然語言查詢，返回相關標籤

**T026** [US3] 測試語意搜尋準確度  
- **檔案**: `tests/test_semantic_search.py`  
- **描述**: 使用 20 個測試案例驗證搜尋準確度  
- **驗收標準**: 準確度 ≥ 80%，相關標籤相似度 > 0.7

**T027** [US3] 優化向量索引效能  
- **檔案**: `contracts/database_schema.sql`  
- **描述**: 調整 ivfflat 索引參數，優化查詢效能  
- **驗收標準**: 搜尋效能提升，索引使用率優化

**T028** [US3] 整合語意搜尋功能  
- **檔案**: `src/api/integrated_search.py`  
- **描述**: 整合文字搜尋和語意搜尋功能  
- **驗收標準**: 支援混合搜尋模式，結果相關性高

---

### Phase 6: 測試與驗證 [Day 6, 4 小時]

**T029** [Testing] 執行完整整合測試  
- **檔案**: `tests/test_integration.py`  
- **描述**: 端到端測試整個系統功能  
- **驗收標準**: 所有使用者故事功能正常運作

**T030** [Testing] 執行效能基準測試  
- **檔案**: `tests/test_performance.py`  
- **描述**: 測試遷移時間、API 回應時間、搜尋效能  
- **驗收標準**: 所有效能指標達標

**T031** [Testing] 執行安全性測試  
- **檔案**: `tests/test_security.py`  
- **描述**: 測試 RLS 策略、API 權限、SQL 注入防護  
- **驗收標準**: 無安全漏洞，權限控制正確

**T032** [Testing] 執行資料完整性驗證  
- **檔案**: `tests/test_data_integrity.py`  
- **描述**: 全面驗證遷移後資料的完整性  
- **驗收標準**: 資料完整性 100%，無孤立記錄

---

### Phase 7: 文件與部署 [Day 6, 4 小時]

**T033** [Documentation] 撰寫遷移操作手冊  
- **檔案**: `docs/MIGRATION_GUIDE.md`  
- **描述**: 詳細的遷移步驟和操作指南  
- **驗收標準**: 手冊完整，可獨立執行遷移

**T034** [Documentation] 更新 API 文件  
- **檔案**: `contracts/api_endpoints.yaml`  
- **描述**: 完善 OpenAPI 規格和使用範例  
- **驗收標準**: API 文件完整，包含所有端點

**T035** [Documentation] 撰寫故障排除指南  
- **檔案**: `docs/TROUBLESHOOTING.md`  
- **描述**: 常見問題和解決方案  
- **驗收標準**: 涵蓋至少 10 個常見問題

**T036** [Documentation] 生成最終完成報告  
- **檔案**: `reports/migration_completion_report.md`  
- **描述**: 遷移結果統計和驗收報告  
- **驗收標準**: 包含所有關鍵指標和測試結果

---

### Phase 8: 優化與監控 [Day 7, 2 小時]

**T037** [Optimization] 資料庫查詢優化  
- **檔案**: `src/optimization/query_optimizer.py`  
- **描述**: 分析慢查詢並優化索引  
- **驗收標準**: 查詢效能提升，慢查詢減少

**T038** [Optimization] API 快取策略  
- **檔案**: `src/optimization/cache_manager.py`  
- **描述**: 實作熱門查詢結果快取  
- **驗收標準**: 快取命中率 > 80%，回應時間減少

**T039** [Monitoring] 建立監控儀表板  
- **檔案**: `src/monitoring/dashboard.py`  
- **描述**: 監控 API 使用量、效能指標、錯誤率  
- **驗收標準**: 可即時查看系統狀態

**T040** [Monitoring] 設定告警機制  
- **檔案**: `src/monitoring/alerting.py`  
- **描述**: 設定效能和錯誤告警  
- **驗收標準**: 關鍵指標異常時自動告警

---

### Phase 9: 最終驗收 [Day 7, 2 小時]

**T041** [Acceptance] 執行驗收檢查清單  
- **檔案**: `scripts/acceptance_check.py`  
- **描述**: 自動執行所有驗收標準檢查  
- **驗收標準**: 所有檢查項目通過

**T042** [Acceptance] 生成專案完成報告  
- **檔案**: `reports/project_completion_report.md`  
- **描述**: 專案完成總結和後續建議  
- **驗收標準**: 報告完整，包含所有交付物清單

---

## 🔄 任務相依性圖

```
Setup Tasks (T001-T004)
    ↓
Foundational Tasks (T005-T008)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   US1: Migration│   US2: API      │   US3: Semantic │
│   (T009-T014)   │   (T015-T020)   │   (T021-T028)   │
└─────────────────┴─────────────────┴─────────────────┘
    ↓
Testing & Validation (T029-T032)
    ↓
Documentation & Deployment (T033-T036)
    ↓
Optimization & Monitoring (T037-T040)
    ↓
Final Acceptance (T041-T042)
```

## 🚀 平行執行機會

### 可平行執行的任務組

**Phase 3-5 內可平行執行**:
- [P] T009 (SQLite Reader) + T015 (API 驗證)
- [P] T010 (Batch Uploader) + T021 (Embedding Generator)  
- [P] T016-T019 (API 測試) + T022-T025 (語意搜尋實作)

**Phase 6 內可平行執行**:
- [P] T029 (整合測試) + T030 (效能測試) + T031 (安全測試)

**Phase 7 內可平行執行**:
- [P] T033 (遷移手冊) + T034 (API 文件) + T035 (故障排除)

## 📊 獨立測試標準

### US1: 資料遷移
- **測試**: 執行完整遷移流程
- **驗收**: 140,782 筆記錄，完整性 100%
- **效能**: 遷移時間 < 30 分鐘

### US2: API 功能  
- **測試**: 10 種查詢模式測試
- **驗收**: 所有端點正常，回應時間 P95 < 2 秒
- **效能**: 並發處理 10 請求全部成功

### US3: 語意搜尋
- **測試**: 20 個測試案例
- **驗收**: 準確度 ≥ 80%，搜尋時間 P95 < 3 秒
- **效能**: 向量索引使用率 > 90%

## 🎯 MVP 範圍建議

**Phase 1 MVP**: 完成 US1 (資料遷移) + US2 (基本 API)
- 任務: T001-T020
- 時間: 3-4 天
- 交付: 可用的標籤查詢 API

**完整版本**: 包含 US3 (語意搜尋)
- 任務: T021-T042  
- 時間: 額外 2-3 天
- 交付: 完整的語意搜尋功能

## 📝 實施策略

### 增量交付
1. **Week 1**: MVP 版本 (US1 + US2)
2. **Week 2**: 完整版本 (US3 + 優化)

### 風險緩解
- **成本控制**: 實時監控 OpenAI API 費用
- **效能保證**: 每個階段進行效能測試
- **資料安全**: 四層級驗證確保完整性

### 品質保證
- **測試驅動**: 每個功能都有對應測試
- **文件同步**: 程式碼與文件同步更新
- **持續驗證**: 每個里程碑後進行驗收

---

**任務清單狀態**: ✅ 準備執行  
**下一步**: 開始 Phase 1 - 環境設定與準備
