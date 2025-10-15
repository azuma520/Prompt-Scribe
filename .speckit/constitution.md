# 🏛️ Prompt-Scribe 專案憲法

**版本**: V1.0.0  
**生效日期**: 2025-10-15  
**權威來源**: [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)

---

## 📜 憲法宣言

本文件定義 **Prompt-Scribe** 專案的核心組織原則和架構規範。所有開發活動、代碼變更、文件組織必須遵循本憲法及其參考的架構文檔。

---

## 🎯 核心原則

### 1️⃣ 架構不可變性原則

**規定**: 專案架構必須嚴格遵循 `PROJECT_STRUCTURE.md` 定義的結構。

**適用範圍**:
- ✅ 所有新增文件必須放置在正確的目錄
- ✅ 所有新功能必須遵循現有模組化設計
- ✅ 所有測試必須放置在對應的 `tests/` 目錄
- ✅ 所有文檔必須放置在 `docs/` 或對應的子目錄

**違反處理**: 任何違反架構的變更必須先更新 `PROJECT_STRUCTURE.md` 並獲得批准。

---

### 2️⃣ 模組職責分離原則

**核心目錄職責**:

```
src/api/
├── models/          → 僅定義資料模型（Pydantic）
├── routers/         → 僅處理 HTTP 路由和端點
├── services/        → 核心業務邏輯（不含路由）
├── middleware/      → HTTP 中間件（日誌、驗證等）
├── data/            → 靜態配置資料（YAML/JSON）
└── tests/           → 完整測試套件
```

**禁止行為**:
- ❌ 在 `models/` 中編寫業務邏輯
- ❌ 在 `routers/` 中直接操作資料庫
- ❌ 在 `services/` 中處理 HTTP 請求/回應
- ❌ 將測試文件放在非 `tests/` 目錄

---

### 3️⃣ 服務模組命名規範

**當前核心服務** (13 個):
```
V1 基礎服務:
- supabase_client.py        # 資料庫客戶端
- keyword_expander.py        # 關鍵字擴展
- cache_manager.py           # 記憶體快取

V2-P1 優化服務:
- keyword_analyzer.py        # 多級權重分析
- ngram_matcher.py           # N-gram 匹配
- relevance_scorer.py        # 相關性評分
- usage_logger.py            # 使用記錄

V2-P2 進階服務:
- tag_combination_analyzer.py # 標籤組合分析
- redis_cache_manager.py      # Redis 快取
- hybrid_cache_manager.py     # 混合快取
- cache_strategy.py           # 快取策略
```

**新增服務規範**:
1. 必須使用 `snake_case.py` 命名
2. 必須放置在 `src/api/services/`
3. 必須包含完整 docstring
4. 必須有對應的單元測試
5. 必須在 `PROJECT_STRUCTURE.md` 中更新記錄

---

### 4️⃣ API 端點組織原則

**路由結構**:
```
routers/
├── v1/                    # 基礎 API (V1)
│   ├── tags.py           # 標籤查詢
│   ├── search.py         # 關鍵字搜尋
│   └── statistics.py     # 統計資訊
│
└── llm/                   # LLM 優化端點 (V2)
    ├── recommendations.py      # 智能推薦
    ├── validation.py           # Prompt 驗證
    ├── helpers.py              # 輔助工具
    └── smart_combinations.py   # 智能組合
```

**新增端點流程**:
1. 在 `models/requests.py` 定義請求模型
2. 在 `models/responses.py` 定義回應模型
3. 在對應的路由文件中實作處理器
4. 在 `main.py` 註冊路由
5. 編寫對應測試（最少 3 個測試用例）
6. 更新 API 文檔

---

### 5️⃣ 測試覆蓋率強制要求

**測試標準**:
- **最低覆蓋率**: 90%
- **目標覆蓋率**: 95%+
- **當前實際**: 98.7% ✅

**測試組織**:
```
src/api/tests/
├── test_basic_api.py           # 基礎 API 測試
├── test_llm_endpoints.py       # LLM 端點測試
├── test_cache.py               # 快取系統測試
├── test_batch_queries.py       # 批量查詢測試
├── test_load_performance.py    # 負載效能測試
└── test_user_scenarios.py      # 使用場景測試
```

**新功能測試要求**:
- ✅ 每個新端點至少 5 個測試用例
- ✅ 每個新服務至少 10 個測試用例
- ✅ 必須包含正常、異常、邊界測試
- ✅ 必須在 PR 前通過所有測試

---

### 6️⃣ 文檔同步更新原則

**文檔層級**:
```
根目錄文檔:
├── README.md                    # 專案概覽（對外）
├── PROJECT_STRUCTURE.md         # 架構規範（內部）⭐
├── CHANGELOG.md                 # 版本歷史
├── DEPLOYMENT_GUIDE.md          # 部署指南
└── OPTIMIZATION_ROADMAP.md      # 優化路線圖

docs/ 專業文檔:
├── api/                         # API 相關
├── testing/                     # 測試文檔
├── migration/                   # 遷移文檔
└── quickstart.md                # 快速開始

專案內文檔:
└── src/api/README.md            # API 開發指南
```

**更新要求**:
- 新增功能 → 更新 `README.md` + `CHANGELOG.md`
- 架構變更 → 更新 `PROJECT_STRUCTURE.md` ⭐
- 新增端點 → 更新 `src/api/README.md`
- 新增測試 → 更新 `tests/TESTING_GUIDE.md`
- 版本發布 → 更新 `CHANGELOG.md` + `DEPLOYMENT_GUIDE.md`

