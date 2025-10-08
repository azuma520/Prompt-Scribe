# Prompt-Scribe - 階段一：本地資料管線

這是 Prompt-Scribe 專案的階段一實作，專注於在本機完成高效的資料處理。

## 📋 概述

階段一負責：
- 收集與清理原始 Prompt 資料
- 資料驗證與品質保證
- （可選）使用資料層 LLM 進行標記與分類
- 產出可攜式的「黃金資料資產」(`tags.db`)

## 🏗️ 架構

```
原始資料 → 資料清理 → 驗證 → LLM 標記 → 驗證 → tags.db
```

## 📁 目錄結構

```
stage1/
├── src/                    # 原始碼
│   ├── __init__.py
│   ├── main.py             # 主程式入口
│   ├── config.py           # 設定檔
│   ├── models/             # 資料模型
│   ├── pipeline/           # 資料管線
│   ├── validation/         # 驗證邏輯
│   ├── llm/                # LLM 整合（資料層）
│   └── utils/              # 工具函式
├── tests/                  # 測試
│   ├── unit/               # 單元測試
│   ├── integration/        # 整合測試
│   └── fixtures/           # 測試資料
├── data/                   # 資料目錄
│   ├── raw/                # 原始資料
│   ├── processed/          # 處理後資料
│   └── output/             # 產出（tags.db）
├── docs/                   # 文件
├── requirements.txt        # 依賴套件
└── README.md               # 本文件
```

## 🚀 快速開始

### 安裝依賴

```bash
cd stage1
pip install -r requirements.txt
```

### 設定環境變數

建立 `.env` 檔案（參考 `.env.example`）：

```bash
# LLM API Keys (Optional)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Processing Options
ENABLE_LLM_TAGGING=false
LOG_LEVEL=INFO
```

### 執行資料處理

```bash
python src/main.py
```

### 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/unit/test_validation.py

# 生成覆蓋率報告
pytest --cov=src --cov-report=html
```

## 📊 資料流程

### 1. 資料輸入
- 支援格式：JSON, CSV, TXT
- 放置位置：`data/raw/`

### 2. 資料清理
- 移除重複項目
- 格式標準化
- 基本品質檢查

### 3. 資料驗證
- 使用 Pydantic 進行結構驗證
- 檢查必填欄位
- 驗證資料類型與格式

### 4. LLM 標記（可選）
- 使用資料層 LLM API 進行內容分析
- 生成標籤與分類
- **所有推理結果完整記錄**

### 5. 最終驗證
- 驗證處理後資料的完整性
- 檢查資料一致性
- 生成品質報告

### 6. 產出黃金資料資產
- 輸出至 SQLite 資料庫：`data/output/tags.db`
- 包含所有處理後的 Prompt 與標籤
- 可直接用於階段二遷移

## 🧪 測試策略

### 單元測試
- 測試覆蓋率目標：≥ 80%
- 測試所有資料驗證邏輯
- 測試 LLM 整合（使用 Mock）

### 整合測試
- 測試完整資料管線
- 測試真實資料處理場景
- 驗證產出資料品質

### 資料品質測試
- 邊界條件測試
- 異常資料處理測試
- 大量資料壓力測試

## 📝 開發指南

### 新增資料處理步驟

1. 在 `.specify/specs/` 建立規格文件
2. 在 `src/pipeline/` 建立處理模組
3. 在 `tests/` 建立對應測試
4. 更新 `main.py` 整合新步驟

### 新增資料驗證規則

1. 在 `src/models/` 更新 Pydantic 模型
2. 在 `src/validation/` 建立驗證邏輯
3. 在 `tests/` 建立驗證測試

### 整合新的 LLM 服務

1. 在 `.specify/specs/` 定義 LLM 使用規格
2. 在 `src/llm/` 建立 API 客戶端
3. **確保實作完整的記錄機制**
4. 在 `tests/` 建立 Mock 測試

## ⚠️ 重要提醒

### 資料品質優先
- 資料正確性是最高優先級
- 發現問題立即修正，不可延後
- 每個處理步驟都要有驗證

### LLM 職責分離
- 只使用資料層 LLM API
- 不要用 IDE LLM 處理生產資料
- 所有 LLM 推理結果必須記錄

### 無雲端依賴
- 除了 LLM API（可選），不依賴其他雲端服務
- 所有處理必須能在本機完成
- 資料主權完全掌握在使用者手中

## 📈 產出物

### tags.db 結構

```sql
-- Prompts 表
CREATE TABLE prompts (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP,
    processed_at TIMESTAMP
);

-- Tags 表
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT
);

-- Prompt-Tag 關聯表
CREATE TABLE prompt_tags (
    prompt_id TEXT,
    tag_id TEXT,
    confidence REAL,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id),
    PRIMARY KEY (prompt_id, tag_id)
);

-- LLM 推理記錄表（若啟用 LLM）
CREATE TABLE llm_inference_log (
    id TEXT PRIMARY KEY,
    prompt_id TEXT,
    model TEXT NOT NULL,
    parameters TEXT,
    input_hash TEXT,
    output TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);
```

## 🔍 除錯

### 啟用詳細日誌

```bash
LOG_LEVEL=DEBUG python src/main.py
```

### 常見問題

**Q: 資料處理失敗怎麼辦？**
A: 檢查 `logs/` 目錄的日誌檔案，找出錯誤原因。

**Q: LLM API 限流怎麼處理？**
A: 實作重試機制與降級邏輯，詳見規格文件。

**Q: tags.db 檔案損壞？**
A: 使用 SQLite 內建的完整性檢查工具修復。

## 📚 相關文件

- [專案開發憲法](../.specify/memory/constitution.md)
- [階段一規格文件](../.specify/specs/)
- [資料處理計畫](../.specify/plans/)

---

**本階段嚴格遵循憲法原則，確保資料品質與可攜性。**

