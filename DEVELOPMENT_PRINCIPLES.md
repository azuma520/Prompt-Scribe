# Prompt-Scribe 開發原則與最佳實踐

## 🚨 **關鍵開發原則**

### **1. 後端服務器啟動原則**

#### **❌ 錯誤做法**：
```bash
# 在專案根目錄直接運行 uvicorn
cd D:\Prompt-Scribe
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### **✅ 正確做法**：
```bash
# 使用 run_server.py 啟動腳本
python run_server.py
```

#### **原因說明**：
- **目錄結構問題**：`api` 目錄在 `src/` 裡面，不在根目錄
- **模組導入路徑**：代碼設計時假設在 `src/api/` 目錄中運行
- **相對導入依賴**：所有 `from config import settings` 等導入都基於這個假設

### **2. 目錄結構與導入路徑**

```
D:\Prompt-Scribe\                    # 專案根目錄
├── src\
│   └── api\                        # 後端代碼目錄（工作目錄）
│       ├── main.py                 # 主應用文件
│       ├── config.py               # 配置文件
│       ├── routers\                # 路由目錄
│       └── services\               # 服務目錄
├── prompt-scribe-web\              # 前端代碼目錄
└── run_server.py                   # 後端啟動腳本
```

### **3. 前端開發原則**

#### **API 連接配置**：
```typescript
// 在 useInspireAgent.ts 中
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
```

#### **前端啟動**：
```bash
# 在 prompt-scribe-web 目錄中
cd prompt-scribe-web
npm run dev
```

### **4. 環境變數設置**

#### **後端環境變數**：
```bash
$env:SUPABASE_URL="http://localhost:54321"
$env:SUPABASE_ANON_KEY="test-key"
$env:OPENAI_API_KEY="your-openai-key"
```

#### **前端環境變數**：
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📋 **開發工作流程**

### **1. 啟動後端服務器**
```bash
# 方法 1：使用啟動腳本（推薦）
python run_server.py

# 方法 2：手動設置環境變數後啟動
$env:SUPABASE_URL="http://localhost:54321"
$env:SUPABASE_ANON_KEY="test-key"
python run_server.py
```

### **2. 啟動前端服務器**
```bash
cd prompt-scribe-web
npm run dev
```

### **3. 驗證服務器狀態**
```bash
# 檢查後端
Test-NetConnection -ComputerName localhost -Port 8000

# 檢查前端
Test-NetConnection -ComputerName localhost -Port 3001
```

## 🔧 **常見問題與解決方案**

### **問題 1：ModuleNotFoundError: No module named 'config'**
- **原因**：在錯誤的目錄中運行 uvicorn
- **解決**：使用 `run_server.py` 而不是直接運行 uvicorn

### **問題 2：前端 API 調用失敗**
- **原因**：API URL 配置錯誤
- **解決**：檢查 `NEXT_PUBLIC_API_URL` 環境變數

### **問題 3：導入路徑錯誤**
- **原因**：修改了相對導入路徑
- **解決**：保持原始導入方式，使用正確的啟動腳本

### **問題 4：Session not found（方法論與實戰）**

#### **🔍 標準修復 SOP（4 階段）**

**階段 1：快速診斷（5分鐘）**
```bash
# 1. 三步驗證法
/start → 記錄 session_id
/status/{session_id} → 檢查是否 404
/continue → 檢查是否 404

# 2. 日誌分析
grep "session_id" server_log.txt | tail -10
grep "Create session result" server_log.txt
```

**階段 2：根因分析（10分鐘）**
```bash
# 1. 代碼審查
- 檢查相關端點的完整流程
- 尋找重複邏輯或競爭條件
- 驗證方法名和依賴關係

# 2. 依賴檢查
- 確認所有方法名正確
- 檢查 import 和依賴注入
```

**階段 3：修復實施（15分鐘）**
```bash
# 1. 參考最佳實踐
- 查詢官方文檔（Context7）
- 學習標準模式

# 2. 分階段修復
- 先修復明顯錯誤（方法名、語法）
- 再優化架構問題（重複創建、競爭條件）
- 最後添加驗證機制（create → update → verify）
```

**階段 4：驗證測試（10分鐘）**
```bash
# 1. 強制重啟
taskkill /F /IM python.exe
python run_server.py

