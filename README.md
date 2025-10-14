# Prompt-Scribe

一個遵循兩階段混合式架構的 Prompt 管理與分析系統。

## 📋 專案概述

**Prompt-Scribe** 是一個設計用於收集、標記、分析與服務化 AI Prompt 的系統。本專案嚴格遵循[專案開發憲法](.specify/memory/constitution.md)，採用兩階段混合式架構：

- **階段一：本地資料管線** - 使用 Python + SQLite 在本機完成高效資料處理
- **階段二：雲端應用後端** - 將處理後的資料遷移至 Supabase，提供 API 與多使用者服務

## 🎯 核心特色

- ✅ **資料主權優先**：核心處理在本地完成，使用者擁有完整控制權
- ✅ **規格驅動開發**：所有功能基於明確的規格文件
- ✅ **LLM 職責分離**：嚴格區分開發助手 LLM 與資料處理 LLM
- ✅ **資料品質保證**：每個處理階段都有完整的驗證邏輯
- ✅ **可審計性**：所有 AI 推理結果都被完整記錄

## 🏗️ 架構設計

### 階段一：本地資料管線

```
原始 Prompts → 資料清理 → 標記分類 → 驗證 → tags.db (黃金資料資產)
```

**技術棧：**
- Python 3.11+
- SQLite
- Pydantic (資料驗證)
- OpenAI/Anthropic API (可選，用於內容分析)

**產出物：**
- `tags.db`: 包含所有處理後的 Prompt 資料與標籤

### 階段二：雲端應用後端

```
tags.db → 遷移 → Supabase (PostgreSQL) → 向量化 → API 服務
```

**技術棧：**
- Supabase (PostgreSQL + pgvector)
- RESTful API
- OpenAI Embeddings (向量化)

**產出物：**
- 雲端資料庫
- 語意搜尋 API
- 多使用者支援

## 📁 專案結構

```
Prompt-Scribe/
│
├── 📁 docs/                    # 專案文檔（分類整理）
│   ├── migration/              # 遷移相關文檔
│   ├── testing/                # 測試相關文檔
│   ├── api-planning/           # API 規劃文檔
│   ├── reports/                # 其他報告
│   └── quickstart.md           # 快速開始
│
├── 📁 specs/                   # 規格和計畫（PLAN-2025-004, 005）
│   └── 001-sqlite-ags-db/      # SQLite 遷移至 Supabase
│       ├── spec.md             # 功能規格
│       ├── plan*.md            # 開發計畫
│       ├── research*.md        # 技術研究
│       ├── tasks*.md           # 任務清單
│       ├── contracts/          # API 規格和資料庫 Schema
│       └── checklists/         # 需求檢查清單
│
├── 📁 src/                     # 原始碼
│   ├── migration/              # ✅ 資料遷移模組（已完成）
│   ├── api/                    # ⏳ API 模組（待開發）
│   └── embeddings/             # ⏳ Embedding 模組（未來）
│
├── 📁 scripts/                 # SQL 資料庫腳本
│   ├── 01_enable_extensions.sql
│   ├── 02_create_tables.sql
│   ├── 03_create_indexes.sql
│   ├── 04_create_rls_policies.sql
│   ├── 05_create_rpc_functions.sql
│   ├── 06_create_search_functions.sql
│   └── README.md
│
├── 📁 tests/                   # 測試程式
│   ├── database/               # ✅ 資料庫測試（已完成）
│   ├── migration/              # ✅ 遷移測試（已完成）
│   └── api/                    # ⏳ API 測試（待開發）
│
├── 📁 stage1/                  # 階段一：本地資料管線
│   ├── src/classifier/         # 標籤分類器
│   ├── output/                 # 輸出檔案（tags.db）
│   ├── docs/                   # 階段一文檔
│   ├── supabase_tools/         # Supabase 工具
│   └── requirements.txt
│
├── 📁 archive/                 # 歸檔目錄
│   ├── test-scripts/           # 臨時測試腳本
│   └── temp-scripts/           # 臨時檔案
│
├── 📄 README.md                # 專案說明（本文件）
├── 📄 LICENSE                  # 授權
└── 📄 requirements.txt         # 專案依賴
```

## 🚀 快速開始

### 前置需求

