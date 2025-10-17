# 🤖 Prompt-Scribe API

> **LLM-Friendly Tag Recommendation System**  
> 專為 AI 圖像生成優化的智能標籤推薦 API

[![Version](https://img.shields.io/badge/version-2.0.2-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-98.7%25%20passing-brightgreen.svg)](src/api/tests/)
[![Production](https://img.shields.io/badge/production-live-brightgreen.svg)](https://prompt-scribe-api.vercel.app)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-automated-success.svg)](.github/workflows/)
[![Deploy](https://img.shields.io/badge/deploy-multi--platform-blue.svg)](DEPLOYMENT_GUIDE.md)

---

## 🌐 生產環境

### 🚀 Live API
- **生產 URL**: https://prompt-scribe-api.vercel.app
- **健康檢查**: https://prompt-scribe-api.vercel.app/health
- **狀態**: ✅ 運行中
- **平台**: Vercel Serverless Functions

### 🛠️ 本地開發環境
- **本地 URL**: http://localhost:8000
- **健康檢查**: http://localhost:8000/health
- **API 文檔**: http://localhost:8000/docs（本機）/ https://prompt-scribe-api.vercel.app/docs（雲端）
- **狀態**: ✅ 已配置並測試通過

#### 快速啟動本地環境

**Windows**:
```bash
# 1. 激活虛擬環境
venv\Scripts\activate

# 2. 啟動本地伺服器
python local_test.py

# 3. 開啟瀏覽器
start "" http://localhost:8000
```

**macOS/Linux**:
```bash
# 1. 激活虛擬環境
source venv/bin/activate

# 2. 啟動本地伺服器
python local_test.py

# 3. 開啟瀏覽器（macOS）
open http://localhost:8000
# 或 Linux
xdg-open http://localhost:8000
```

---

## 🚀 立即試用（5 秒開始）

### 一鍵測試 Live API

複製以下指令到終端機即可測試：

```bash
# 測試 1: 健康檢查 ✅
curl https://prompt-scribe-api.vercel.app/health

# 測試 2: 智能標籤推薦（核心功能）🎯
curl -X POST https://prompt-scribe-api.vercel.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description":"cute girl in school uniform"}'

# 測試 3: 智能組合建議（V2.0 新功能）⭐
curl -X POST https://prompt-scribe-api.vercel.app/api/llm/suggest-combinations \
  -H "Content-Type: application/json" \
  -d '{"tags":["1girl","long_hair"]}'
```

### 💡 互動式測試

想要更方便的測試體驗？打開 **[API 互動式文檔](https://prompt-scribe-api.vercel.app/docs)** 可直接在瀏覽器中測試所有端點。

### ⚡ 零配置雲端測試（免本機！）

不想安裝任何東西？直接測試雲端 API：

```bash
# 健康檢查（雲端）
curl -s https://prompt-scribe-api.vercel.app/health

# 智能標籤推薦（雲端）
curl -s -X POST https://prompt-scribe-api.vercel.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description":"a lonely girl in cyberpunk city at night"}'

# 智能組合建議（雲端）
curl -s -X POST https://prompt-scribe-api.vercel.app/api/llm/suggest-combinations \
  -H "Content-Type: application/json" \
  -d '{"tags":["1girl","long_hair"]}'
```

💡 **提示**: 以上指令直接使用生產環境 API，無需任何設置！

---

## 🎯 5 分鐘理解 Prompt-Scribe

### 一句話定位
**兩階段 AI 提示詞（prompt）資料系統**：本地清洗與標記 → 雲端向量化與 API 服務

### 系統架構

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────┐
│   Stage 1       │      │    Stage 2       │      │   使用者     │
│  本地資料處理    │ ───> │   雲端 API 服務   │ <─── │  LLM/Apps   │
│  (SQLite)       │      │  (Supabase+API)  │      │             │
└─────────────────┘      └──────────────────┘      └─────────────┘
   Python 3.9+            FastAPI + Redis           REST API
  （推薦 3.11+）          pgvector 向量化           多平台部署
   140K+ 標籤處理          語意搜尋支援              結構化存取
```

### 核心價值主張

| 特性 | 說明 | 為什麼重要 |
|------|------|-----------|
| 🏠 **資料主權** | 本地完全控制原始資料 | 敏感資料不上雲，符合法規 |
| 📋 **規格驅動** | `.speckit/` 目錄管理所有規格 | 可審計、可追溯、可協作 |
| 🤖 **LLM 職責分離** | 清楚界定 LLM 處理範圍 | 成本可控、結果可預測 |
| ✅ **資料品質** | 多階段驗證與標記 | 高品質輸入 → 高品質輸出 |

### 技術亮點（V2.0）

- ⚡ **多級關鍵字權重** - 名詞 1.0、形容詞 0.85、介詞 0.3（智能識別詞性）
- 🔤 **N-gram 複合詞匹配** - 優先識別 "school uniform" 等複合概念
- 🎨 **智能組合建議** - 10+ 預定義模式，自動推薦完整標籤組合
- 💾 **雙層快取架構** - L1 記憶體 + L2 Redis，命中率 90%+
- 🌍 **全球邊緣部署** - Vercel CDN，P90 延遲 319ms

### 效能指標（實測 vs 目標）

| 指標 | V1.0 | **V2.0** | 提升 | 狀態 |
|------|------|----------|------|------|
| 準確率 | 70-80% | **85-90%** | +15% | ✅ 超標 |
| 響應時間 (P90) | 350ms | **319ms** | -9% | ✅ 超標 |
| 吞吐量 | 100 req/s | **770 req/s** | 7.7x | ✅ 超標 |
| 測試覆蓋 | 63% | **98.7%** | +35.7% | ✅ 超標 |
| 部署方案 | 1 種 | **4 種** | 4x | ✅ 完成 |

**量測條件**: 
- 📍 環境: Vercel Serverless (512MB 記憶體, 1 vCPU)
- 🔧 工具: wrk 30s 壓測, 50 並發連接
- 📊 資料集: 140,782 標籤
- 🌏 區域: Asia Pacific (Singapore)
- 💾 快取: 混合快取啟用（命中率 90%+）

---

## ✨ 特色功能

### 🎯 V2.0 - Production-Grade Release

- ⚡ **智能關鍵字分析** - 多級權重系統，主詞優先匹配
- 🔤 **N-gram 複合詞** - 優先識別 "school uniform" 等複合概念
- 🎨 **智能組合建議** - 自動推薦完整的標籤組合模式
- 💾 **雙層快取架構** - 記憶體 + Redis 混合快取，命中率 90%+
- 🌍 **全球邊緣部署** - 支援 Vercel/Railway/Docker/自主機
- 🤖 **CI/CD 自動化** - 多版本測試，自動部署，效能監控
- 📊 **使用數據收集** - 數據驅動優化決策

### 📈 效能指標

| 指標 | V1.0 | **V2.0** | 改善 |
|------|------|----------|------|
| **準確率** | 70-80% | **85-90%** | +15-20% ⭐ |
| **響應時間 (P90)** | 350ms | **319ms** | -9% ⭐ |
| **吞吐量** | 100 req/s | **770 req/s** | 7.7x ⭐ |
| **測試通過率** | 63% | **98.7%** | +35.7% ⭐ |
| **部署方案** | 1 種 | **4 種** | 4x ⭐ |

---

## 🚀 快速開始

### 方式 1: 使用 Docker（推薦）

```bash
# 克隆專案
git clone https://github.com/azuma520/Prompt-Scribe.git
cd Prompt-Scribe

# 配置環境變數
cp env.example .env
# 編輯 .env 設置 SUPABASE_URL 和 SUPABASE_ANON_KEY

# 啟動服務（包含 API + Redis）
docker-compose up -d

# 驗證
curl http://localhost:8000/health
```

### 方式 2: 本地開發

```bash
# 安裝依賴
cd src/api
pip install -r requirements.txt

# 配置環境變數
export SUPABASE_URL=https://your-supabase-project.supabase.co
export SUPABASE_ANON_KEY=your-supabase-anon-key

# 啟動服務
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 訪問 API 文檔
# 本機: http://localhost:8000/docs
# 雲端: https://prompt-scribe-api.vercel.app/docs

# 開啟瀏覽器（選擇您的系統）
# Windows: start "" http://localhost:8000/docs
# macOS: open http://localhost:8000/docs
# Linux: xdg-open http://localhost:8000/docs
```

### 方式 3: 一鍵部署到雲端

**Vercel（全球 CDN，零配置）**:
```bash
vercel --prod
```

**Railway（完整功能，Redis 支援）**:
```bash
railway up
railway add redis
```

詳細部署指南: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## ⚙️ 環境變數配置

### 必需變數

這些變數是啟動 API 必須設置的：

| 變數名 | 必填 | 說明 | 獲取方式 | 範例值 | 注意事項 |
|--------|------|------|----------|--------|----------|
| `SUPABASE_URL` | ✅ | Supabase 專案 URL | Dashboard → Settings → API → Project URL | `https://xxx.supabase.co` | 必須以 `https://` 開頭 |
| `SUPABASE_ANON_KEY` | ✅ | Supabase 公開 API 金鑰 | Dashboard → Settings → API → anon public | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | 使用 **anon** 金鑰，不是 service_role |

### 可選變數（進階配置）

| 變數名 | 預設值 | 說明 | 可選值 |
|--------|--------|------|--------|
| `CACHE_STRATEGY` | `memory` | 快取策略選擇 | `memory`, `redis`, `hybrid` |
| `REDIS_ENABLED` | `false` | 是否啟用 Redis 快取 | `true`, `false` |
| `REDIS_URL` | - | Redis 連接 URL | `redis://localhost:6379/0` |
| `DEBUG` | `false` | 調試模式（生產環境應設為 false） | `true`, `false` |
| `LOG_LEVEL` | `INFO` | 日誌輸出等級 | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CORS_ORIGINS` | `*` | 允許的跨域來源 | `*` 或 JSON 陣列 |

### 快速設定步驟

```bash
# 1. 複製範例檔案
cp env.example .env

# 2. 編輯 .env 檔案（填入您的 Supabase 資訊）
# Windows: notepad .env
# Mac/Linux: nano .env

# 3. 驗證配置（可選）
python -c "from src.api.config import settings; print(f'✓ 配置載入成功: {settings.app_name}')"
```

### 💡 提示

- 📄 **完整配置說明**: 查看 [env.example](env.example) 了解所有可用選項
- 🔒 **安全提醒**: 絕不要將 `.env` 提交到 Git（已在 `.gitignore` 中排除）
- 🚀 **部署環境**: 在 Vercel/Railway 等平台使用環境變數設置介面，不需要 `env.example` 檔案

---

## 🔒 安全與速率限制

### 當前狀態（Demo 環境）

目前生產環境為**開放測試狀態**：

- ✅ **匿名可用**: 無需認證即可使用 API
- ⚠️ **Demo 期間**: 開放存取以便測試和評估
- ⚠️ **可能變更**: 未來可能調整為需要 API Key 或 JWT

### 生產環境建議（企業部署）

如果您要部署自己的實例，建議啟用以下安全措施：

**1. API 認證**
```bash
# 使用 API Key（推薦）
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-api.com/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description":"your prompt"}'
```

**2. CORS 白名單**
```bash
# .env（生產環境配置）
CORS_ORIGINS=["https://your-app.com","https://admin.your-app.com"]

# ⚠️ 不要在生產使用 CORS_ORIGINS=*
```

**3. 速率限制（建議）**
- **限制**: 每 IP 每分鐘 60 次請求
- **工具**: FastAPI-Limiter 或 slowapi
- **回應**: 429 Too Many Requests
- **配置範例**:
  ```python
  from slowapi import Limiter
  limiter = Limiter(key_func=get_remote_address)
  
  @limiter.limit("60/minute")
  @app.post("/api/llm/recommend-tags")
  async def recommend_tags(...):
      ...
  ```

### 💡 安全最佳實踐

- 🔐 生產環境使用 HTTPS（Vercel/Railway 自動提供）
- 🔑 定期輪換 API Keys
- 📊 監控異常流量和請求模式
- 🚫 限制請求大小（預設已設定）
- 📝 記錄所有 API 訪問（使用 `usage_logger` 服務）

---

## 📚 使用範例

### 1. 智能標籤推薦

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/llm/recommend-tags",
        json={
            "description": "a lonely girl in cyberpunk city at night"
        }
    )
    data = response.json()
    
    # 自動分析和推薦
    print(data["recommended_tags"])
    # [
    #   {"tag": "1girl", "confidence": 0.95},
    #   {"tag": "solo", "confidence": 0.90},
    #   {"tag": "cyberpunk", "confidence": 0.88},
    #   {"tag": "city", "confidence": 0.85},
    #   {"tag": "night", "confidence": 0.82},
    #   ...
    # ]
```

### 2. 智能組合建議（V2.0 新功能）

```python
response = await client.post(
    "http://localhost:8000/api/llm/suggest-combinations",
    json={
        "tags": ["1girl", "long_hair"]
    }
)

# 獲得完整的組合建議
data = response.json()
print(data["complete_prompts"])
# [
#   {
#     "theme": "基礎角色",
#     "basic": "1girl, solo, long_hair",
#     "extended": "1girl, solo, long_hair, smile, looking_at_viewer",
#     "popularity": "very_popular"
#   },
#   ...
# ]
```

### 3. 標籤驗證

```python
response = await client.post(
    "http://localhost:8000/api/llm/validate-prompt",
    json={
        "tags": ["1girl", "2girls", "nsfw", "masterpiece"]
    }
)

data = response.json()
print(f"Overall Score: {data['overall_score']}/100")
print(f"Issues: {data['issues']}")
# 自動檢測衝突、冗餘、不當標籤
```

### 4. 常見錯誤與處理

#### 錯誤 1: 缺少必需參數（400 Bad Request）

```bash
# 缺少 description 參數
curl -X POST https://prompt-scribe-api.vercel.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{}'
```

**回應**:
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

**解決**: 確保提供所有必需參數，參考 [API 文檔](https://prompt-scribe-api.vercel.app/docs)

#### 錯誤 2: 無效的資料類型（422 Unprocessable Entity）

```bash
# tags 應該是陣列，不是字串
curl -X POST https://prompt-scribe-api.vercel.app/api/llm/validate-prompt \
  -H "Content-Type: application/json" \
  -d '{"tags": "not-an-array"}'
```

**回應**:
```json
{
  "detail": [
    {
      "loc": ["body", "tags"],
      "msg": "value is not a valid list",
      "type": "type_error.list"
    }
  ]
}
```

**解決**: 檢查資料類型，`tags` 必須是字串陣列：`["1girl", "solo"]`

💡 **提示**: 完整的錯誤代碼對照表請查看 → [故障排除](#-故障排除troubleshooting)

---

## 🏗️ 專案結構

```
prompt-scribe/
├── src/api/                    # API 主程式
│   ├── main.py                # FastAPI 應用入口
│   ├── config.py              # 配置管理
│   ├── models/                # Pydantic 模型
│   ├── routers/               # API 路由
│   │   ├── v1/               # 基礎端點
│   │   └── llm/              # LLM 優化端點
│   ├── services/             # 核心業務邏輯
│   │   ├── keyword_analyzer.py      # P1: 關鍵字權重
│   │   ├── ngram_matcher.py         # P1: N-gram 匹配
│   │   ├── tag_combination_analyzer.py  # P2: 智能組合
│   │   ├── redis_cache_manager.py   # P2: Redis 快取
│   │   └── hybrid_cache_manager.py  # P2: 混合快取
│   ├── middleware/           # 中間件
│   └── tests/                # 完整測試套件
│
├── scripts/                   # 資料庫初始化腳本
├── docs/                      # 文檔
│   ├── api/                  # API 文檔
│   ├── testing/              # 測試文檔
│   └── P1_P2_OPTIMIZATION_COMPLETE.md
├── .github/workflows/         # CI/CD 配置
├── Dockerfile                 # Docker 配置
├── docker-compose.yml         # 服務編排
├── vercel.json               # Vercel 配置
├── railway.toml              # Railway 配置
└── DEPLOYMENT_GUIDE.md       # 部署指南
```

---

## 🧪 測試

### 運行測試

```bash
cd src/api

# 所有測試
pytest tests/ -v

# 特定測試套件
pytest tests/test_user_scenarios.py -v

# 含覆蓋率報告
pytest tests/ --cov=services --cov=routers --cov-report=html
```

### 測試覆蓋率

- **總體**: 98.7% ⭐
- **核心服務**: 95%+
- **API 端點**: 100%
- **測試數量**: 75 個

查看詳細報告: [TEST_EXECUTION_SUMMARY.md](TEST_EXECUTION_SUMMARY.md)

---

## 📖 完整文檔

### 核心文檔
- [📘 API 文檔（雲端）](https://prompt-scribe-api.vercel.app/docs) - Swagger UI 互動式測試
- [📘 API 文檔（本機）](http://localhost:8000/docs) - 本地開發文檔
- [📄 OpenAPI 規格](https://prompt-scribe-api.vercel.app/openapi.json) - 匯入 Postman/Insomnia
- [🚀 部署指南](DEPLOYMENT_GUIDE.md) - 完整部署步驟
- [📝 CHANGELOG](CHANGELOG.md) - 版本歷史
- [🎯 優化路線圖](OPTIMIZATION_ROADMAP.md) - 未來規劃

### 技術文檔
- [⚡ P1 & P2 優化總結](docs/P1_P2_OPTIMIZATION_COMPLETE.md)
- [🧪 測試指南](src/api/tests/TESTING_GUIDE.md)
- [🔧 CI/CD 設置](.github/CICD_SETUP_GUIDE.md)
- [💾 快取策略](OPTIMIZATION_ROADMAP.md#方向-2-💾-快取系統升級)

### 使用指南
- [🆕 快速開始](docs/quickstart.md)
- [🔌 LLM 整合指南](docs/api/LLM_INTEGRATION_GUIDE.md)
- [📊 效能筆記](docs/api/PERFORMANCE_NOTES.md)

---

## 🛠️ 技術棧

### 後端
- **Framework**: FastAPI 0.109+
- **Database**: Supabase (PostgreSQL 15+)
- **Cache**: Redis 7+ (optional) + In-memory LRU
- **Language**: Python 3.9+（推薦 3.11+ 以獲得最佳效能）

### 優化技術 (V2.0)
- **詞性分析**: 自動關鍵字權重分配
- **N-gram**: 複合詞優先匹配
- **雙層快取**: 記憶體 + Redis 混合架構
- **智能分析**: 標籤組合模式識別

### 基礎設施
- **部署**: Vercel, Railway, Docker, Self-hosted
- **CI/CD**: GitHub Actions
- **監控**: 內建健康檢查和快取統計
- **測試**: Pytest with 98.7% coverage

---

## 🎯 核心 API 端點

### LLM 優化端點（推薦使用）

| 端點 | 方法 | 描述 | 新功能 |
|------|------|------|--------|
| `/api/llm/recommend-tags` | POST | 智能標籤推薦 | ⚡ P1 優化 |
| `/api/llm/validate-prompt` | POST | Prompt 驗證 | - |
| `/api/llm/suggest-combinations` | POST | 智能組合建議 | ⭐ P2 新增 |
| `/api/llm/analyze-tags` | POST | 標籤平衡分析 | ⭐ P2 新增 |

### 基礎端點

| 端點 | 方法 | 描述 |
|------|------|------|
| `/api/v1/tags` | GET | 查詢標籤 |
| `/api/v1/search` | POST | 關鍵字搜尋 |
| `/api/v1/categories` | GET | 分類統計 |
| `/health` | GET | 健康檢查 |
| `/cache/stats` | GET | 快取統計 |
| `/cache/health` | GET | 快取健康檢查 |

完整 API 文檔: https://prompt-scribe-api.vercel.app/docs（線上）/ http://localhost:8000/docs（本機）

---

## 🌟 V2.0 主要改進

### P1 優化（準確率提升）

✅ **多級關鍵字權重** - 名詞 1.0, 形容詞 0.85, 介詞 0.3  
✅ **N-gram 複合詞** - "school uniform" 優先匹配  
✅ **使用數據收集** - 自動記錄 API 調用  
✅ **CI/CD 自動化** - Python 3.9-3.13 多版本測試

### P2 優化（體驗提升）

✅ **智能標籤組合** - 10+ 預定義模式，自動建議  
✅ **Redis 快取升級** - 持久化，跨實例共享  
✅ **混合快取策略** - L1 記憶體 + L2 Redis  
✅ **CDN 邊緣部署** - 全球 4 種部署方案

詳細內容: [docs/P1_P2_OPTIMIZATION_COMPLETE.md](docs/P1_P2_OPTIMIZATION_COMPLETE.md)

---

## 🚀 部署方案選擇

### 快速對比（選擇最適合你的方案）

| 方案 | 最適合 | 快取支援 | 設定難度 | 月成本 | 一鍵啟動 |
|------|--------|----------|----------|--------|----------|
| **Vercel** | 個人專案、Demo | 僅記憶體 | ⭐ 簡單 | $0-20 | `vercel --prod` |
| **Railway** | 中小型應用 | Redis ✅ | ⭐⭐ 中等 | $15-25 | `railway up` |
| **Docker** | 完全控制、企業 | 全功能 ✅ | ⭐⭐⭐ 進階 | 自訂 | `docker-compose up` |

### 選擇建議

**我應該選哪個？**
- 🆕 **剛開始學習** → Vercel（最簡單，免費）
- 🚀 **準備上線的小專案** → Railway（功能完整，價格合理）
- 🏢 **企業或需要完全控制** → Docker（最靈活，需維護）

---

### 詳細部署步驟

<details>
<summary><b>方案 1: Vercel（推薦新手）</b> - 點擊展開</summary>

#### 優勢
- ✅ 全球 CDN（180+ 邊緣節點）
- ✅ 零配置 HTTPS
- ✅ GitHub 自動部署
- ✅ 免費額度 100GB/月

#### 限制
- ⚠️ 函數執行時間 30 秒
- ⚠️ 僅支援記憶體快取（無 Redis）

#### 部署步驟
```bash
# 1. 安裝 Vercel CLI
npm i -g vercel

# 2. 登入
vercel login

# 3. 部署
vercel --prod

# 4. 設置環境變數
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY

# 5. 驗證
curl https://prompt-scribe-api.vercel.app/health
```

⏱️ **預計時間**: 10 分鐘

</details>

<details>
<summary><b>方案 2: Railway（推薦生產環境）</b> - 點擊展開</summary>

#### 優勢
- ✅ 支援 Redis 持久化快取
- ✅ 無函數時間限制
- ✅ 簡單配置
- ✅ 自動部署與回滾

#### 部署步驟
```bash
# 1. 安裝 Railway CLI
npm i -g @railway/cli

# 2. 登入
railway login

# 3. 初始化專案
railway init

# 4. 部署 API
railway up

# 5. 添加 Redis（可選）
railway add redis

# 6. 設置環境變數
railway variables set SUPABASE_URL=xxx
railway variables set SUPABASE_ANON_KEY=xxx
railway variables set REDIS_ENABLED=true

# 7. 驗證
railway open
```

⏱️ **預計時間**: 15 分鐘

</details>

<details>
<summary><b>方案 3: Docker（完全控制）</b> - 點擊展開</summary>

#### 優勢
- ✅ 完全控制所有配置
- ✅ 本地或任何雲端平台
- ✅ 包含 Redis 和所有功能
- ✅ 可客製化優化

#### 部署步驟
```bash
# 1. 克隆專案
git clone https://github.com/azuma520/Prompt-Scribe.git
cd Prompt-Scribe

# 2. 設置環境變數
cp env.example .env
# 編輯 .env 填入您的 Supabase 資訊

# 3. 啟動服務（包含 API + Redis）
docker-compose up -d

# 4. 檢查狀態
docker-compose ps
curl http://localhost:8000/health

# 5. 查看日誌
docker-compose logs -f api
```

⏱️ **預計時間**: 20 分鐘（含 Docker 安裝）

</details>

---

📖 **完整部署指南**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📊 系統需求

### 最低配置
- CPU: 1 core
- RAM: 512MB
- Storage: 1GB
- Python: 3.9+

### 推薦配置
- CPU: 2+ cores
- RAM: 2GB+
- Storage: 5GB+
- Python: 3.11+
- Redis: 7+ (可選)

---

## 🤝 貢獻指南

我們歡迎貢獻！歡迎提交 Pull Request 或建立 Issue。

### 開發流程
1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. Push 到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 代碼標準
- 遵循 PEP 8
- 類型提示
- 單元測試覆蓋率 > 90%
- 通過 CI/CD 檢查

---

## 📜 授權

本專案採用 MIT 授權 - 查看 [LICENSE](LICENSE) 文件了解詳情

---

## 🙏 致謝

- [FastAPI](https://fastapi.tiangolo.com/) - 高效能 Web 框架
- [Supabase](https://supabase.com/) - 開源 Backend as a Service
- [Redis](https://redis.io/) - 快取系統
- [Danbooru](https://danbooru.donmai.us/) - 標籤數據來源

---

## ❓ 常見問題（FAQ）

<details>
<summary><b>Q1: 如何獲取 Supabase API Keys？</b></summary>

**步驟**:
1. 登入 [Supabase Dashboard](https://supabase.com/dashboard)
2. 選擇你的專案
3. 左側選單：Settings → API
4. 複製以下資訊：
   - **Project URL** → 設為 `SUPABASE_URL`
   - **anon public** → 設為 `SUPABASE_ANON_KEY`

💡 **提示**: 這兩個是公開安全的金鑰，可以放在前端使用。

</details>

<details>
<summary><b>Q2: 本地啟動失敗怎麼辦？</b></summary>

**常見原因與解決方案**:

1. **Python 版本錯誤**
   ```bash
   python --version  # 需要 3.9+
   # 如果版本太舊，請安裝 Python 3.9 或更高版本
   ```

2. **環境變數未設定**
   ```bash
   # 檢查 .env 檔案是否存在
   ls -la .env  # Windows: dir .env
   
   # 確認內容包含 SUPABASE_URL 和 SUPABASE_ANON_KEY
   cat .env  # Windows: type .env
   ```

3. **依賴包未安裝**
   ```bash
   cd src/api
   pip install -r requirements.txt
   ```

4. **端口被占用（Port 8000）**
   ```bash
   # 更換端口
   uvicorn main:app --port 8001
   ```

</details>

<details>
<summary><b>Q3: 部署後出現 502 Bad Gateway？</b></summary>

**檢查清單**:

- [ ] **Vercel 環境變數已正確設定**
  ```bash
  vercel env ls  # 檢查環境變數
  ```

- [ ] **Supabase 專案狀態正常**
  - 登入 Dashboard 確認專案未暫停
  - 檢查 API URL 和 Key 是否正確

- [ ] **查看部署日誌**
  ```bash
  vercel logs  # 查看錯誤訊息
  ```

- [ ] **測試本地是否正常**
  ```bash
  # 使用相同環境變數在本地測試
  export SUPABASE_URL=xxx
  export SUPABASE_ANON_KEY=xxx
  uvicorn main:app --reload
  ```

**常見錯誤**:
- `ModuleNotFoundError` → 檢查 `requirements.txt` 是否完整
- `Connection refused` → 檢查 Supabase URL 和 Key 是否正確
- `Timeout` → 檢查資料庫連接或增加 timeout 設定

</details>

<details>
<summary><b>Q4: 如何提升 API 效能？</b></summary>

**優化建議**:

1. **啟用 Redis 快取**（Railway/Docker）
   ```bash
   # .env
   CACHE_STRATEGY=redis
   REDIS_ENABLED=true
   REDIS_URL=redis://localhost:6379/0
   ```

2. **使用混合快取**（最佳效能）
   ```bash
   CACHE_STRATEGY=hybrid
   HYBRID_L1_TTL=300
   HYBRID_L2_TTL=3600
   ```

3. **監控快取效能**
   ```bash
   curl http://your-api/cache/stats
   # 目標：hit_rate > 80%
   ```

4. **調整資料庫連接池**
   ```bash
   DB_CONNECTION_POOL_SIZE=20  # 預設 10
   ```

</details>

<details>
<summary><b>Q5: Stage 1 和 Stage 2 的關係？</b></summary>

**簡單說明**:

- **Stage 1（`stage1/` 目錄）**：歷史資料處理腳本
  - 用途：初始資料清洗、標記、遷移
  - 狀態：已完成任務，保留供參考
  - 不需要運行：除非你要重新處理原始資料

- **Stage 2（實際在 `src/api/`）**：生產環境 API
  - 用途：提供 REST API 服務
  - 狀態：✅ 已部署運行中
  - 這是你要使用的部分

**新用戶只需要**:
1. 使用現有的 Live API：https://prompt-scribe-api.vercel.app
2. 或部署自己的 API（參考快速開始）

💡 **不需要運行 Stage 1**，資料庫已準備就緒。

</details>

---

## 🔧 故障排除（Troubleshooting）

### 快速診斷

```bash
# 1. 檢查 API 健康狀態
curl https://prompt-scribe-api.vercel.app/health

# 2. 檢查快取系統
curl https://prompt-scribe-api.vercel.app/cache/health

# 3. 測試基本查詢
curl "https://prompt-scribe-api.vercel.app/api/v1/tags?limit=5"
```

### 錯誤代碼對照

| 狀態碼 | 錯誤 | 可能原因 | 解決方案 |
|--------|------|---------|---------|
| 400 | Bad Request | 請求格式錯誤 | 檢查 JSON 格式，參考 [API 文檔](https://prompt-scribe-api.vercel.app/docs) |
| 401 | Unauthorized | API Key 錯誤 | 確認環境變數設定正確 |
| 404 | Not Found | 端點不存在 | 檢查 URL 路徑，參考 `/docs` |
| 429 | Too Many Requests | 超過速率限制 | 降低請求頻率或升級方案 |
| 500 | Internal Server Error | 伺服器錯誤 | 查看日誌，檢查資料庫連接 |
| 502 | Bad Gateway | 部署配置問題 | 檢查環境變數和部署日誌 |

### 需要更多幫助？

- 📖 **查看文檔**: [docs/](docs/) 目錄包含完整指南
- 🐛 **回報問題**: [GitHub Issues](https://github.com/azuma520/Prompt-Scribe/issues)
- 💬 **社群討論**: [GitHub Discussions](https://github.com/azuma520/Prompt-Scribe/discussions)
- 📧 **聯繫我們**: 透過 [建立 Issue](https://github.com/azuma520/Prompt-Scribe/issues/new) 聯繫

---

## 📞 支援與聯繫

- **文檔**: [docs/](docs/)
- **問題追蹤**: [GitHub Issues](https://github.com/azuma520/Prompt-Scribe/issues)
- **討論區**: [GitHub Discussions](https://github.com/azuma520/Prompt-Scribe/discussions)

---

## 🎯 路線圖

### V2.1（計畫中）
- [ ] 同義詞字典擴展（+800 條目）
- [ ] 點擊率學習系統
- [ ] 標籤共現分析

### V3.0（未來）
- [ ] 向量搜尋實作
- [ ] 機器學習排序
- [ ] 個人化推薦
- [ ] 多語言支援

查看完整路線圖: [OPTIMIZATION_ROADMAP.md](OPTIMIZATION_ROADMAP.md)

---

<div align="center">

**⭐ 如果這個專案對你有幫助，請給我們一顆星！**

Made with ❤️ by Prompt-Scribe Team

[🏠 主頁](https://github.com/azuma520/Prompt-Scribe) • [📖 文檔](docs/) • [🚀 快速開始](#-快速開始) • [💬 討論](https://github.com/azuma520/Prompt-Scribe/discussions)

</div>
