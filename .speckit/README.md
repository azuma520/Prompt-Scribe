# 📋 Speckit - Prompt-Scribe 架構規範系統

**版本**: V1.0.0  
**建立日期**: 2025-10-15

---

## 🎯 系統概述

Speckit 是 Prompt-Scribe 專案的架構規範管理系統,確保整個代碼庫始終遵循 `PROJECT_STRUCTURE.md` 定義的架構標準。

### 核心功能

✅ **架構憲法** - 定義不可違反的組織原則  
✅ **自動驗證** - 檢查專案是否符合規範  
✅ **配置管理** - 集中管理架構規則  
✅ **持續監控** - CI/CD 整合確保合規

---

## 📁 系統組成

```
.speckit/
├── constitution.md       # 📜 專案憲法（架構規範）
├── config.yaml          # ⚙️  架構配置（規則定義）
├── validate.py          # 🔍 驗證工具（自動檢查）
└── README.md            # 📖 使用說明（本文件）
```

### 文件說明

#### 1. `constitution.md` - 專案憲法

**用途**: 定義 Prompt-Scribe 的架構憲法和核心原則

**內容**:
- 8 大核心原則
- 目錄職責定義
- 開發流程規範
- 代碼品質標準
- 測試覆蓋要求
- 文檔同步原則

**權威性**: ⭐⭐⭐ 最高級別,所有開發必須遵循

#### 2. `config.yaml` - 架構配置

**用途**: 機器可讀的架構規則配置

**內容**:
- 目錄結構定義
- 核心服務清單
- API 路由規範
- 測試標準
- 代碼品質規則
- CI/CD 配置

**用途**: 被 `validate.py` 工具讀取進行自動驗證

#### 3. `validate.py` - 驗證工具

**用途**: 自動檢查專案是否符合架構規範

**功能**:
- ✅ 目錄結構驗證
- ✅ 核心服務檢查
- ✅ API 路由驗證
- ✅ 測試覆蓋檢查
- ✅ 文檔完整性驗證
- ✅ 命名規範檢查
- ✅ 禁止模式檢測

**輸出**: 詳細驗證報告 + 評級 (A+/A/B/C)

---

## 🚀 快速開始

### 安裝依賴

```bash
# 安裝 PyYAML (用於讀取配置)
pip install pyyaml
```

### 運行驗證

```bash
# 在專案根目錄執行
python .speckit/validate.py

# 或指定專案路徑
python .speckit/validate.py --project-root /path/to/prompt-scribe

# 嚴格模式 (警告也視為失敗)
python .speckit/validate.py --strict
```

### 查看憲法

```bash
# 閱讀專案憲法
cat .speckit/constitution.md

# 或用 Markdown 查看器打開
code .speckit/constitution.md
```

---

## 📊 驗證報告範例

### 完全符合 (A+ 評級)

```
🚀 Prompt-Scribe 架構規範驗證
📁 專案路徑: D:\Prompt-Scribe
📋 配置文件: .speckit\config.yaml
📌 專案版本: V2.0.0

🔍 檢查目錄結構...
🔍 檢查核心服務...
🔍 檢查 API 路由...
🔍 檢查測試套件...
🔍 檢查文檔完整性...
🔍 檢查 CI/CD 配置...
🔍 檢查部署配置...
🔍 檢查命名規範...
🔍 檢查代碼模式...

======================================================================
📊 Prompt-Scribe 架構驗證報告
======================================================================

✅ 通過檢查: 47
⚠️  警告事項: 0
❌ 錯誤事項: 0
📈 通過率: 100.0%

✅ 主要檢查通過:
  ✓ 目錄存在: 12 項
  ✓ 服務存在: 13 項
  ✓ 路由存在: 7 項
  ✓ 測試存在: 6 項
  ✓ 文檔存在: 9 項

======================================================================
🏆 評級: A+ (完全符合架構規範)
```

### 有改進空間 (A 評級)

