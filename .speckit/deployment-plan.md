# 🚀 Speckit 部署計劃 - 修復測試與上線部署

**計劃編號**: SPECKIT-DEPLOY-001  
**版本**: V1.0.0  
**建立日期**: 2025-10-15  
**目標**: 修復測試問題並部署 V2.0.0 到生產環境  
**狀態**: 📋 規劃中

---

## 📊 前置作業檢查

### ✅ 已完成的部署前置

#### 1. 部署配置文件（全部完成）
- ✅ `Dockerfile` - Docker 容器配置
- ✅ `docker-compose.yml` - 服務編排（API + Redis + Redis Commander）
- ✅ `vercel.json` - Vercel 部署配置
- ✅ `railway.toml` - Railway 部署配置

#### 2. CI/CD 工作流（全部完成）
- ✅ `.github/workflows/api-tests.yml` - 自動測試（Python 3.9-3.13）
- ✅ `.github/workflows/api-deploy.yml` - 自動部署
- ✅ `.github/workflows/performance-check.yml` - 效能監控

#### 3. 核心功能（全部完成）
- ✅ 13 個核心服務模組
- ✅ 12 個 API 端點
- ✅ 77 個測試用例
- ✅ 完整文檔系統

#### 4. 資料庫（全部完成）
- ✅ Supabase 專案設置
- ✅ 140,782 筆標籤資料
- ✅ 12 個資料庫遷移
- ✅ RLS 政策和索引
- ✅ 安全性修復（今天完成）

### ❌ 需要修復的問題

#### 1. 代碼錯誤
**問題**: `src/api/main.py` 第 121 行
```python
if MIDDLEWARE_AVAILABLE:  # ← 變數未定義
    app.add_middleware(UsageLoggingMiddleware)
```

**影響**: 
- ❌ 測試完全無法運行（NameError）
- ❌ API 無法啟動
- ❌ 部署會失敗

**嚴重性**: 🔴 **Critical** - 必須立即修復

#### 2. 環境配置文件缺失
**問題**: 缺少 `.env.example` 文件

**影響**:
- ⚠️ 新開發者不知道需要哪些環境變數
- ⚠️ 部署時容易遺漏配置

**嚴重性**: 🟡 **Medium** - 建議修復

---

## 🎯 部署計劃 - 三階段執行

### 階段 1: 修復與驗證 ⚡ (優先級: P0 - Critical)

**目標**: 修復代碼錯誤，確保測試通過

#### Task 1.1: 修復 main.py 的 MIDDLEWARE_AVAILABLE 錯誤
**負責模組**: `src/api/main.py`  
**預估時間**: 10 分鐘  
**優先級**: 🔴 P0 - Critical

**修復方案**:
```python
# 在 main.py 頂部檢查並定義 MIDDLEWARE_AVAILABLE

# 方案 A: 條件導入（推薦）
try:
    from middleware.logging_middleware import UsageLoggingMiddleware
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    MIDDLEWARE_AVAILABLE = False
    logger.warning("⚠️ Usage logging middleware not available")

# 方案 B: 直接移除（如果不需要）
# 刪除第 121-123 行
```

**驗證**:
```bash
cd src/api
python -c "import main"  # 應該無錯誤
```

#### Task 1.2: 創建 .env.example 文件
**位置**: 專案根目錄  
**預估時間**: 5 分鐘  
**優先級**: 🟡 P1 - High

**內容**:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Application Settings
APP_NAME=Prompt-Scribe API
APP_VERSION=2.0.0
DEBUG=false
LOG_LEVEL=INFO

# Cache Configuration
CACHE_STRATEGY=hybrid  # Options: memory, redis, hybrid
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Redis Configuration (Optional)
REDIS_ENABLED=false
REDIS_URL=redis://localhost:6379/0

# CORS Settings
CORS_ORIGINS=*  # 生產環境應限制為特定域名

# Performance Settings
MAX_WORKERS=4
TIMEOUT=30
```

#### Task 1.3: 運行完整測試套件
**預估時間**: 5 分鐘  
**優先級**: 🔴 P0 - Critical

**執行**:
```bash
cd src/api
python -m pytest tests/ -v --tb=short --cov=services --cov=routers
```

**預期結果**:
- ✅ 77/77 測試通過（100%）
- ✅ 代碼覆蓋率 > 95%
- ✅ 無錯誤和警告

#### Task 1.4: 本地啟動測試
**預估時間**: 5 分鐘  
**優先級**: 🟡 P1 - High

**執行**:
```bash
cd src/api
uvicorn main:app --reload

