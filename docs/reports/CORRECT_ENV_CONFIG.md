# 正確的環境配置

## 問題發現

您的 `.env` 文件中的 Supabase URL 指向不同的專案：
- **舊的**: `https://bdldjoopfkzztbnpnrmt.supabase.co`
- **新的（MCP 專案）**: `https://fumuvmbhmmzkenizksyq.supabase.co`

我們使用 Supabase MCP 建立的資料庫結構在專案 `fumuvmbhmmzkenizksyq` 中。

## 需要更新的配置

請更新您的 `specs/001-sqlite-ags-db/.env` 文件：

```env
# 正確的 Supabase 配置（MCP 專案）
SUPABASE_URL=https://fumuvmbhmmzkenizksyq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1bXV2bWJobW16a2VuaXprc3lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAzMTg2OTAsImV4cCI6MjA3NTg5NDY5MH0.zQn4miaoW1wpwVYFHWhZLaapfOcfOrsKOGjkMqDS7lo
SUPABASE_SERVICE_ROLE_KEY=<需要從 Supabase Dashboard 獲取>

# 其他配置保持不變...
```

## 如何獲取 Service Role Key

1. 前往 [Supabase Dashboard](https://app.supabase.com/)
2. 選擇專案 `prompt-scribe-tags`
3. 前往 Settings → API
4. 複製 **service_role** key（secret）

## 驗證配置

更新後，運行測試：

```bash
python test_upload_debug.py
```

應該會看到成功插入記錄的訊息。

## 專案信息

- **專案名稱**: prompt-scribe-tags
- **專案 ID**: fumuvmbhmmzkenizksyq
- **區域**: us-east-1
- **狀態**: ACTIVE_HEALTHY
- **資料庫版本**: PostgreSQL 17.6

## 已完成的資料庫設置

✅ pgvector 擴展已啟用
✅ tags_final 表已建立（含所有欄位和索引）
✅ tag_embeddings 表已建立（含向量索引）
✅ migration_log 表已建立
✅ RLS 策略已設定
✅ RPC 函式已建立（6 個函式）

## 下一步

1. 更新 `.env` 文件中的 Supabase 配置
2. 運行測試確認連接正常
3. 執行小批次遷移測試
4. 執行完整遷移