```
======================================================================
📊 Prompt-Scribe 架構驗證報告
======================================================================

✅ 通過檢查: 45
⚠️  警告事項: 3
❌ 錯誤事項: 0
📈 通過率: 93.8%

⚠️  警告事項:
  • CI/CD 工作流缺失: performance-check.yml (觸發: schedule_daily)
  • 服務文件缺失: redis_cache_manager.py (Redis 快取, V2-P2)
  • API 文檔缺失: src/api/tests/TESTING_GUIDE.md

======================================================================
🥈 評級: A (符合核心規範,有改進空間)
```

### 需要修正 (B 評級)

```
======================================================================
📊 Prompt-Scribe 架構驗證報告
======================================================================

✅ 通過檢查: 40
⚠️  警告事項: 8
❌ 錯誤事項: 3
📈 通過率: 78.4%

❌ 嚴重錯誤:
  • 必要文檔缺失: PROJECT_STRUCTURE.md
  • 缺少必要目錄: src/api/services (核心服務)
  • 缺少必要目錄: src/api/tests (測試套件)

======================================================================
⚠️  評級: B (有少量違規,需要修正)
```

---

## 🔧 整合到開發流程

### 1. Pre-commit Hook

在 `.git/hooks/pre-commit` 添加:

```bash
#!/bin/bash
echo "🔍 執行架構驗證..."
python .speckit/validate.py --strict

if [ $? -ne 0 ]; then
    echo "❌ 架構驗證失敗,請修正後再提交"
    exit 1
fi

echo "✅ 架構驗證通過"
```

```bash
chmod +x .git/hooks/pre-commit
```

### 2. CI/CD 整合

在 `.github/workflows/architecture-check.yml`:

```yaml
name: Architecture Validation

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install pyyaml
      
      - name: Run architecture validation
        run: python .speckit/validate.py --strict
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: architecture-report
          path: architecture-report.txt
```

### 3. VS Code Task

在 `.vscode/tasks.json` 添加:

```json
{
  "label": "驗證架構規範",
  "type": "shell",
  "command": "python",
  "args": [".speckit/validate.py"],
  "group": {
    "kind": "test",
    "isDefault": false
  },
  "presentation": {
    "reveal": "always",
    "panel": "new"
  }
}
```

---

## 📖 使用場景

### 場景 1: 新開發者入職

```bash
# 1. 閱讀專案憲法
cat .speckit/constitution.md

# 2. 了解架構規範
cat PROJECT_STRUCTURE.md

# 3. 驗證當前環境
python .speckit/validate.py
```

### 場景 2: 添加新功能前

```bash
# 1. 檢查當前架構狀態
python .speckit/validate.py

# 2. 參考憲法確定文件位置
# 查看 constitution.md 的 "新功能添加流程"

# 3. 開發完成後再次驗證
python .speckit/validate.py
```

### 場景 3: 重構代碼

```bash
# 1. 記錄重構前狀態
python .speckit/validate.py > before.txt

# 2. 進行重構

# 3. 對比驗證
python .speckit/validate.py > after.txt
diff before.txt after.txt
```

### 場景 4: Pull Request 審查

```bash
# 審查者執行
git checkout feature-branch
python .speckit/validate.py --strict

# 確保符合架構規範再批准 PR
```

---

## 🎓 核心原則速查

### 8 大核心原則

1. **架構不可變性** - 嚴格遵循 PROJECT_STRUCTURE.md
2. **模組職責分離** - 每個目錄有明確職責
3. **服務模組規範** - 13 個核心服務的組織方式
4. **API 端點組織** - V1 基礎 + LLM 優化的結構
5. **測試覆蓋要求** - 最低 90%, 目標 95%+
6. **文檔同步原則** - 代碼變更必須同步文檔
7. **配置管理規範** - 環境變數 + 平台配置
8. **CI/CD 自動化** - 自動測試 + 部署 + 監控

### 目錄職責

```
src/api/models/      → 僅資料模型 (Pydantic)
src/api/routers/     → 僅 HTTP 路由
src/api/services/    → 核心業務邏輯
src/api/middleware/  → HTTP 中間件
src/api/data/        → 靜態配置
src/api/tests/       → 完整測試
```

### 禁止行為

❌ 在 `models/` 寫業務邏輯  
❌ 在 `routers/` 直接操作資料庫  
❌ 在 `services/` 處理 HTTP  
❌ 測試文件放在非 `tests/` 目錄  
❌ 硬編碼敏感資訊  
❌ 提交 `.env` 文件

