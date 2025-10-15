# Supabase 部署問題統整報告

## 專案概況

**目標**: 將 SQLite 數據庫 (tags.db) 部署到 Supabase PostgreSQL  
**數據規模**: 140,782 筆標籤數據  
**部署方式**: 使用 Supabase MCP (Model Context Protocol)

---

## 問題分類與解決方案

### 一、環境配置問題

#### 1.1 環境變數編碼問題
**問題描述**:
- `.env` 文件編碼導致 `UnicodeDecodeError`
- 錯誤: `'utf-8' codec can't decode byte 0xff`

**原因分析**:
- `.env` 文件可能使用了 UTF-16 或其他編碼
- BOM (Byte Order Mark) 標記導致解析失敗

**解決方案**:
- 重新創建 `.env` 文件，確保使用 UTF-8 編碼
- 使用 `encoding='utf-8'` 參數載入環境變數

#### 1.2 API 連接認證問題
**問題描述**:
- Supabase API 連接失敗: 401 Unauthorized
- 錯誤訊息: "Invalid API key"

**原因分析**:
- API Key 格式錯誤（包含換行符）
- Anon Key vs Service Role Key 混淆
- API URL 格式不正確

**解決方案**:
- 確認使用正確的 API Key（去除多餘空白和換行）
- 使用 Service Role Key 進行管理操作
- API URL 格式: `https://[project-ref].supabase.co`

#### 1.3 直接資料庫連接超時
**問題描述**:
- PostgreSQL 直接連接超時
- 錯誤: `connection to server at "db.fumuvmbhmmzkenizksyq.supabase.co" failed: Connection timed out`

**原因分析**:
- Supabase 專案可能處於暫停狀態
- 網路/防火牆限制
- 需要啟用直接資料庫訪問

**解決方案**:
- 改用 Supabase MCP 進行資料庫操作
- 透過 MCP `execute_sql` 工具執行 SQL

---

### 二、程式碼編碼問題

#### 2.1 Unicode 字元輸出錯誤
**問題描述**:
- Windows PowerShell 無法顯示 Unicode 字元（emoji、特殊符號）
- 錯誤: `'cp950' codec can't encode character`

**受影響檔案**:
- `check_env.py`
- `deploy_to_supabase.py`
- `migrate_to_supabase.py`
- `export_full_data.py`
- `check_fix_results.py`

**解決方案**:
- 移除所有 print 語句中的 emoji 和特殊 Unicode 字元
- 使用純文字或 ASCII 字元替代
- 為檔案操作添加 `encoding='utf-8'` 參數

#### 2.2 路徑解析錯誤
**問題描述**:
- 腳本執行時找不到目標檔案
- 錯誤: `can't open file 'D:\\Prompt-Scribe\\stage1\\stage1\\...'`（路徑重複）

**原因分析**:
- 相對路徑計算錯誤
- `os.getcwd()` 與腳本位置不一致

**解決方案**:
- 使用 `os.path.dirname(__file__)` 獲取腳本路徑
- 統一使用 `cwd` 參數設定工作目錄
- 修改為: `cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))`

---

### 三、數據遷移挑戰

#### 3.1 批次大小限制
**問題描述**:
- 無法一次上傳所有數據（140,782 筆）
- 單一 SQL 檔案過大導致 token 限制超出

**嘗試的方案與結果**:

| 批次類型 | 每批記錄數 | 總批次數 | 檔案大小 | Token 數 | 結果 |
|---------|-----------|---------|---------|---------|------|
| Large Batch | 5,000 | 29 | 約 180KB | 90,518 | ❌ 超出 25K token 限制 |
| Mini Batch | 500 | 282 | 約 35KB | 18,000 | ❌ 仍超出限制 |
| Combined Batch | 5,000 (10個mini) | 29 | 約 350KB | 180K+ | ❌ 遠超限制 |
| Small Batch | 2,500 (5個mini) | 57 | 約 175KB | 90K+ | ❌ 超出限制 |
| Tiny Batch | 1,500 (3個mini) | 94 | 約 110KB | 27,173 | ❌ 仍超出限制 |

**核心問題**:
- MCP `read_file` 工具限制: 25,000 tokens
- SQL INSERT 語句冗長（包含完整列名和值）
- 無法使用 `COPY FROM STDIN`（MCP 不支援數據流）

#### 3.2 COPY FROM STDIN 不支援
**問題描述**:
- 嘗試使用 PostgreSQL 的 `COPY FROM STDIN` 進行高效批量導入
- 錯誤: `COPY from stdin failed: No source stream defined`

**原因分析**:
- MCP `execute_sql` 工具只接受 SQL 字串
- 不支援數據流（stdin）輸入
- 設計上只支援直接 SQL 執行

**影響**:
- 無法使用最高效的批量導入方式
- 必須使用 INSERT 語句，效率較低

