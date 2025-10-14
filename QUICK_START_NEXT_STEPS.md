# 🚀 快速開始：下一步行動指南

**狀態**: T001-T014 已完成 ✅  
**進度**: 14/42 任務 (33%)  
**當前階段**: 準備執行實際遷移

---

## ✅ 已完成的工作

### 1. 資料庫結構（使用 Supabase MCP）
- ✅ 啟用 pgvector 擴展
- ✅ 建立 3 個表（tags_final, tag_embeddings, migration_log）
- ✅ 建立 11 個索引（含向量索引）
- ✅ 設定 RLS 策略
- ✅ 建立 6 個 RPC 函式

### 2. 遷移工具（Python）
- ✅ SQLite 讀取器
- ✅ 批次上傳器（含重試和檢查點）
- ✅ 遷移日誌系統
- ✅ 四層級驗證器
- ✅ 完整遷移流程
- ✅ 測試套件

---

## ⚠️ 重要：環境配置需要更新

### 問題
您的 `.env` 文件中的 Supabase URL 指向舊專案 `bdldjoopfkzztbnpnrmt`，  
但我們使用 MCP 建立的資料庫在新專案 `fumuvmbhmmzkenizksyq` 中。

### 解決方案

**步驟 1**: 編輯 `specs/001-sqlite-ags-db/.env`

將以下行：
```env
SUPABASE_URL=https://bdldjoopfkzztbnpnrmt.supabase.co
SUPABASE_ANON_KEY=sb_publishable_IZzuJSJTTxu-MGnIKfkAqQ
SUPABASE_SERVICE_ROLE_KEY=sb_secret_XWNyqtopza3rmo0u5pYX
```

更新為：
```env
SUPABASE_URL=https://fumuvmbhmmzkenizksyq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1bXV2bWJobW16a2VuaXprc3lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAzMTg2OTAsImV4cCI6MjA3NTg5NDY5MH0.zQn4miaoW1wpwVYFHWhZLaapfOcfOrsKOGjkMqDS7lo
SUPABASE_SERVICE_ROLE_KEY=<從 Supabase Dashboard 獲取>
```

**步驟 2**: 獲取 Service Role Key

1. 前往 https://app.supabase.com/
2. 選擇專案 "prompt-scribe-tags"
3. Settings → API
4. 複製 **service_role** key (secret)
5. 貼到 `.env` 文件

---

## 📋 立即執行的步驟

### Step 1: 更新環境配置 ⚠️ 必需

```bash
# 編輯 specs/001-sqlite-ags-db/.env
# 更新 SUPABASE_URL 和 API keys
```

### Step 2: 測試連接

```bash
python test_upload_debug.py
```

**預期結果**: 應該看到 `[SUCCESS] Record inserted!`

### Step 3: 測試小批次遷移（100 筆）

```bash
python src/migration/migrate_to_supabase.py --limit 100
```

**預期時間**: ~20 秒  
**預期結果**: 100 筆記錄成功上傳

### Step 4: 驗證測試結果

```bash
python src/migration/validator.py
```

或在 Supabase Dashboard SQL Editor 中：

```sql
-- 檢查記錄數
SELECT COUNT(*) FROM tags_final;

-- 檢查前10筆
SELECT name, main_category, post_count 
FROM tags_final 
ORDER BY post_count DESC 
LIMIT 10;
```

### Step 5: 執行完整遷移（140,782 筆）

確認測試成功後：

```bash
python src/migration/migrate_to_supabase.py
```

**預估時間**: 15-25 分鐘  
**預估批次數**: 282 批次（每批次 500 筆）

---

## 🎯 遷移完成後的驗證

### 自動驗證

```bash
python src/migration/validator.py
```

這會執行：
- Level 1: 記錄數量驗證（應該是 140,782）
- Level 2: 抽樣驗證（100 筆逐欄位比對）
- Level 3: 統計分佈驗證
- Level 4: 資料庫約束驗證

### 手動驗證

在 Supabase Dashboard 中執行：

```sql
-- 使用 RPC 函式檢查完整性
SELECT * FROM check_data_integrity();

-- 查看覆蓋率統計
SELECT * FROM get_coverage_stats();

-- 查看分類統計
SELECT * FROM get_category_statistics();
```

---

## 🔧 故障排除

### 問題 1: 連接失敗

**症狀**: `Could not find the table in schema cache`

**解決**: 
1. 確認 `.env` 中的 URL 是 `https://fumuvmbhmmzkenizksyq.supabase.co`
2. 確認 Service Role Key 正確

### 問題 2: 上傳失敗

**症狀**: Batch upload 錯誤

**解決**:
1. 檢查網路連接
2. 確認 Service Role Key 權限
3. 查看 `migration_checkpoint.json` 確認進度

### 問題 3: 記錄重複

**症狀**: Unique constraint violation

**解決**:
```bash
# 清空表（謹慎使用）
# 在 Supabase SQL Editor 中：
TRUNCATE TABLE tags_final CASCADE;

# 或重置檢查點重新開始
python -c "from src.migration.batch_uploader import BatchUploader; BatchUploader().reset_checkpoint()"
```

---

## 📞 需要幫助？

### 查看日誌

```python
from src.migration.migration_logger import MigrationLogger

logger = MigrationLogger()
logger.print_status()
```

### 檢查檢查點

```bash
cat migration_checkpoint.json
```

### 查看測試資料

```bash
python test_upload_debug.py
```

---

## 🎓 已應用的最佳實踐

1. **模組化設計** - 每個功能獨立模組
2. **錯誤處理** - 自動重試機制（tenacity）
3. **檢查點機制** - 支援斷點續傳
4. **完整日誌** - 所有操作記錄至資料庫
5. **多層驗證** - 確保資料完整性
6. **Context7 查詢** - 使用最新的 Supabase 文檔

---

**準備好了嗎？更新 `.env` 文件後，就可以開始遷移了！** 🚀