# 另一個終端測試
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

**驗證檢查清單**:
- [ ] API 成功啟動（無錯誤）
- [ ] /health 端點回應 200
- [ ] /docs Swagger UI 可訪問
- [ ] 日誌顯示正常

---

### 階段 2: 環境準備 🔧 (優先級: P1 - High)

**目標**: 準備生產環境配置和 secrets

#### Task 2.1: 創建生產環境 .env 文件
**位置**: 本地（不提交到 Git）  
**預估時間**: 5 分鐘  
**優先級**: 🔴 P0 - Critical

**執行**:
```bash
# 複製範例文件
cp .env.example .env

# 編輯 .env 填入實際值
# SUPABASE_URL: https://fumuvmbhmmzkenizksyq.supabase.co
# SUPABASE_ANON_KEY: 從 Supabase Dashboard 獲取
```

**獲取 Supabase Keys**:
1. 訪問: https://app.supabase.com/project/fumuvmbhmmzkenizksyq/settings/api
2. 複製 **Project URL**
3. 複製 **anon public** key
4. 複製 **service_role secret** key（僅管理功能）

#### Task 2.2: 設置 GitHub Secrets（用於 CI/CD）
**平台**: GitHub Repository Settings  
**預估時間**: 10 分鐘  
**優先級**: 🟡 P1 - High

**需要設置的 Secrets**:
```
SUPABASE_URL=https://fumuvmbhmmzkenizksyq.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>

# 如果使用 Vercel
VERCEL_TOKEN=<your-vercel-token>
ORG_ID=<vercel-org-id>
PROJECT_ID=<vercel-project-id>

# 如果使用 Railway
RAILWAY_TOKEN=<your-railway-token>
```

**設置步驟**:
1. 前往 GitHub 倉庫
2. Settings → Secrets and variables → Actions
3. 點擊 "New repository secret"
4. 逐個添加上述 secrets

#### Task 2.3: 選擇部署平台
**預估時間**: 決策時間  
**優先級**: 🟢 P2 - Medium

**平台對比**:

| 平台 | 優點 | 缺點 | 適用場景 | 成本 |
|------|------|------|----------|------|
| **Vercel** | • 全球 CDN<br>• 零配置<br>• 自動 HTTPS | • 無 Redis<br>• 僅記憶體快取 | 快速原型<br>全球訪問 | Free |
| **Railway** | • Redis 支援<br>• 完整功能<br>• 簡單部署 | • 單區域 | 完整功能<br>需要 Redis | $5/月 |
| **Docker** | • 完全控制<br>• 本地/雲端 | • 需要自己管理 | 自主機<br>企業部署 | 依主機 |

**建議**: 
- **快速上線**: Vercel（5 分鐘部署）
- **完整功能**: Railway（Redis 快取）
- **企業級**: Docker + 自主機

---

### 階段 3: 部署上線 🚀 (優先級: P1 - High)

**目標**: 部署到選定平台並驗證

#### 選項 A: Vercel 部署（推薦快速開始）

**Task 3A.1: 安裝 Vercel CLI**
```bash
npm install -g vercel
```

**Task 3A.2: 登入 Vercel**
```bash
vercel login
```

**Task 3A.3: 部署到生產**
```bash
vercel --prod
```

**Task 3A.4: 設置環境變數**
```bash
vercel env add SUPABASE_URL production
vercel env add SUPABASE_ANON_KEY production
```

**Task 3A.5: 驗證部署**
```bash
curl https://your-project.vercel.app/health
curl https://your-project.vercel.app/docs
```

#### 選項 B: Railway 部署（推薦完整功能）

**Task 3B.1: 安裝 Railway CLI**
```bash
npm install -g @railway/cli
# 或
curl -fsSL https://railway.app/install.sh | sh
```

**Task 3B.2: 登入並初始化**
```bash
railway login
railway init
```

**Task 3B.3: 添加 Redis 服務**
```bash
railway add redis
```

**Task 3B.4: 設置環境變數**
```bash
railway variables set SUPABASE_URL=https://fumuvmbhmmzkenizksyq.supabase.co
railway variables set SUPABASE_ANON_KEY=your-key
railway variables set REDIS_ENABLED=true
```

**Task 3B.5: 部署**
```bash
railway up
```

**Task 3B.6: 獲取 URL 並驗證**
```bash
railway open
```

#### 選項 C: Docker 本地部署

**Task 3C.1: 創建 .env 文件**（已在 Task 2.1）

**Task 3C.2: 建置並啟動**
```bash
docker-compose up -d --build
```

