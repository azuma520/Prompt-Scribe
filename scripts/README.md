# Database Setup Scripts

這些腳本專為 **Supabase MCP** 設計，可避免 token 限制問題。

## 執行順序

由於 MCP 有 token 限制（約 25K tokens），完整的 `database_schema.sql` 太大無法一次執行。  
請按以下順序在 **Cursor** 中使用 **Supabase MCP** 執行這些腳本：

### 1. Enable Extensions (T005-T006)
```bash
File: 01_enable_extensions.sql
Purpose: Enable pgvector extension for vector search
```

### 2. Create Tables (T005)
```bash
File: 02_create_tables.sql
Purpose: Create tags_final, tag_embeddings, migration_log tables
```

### 3. Create Indexes (T005)
```bash
File: 03_create_indexes.sql
Purpose: Create indexes for query optimization and vector search
```

### 4. Create RLS Policies (T007)
```bash
File: 04_create_rls_policies.sql
Purpose: Set up Row-Level Security policies
```

### 5. Create RPC Functions - Statistics (T008)
```bash
File: 05_create_rpc_functions.sql
Purpose: Create statistics functions (get_category_statistics, get_coverage_stats, get_top_tags)
```

### 6. Create RPC Functions - Search (T008)
```bash
File: 06_create_search_functions.sql
Purpose: Create search functions (search_similar_tags, search_tags_by_text, check_data_integrity)
```

### 7. Security Fixes (Applied 2025-10-15) 🔒
```bash
File: 07_security_fixes.sql
Purpose: Documentation of security fixes applied via Supabase MCP
- Fixed search_path vulnerabilities in 9 functions
- Enhanced 4 statistics functions with SECURITY DEFINER
- Fixed get_category_statistics return type compatibility
Status: ✅ Already applied to production database
```

### 8. Fix Security Warnings (2025-01-27) 🔒
```bash
File: 13_fix_security_warnings.sql
Purpose: Fix Supabase Advisor security warnings
- Fix Function Search Path Mutable: public.semantic_tag_search
- Move vector extension from public to extensions schema
- Move pg_trgm extension from public to extensions schema
- Update database search_path to include extensions schema
Status: ⚠️ Run this script to fix current security warnings
```

**重要**: 此腳本會：
1. 自動偵測並修復 `semantic_tag_search` 函式的 search_path 設定
2. 將 `vector` 和 `pg_trgm` 擴充套件移動到 `extensions` schema
3. 更新資料庫的預設 search_path 以包含 extensions

執行此腳本後，Supabase Advisor 的三個警告應該會消失。

## 使用 Supabase MCP

在 Cursor 中執行：

1. 確保 Supabase MCP 已配置（`.cursor/mcp.json`）
2. 使用 Supabase MCP 工具選擇您的專案
3. 逐個複製貼上上述腳本內容
4. 執行每個腳本
5. 驗證執行結果

## 驗證

執行所有腳本後，可以運行以下查詢驗證：

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check pgvector extension
SELECT extname, extversion 
FROM pg_extension 
WHERE extname = 'vector';

-- Check RPC functions
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_type = 'FUNCTION'
ORDER BY routine_name;
```

## 任務對應

- **T005**: Scripts 01, 02, 03 (建立資料庫結構)
- **T006**: Script 01 (啟用 pgvector)
- **T007**: Script 04 (設定 RLS 策略)
- **T008**: Scripts 05, 06 (建立 RPC 函式)

## 故障排除

如果遇到錯誤：
1. 確認 Supabase MCP 連接正常
2. 確認您有 service_role 權限
3. 檢查是否有表或函式名稱衝突
4. 使用 `DROP TABLE IF EXISTS` 清理後重試（謹慎使用）