#### 3.3 檔案數量爆炸
**問題描述**:
- 為了符合 token 限制，創建了過多批次檔案
- 最終產生 4,716 個 SQL 檔案

**批次檔案分布**:
- Mini Batch: 282 個
- Combined Batch: 29 個  
- Small Batch: 57 個
- Tiny Batch: 94 個
- 其他測試批次: 4,254 個

**後果**:
- 專案目錄混亂
- 難以管理和追蹤上傳進度
- 需要額外的整理工作

---

### 四、技術限制分析

#### 4.1 MCP 工具限制
| 限制項目 | 具體限制 | 影響 |
|---------|---------|------|
| Token 限制 | 25,000 tokens/次 | 無法讀取大檔案 |
| 不支援數據流 | 無 stdin 支援 | 無法使用 COPY |
| 執行模式 | 單次 SQL 執行 | 無批次優化 |

#### 4.2 數據格式挑戰
**問題描述**:
- 標籤數據包含特殊字元（引號、逗號、換行）
- SQL 字串轉義複雜
- Unicode 字元處理

**影響**:
- SQL 語句長度增加
- 需要額外的轉義處理
- 增加 token 使用量

---

### 五、目前狀態

#### 5.1 已完成
✅ 環境配置完成（API Key、專案設定）  
✅ MCP 連接建立  
✅ 數據導出到 CSV (140,782 筆)  
✅ 創建表結構（tags 表）  
✅ 測試單批次上傳成功（500 筆）  
✅ 專案檔案整理（4,716 個檔案已分類）

#### 5.2 待解決
🔄 大規模數據上傳（140,282 筆待上傳）  
⏳ 數據完整性驗證  
⏳ SQL 查詢功能測試  
⏳ 向量化設置

---

## 關鍵發現與建議

### 發現

1. **MCP 設計限制**
   - MCP 主要設計用於執行查詢和單一操作
   - 不適合大規模數據遷移
   - Token 限制是硬性約束

2. **批次策略困境**
   - 批次太大：超出 token 限制
   - 批次太小：檔案數量過多，管理困難
   - 最佳平衡點難以找到

3. **工具選擇重要性**
   - 直接使用 psycopg2 可能更高效
   - 但 MCP 提供更好的抽象和安全性
   - 需要權衡便利性與效能

### 建議方案

#### 方案 A: 繼續使用 MCP 微批次上傳
**優點**: 使用現有工具，安全性高  
**缺點**: 需要執行 282+ 次上傳，耗時長  
**實施**: 創建自動化腳本逐批上傳

#### 方案 B: 使用 Supabase REST API
**優點**: 可能有更高的數據限制  
**缺點**: 需要重寫上傳邏輯  
**實施**: 使用 Service Role Key 直接調用 REST API

#### 方案 C: 使用 Supabase CLI
**優點**: 專為數據遷移設計  
**缺點**: 需要額外工具安裝  
**實施**: `supabase db push` 或 `pg_restore`

#### 方案 D: 分階段遷移
**優點**: 漸進式，可控制  
**缺點**: 過程複雜  
**實施**: 
1. 上傳核心數據（高頻標籤）
2. 批次上傳中頻標籤
3. 最後上傳低頻標籤

---

## 下一步行動建議

### 立即行動（推薦）

1. **評估實際需求**
   - 確認是否需要完整 140K 數據
   - 可否先上傳核心數據集（如前 10K 或 20K）

2. **選擇最佳方案**
   - 如果堅持用 MCP：實施自動化批次上傳
   - 如果追求效率：考慮 Supabase CLI 或直接資料庫連接

3. **建立監控機制**
   - 上傳進度追蹤
   - 錯誤處理和重試機制
   - 數據完整性檢查

### 長期優化

1. **改善數據格式**
   - 考慮壓縮或二進制格式
   - 優化 SQL 語句結構

2. **建立 CI/CD 流程**
   - 自動化部署腳本
   - 數據版本管理

3. **文檔完善**
   - 部署操作手冊
   - 問題排查指南

---

## 總結

我們在 Supabase 部署過程中遇到了多層面的挑戰，從環境配置、編碼問題到數據遷移的技術限制。核心問題是 **MCP 工具的 token 限制與大規模數據遷移需求之間的矛盾**。

雖然成功建立了連接並完成了測試上傳，但要完成全部 140K 數據的遷移，需要重新評估策略，選擇更適合大規模數據遷移的方案。

**建議**: 優先考慮使用 Supabase CLI 或建立自動化的微批次上傳系統，同時完善錯誤處理和進度追蹤機制。

---

*報告生成時間: 2025-01-13*  
*數據規模: 140,782 筆記錄*  
*生成批次檔案: 4,716 個*  
*已上傳數據: 500 筆（測試）*
