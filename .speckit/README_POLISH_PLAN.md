# 📋 README 細節打磨計畫

**版本**: 1.0  
**創建日期**: 2025-10-17  
**基於**: 用戶深度分析反饋  
**目標**: 消除一致性問題，提升專業度到 99%

---

## 🎯 問題清單（已驗證）

### 🔴 P0 - 一致性問題（立即修正）

| 問題 | 位置 | 影響 | 修正 |
|------|------|------|------|
| Python 版本不一致 | Badge 3.9+, 文中 3.11+ | 混淆 | 統一為 3.9+ |
| .env.example 不一致 | 3 處 env.example, 1 處 .env.example | 命令錯誤 | 統一為 env.example |
| 文件名不一致 | P1_P2_OPTIMIZATION_COMPLETE vs FINAL_SUMMARY | 連結失效 | 統一為 P1_P2_OPTIMIZATION_COMPLETE.md |
| 大小寫不一致 | prompt-scribe vs Prompt-Scribe | Clone 失敗 | 統一為 Prompt-Scribe |

### 🟡 P1 - DX 改善（建議補充）

| 項目 | 當前 | 建議 |
|------|------|------|
| OS 指令 | 僅單一系統 | Windows/Mac/Linux 並列 |
| 錯誤範例 | 僅成功案例 | 補充 400/401 錯誤 |
| OpenAPI | 未提及 | 補充 /openapi.json 連結 |
| 安全說明 | 缺少 | 補充認證與速率限制說明 |

### 🟢 P2 - 進階優化（可選）

| 項目 | 價值 |
|------|------|
| Postman Collection | 方便測試 |
| 架構 PNG 圖 | 視覺化 |
| 量測條件說明 | 專業度 |

---

## 🚀 執行計畫

### Task 1: Python 版本統一（5 分鐘）

**問題**: Badge 顯示 3.9+，但架構圖寫 3.11+

**決策**: 
- 實際支援：3.9+ (requirements.txt 標註)
- CI 測試：3.9-3.13
- 推薦版本：3.11+

**統一方案**:
```markdown
- Badge: 3.9+ (實際最低支援)
- 架構圖: 3.9+ (一致)
- 說明補充：推薦 3.11+，CI 已驗證 3.9-3.13
```

**修改位置**:
- README.md 第 105 行：`Python 3.11+` → `Python 3.9+（推薦 3.11+）`

---

### Task 2: .env 檔名統一（3 分鐘）

**問題**: 3 處 `env.example`，1 處 `.env.example`

**決策**: 實際檔案是 `env.example`（已驗證）

**統一方案**: 所有地方都使用 `env.example`

**修改位置**:
- README.md 第 173 行：`.env.example` → `env.example`

---

### Task 3: 文件連結統一（5 分鐘）

**問題**: 同時提到兩個不同檔名

**決策**: 實際存在 `docs/P1_P2_OPTIMIZATION_COMPLETE.md`

**統一方案**: 
- 移除對 `P1_P2_FINAL_SUMMARY.md` 的引用
- 或創建符號連結

**修改位置**:
- README.md 第 483 行

---

### Task 4: OS 指令並列（10 分鐘）

**新增**: 跨平台指令說明

**位置**: 快速開始區塊

**內容**:
```markdown
### 💻 跨平台指令參考

#### 啟用虛擬環境
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 開啟 API 文檔
```bash
# Windows
start "" http://localhost:8000/docs

# macOS
open http://localhost:8000/docs

# Linux
xdg-open http://localhost:8000/docs
```
```

---

### Task 5: 補充安全說明（10 分鐘）

**新增**: 認證與速率限制區塊

**位置**: 環境變數配置之後

