# 📚 部署學習總結

**專案**: Prompt-Scribe API  
**學習日期**: 2025-10-15  
**部署平台**: Vercel Serverless Functions  
**學習目標**: Serverless 部署最佳實踐與問題解決

---

## 🎯 核心學習要點

### 1. Serverless 環境的本質差異

#### 本地開發 vs Serverless 生產環境

**本地環境**:
```python
# 複雜模組結構可以正常工作
from src.api.main import app
from config import settings
from services.cache_strategy import get_cache_strategy_manager
```

**Serverless 環境**:
```python
# 必須是自包含的，無外部依賴
from fastapi import FastAPI
app = FastAPI(title="My API")
# 直接在入口點定義所有必要代碼
```

#### 關鍵洞察
- **沙盒化**: Serverless 環境是隔離的，無法訪問複雜的專案結構
- **冷啟動**: 每次請求可能在不同的實例上，狀態不持久
- **檔案限制**: 有嚴格的檔案大小和依賴限制

### 2. 模組導入錯誤的根本原因

#### 錯誤模式分析

**問題代碼**:
```python
# api/index.py
from api.main import app  # ← 這裡開始出錯
```

**錯誤鏈**:
1. `api/index.py` 導入 `src/api/main.py`
2. `main.py` 導入 `from config import settings`
3. `config.py` 在 Vercel 環境中找不到
4. `ModuleNotFoundError: No module named 'config'`

#### 解決方案演進

**嘗試 1**: 路徑修正
```python
sys.path.insert(0, str(src_path))
# 仍然失敗：環境差異
```

**嘗試 2**: 運行時配置
```json
{
  "runtime": "@vercel/python@2.0.3"
}
// 仍然失敗：版本問題
```

**最終方案**: 自包含入口點
```python
# api/index.py - 完全自包含
from fastapi import FastAPI
app = FastAPI()
# 不依賴任何外部模組
```

### 3. Vercel 部署配置最佳實踐

#### 配置演進過程

**初始配置（失敗）**:
```json
{
  "builds": [...],
  "functions": {...},  // ← 衝突
  "regions": ["all"]   // ← 免費方案不支援
}
```

**最終配置（成功）**:
```json
{
  "builds": [{
    "src": "api/index.py",
    "use": "@vercel/python"
  }],
  "routes": [{
    "src": "/(.*)",
    "dest": "api/index.py"
  }]
}
```

#### 關鍵配置要點
- **單一配置**: 不要同時使用 `builds` 和 `functions`
- **免費限制**: 免費方案不支援多區域部署
- **檔案過濾**: 使用 `.vercelignore` 排除大型檔案

---

## 🔧 技術問題解決流程

### 問題診斷方法

#### 1. 錯誤分類
```
FUNCTION_INVOCATION_FAILED
├── 模組導入錯誤 (ModuleNotFoundError)
├── 運行時配置錯誤 (Invalid runtime)
├── 檔案大小錯誤 (File size limit)
└── 環境變數錯誤 (Missing environment)
```

#### 2. 逐步排查
1. **檢查日誌**: `vercel logs <deployment-url>`
2. **簡化入口點**: 移除複雜依賴
3. **環境變數**: 確保所有必要的環境變數已設置
4. **配置驗證**: 檢查 `vercel.json` 語法

#### 3. 迭代修復
- **小步快跑**: 每次只修復一個問題
- **驗證結果**: 每次修復後立即測試
- **記錄過程**: 記錄每次嘗試和結果

### 部署嘗試記錄

| 嘗試 | 問題 | 解決方案 | 學習點 |
|------|------|----------|--------|
| 1 | builds + functions 衝突 | 移除 functions | 配置衝突檢測 |
| 2 | 多區域部署限制 | 移除 regions | 免費方案限制 |
| 3 | 檔案大小超限 | 創建 .vercelignore | 檔案過濾策略 |
| 4 | 環境變數引用錯誤 | 修正 vercel.json | 環境變數管理 |
| 5 | Python 運行時版本 | 更新為 @vercel/python | 運行時兼容性 |
| 6 | 模組導入錯誤 | 創建簡化入口點 | **核心學習** |

