# 🚀 Zeabur 快速部署指南

**目標**: 5-10 分鐘內將 Prompt-Scribe API 部署到 Zeabur  
**更新日期**: 2025-10-17  
**狀態**: ✅ 生產就緒

---

## 🎯 為什麼選擇 Zeabur？

### 核心優勢

✅ **亞洲延遲最低** - 台灣/香港節點，20-50ms  
✅ **前後端一體** - 一個專案部署所有服務  
✅ **完整功能** - 支援 Redis、環境變數、監控  
✅ **成本最優** - $10-15/月（比 Vercel+Railway 省 50%）  
✅ **中文友好** - 繁體中文介面和文檔  

---

## ⚡ 快速開始（3 種方式）

### 方式 1: 使用 CLI（推薦）⭐⭐⭐

**5 分鐘完成部署**

```bash
# 1. 安裝 Zeabur CLI
npm install -g @zeabur/cli

# 2. 登入（會開啟瀏覽器）
zeabur login

# 3. 初始化專案（在 Prompt-Scribe 目錄）
cd d:\Prompt-Scribe
zeabur init

# 4. 部署
zeabur deploy

# 5. 添加 Redis（在 Dashboard 或用 CLI）
zeabur service add redis

# 6. 設定環境變數（在 Dashboard）
# 訪問: https://dash.zeabur.com
# 設定 SUPABASE_URL 和 SUPABASE_ANON_KEY

# 7. 完成！
# 你的 API 會在: https://your-project.zeabur.app
```

---

### 方式 2: 使用 GitHub 整合（最簡單）⭐⭐⭐⭐⭐

**零 CLI，純網頁操作**

#### 步驟 1: 推送程式碼到 GitHub

```bash
# 確認程式碼已推送
git status
git push origin main
```

#### 步驟 2: 在 Zeabur 創建專案