# 2. 完整測試
- 重新執行三步驗證
- 確認所有端點正常
- 檢查日誌一致性
```

#### **🎯 關鍵成功因素**

1. **不盲目修復**：先診斷再修復
2. **系統性思考**：從日誌到代碼到依賴關係
3. **參考權威**：查詢官方文檔和最佳實踐
4. **分階段實施**：一次解決一個問題
5. **強制驗證**：確保修改真的生效

#### **📋 實戰檢查清單**

- [ ] **快速定位**：固定一個 session_id，連續呼叫 `/api/inspire/start` → `/api/inspire/status/{id}` → `/api/inspire/continue`，看是哪一步出錯。
- [ ] **單一權威**：只允許 `/start` 建立 session；其他端點只讀/更新，避免多點新建造成競爭條件。
- [ ] **同步落庫**：`create → update → verify(get)` 三段式同步執行，verify 失敗就回 500，不吞錯。
- [ ] **一致日誌**：每步都打印 `session_id`、`phase`、`last_response_id`、`turn_count` 與 `create/update/verify` 結果。
- [ ] **Schema 快取錯誤**：若 Supabase 回 `PGRST204`（欄位不存在），先暫停寫入該欄位以確保主流程通，再排程修復 migration/schema-cache。
- [ ] **啟動原則**：後端一律 `python run_server.py`；若 reloader 不生效，殺掉殘留 python 後重啟。

## 📝 **文件更新原則**

### **當修改後端代碼時**：
1. 確保在 `src/api/` 目錄結構中工作

## 🤝 **協作修復原則**

### **核心承諾**

- **先嘗試、後回報**：先依「標準修復 SOP」完成快速診斷與初步修復；若 30 分鐘內無法穩定復現與修好，立即回報現況。
- **透明溝通**：不隱瞞、不拖延，所有阻礙（技術限制、外部依賴、權限、時間成本、不確定性）第一時間同步。
- **一次只解一件事**：分階段修復，每步都有明確預期結果與驗證方法。

### **何時立即升級討論**

- 需要重大重構或會影響架構邊界
- 依賴第三方（API/權限/基礎建設）而短期無法解決
- 風險或成本超出預期（時間 > 2 小時或影響關鍵路徑）
- 存在多個可行方案需要產品/技術決策

### **對話模板（回報與共識）**

```
🔍 問題分析
- 根因：...
- 影響範圍：...
- 已嘗試：A / B / C（含結果）

🧭 可行方案
- 方案A：預期成效 / 風險 / 時間
- 方案B：預期成效 / 風險 / 時間

🙋 需要決策
- 你傾向哪個？有無其他考量？

✅ 下一步
- 選A則：...
- 選B則：...
```

### **行為準則**

- **不瞎做**：每次修改皆有明確目標與驗證點
- **不重複**：相同錯誤不犯第二次，將教訓納入文檔（本檔）
- **不失控**：任何改動可回滾，避免大規模未驗證更動

2. 保持相對導入方式不變
3. 使用 `run_server.py` 測試修改

### **當修改前端代碼時**：
1. 確保在 `prompt-scribe-web/` 目錄中工作
2. 檢查 API 連接配置
3. 使用 `npm run dev` 測試修改

### **當添加新功能時**：
1. 後端：在 `src/api/` 目錄中添加
2. 前端：在 `prompt-scribe-web/` 目錄中添加
3. 更新相關文檔

## 🎯 **最佳實踐總結**

1. **永遠使用 `run_server.py` 啟動後端**
2. **永遠在 `prompt-scribe-web/` 目錄中啟動前端**
3. **不要修改相對導入路徑**
4. **保持目錄結構的一致性**
5. **在修改代碼前先理解現有的架構**

## 📚 **相關文件**

- `run_server.py` - 後端啟動腳本
- `prompt-scribe-web/package.json` - 前端配置
- `src/api/main.py` - 後端主應用
- `prompt-scribe-web/lib/hooks/useInspireAgent.ts` - 前端 API 連接

---

**最後更新**：2025-10-22  
**維護者**：AI Assistant  
**版本**：1.0.0
