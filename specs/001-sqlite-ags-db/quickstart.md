# 快速入門指南：SQLite 遷移至 Supabase

**專案**: PLAN-2025-004  
**更新日期**: 2025-10-14  
**預估時間**: 2-3 小時

---

## 📋 概述

本指南將幫助您在 2-3 小時內完成 SQLite (tags.db) 遷移至 Supabase 的完整流程。

---

## ✅ 前置需求

### 必要條件

- [x] Python 3.11+ 已安裝
- [x] 擁有 Supabase 帳號
- [x] 擁有 OpenAI API 金鑰（用於向量生成）
- [x] `tags.db` 檔案存在於 `stage1/output/` 目錄
- [x] 穩定的網路連線

### 可選條件

- [ ] Supabase CLI（用於本地開發）
- [ ] Git（用於版本控制）

---

## 🚀 步驟 1：環境設定（15 分鐘）

### 1.1 建立 Supabase 專案

1. 前往 [Supabase Dashboard](https://app.supabase.com/)
2. 點擊 "New Project"
3. 填寫專案資訊：
   - Name: `prompt-scribe-tags`
   - Database Password: （請妥善保存）
   - Region: 選擇最近的區域（例如：`us-east-1`）
4. 等待專案建立完成（約 2-3 分鐘）

### 1.2 取得 API 金鑰

1. 在 Supabase Dashboard 中，前往 "Settings" → "API"
2. 複製以下金鑰：
   - **Project URL**: `https://your-project-id.supabase.co`
   - **anon public key**: `eyJ...`（用於前端存取）
   - **service_role key**: `eyJ...`（用於管理操作）

⚠️ **重要**: `service_role key` 具有完整權限，請勿公開！

### 1.3 建立環境配置

在專案根目錄建立 `.env` 檔案：

```bash
# 複製範例檔案
cp .env.example .env

# 使用編輯器開啟
code .env  # 或使用您喜歡的編輯器
```

填入以下內容：

```env
# Supabase 配置
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...your-anon-key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...your-service-role-key

# OpenAI 配置
OPENAI_API_KEY=sk-proj-your-openai-key

# 遷移配置
SOURCE_DB_PATH=./stage1/output/tags.db
BATCH_SIZE=500
EMBEDDING_BATCH_SIZE=1000
MAX_RETRIES=3

# 成本控制
MAX_BUDGET_USD=10.00
ENABLE_COST_MONITORING=true
```

### 1.4 安裝 Python 依賴

```bash
cd stage1/supabase_tools
pip install -r requirements.txt
```

**預期輸出**:
```
Successfully installed supabase-2.0.0 openai-1.0.0 ...
```

### 1.5 驗證環境

```bash
python check_env.py
```

**預期輸出**:
```
✅ Supabase 連線成功
✅ OpenAI API 金鑰有效
✅ tags.db 檔案存在 (315 MB, 140,782 標籤)
✅ 環境配置完成
```

---

## 🗄️ 步驟 2：建立資料庫結構（10 分鐘）

### 2.1 執行 Schema 腳本

1. 前往 Supabase Dashboard
2. 點擊左側選單 "SQL Editor"
3. 點擊 "New query"
4. 複製貼上 `contracts/database_schema.sql` 的內容
5. 點擊 "Run" 執行

**預期輸出**:
```
Success. Rows returned: 1
message: "Supabase Schema v1.0.0 initialized successfully"
```

### 2.2 驗證表結構

在 SQL Editor 中執行：

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

**預期結果**:
- ✅ tags_final
- ✅ tag_embeddings
- ✅ migration_log

### 2.3 檢查 pgvector 擴展

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**預期結果**: 應顯示 `vector` 擴展已安裝。

---

## 📤 步驟 3：資料遷移（20-30 分鐘）

### 3.1 執行資料遷移

```bash
python migrate_to_supabase.py \
  --source ../output/tags.db \
  --batch-size 500 \
  --validate
```

**執行過程**:
```
[2025-10-14 10:00:00] 開始遷移...
[2025-10-14 10:00:01] ✅ 連線到 Supabase
[2025-10-14 10:00:02] ✅ 讀取 SQLite 資料庫
[2025-10-14 10:00:03] 📊 總標籤數: 140,782
[2025-10-14 10:00:04] 🚀 開始批次上傳...

批次進度: 100%|████████████| 282/282 [20:15<00:00,  4.5s/batch]

[2025-10-14 10:20:19] ✅ 資料上傳完成
[2025-10-14 10:20:20] 🔍 驗證資料完整性...
[2025-10-14 10:20:25] ✅ 記錄數一致: 140,782
[2025-10-14 10:20:30] ✅ 抽樣檢查通過: 100/100
[2025-10-14 10:20:35] ✅ 統計分佈一致

✅ 遷移成功完成！
耗時: 20 分 35 秒
成功: 140,782 筆
失敗: 0 筆
```

### 3.2 驗證遷移結果

**方法 1：使用驗證腳本**

```bash
python validate_migration.py
```

**方法 2：手動查詢**

在 Supabase SQL Editor 中執行：

```sql
-- 檢查記錄總數
SELECT COUNT(*) as total FROM tags_final;
-- 預期: 140782

-- 檢查分類分佈
SELECT main_category, COUNT(*) as count 
FROM tags_final 
WHERE main_category IS NOT NULL
GROUP BY main_category 
ORDER BY count DESC;

-- 檢查TOP 10標籤
SELECT name, post_count, main_category 
FROM tags_final 
ORDER BY post_count DESC 
LIMIT 10;
```

---

## 🧠 步驟 4：生成向量嵌入（1-2 小時）

### 4.1 執行向量生成

```bash
python generate_embeddings.py \
  --batch-size 1000 \
  --monitor-cost
```

**執行過程**:
```
[2025-10-14 10:30:00] 開始生成向量嵌入...
[2025-10-14 10:30:01] 📊 待處理標籤: 140,782
[2025-10-14 10:30:02] 💰 預估成本: $0.014
[2025-10-14 10:30:03] 🚀 開始批次處理...

批次進度: 100%|████████████| 141/141 [1:45:32<00:00, 45s/batch]

[2025-10-14 12:15:35] ✅ 向量生成完成
[2025-10-14 12:15:36] 📊 統計資訊:
  - 成功: 139,374 (99.0%)
  - 失敗: 1,408 (1.0%)
  - 實際成本: $1.42
[2025-10-14 12:15:37] 💾 儲存至 Supabase...
[2025-10-14 12:17:20] ✅ 所有向量已儲存

✅ 向量生成完成！
耗時: 1 小時 47 分
成功率: 99.0%
總成本: $1.42
```

### 4.2 處理失敗的標籤（如有）

如果有標籤失敗，執行重試：

```bash
python retry_failed_embeddings.py
```

### 4.3 驗證向量品質

```bash
python validate_embeddings.py --sample-size 100
```

**預期輸出**:
```
✅ 向量維度正確: 100/100
✅ 無異常向量 (NaN/Inf): 100/100
✅ 語意相似度測試通過: 18/20 (90%)

測試案例:
- "school_uniform" vs "student": 0.85 ✅
- "smile" vs "happy": 0.78 ✅
- "forest" vs "tree": 0.82 ✅
```

---

## 🔌 步驟 5：測試 API（15 分鐘）

### 5.1 基本查詢測試

```bash
# 測試基本查詢
curl -H "apikey: YOUR_ANON_KEY" \
     -H "Authorization: Bearer YOUR_ANON_KEY" \
     "https://your-project.supabase.co/rest/v1/tags_final?select=*&limit=5"
```

**預期回應**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "1girl",
    "post_count": 5234567,
    "main_category": "CHARACTER_RELATED",
    ...
  },
  ...
]
```

### 5.2 統計資訊測試

```bash
# 測試統計 API
curl -X POST \
     -H "apikey: YOUR_ANON_KEY" \
     -H "Authorization: Bearer YOUR_ANON_KEY" \
     -H "Content-Type: application/json" \
     "https://your-project.supabase.co/rest/v1/rpc/get_coverage_stats"
