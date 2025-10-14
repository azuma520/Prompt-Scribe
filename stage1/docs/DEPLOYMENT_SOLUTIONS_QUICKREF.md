# Supabase 部署解決方案快速參考

## 核心問題

**主要挑戰**: 140,782 筆數據 → Supabase，受限於 MCP token 限制（25K tokens/次）

---

## 三大解決方案對比

### 方案 1: MCP 微批次自動上傳 ⭐ 推薦（當前）

**適用場景**: 
- 堅持使用 MCP 工具
- 優先考慮安全性
- 可接受較長上傳時間

**實施步驟**:
```python
# 1. 使用現有的 mini_batch (282 個檔案，每個 500 筆)
# 2. 創建自動化上傳腳本
# 3. 實現進度追蹤和錯誤重試

for i in range(1, 283):
    batch_file = f"output/mini_batches/batch_{i:04d}.sql"
    # 讀取批次（需分塊讀取以避免 token 限制）
    # 執行 SQL
    # 記錄進度
```

**優點**:
- ✅ 使用現有工具，無需額外安裝
- ✅ MCP 提供良好抽象和安全性
- ✅ 已有測試成功案例（500 筆）

**缺點**:
- ❌ 需要執行 282 次上傳
- ❌ 預估耗時較長（約 1-2 小時）
- ❌ 需要處理 token 限制（分塊讀取）

**實施難度**: ⭐⭐⭐ 中等

---

### 方案 2: Supabase CLI 直接遷移 ⭐⭐⭐ 最高效

**適用場景**:
- 追求效率
- 願意安裝額外工具
- 一次性大規模遷移

**實施步驟**:
```bash
# 1. 安裝 Supabase CLI
npm install -g supabase

# 2. 登入
supabase login

# 3. 連結專案
supabase link --project-ref fumuvmbhmmzkenizksyq

# 4. 方式 A: 使用 SQL 檔案
supabase db execute -f export_all.sql

# 5. 方式 B: 使用 PostgreSQL COPY
psql $DATABASE_URL -c "\COPY tags FROM 'tags_data.csv' WITH CSV HEADER"
```

**優點**:
- ✅ 專為數據遷移設計
- ✅ 支援大檔案和高效批量操作
- ✅ 執行速度快（預估 5-10 分鐘）
- ✅ 原生支援 PostgreSQL 所有功能

**缺點**:
- ❌ 需要安裝額外工具
- ❌ 需要學習新的 CLI 命令
- ❌ 可能需要處理防火牆問題

**實施難度**: ⭐⭐ 簡單

---

### 方案 3: Supabase REST API 批量上傳

**適用場景**:
- 需要程式化控制
- 整合到現有 Python 工作流
- 中等規模數據

**實施步驟**:
```python
import requests
import pandas as pd

# 讀取數據
df = pd.read_csv('output/tags_data.csv')

# Supabase REST API endpoint
url = f"{SUPABASE_URL}/rest/v1/tags"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"  # 減少回傳數據
}

# 批次上傳（每次 1000 筆）
for i in range(0, len(df), 1000):
    batch = df[i:i+1000].to_dict('records')
    response = requests.post(url, json=batch, headers=headers)
    print(f"Batch {i//1000 + 1}: {response.status_code}")
```

**優點**:
- ✅ 使用 Python，易於整合
- ✅ 可自訂批次大小
- ✅ 良好的錯誤處理和重試機制

**缺點**:
- ❌ API 可能有速率限制
- ❌ 需要處理大型 JSON 序列化
- ❌ 相比 SQL 效率較低

**實施難度**: ⭐⭐⭐ 中等

---

## 分階段遷移策略

### 階段 1: 核心數據（高優先級）
```sql
-- 上傳高頻標籤（使用次數 > 1000）
-- 預估: 約 5,000-10,000 筆
```

### 階段 2: 主要數據（中優先級）
```sql  
-- 上傳中頻標籤（使用次數 100-1000）
-- 預估: 約 30,000-50,000 筆
```

### 階段 3: 完整數據（低優先級）
```sql
-- 上傳所有剩餘標籤
-- 預估: 約 80,000-100,000 筆
```

**優點**: 漸進式，可快速驗證核心功能  
**缺點**: 需要多次部署

---

## 快速決策表

| 考量因素 | 方案 1: MCP | 方案 2: CLI | 方案 3: API |
|---------|------------|------------|------------|
| **執行時間** | 1-2 小時 | 5-10 分鐘 | 30-60 分鐘 |
| **額外安裝** | ❌ 不需要 | ✅ 需要 | ❌ 不需要 |
| **技術難度** | 中 | 低 | 中 |
| **可控性** | 高 | 中 | 高 |
| **效率** | 低 | 高 | 中 |
| **適合情境** | 小規模/測試 | 大規模遷移 | 程式整合 |

---

## 推薦行動方案

### 🎯 最佳實踐（推薦）

**第一步**: 使用 **方案 2 (Supabase CLI)** 完成主要遷移
```bash
# 快速、高效、專業
supabase db execute -f output/complete_data.sql
```

**第二步**: 使用 **方案 1 (MCP)** 進行驗證和增量更新
```python
# 驗證數據完整性
# 後續小批量更新
```

**第三步**: 建立 **方案 3 (API)** 作為備用方案
```python
# 用於應用層的數據操作
# 整合到自動化流程
```

### 🚀 立即可執行

如果想**馬上開始**:

1. **最快方案**: 安裝 Supabase CLI（5 分鐘搞定）
   ```bash
   npm install -g supabase
   supabase login
   ```

2. **穩健方案**: 完善 MCP 自動上傳腳本
   ```python
   # 創建 automated_uploader.py
   # 實現進度追蹤、錯誤處理、斷點續傳
   ```

3. **混合方案**: CLI 主要遷移 + MCP 驗證
   - 用 CLI 快速上傳
   - 用 MCP 查詢驗證

---

## 常見問題 FAQ

### Q1: 為什麼不能一次上傳所有數據？
**A**: MCP `read_file` 限制 25K tokens，完整數據需要 90K+ tokens

### Q2: 微批次上傳會不會很慢？
**A**: 282 個批次，每個約 2-3 秒，總計約 15-20 分鐘（含網路延遲）

### Q3: 上傳失敗怎麼辦？
**A**: 實施斷點續傳機制，記錄已上傳批次，失敗時從中斷處繼續

### Q4: 如何驗證數據完整性？
**A**: 
```sql
-- 檢查記錄數
SELECT COUNT(*) FROM tags;

-- 檢查數據範圍
SELECT MIN(id), MAX(id) FROM tags;

-- 抽樣驗證
SELECT * FROM tags WHERE id IN (1, 1000, 10000, 100000);
```

---

## 立即執行清單

- [ ] 決定使用哪個方案
- [ ] 如果選擇 CLI：安裝 Supabase CLI
- [ ] 如果選擇 MCP：創建自動化上傳腳本
- [ ] 建立進度追蹤機制
- [ ] 實施錯誤處理和重試邏輯
- [ ] 設定數據驗證檢查點
- [ ] 測試上傳第一批數據
- [ ] 執行完整遷移
- [ ] 驗證數據完整性
- [ ] 測試 SQL 查詢功能

---

*更新時間: 2025-01-13*  
*當前狀態: 已上傳 500/140,782 筆 (0.35%)*