**Task 3C.3: 查看日誌**
```bash
docker-compose logs -f api
```

**Task 3C.4: 驗證**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

**Task 3C.5: 停止服務**（如需要）
```bash
docker-compose down
```

---

### 階段 4: 驗證與監控 ✅ (優先級: P1 - High)

**目標**: 確保部署成功，系統健康運行

#### Task 4.1: 功能驗證
**預估時間**: 10 分鐘  
**檢查清單**:

```bash
# 1. 健康檢查
curl https://your-api-url/health
# 預期: {"status": "healthy", "version": "2.0.0"}

# 2. API 文檔
curl https://your-api-url/docs
# 預期: Swagger UI 頁面

# 3. 基礎端點
curl https://your-api-url/api/v1/stats
# 預期: 統計資訊

# 4. LLM 端點測試
curl -X POST https://your-api-url/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description": "cute girl", "max_results": 5}'
# 預期: 標籤推薦結果
```

#### Task 4.2: 效能驗證
**預估時間**: 10 分鐘

**測試腳本**:
```python
# test_deployment.py
import httpx
import time
import asyncio

async def test_performance():
    base_url = "https://your-api-url"
    
    # 測試響應時間
    start = time.time()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/api/llm/recommend-tags",
            json={"description": "cute girl", "max_results": 10}
        )
    duration = (time.time() - start) * 1000
    
    print(f"Response time: {duration:.2f}ms")
    print(f"Status: {response.status_code}")
    print(f"Tags: {len(response.json()['recommended_tags'])}")
    
    assert duration < 2000, "Response too slow"
    assert response.status_code == 200, "Request failed"

asyncio.run(test_performance())
```

**預期**:
- ✅ 響應時間 < 2000ms（目標 < 500ms）
- ✅ 狀態碼 200
- ✅ 正確返回推薦標籤

#### Task 4.3: 設置監控（可選）
**預估時間**: 30 分鐘  
**優先級**: 🟢 P2 - Medium

**選項**:
1. **Vercel Analytics** - 免費，自動整合
2. **Sentry** - 錯誤追蹤
3. **UptimeRobot** - 可用性監控

---

## 📋 執行檢查清單

### 階段 1: 修復與驗證（必須完成）

- [ ] **1.1** 修復 `MIDDLEWARE_AVAILABLE` 錯誤
- [ ] **1.2** 創建 `.env.example` 文件
- [ ] **1.3** 運行完整測試套件（確保 100% 通過）
- [ ] **1.4** 本地啟動 API 測試

### 階段 2: 環境準備（必須完成）

- [ ] **2.1** 創建生產環境 `.env` 文件
- [ ] **2.2** 從 Supabase 獲取 API Keys
- [ ] **2.3** 設置 GitHub Secrets（如使用 CI/CD）
- [ ] **2.4** 選擇部署平台

### 階段 3: 部署上線（選擇一種）

**選項 A: Vercel**
- [ ] **3A.1** 安裝 Vercel CLI
- [ ] **3A.2** 登入 Vercel
- [ ] **3A.3** 部署到生產
- [ ] **3A.4** 設置環境變數
- [ ] **3A.5** 驗證部署

**選項 B: Railway**
- [ ] **3B.1** 安裝 Railway CLI
- [ ] **3B.2** 登入並初始化
- [ ] **3B.3** 添加 Redis 服務
- [ ] **3B.4** 設置環境變數
- [ ] **3B.5** 部署
- [ ] **3B.6** 驗證部署

**選項 C: Docker**
- [ ] **3C.1** 創建 .env 文件
- [ ] **3C.2** 建置並啟動容器
- [ ] **3C.3** 查看日誌確認正常
- [ ] **3C.4** 驗證端點
- [ ] **3C.5** （可選）設置反向代理

### 階段 4: 驗證與監控（推薦完成）

- [ ] **4.1** 功能驗證（5 個核心端點）
- [ ] **4.2** 效能驗證（響應時間測試）
- [ ] **4.3** 設置監控（可選）

---

## ⚠️ 風險評估

### 高風險項目

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|----------|
| MIDDLEWARE_AVAILABLE 錯誤未修復 | 高 | 高 | ✅ Task 1.1 必須優先執行 |
| 環境變數未正確設置 | 中 | 高 | ✅ 詳細文檔和檢查清單 |
| Supabase 連接失敗 | 低 | 高 | ✅ 測試階段驗證連接 |

### 中低風險項目

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|----------|
| 部署平台問題 | 低 | 中 | 提供 3 種備選方案 |
| 效能不符預期 | 低 | 中 | 本地測試已驗證 |
| Redis 連接問題 | 中 | 低 | 可降級為記憶體快取 |