```

**預期回應**:
```json
[
  {
    "total_tags": 140782,
    "classified_tags": 135941,
    "coverage_rate": 96.56,
    "vectorized_tags": 139374,
    "vectorization_rate": 99.0
  }
]
```

### 5.3 語意搜尋測試

```bash
# 執行測試腳本
python test_semantic_search.py --query "school uniform"
```

**預期輸出**:
```
查詢: "school uniform"
相似標籤:
1. school_uniform (0.89)
2. student (0.85)
3. uniform (0.83)
4. serafuku (0.80)
5. blazer (0.76)
```

### 5.4 執行完整測試套件

```bash
python test_deployment.py
```

**預期結果**: 所有測試通過 ✅

---

## 📊 步驟 6：效能驗證（10 分鐘）

### 6.1 執行效能測試

```bash
python performance_tests.py
```

**預期結果**:
```
📊 效能測試結果:

API 查詢效能:
- P50: 0.45 秒 ✅
- P95: 1.20 秒 ✅
- P99: 1.85 秒 ✅

語意搜尋效能:
- P50: 1.20 秒 ✅
- P95: 2.50 秒 ✅
- P99: 2.95 秒 ✅

並發測試 (10 concurrent):
- 成功率: 100% ✅
- 平均延遲: 1.15 秒 ✅