---

## 🔄 更新 Speckit

### 修改配置規則

1. 編輯 `.speckit/config.yaml`
2. 測試驗證工具: `python .speckit/validate.py`
3. 更新文檔: `.speckit/constitution.md`
4. 提交變更

### 修改憲法原則

1. 提出修正案 (Issue/RFC)
2. 團隊審查討論
3. 更新 `constitution.md` + 版本號
4. 同步更新 `config.yaml`
5. 通知所有開發者

### 擴展驗證工具

1. 編輯 `.speckit/validate.py`
2. 添加新的驗證方法
3. 在 `run()` 中調用
4. 測試完整性
5. 更新文檔

---

## 📊 統計資訊

### Speckit V1.0.0

```
文件數:       4
代碼行數:     1,200+
驗證規則:     50+
覆蓋檢查:     9 大類
配置項:       100+
```

### 驗證能力

```
目錄結構:     12+ 必要目錄
核心服務:     13 個服務
API 路由:     7 個路由
測試套件:     6 個測試文件
文檔文件:     15+ 必要文檔
CI/CD 流程:   3 個工作流
部署配置:     4 種平台
```

---

## 🆘 常見問題

### Q1: 驗證失敗怎麼辦?

**A**: 查看驗證報告,根據錯誤和警告逐項修正:
- **錯誤** (❌): 必須修正
- **警告** (⚠️): 建議修正
- **通過** (✅): 保持現狀

### Q2: 需要修改架構怎麼辦?

**A**: 遵循憲法修正案流程:
1. 提出修正案說明原因
2. 更新 PROJECT_STRUCTURE.md
3. 更新 .speckit/constitution.md
4. 更新 .speckit/config.yaml
5. 獲得團隊批准

### Q3: 新功能放在哪個目錄?

**A**: 參考 constitution.md 的「新功能添加流程」:
- 端點 → `routers/`
- 業務邏輯 → `services/`
- 資料模型 → `models/`
- 測試 → `tests/`

### Q4: 如何提高驗證通過率?

**A**:
1. 閱讀 constitution.md 了解規範
2. 參考 PROJECT_STRUCTURE.md 了解架構
3. 運行 validate.py 查看具體問題
4. 逐項修正錯誤和警告
5. 再次驗證直到通過

### Q5: 嚴格模式什麼時候用?

**A**: 
- **CI/CD**: 使用嚴格模式確保品質
- **本地開發**: 普通模式,允許警告
- **重構**: 嚴格模式確保不破壞架構
- **PR 審查**: 嚴格模式作為合並條件

---

## 🌟 最佳實踐

### 開發前

✅ 閱讀 constitution.md 了解規範  
✅ 運行 validate.py 確認當前狀態  
✅ 規劃文件放置位置

### 開發中

✅ 遵循目錄職責分離原則  
✅ 保持命名規範一致  
✅ 編寫對應測試  
✅ 添加適當文檔

### 開發後

✅ 運行 validate.py 驗證架構  
✅ 運行測試確保覆蓋率  
✅ 更新相關文檔  
✅ 通過 CI/CD 檢查

### 提交前

✅ 本地驗證通過  
✅ 測試全部通過  
✅ 文檔已同步  
✅ 遵循 Git 規範

---

## 📚 相關文檔

- [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) - 專案架構文檔
- [README.md](../README.md) - 專案主說明
- [CHANGELOG.md](../CHANGELOG.md) - 版本歷史
- [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) - 部署指南
- [src/api/README.md](../src/api/README.md) - API 開發指南

---

## 🔮 未來規劃

### V1.1
- [ ] 添加代碼複雜度檢查
- [ ] 集成依賴關係分析
- [ ] 生成架構圖表

### V1.2
- [ ] 自動修復常見問題
- [ ] 互動式驗證模式
- [ ] Web UI 儀表板

### V2.0
- [ ] AI 輔助架構建議
- [ ] 歷史趨勢分析
- [ ] 多專案支援

---

**Speckit 狀態**: ✅ 生產就緒  
**更新日期**: 2025-10-15  
**版本**: V1.0.0

---

> "架構規範不是限制創新,而是確保創新建立在穩固的基礎之上。"