1. 訪問 [Zeabur Dashboard](https://dash.zeabur.com)
2. 點擊「Create New Project」
3. 選擇「Import from GitHub」
4. 授權 GitHub 訪問
5. 選擇 `azuma520/Prompt-Scribe` 倉庫
6. 點擊「Deploy」

#### 步驟 3: 配置服務

**檢測結果**:
- ✅ Zeabur 會自動檢測到 Python 專案
- ✅ 自動讀取 `zeabur.yaml` 配置
- ✅ 自動安裝依賴

**你需要做的**:
1. 在 Dashboard 點擊 API 服務
2. 進入「Environment Variables」
3. 添加以下變數：

```
SUPABASE_URL=https://fumuvmbhmmzkenizksyq.supabase.co
SUPABASE_ANON_KEY=你的-anon-key
```

#### 步驟 4: 添加 Redis

1. 在專案頁面點擊「Add Service」
2. 選擇「Redis」
3. 點擊「Deploy」
4. Redis 會自動連接到 API（環境變數自動注入）

#### 步驟 5: 驗證部署

```bash
# 檢查健康狀態
curl https://your-project.zeabur.app/health

# 測試 API
curl -X POST https://your-project.zeabur.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description":"cute girl in school uniform"}'
```

✅ **完成！API 已上線！**

---

### 方式 3: 使用配置文件（進階）

**適合**: 需要精細控制配置的用戶

已為您準備好配置文件：
- ✅ `zeabur.yaml` - 主要配置
- ✅ `.zeabur/config.json` - 詳細配置

**部署**:
```bash
# 1. 確認配置文件存在
ls zeabur.yaml
ls .zeabur/config.json

# 2. 部署（自動讀取配置）
zeabur deploy

# 3. 配置會自動應用
```

---

## 📋 環境變數設定

### 必需變數（必須在 Dashboard 設定）

| 變數名 | 說明 | 獲取方式 | 範例 |
|--------|------|----------|------|
| `SUPABASE_URL` | Supabase 專案 URL | Dashboard → Settings → API | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase 公開金鑰 | Dashboard → Settings → API → anon public | `eyJhbGc...` |

### 自動配置的變數（Zeabur 自動注入）

| 變數名 | 說明 | 來源 |
|--------|------|------|
| `PORT` | 應用端口 | Zeabur 自動提供 |
| `REDIS_URL` | Redis 連接 URL | 添加 Redis 服務後自動注入 |
| `ZEABUR_DOMAIN` | 應用域名 | Zeabur 自動提供 |

### 已預配置的變數（在 zeabur.yaml）

這些變數已在配置文件中設定，不需要手動添加：
- `REDIS_ENABLED=true`
- `CACHE_STRATEGY=hybrid`
- `APP_VERSION=2.0.2`
- `DEBUG=false`
- 等等...

---

## 🔧 詳細配置說明

### zeabur.yaml 配置解析

```yaml
name: prompt-scribe-api  # 專案名稱

services:
  api:
    source:
      type: git
      path: ./src/api     # API 程式碼路徑
    
    build:
      runtime: python:3.11           # Python 版本
      buildCommand: pip install ...  # 安裝依賴
      startCommand: uvicorn ...      # 啟動命令
    
    resources:
      memory: 1024  # 1GB 記憶體（推薦）
      cpu: 1        # 1 vCPU
    
    health:
      path: /health  # 健康檢查端點
      interval: 30   # 每 30 秒檢查一次

  redis:
    image: redis:7-alpine  # Redis 映像
    resources:
      memory: 256  # 256MB（夠用）
```

### 為什麼這樣配置？

**記憶體 1GB**:
- FastAPI + 依賴: ~400MB
- 記憶體快取: ~300MB
- 系統開銷: ~200MB
- 緩衝: ~100MB

**Redis 256MB**:
- 快取資料: ~150MB
- Redis 開銷: ~50MB
- 緩衝: ~56MB

---

## 🌏 區域選擇建議

### 可用區域

| 區域 | 延遲（從台灣） | 適合 | 推薦度 |
|------|---------------|------|--------|
| **Hong Kong** | 20-30ms | 台灣/香港用戶 | ⭐⭐⭐⭐⭐ |
| **Singapore** | 50-80ms | 東南亞用戶 | ⭐⭐⭐⭐ |
| **Tokyo** | 40-60ms | 日本/台灣用戶 | ⭐⭐⭐⭐ |
| **US West** | 150-200ms | 美國西岸 | ⭐⭐ |

**建議**: 
- 主要用戶在台灣/香港 → 選 **Hong Kong**
- 主要用戶在東南亞 → 選 **Singapore**
- 主要用戶在日本 → 選 **Tokyo**

**修改方式**:
```yaml
# zeabur.yaml
region: hong-kong  # 或 singapore, tokyo
```

---

## 🎯 部署後驗證清單

### 基本驗證

```bash
# 1. 健康檢查
curl https://your-project.zeabur.app/health

# 預期回應:
# {"status":"healthy","version":"2.0.2","timestamp":...}

# 2. 快取健康檢查
curl https://your-project.zeabur.app/cache/health

# 預期回應:
# {"status":"healthy","cache_type":"hybrid","redis_available":true}

# 3. 測試核心功能
curl -X POST https://your-project.zeabur.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description":"1girl in school"}'

# 預期: 返回推薦標籤列表
```

### 進階驗證

```bash
# 4. 檢查快取統計
curl https://your-project.zeabur.app/cache/stats

# 5. 測試批量查詢
curl "https://your-project.zeabur.app/api/v1/tags?limit=10"

# 6. 測試智能組合
curl -X POST https://your-project.zeabur.app/api/llm/suggest-combinations \
  -H "Content-Type: application/json" \
  -d '{"tags":["1girl","solo"]}'
```

### Dashboard 檢查

登入 [Zeabur Dashboard](https://dash.zeabur.com)：

- [ ] API 服務狀態: Running ✅
- [ ] Redis 服務狀態: Running ✅
- [ ] 環境變數已設定: SUPABASE_URL, SUPABASE_ANON_KEY ✅
- [ ] 日誌無錯誤 ✅
- [ ] 健康檢查通過 ✅

---

## 💰 成本估算

### 小型專案（< 1000 用戶/天）

**資源使用**:
- API: 1GB RAM, 1 CPU
- Redis: 256MB
- 流量: 20GB/月
- 運行時間: 720 小時/月

**預估費用**: **$10-15/月**

### 中型專案（1000-5000 用戶/天）

**資源使用**:
- API: 2GB RAM, 2 CPU（自動擴展）
- Redis: 512MB
- 流量: 100GB/月
- 運行時間: 720 小時/月

**預估費用**: **$20-30/月**

### 與其他方案對比

| 方案 | 小型 | 中型 | 備註 |
|------|------|------|------|
| **Zeabur** | $10-15 | $20-30 | 前端+後端+Redis ⭐ |
| Vercel + Railway | $20-30 | $40-60 | 需管理兩平台 |
| Railway | $20-25 | $35-50 | 僅後端，前端另找 |

**結論**: Zeabur 省 **40-50% 成本**！

---

## 🔧 常見問題

### Q1: 如何查看部署日誌？

**在 Dashboard**:
1. 進入專案
2. 點擊 API 服務
3. 點擊「Logs」標籤
4. 即時查看日誌

**使用 CLI**:
```bash
zeabur logs api
# 或即時查看
zeabur logs api --follow
```

---

### Q2: 如何設定自訂域名？

**步驟**:
1. Dashboard → API 服務 → Domains
2. 點擊「Add Domain」
3. 輸入域名：`api.your-domain.com`
4. 按照指示設定 DNS（CNAME 記錄）
5. 等待 SSL 憑證自動配置（1-5 分鐘）

**DNS 設定**:
```
類型: CNAME
名稱: api
值: your-project.zeabur.app
```

---

### Q3: 如何更新程式碼？

**自動部署**（推薦）:
```bash
# 推送到 GitHub
git add .
git commit -m "update: 新功能"
git push origin main

# Zeabur 自動偵測並重新部署（1-2 分鐘）
```

**手動部署**:
```bash
zeabur deploy
```

---

### Q4: 如何擴展資源？

**在 Dashboard**:
1. 點擊 API 服務
2. 進入「Resources」
3. 調整記憶體/CPU
4. 儲存（自動重啟）

**建議配置**:

| 用戶量 | 記憶體 | CPU | 成本增加 |
|--------|--------|-----|---------|
| < 1K | 512MB | 0.5 | $0 |
| 1K-5K | 1GB | 1 | +$5 |
| 5K-10K | 2GB | 2 | +$10 |
| 10K+ | 考慮自動擴展 | - | 動態 |

---

### Q5: Redis 連接有問題？

**檢查步驟**:

1. **確認 Redis 已部署**
   ```bash
   # Dashboard 查看 Redis 狀態
   # 應該顯示: Running
   ```

2. **檢查環境變數**
   ```bash
   # API 服務的環境變數應該有:
   REDIS_URL=redis://redis:6379
   # Zeabur 自動注入
   ```

3. **查看日誌**
   ```bash
   zeabur logs api
   # 應該看到: "Cache system: healthy (hybrid)"
   ```

4. **測試連接**
   ```bash
   curl https://your-project.zeabur.app/cache/health
   # 應該返回: {"redis_available": true}
   ```

---

## 📊 部署架構圖

### Zeabur 上的 Prompt-Scribe

```
┌──────────────────────────────────────────────┐
│           Zeabur 專案（香港節點）             │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  API 服務 (FastAPI)                    │ │
│  │  - 記憶體: 1GB                         │ │
│  │  - CPU: 1 vCPU                        │ │
│  │  - 端口: 8000                         │ │
│  │  - 健康檢查: /health                   │ │
│  └────────────────────────────────────────┘ │
│                  ↓ 內網連接（< 1ms）         │
│  ┌────────────────────────────────────────┐ │
│  │  Redis 服務                            │ │
│  │  - 記憶體: 256MB                       │ │
│  │  - 持久化: 啟用                        │ │
│  │  - 快取策略: LRU                       │ │
│  └────────────────────────────────────────┘ │
│                                              │
└──────────────────────────────────────────────┘
                    ↓
        外部網路連接（50-100ms）
                    ↓
          ┌──────────────────┐
          │   Supabase       │
          │  (PostgreSQL)    │
          │  140K+ 標籤      │
          └──────────────────┘
```

### 請求流程

```
用戶（台灣）
    ↓ (20-30ms)
Zeabur 香港節點
    ├─ API 處理請求 (10ms)
    ├─ 檢查 Redis 快取 (1ms)
    │  ├─ 命中 → 立即返回 ✅
    │  └─ 未命中 ↓
    └─ 查詢 Supabase (50-80ms)
       └─ 儲存到 Redis
       └─ 返回結果

總延遲: 30-50ms（快取命中）
       80-120ms（未命中）

對比 Vercel: 120-200ms
快 2-3 倍！
```

---

## 🎯 進階配置

### 自動擴展設定

編輯 `zeabur.yaml`:

```yaml
scaling:
  api:
    min: 1      # 至少 1 個實例
    max: 3      # 最多 3 個（高流量時自動擴展）
    metric: cpu
    target: 70  # CPU > 70% 時擴展
```

**效果**:
- 正常流量: 1 個實例（$10/月）
- 高流量: 自動擴展到 2-3 個
- 流量降低: 自動縮減回 1 個

---

### 自訂域名設定

**方式 1: 在 Dashboard**
1. API 服務 → Domains → Add Domain
2. 輸入: `api.your-domain.com`
3. 設定 DNS CNAME
4. 等待 SSL 自動配置

**方式 2: 在 zeabur.yaml**
```yaml
services:
  api:
    domains:
      - domain: api.your-domain.com
```

**DNS 設定**（在您的域名服務商）:
```
類型: CNAME
名稱: api
值: your-project.zeabur.app
TTL: 3600
```

---

### CORS 白名單（生產環境）

**開發階段**（當前）:
```yaml
env:
  - key: CORS_ORIGINS
    value: "*"  # 允許所有來源
```

**生產環境**（前端上線後）:
```yaml
env:
  - key: CORS_ORIGINS
    value: '["https://your-frontend.zeabur.app","https://your-domain.com"]'
```

---

## 🚨 故障排除

### 問題 1: 部署失敗

**症狀**: Build 或 Deploy 失敗

**檢查**:
```bash
# 1. 查看部署日誌
zeabur logs api --build

# 2. 常見原因:
# - requirements.txt 依賴衝突
# - Python 版本不符
# - 啟動命令錯誤
```

**解決**:
```bash
# 本地測試部署
cd src/api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# 確保本地可以運行，再部署
```

---

### 問題 2: 環境變數未生效

**症狀**: API 無法連接 Supabase

**檢查**:
```bash
# 1. Dashboard 確認環境變數已設定
# 2. 重新部署（環境變數更改需重啟）
zeabur redeploy api

# 3. 查看日誌確認
zeabur logs api | grep SUPABASE
```

---

### 問題 3: Redis 連接失敗

**症狀**: `/cache/health` 顯示 `redis_available: false`

**檢查**:
```bash
# 1. 確認 Redis 服務已部署
# Dashboard 應顯示 Redis: Running

# 2. 確認環境變數
# REDIS_URL 應該自動注入

# 3. 檢查網路連接
zeabur logs api | grep -i redis
```

**解決**:
```bash
# 重新部署 Redis
zeabur service redeploy redis

# 重新部署 API
zeabur service redeploy api
```

---

## 📊 效能優化建議

### 快取優化

**當前配置**（已優化）:
```yaml
CACHE_STRATEGY=hybrid    # 混合快取（最佳）
HYBRID_L1_TTL=300        # L1（記憶體）5 分鐘
HYBRID_L2_TTL=3600       # L2（Redis）1 小時
```

**監控快取效能**:
```bash
curl https://your-project.zeabur.app/cache/stats

# 目標指標:
# - hit_rate > 80%（快取命中率）
# - avg_latency < 50ms
```

### 資料庫連接池

**調整**（如果 QPS 很高）:
```yaml
env:
  - key: DB_CONNECTION_POOL_SIZE
    value: "20"  # 預設 10，高流量時增加
```

---

## 🎉 部署完成後

### 你會得到

✅ **API URL**: `https://your-project.zeabur.app`  
✅ **健康檢查**: `https://your-project.zeabur.app/health`  
✅ **API 文檔**: `https://your-project.zeabur.app/docs`  
✅ **Redis 快取**: 已啟用（混合快取）  
✅ **自動部署**: Git push 自動觸發  
✅ **監控日誌**: Dashboard 即時查看  
✅ **SSL 憑證**: 自動配置  

### 告訴前端開發者

```javascript
// 前端連接 API
const API_URL = 'https://your-project.zeabur.app';

// 測試連接
fetch(`${API_URL}/health`)
  .then(res => res.json())
  .then(data => console.log('API 健康狀態:', data));

// 使用 API
fetch(`${API_URL}/api/llm/recommend-tags`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ description: 'cute girl' })
})
  .then(res => res.json())
  .then(data => console.log('推薦標籤:', data));
```

---

## 📚 相關文檔

### Zeabur 官方
- [Zeabur 文檔（繁中）](https://zeabur.com/docs/zh-TW)
- [Python 部署指南](https://zeabur.com/docs/zh-TW/guides/python)
- [Redis 服務](https://zeabur.com/docs/zh-TW/marketplace/redis)

### 本專案
- [Vercel → Zeabur 遷移指南](ZEABUR_MIGRATION.md)
- [完整部署指南](DEPLOYMENT_GUIDE.md)
- [API 文檔](https://your-project.zeabur.app/docs)

---

## 🆘 需要幫助？

### Zeabur 支援
- 📖 [文檔中心](https://zeabur.com/docs/zh-TW)
- 💬 [Discord 社群](https://discord.gg/zeabur)（中文）
- 📧 Email: support@zeabur.com

### Prompt-Scribe 支援
- 🐛 [GitHub Issues](https://github.com/azuma520/Prompt-Scribe/issues)
- 💬 [GitHub Discussions](https://github.com/azuma520/Prompt-Scribe/discussions)

---

## ✅ 檢查清單

### 部署前

- [ ] GitHub 程式碼已推送
- [ ] Supabase URL 和 Key 已準備好
- [ ] 註冊 Zeabur 帳號
- [ ] 安裝 Zeabur CLI（如果用 CLI）

### 部署中

- [ ] 專案已創建
- [ ] API 服務已部署
- [ ] Redis 已添加
- [ ] 環境變數已設定（SUPABASE_URL, SUPABASE_ANON_KEY）
- [ ] 服務狀態: Running

### 部署後

- [ ] 健康檢查通過
- [ ] 快取系統正常
- [ ] API 功能測試通過
- [ ] 日誌無錯誤
- [ ] （可選）自訂域名已設定

---

**準備好了嗎？開始部署！** 🚀

選擇您喜歡的方式：
- **方式 1（CLI）**: 適合熟悉命令行的開發者
- **方式 2（GitHub）**: 適合所有人，最簡單 ⭐

**預計時間**: 5-10 分鐘  
**難度**: ⭐ 超簡單

---

**最後更新**: 2025-10-17  
**狀態**: ✅ 已準備就緒，可立即部署