**內容**:
```markdown
## 🔒 安全與速率限制

### 當前狀態（Demo 環境）

- ✅ **匿名可用**: 生產 API 目前開放匿名訪問
- ⚠️ **速率限制**: 建議實施（每 IP 每分鐘 60 次）
- ⚠️ **政策變更**: Demo 期間開放，可能隨時調整

### 生產環境建議

**啟用認證**:
```bash
# 使用 API Key（推薦）
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-api/api/llm/recommend-tags
```

**CORS 白名單**:
```bash
# .env（生產環境）
CORS_ORIGINS=["https://your-app.com","https://your-other-app.com"]
# 不要使用 CORS_ORIGINS=*
```

**速率限制**:
- 建議：每 IP 60 req/min
- 工具：使用 slowapi 或 FastAPI-Limiter
- 回應：429 Too Many Requests

📖 **詳細配置**: 查看 [安全最佳實踐](docs/SECURITY.md)（待建立）
```

---

### Task 6: 錯誤回應範例（10 分鐘）

**新增**: API 使用範例中的錯誤案例

**位置**: 使用範例區塊

**內容**:
```markdown
### 常見錯誤與處理

#### 缺少必需參數（400 Bad Request）
```bash
curl -X POST https://prompt-scribe-api.vercel.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{}'
```

回應:
```json
{
  "detail": [
    {
      "loc": ["body", "description"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 無效的標籤格式（422 Unprocessable Entity）
```bash
curl -X POST https://prompt-scribe-api.vercel.app/api/llm/validate-prompt \
  -H "Content-Type: application/json" \
  -d '{"tags": "not-an-array"}'
```

💡 **提示**: 查看完整錯誤代碼對照表 → [Troubleshooting](#-故障排除troubleshooting)
```

---

### Task 7: OpenAPI JSON 連結（3 分鐘）

**新增**: OpenAPI 規格下載連結

**位置**: API 文檔區塊

**內容**:
```markdown
### 核心文檔
- [📘 API 文檔（雲端）](https://prompt-scribe-api.vercel.app/docs) - Swagger UI
- [📘 API 文檔（本機）](http://localhost:8000/docs) - 本地開發
- [📄 OpenAPI JSON](https://prompt-scribe-api.vercel.app/openapi.json) - 匯入 Postman/Insomnia
```

---

### Task 8: 效能數據量測條件（5 分鐘）

**新增**: 效能指標腳註

**位置**: 效能指標表格之後

**內容**:
```markdown
**量測條件**: 
- 環境: Vercel Serverless (512MB, 1 vCPU)
- 工具: wrk 30s 壓測, 50 並發連接
- 資料集: 140,782 標籤
- 區域: Asia Pacific (Singapore)
- 快取: 混合快取啟用（90%+ 命中率）
```

---

## 📊 優先級與時間

| Task | 優先級 | 時間 | ROI |
|------|--------|------|-----|
| 1. Python 版本統一 | 🔴 P0 | 5min | ⭐⭐⭐⭐⭐ |
| 2. .env 檔名統一 | 🔴 P0 | 3min | ⭐⭐⭐⭐⭐ |
| 3. 文件連結統一 | 🔴 P0 | 5min | ⭐⭐⭐⭐ |
| 4. OS 指令並列 | 🟡 P1 | 10min | ⭐⭐⭐⭐ |
| 5. 安全說明 | 🟡 P1 | 10min | ⭐⭐⭐ |
| 6. 錯誤範例 | 🟡 P1 | 10min | ⭐⭐⭐ |
| 7. OpenAPI 連結 | 🟢 P2 | 3min | ⭐⭐ |
| 8. 量測條件 | 🟢 P2 | 5min | ⭐⭐ |

**總計**: 51 分鐘

---

## ✅ 執行建議

### 方案 A: 全部執行（推薦）
- 時間: 51 分鐘
- 完成度: 100%
- 專業度: 99%

### 方案 B: 僅 P0（快速修正）
- 時間: 13 分鐘
- 完成度: 核心問題
- 專業度: 95%

### 方案 C: P0 + P1（平衡）
- 時間: 36 分鐘
- 完成度: 主要問題
- 專業度: 97%

---

**建議**: 方案 A（全部執行）  
**原因**: 51 分鐘內完成所有細節，達到 99% 專業度

---

**創建日期**: 2025-10-17  
**狀態**: 🟡 待確認執行

