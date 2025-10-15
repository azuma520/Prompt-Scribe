# 專案檔案整理報告

## 整理摘要

### 問題識別
- 專案根目錄有 **4,716 個 SQL 檔案**，造成目錄混亂
- 大量臨時腳本檔案散落在根目錄
- 缺乏清晰的檔案組織結構

### 整理行動

#### 1. SQL 批次檔案整理
- 將 **4,716 個 batch_*.sql 檔案** 移至 `output/` 目錄
- 這些檔案包含從 SQLite 導出的批次資料，用於 Supabase 上傳

#### 2. 臨時腳本檔案整理
創建 `temp_files/` 目錄並移入 **50 個臨時腳本**：
- 批次處理相關：`create_*.py`, `batch_*.py`, `upload_*.py`
- 執行相關：`execute_*.py`, `auto_*.py`, `chunked_*.py`
- 檢查相關：`check_*.py`, `fix_*.py`, `analyze_*.py`
- 其他工具：`mcp_*.py`, `migrate_*.py`, `identify_*.py`

#### 3. 文檔整理
- 將所有 `.md` 檔案移至 `docs/` 目錄
- 保持文檔結構清晰

#### 4. 資料檔案整理
- 將 `tags_data.csv` 移至 `output/` 目錄
- 確保資料檔案集中管理

### 整理後結構

#### 主要目錄
```
stage1/
├── src/                    # 核心源碼
├── output/                 # 輸出檔案 (3,016 個檔案)
│   ├── batch_*.sql        # SQL 批次檔案
│   ├── tags_data.csv      # 導出的資料
│   └── ...
├── temp_files/            # 臨時檔案 (50 個腳本)
├── docs/                  # 文檔檔案
├── deployment_tools/      # 部署工具
├── supabase_tools/        # Supabase 工具
├── data/                  # 原始資料
├── tests/                 # 測試檔案
└── archive/               # 封存檔案
```

#### 核心檔案
- `config.py` - 配置檔案
- `optimized_llm_classifier.py` - 優化的 LLM 分類器
- `qwen_classifier.py` - Qwen 分類器
- `export_sqlite_to_csv.py` - 資料導出工具
- `requirements.txt` - Python 依賴

### 效益

#### 1. 目錄清晰度
- 根目錄檔案數量從 4,700+ 減少到 50+
- 清晰的目錄結構便於導航

#### 2. 維護性提升
- 臨時檔案集中管理
- 核心檔案易於識別
- 文檔統一存放

#### 3. 部署準備
- 輸出檔案集中管理
- 批次檔案便於批量處理
- 工具腳本分類整理

### 後續建議

#### 1. 批次檔案處理
- 考慮壓縮 output 目錄中的 SQL 檔案
- 建立批次上傳的自動化腳本

#### 2. 清理策略
- 定期清理 temp_files 中的過期腳本
- 建立檔案生命週期管理

#### 3. 文檔維護
- 更新 README 反映新的目錄結構
- 建立檔案用途說明

## 總結

成功整理了專案檔案結構，從混亂的 4,700+ 檔案狀態改善為清晰的目錄組織。這為後續的 Supabase 部署和專案維護奠定了良好的基礎。

**整理時間**: 2025-01-13
**處理檔案**: 4,766 個檔案
**新增目錄**: 1 個 (temp_files)
**移動檔案**: 4,716 個 SQL 檔案 + 50 個腳本檔案


