# 🤖 Prompt-Scribe API

> **LLM-Friendly Tag Recommendation System**  
> 專為 AI 圖像生成優化的智能標籤推薦 API

[![Version](https://img.shields.io/badge/version-2.0.1-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-98.7%25%20passing-brightgreen.svg)](src/api/tests/)
[![Production](https://img.shields.io/badge/production-live-brightgreen.svg)](https://prompt-scribe-api.vercel.app)

---

## 🌐 生產環境

### 🚀 Live API
- **生產 URL**: https://prompt-scribe-api.vercel.app
- **健康檢查**: https://prompt-scribe-api.vercel.app/health
- **狀態**: ✅ 運行中
- **平台**: Vercel Serverless Functions

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
git clone https://github.com/your-org/prompt-scribe.git
cd prompt-scribe

# 配置環境變數
cp .env.example .env
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
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_ANON_KEY=your-anon-key

# 啟動服務
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 訪問 API 文檔
open http://localhost:8000/docs
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
- [📘 API 文檔](http://localhost:8000/docs) - Swagger UI
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
- **Language**: Python 3.9+

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

完整 API 文檔: http://localhost:8000/docs

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

詳細內容: [P1_P2_FINAL_SUMMARY.md](P1_P2_FINAL_SUMMARY.md)

---

## 🚀 部署選項

### 選項 1: Vercel（推薦個人專案）
- ✅ 全球 CDN，零配置 HTTPS
- ✅ 自動擴展，免費額度 100GB/月
- ⚠️ 無狀態（記憶體快取only）

### 選項 2: Railway（推薦生產環境）
- ✅ 支援 Redis 持久化快取
- ✅ 無限制，自動部署
- 💰 $15-25/月

### 選項 3: Docker（完全控制）
- ✅ 完整功能，可客製化
- ✅ 本地或雲端均可
- 💰 成本可控

### 選項 4: 自主機（企業級）
- ✅ 完全控制和安全性
- ✅ 多區域部署
- 💰 $50+/月

詳細比較: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

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

我們歡迎貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md)（待建立）

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

## 📞 支援與聯繫

- **文檔**: [docs/](docs/)
- **問題追蹤**: [GitHub Issues](https://github.com/your-org/prompt-scribe/issues)
- **討論區**: [GitHub Discussions](https://github.com/your-org/prompt-scribe/discussions)

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

[🏠 主頁](https://github.com/your-org/prompt-scribe) • [📖 文檔](docs/) • [🚀 快速開始](#-快速開始) • [💬 討論](https://github.com/your-org/prompt-scribe/discussions)

</div>