---

## 📊 時間估算

### 保守估算

```
階段 1: 修復與驗證
- 修復代碼錯誤:     10 分鐘
- 創建 .env.example: 5 分鐘
- 運行測試:         5 分鐘
- 本地啟動測試:     5 分鐘
小計: 25 分鐘

階段 2: 環境準備
- 創建 .env:        5 分鐘
- 獲取 API Keys:    5 分鐘
- 設置 GitHub Secrets: 10 分鐘
- 平台選擇:         5 分鐘
小計: 25 分鐘

階段 3: 部署上線（以 Vercel 為例）
- 安裝 CLI:        2 分鐘
- 登入:            2 分鐘
- 部署:            5 分鐘
- 設置環境變數:    5 分鐘
- 驗證:            5 分鐘
小計: 19 分鐘

階段 4: 驗證與監控
- 功能驗證:        10 分鐘
- 效能驗證:        10 分鐘
- 設置監控:        30 分鐘（可選）
小計: 20-50 分鐘

總計: 1.5-2 小時（含可選項目）
最快路徑: 1 小時（僅必要項目）
```

### 樂觀估算

```
如果一切順利:
- 修復錯誤: 5 分鐘
- 部署到 Vercel: 10 分鐘
- 驗證: 5 分鐘

最快: 20 分鐘
```

---

## 🎯 成功標準

### 階段 1 完成標準
- ✅ 代碼無錯誤（可以 import main）
- ✅ 測試 100% 通過（77/77）
- ✅ 本地 API 成功啟動
- ✅ Swagger UI 可訪問

### 階段 2 完成標準
- ✅ .env.example 文件完整
- ✅ 生產 .env 配置正確
- ✅ Supabase 連接測試成功
- ✅ 已選擇部署平台

### 階段 3 完成標準
- ✅ 應用成功部署到雲端
- ✅ 獲得公開訪問 URL
- ✅ HTTPS 自動配置
- ✅ 環境變數正確設置

### 階段 4 完成標準
- ✅ 所有核心端點正常工作
- ✅ 響應時間符合預期
- ✅ 無錯誤日誌
- ✅ （可選）監控已設置

---

## 🔄 回滾計劃

### 如果部署失敗

**Vercel**:
```bash
vercel rollback  # 回滾到上一個版本
```

**Railway**:
```bash
railway rollback  # 在 Railway Dashboard 操作
```

**Docker**:
```bash
docker-compose down
# 修復問題後
docker-compose up -d --build
```

### 如果發現嚴重 Bug

1. 立即回滾部署
2. 在本地修復問題
3. 運行完整測試
4. 重新部署

---

## 📞 緊急聯絡

### 問題分類

| 問題類型 | 處理方式 |
|----------|----------|
| 代碼錯誤 | 查看錯誤日誌，本地重現並修復 |
| 部署失敗 | 檢查部署日誌，驗證配置 |
| API 無回應 | 檢查健康端點，查看應用日誌 |
| 效能問題 | 查看監控數據，分析瓶頸 |

---

## 🎊 部署後行動

### 立即驗證（部署後 5 分鐘內）
1. ✅ 訪問 API 文檔
2. ✅ 測試核心端點
3. ✅ 檢查錯誤日誌

### 第一天監控
1. 📊 觀察響應時間
2. 📊 檢查錯誤率
3. 📊 驗證快取命中率

### 第一週優化
1. 🎯 收集使用數據
2. 🎯 分析實際效能
3. 🎯 根據數據調整配置

---

## 📚 相關文檔

- [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) - 詳細部署指南
- [.github/CICD_SETUP_GUIDE.md](../.github/CICD_SETUP_GUIDE.md) - CI/CD 設置
- [src/api/README.md](../src/api/README.md) - API 開發指南
- [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) - 專案架構

---

## ✅ Speckit 合規性

本計劃符合以下 Speckit 憲法原則：

- ✅ **架構不可變性**: 不修改核心架構，僅修復 bug
- ✅ **測試覆蓋要求**: 確保 100% 測試通過
- ✅ **文檔同步原則**: 創建必要的配置文檔
- ✅ **品質保證**: 多階段驗證確保品質
- ✅ **風險控制**: 詳細的風險評估和回滾計劃

---

**計劃狀態**: 📋 等待執行  
**預計完成時間**: 1-2 小時  
**成功機率**: 95%+  
**風險等級**: 🟢 低（有完整緩解措施）

---

> "好的部署計劃，就是成功的一半。"