---

### 7️⃣ 配置文件管理規範

**部署配置**:
```
根目錄:
├── Dockerfile              # Docker 容器配置
├── docker-compose.yml      # 服務編排
├── vercel.json             # Vercel 部署
├── railway.toml            # Railway 部署
└── .env.example            # 環境變數範本
```

**配置優先級**:
1. 環境變數（`.env`）
2. 平台配置（Vercel/Railway）
3. 預設值（`config.py`）

**禁止行為**:
- ❌ 硬編碼敏感資訊（API Key、密碼）
- ❌ 提交 `.env` 到 Git
- ❌ 在代碼中直接使用平台特定配置

---

### 8️⃣ CI/CD 自動化要求

**GitHub Actions 工作流**:
```
.github/workflows/
├── api-tests.yml              # 自動測試（PR 觸發）
├── api-deploy.yml             # 自動部署（Push 觸發）
└── performance-check.yml      # 效能監控（定時）
```

**強制檢查**:
- ✅ 所有 PR 必須通過測試
- ✅ 覆蓋率不得低於 90%
- ✅ 代碼風格必須符合 PEP 8
- ✅ 響應時間不得超過 2 秒

---

## 🛡️ 架構保護機制

### 自動驗證清單

**每次變更前檢查**:
- [ ] 文件放置在正確的目錄？
- [ ] 遵循命名規範？
- [ ] 模組職責單一？
- [ ] 添加了對應測試？
- [ ] 更新了相關文檔？
- [ ] 通過 CI/CD 檢查？

**每次發布前檢查**:
- [ ] `PROJECT_STRUCTURE.md` 已更新？
- [ ] `CHANGELOG.md` 已更新？
- [ ] 所有測試通過？
- [ ] 文檔同步？
- [ ] 版本號正確？

---

## 📐 代碼品質標準

### Python 代碼規範

**風格**: PEP 8  
**類型**: 強制使用類型提示  
**文檔**: 所有 public 函數需要 docstring  
**測試**: 覆蓋率 > 90%  
**日誌**: 使用 `logging` 模組，不使用 `print`

**範例**:
```python
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def process_tags(
    tags: List[str],
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    處理標籤查詢。
    
    Args:
        tags: 標籤列表
        filters: 可選的過濾條件
        
    Returns:
        處理後的標籤資料
        
    Raises:
        ValueError: 當標籤格式無效時
    """
    logger.info(f"Processing {len(tags)} tags")
    # 實作...
```

---

## 🚀 版本管理規範

### 語義化版本

**格式**: `MAJOR.MINOR.PATCH`

**範例**:
- `V1.0.0` - 初始版本
- `V2.0.0` - 重大架構升級
- `V2.1.0` - 新增功能
- `V2.1.1` - Bug 修復

**當前版本**: `V2.0.0`

---

## 📊 效能指標要求

### 生產環境標準

| 指標 | 目標 | 監控 |
|------|------|------|
| 響應時間 | < 2s | ✅ 每日檢查 |
| 吞吐量 | > 100/s | ✅ 每日檢查 |
| 準確率 | > 80% | ✅ 每週評估 |
| 可用性 | > 99% | ✅ 即時監控 |
| 覆蓋率 | > 90% | ✅ PR 自動檢查 |

---

## 🔄 架構演進流程

### 提案 → 審查 → 實施 → 驗證

**重大架構變更**:
1. 提交架構提案（RFC）
2. 團隊審查討論
3. 更新 `PROJECT_STRUCTURE.md`
4. 分階段實施
5. 更新所有相關文檔
6. 驗證並發布

**小型優化**:
1. 確保符合現有架構
2. 實施變更
3. 更新局部文檔
4. 通過測試驗證

---

## 🎓 學習與參考

### 核心文檔

1. **架構規範**: `PROJECT_STRUCTURE.md` ⭐
2. **API 指南**: `src/api/README.md`
3. **測試指南**: `src/api/tests/TESTING_GUIDE.md`
4. **部署指南**: `DEPLOYMENT_GUIDE.md`
5. **CI/CD 指南**: `.github/CICD_SETUP_GUIDE.md`

### 最佳實踐

**開發流程**:
```
需求分析 → 架構設計 → 實作 → 測試 → 文檔 → 部署
```

**代碼審查重點**:
- 是否符合架構規範？
- 是否遵循命名規範？
- 是否有足夠測試？
- 是否更新文檔？
- 是否考慮效能影響？

---

## ⚖️ 憲法修正案流程

**修正本憲法**:
1. 提出修正案（Issue/RFC）
2. 詳細說明原因和影響
3. 團隊審查投票
4. 通過後更新版本號
5. 通知所有開發者

**修正記錄**:
- V1.0.0 (2025-10-15) - 初始版本

---

## 📝 結語

本憲法旨在維護 Prompt-Scribe 專案的架構一致性、代碼品質和長期可維護性。所有貢獻者都應該：

✅ **熟讀並遵循本憲法**  
✅ **參考 PROJECT_STRUCTURE.md**  
✅ **保持代碼品質標準**  
✅ **維護文檔同步**  
✅ **持續優化改進**

---

**憲法權威**: ⭐⭐⭐  
**生效狀態**: ✅ 立即生效  
**最後更新**: 2025-10-15

---

> "優秀的架構不是一次性設計出來的，而是通過持續遵循良好原則演進而來的。"