- Python 3.11 或更高版本
- Git
- （可選）Supabase 帳號（用於階段二）
- （可選）OpenAI/Anthropic API 金鑰（用於 LLM 功能）

### 階段一：本地資料處理

```bash
# Clone 專案
git clone https://github.com/your-username/Prompt-Scribe.git
cd Prompt-Scribe

# 進入階段一目錄
cd stage1

# 安裝依賴
pip install -r requirements.txt

# 執行資料處理
python src/main.py

# 執行測試
pytest tests/
```

### 階段二：雲端部署

（待階段一完成後更新此部分）

## 📚 文件導覽

### 治理文件
- [專案開發憲法](.specify/memory/constitution.md) - 專案最高指導原則
- [合規性審查記錄](.specify/memory/compliance-log.md) - 季度合規審查結果
- [原則例外記錄](.specify/memory/exceptions-log.md) - 已批准的原則例外

### 開發文件
- [規格文件目錄](.specify/specs/) - 所有功能規格
- [開發計畫目錄](.specify/plans/) - 開發計畫與時程
- [任務清單目錄](.specify/tasks/) - 詳細任務分解

### 模板文件
- [規格模板](.specify/templates/spec-template.md) - 撰寫新規格時使用
- [計畫模板](.specify/templates/plan-template.md) - 規劃新開發時使用
- [任務模板](.specify/templates/tasks-template.md) - 任務分解時使用

## 🔧 開發指南

### 規格驅動開發流程（SDD）

1. **撰寫規格**：在 `.specify/specs/` 中創建規格文件
2. **審查規格**：進行技術審查與憲法合規性檢查
3. **批准規格**：規格狀態更新為 "Approved"
4. **實作功能**：基於規格進行開發
5. **驗收測試**：確認符合規格中的驗收標準

### 使用 Speckit 命令

本專案使用 Speckit 框架進行文件管理：

```bash
# 建立或更新憲法
/speckit.constitution

# 建立新規格
/speckit.spec

# 建立開發計畫
/speckit.plan

# 建立任務清單
/speckit.tasks
```

### 程式碼風格

- Python: 遵循 PEP 8
- 使用 Black 進行程式碼格式化
- 使用 pylint 進行程式碼檢查
- 單元測試覆蓋率 ≥ 80%

### Git 工作流程

```bash
# 建立功能分支
git checkout -b feature/SPEC-YYYY-NUMBER-feature-name

# 提交變更
git commit -m "feat(scope): description [SPEC-YYYY-NUMBER]"

# 推送並建立 PR
git push origin feature/SPEC-YYYY-NUMBER-feature-name
```

## 🧪 測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_data_validation.py

# 生成覆蓋率報告
pytest --cov=src --cov-report=html
```

## 📊 專案狀態

### 當前進度

- ✅ **階段一**：本地資料管線（已完成，140,782 筆標籤）
- ✅ **資料遷移**：SQLite → Supabase（100% 成功）
- ✅ **資料庫測試**：完整測試套件已建立
- ⏳ **API 開發**：規劃完成，準備實作
- ⏳ **前端開發**：待後續進行

### 重要里程碑

- **2025-01-14**: 完成資料遷移（140,782 筆記錄）
- **2025-01-14**: 完成資料庫測試套件
- **2025-01-14**: 完成 API 優化計畫
- **Next**: 開始 API 實作

### 快速連結

- [遷移完成報告](docs/migration/FINAL_COMPLETION_REPORT.md)
- [測試套件文檔](docs/testing/DATABASE_TEST_SUITE_COMPLETE.md)
- [API 優化計畫](docs/api-planning/API_OPTIMIZATION_PLANNING_COMPLETE.md)
- [資料庫測試](tests/database/README.md)

## 🤝 貢獻指南

1. 閱讀[專案開發憲法](.specify/memory/constitution.md)
2. 確保所有變更基於已審核的規格
3. 提交前執行完整測試
4. 遵循 Git 提交訊息規範
5. 所有 PR 必須通過 Code Review

## 📄 授權

（待定）

## 📞 聯絡方式

（待定）

---

**本專案嚴格遵循[專案開發憲法](.specify/memory/constitution.md)。所有參與者必須熟悉並遵守憲法中的核心原則。**