---

## 🎓 最佳實踐總結

### Serverless 部署原則

#### 1. **自包含性原則**
```python
# ✅ 好的模式
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
# 直接在入口點定義所有代碼

# ❌ 避免的模式
from complex.module import something
from config import settings
# 複雜的模組導入
```

#### 2. **環境差異處理**
```python
# ✅ 環境適應性代碼
import os
database_url = os.getenv("DATABASE_URL", "default_value")

# ❌ 硬編碼配置
database_url = "hardcoded://localhost:5432"
```

#### 3. **最小化依賴**
```python
# ✅ 最小依賴
from fastapi import FastAPI
import httpx  # 標準庫或明確安裝的包

# ❌ 複雜依賴
from myproject.services.cache import CacheManager
from myproject.utils.helpers import complex_helper
```

### 配置管理最佳實踐

#### 1. **環境變數策略**
- 使用平台原生的環境變數管理
- 不要將敏感信息提交到代碼庫
- 為不同環境創建不同的配置

#### 2. **檔案結構優化**
```
專案根目錄/
├── api/           # Serverless 入口點
│   └── index.py   # 自包含的 FastAPI 應用
├── src/           # 完整應用代碼（用於其他部署）
├── vercel.json    # Vercel 配置
└── .vercelignore  # 檔案過濾
```

#### 3. **錯誤處理策略**
```python
# ✅ 優雅的錯誤處理
try:
    from optional_module import something
    FEATURE_AVAILABLE = True
except ImportError:
    FEATURE_AVAILABLE = False
    logger.warning("Optional feature not available")

# ❌ 硬性依賴
from required_module import something  # 如果不存在就崩潰
```

---

## 🚀 未來改進方向

### 短期改進（1-2 週）

#### 1. **功能擴展**
- 將 `src/api/routers/` 中的功能遷移到 Vercel
- 添加 Supabase 數據庫集成
- 實現完整的 API 端點

#### 2. **監控與日誌**
- 配置 Vercel Analytics
- 設置錯誤追蹤
- 實現性能監控

### 中期改進（1-2 個月）

#### 1. **架構優化**
- 評估微服務架構
- 考慮多平台部署（Railway 備份）
- 實現自動化 CI/CD

#### 2. **性能優化**
- 實現 Redis 快取（需要付費方案）
- 優化冷啟動時間
- 添加 CDN 配置

### 長期規劃（3-6 個月）

#### 1. **可擴展性**
- 多區域部署
- 負載均衡
- 自動擴展

#### 2. **功能完整性**
- 完整的 LLM 集成
- 高級快取策略
- 實時監控儀表板

---

## 📖 相關資源

### 官方文檔
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Serverless Functions Best Practices](https://vercel.com/docs/functions/serverless-functions)

### 學習資源
- [Serverless Architecture Patterns](https://serverlessland.com/patterns)
- [Python Packaging Best Practices](https://packaging.python.org/en/latest/)
- [Environment Variables Management](https://12factor.net/config)

---

## 🎯 關鍵收穫

### 技術收穫
1. **Serverless 環境理解**: 深入理解 Serverless 的限制和優勢
2. **模組化設計**: 學會為不同部署環境設計不同的入口點
3. **問題解決流程**: 建立系統性的部署問題診斷和解決流程

### 流程收穫
1. **迭代修復**: 小步快跑，逐步解決問題
2. **文檔記錄**: 詳細記錄每次嘗試和結果
3. **學習導向**: 將每次錯誤轉化為學習機會

### 心態收穫
1. **耐心與堅持**: 部署是一個迭代過程，需要耐心
2. **系統性思考**: 從架構層面理解問題的根本原因
3. **最佳實踐**: 建立可重用的部署模式和流程

---

**總結**: 這次部署經歷讓我們深刻理解了 Serverless 環境的特殊性，學會了如何為不同的部署平台設計適合的架構。最重要的是，我們建立了系統性的問題解決流程，這將在未來的部署中發揮重要作用。

> "每一次部署失敗都是一次學習機會，每一次成功都是下一次挑戰的起點。"