所有效能指標達標！✅
```

---

## ✅ 步驟 7：最終驗收（10 分鐘）

### 7.1 執行驗收檢查清單

```bash
python final_acceptance_check.py
```

**檢查項目**:

- [x] 資料完整性 100%（140,782 筆）
- [x] 向量生成率 ≥ 99%
- [x] 所有 API 端點可用
- [x] 效能指標達標
- [x] 安全策略正確設定
- [x] 成本在預算內

### 7.2 生成完成報告

```bash
python generate_completion_report.py
```

報告將儲存至：`reports/migration_completion_report_YYYYMMDD.md`

---

## 🎉 完成！

恭喜！您已成功完成 SQLite 至 Supabase 的遷移。

### 下一步行動

#### 立即

1. **檢視資料**: 前往 [Supabase Dashboard](https://app.supabase.com/) 瀏覽資料
2. **測試 API**: 使用 [API Documentation](./contracts/api_endpoints.yaml) 測試各個端點
3. **設定監控**: 在 Supabase Dashboard 設定錯誤告警

#### 1 週內

1. 收集 API 使用回饋
2. 監控效能指標
3. 記錄常見問題

#### 1 個月內

1. 優化查詢效能
2. 擴展 API 功能
3. 開始前端開發

---

## 🆘 故障排除

### 問題 1：環境檢查失敗

**症狀**: `check_env.py` 報錯

**解決方案**:
1. 檢查 `.env` 檔案格式
2. 確認 API 金鑰正確（無多餘空格）
3. 測試網路連線：`ping supabase.com`

### 問題 2：資料上傳超時

**症狀**: 批次上傳過程中超時

**解決方案**:
1. 減少批次大小：`--batch-size 250`
2. 檢查網路穩定性
3. 從檢查點恢復：`--resume-from-checkpoint`

### 問題 3：向量生成成本超支

**症狀**: 成本監控警告

**解決方案**:
1. 暫停生成：按 `Ctrl+C`
2. 檢查已處理數量
3. 調整預算或批次大小

### 問題 4：API 回應 401 錯誤

**症狀**: API 測試返回 401 Unauthorized

**解決方案**:
1. 檢查 API Key 是否正確
2. 確認使用正確的 Authorization header
3. 檢查 RLS 策略是否啟用

### 問題 5：語意搜尋結果不相關

**症狀**: 搜尋結果與查詢不相關

**解決方案**:
1. 調整相似度閾值：增加 `match_threshold`
2. 檢查向量品質
3. 確認查詢向量正確生成

---

## 📚 參考資料

### 專案文件

- [完整規格](./spec.md)
- [實作計畫](./plan.md)
- [技術研究](./research.md)
- [資料模型](./data-model.md)
- [API 文件](./contracts/api_endpoints.yaml)

### 外部資源

- [Supabase 官方文檔](https://supabase.com/docs)
- [pgvector 文檔](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)

### 支援

- 問題回報：[GitHub Issues](https://github.com/your-org/prompt-scribe/issues)
- 專案文檔：[docs/](../../docs/)

---

## 📋 檢查清單

完成後請確認以下項目：

- [ ] Supabase 專案已建立
- [ ] 環境變數已配置
- [ ] 資料庫 Schema 已建立
- [ ] 140,782 筆資料已遷移
- [ ] ≥ 99% 標籤已向量化
- [ ] 所有 API 測試通過
- [ ] 效能測試達標
- [ ] 成本在預算內（< $10）
- [ ] 完成報告已生成
- [ ] 文件已審查

---

**文件版本**: 1.0.0  
**最後更新**: 2025-10-14  
**預計時間**: 2-3 小時  
**難度**: ⭐⭐⭐☆☆ (中等)

