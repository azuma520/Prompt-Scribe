# Stage1 檔案整理計劃

## 📁 檔案分類

### ✅ 核心程式（保留）

**主要程式**：
- `config.py` - 專案配置
- `data_rules.py` - 分類規則
- `run_pipeline.py` - 主要執行腳本
- `requirements.txt` - Python 依賴
- `README.md` - 說明文件

**分類系統**：
- `src/` - 核心程式碼目錄
  - `classifier/categories.py` - 分類定義
  - `classifier/rule_classifier.py` - 規則分類器
  - `classifier/rules/` - 規則模組

**LLM 增強**：
- `llm_config.py` - LLM 配置
- `qwen_classifier.py` - LLM 分類器
- `migrate_db_for_llm.py` - 資料庫遷移
- `run_llm_auto.py` - 自動批次處理

**工具腳本**：
- `quick_stats.py` - 快速統計
- `test_classification_quality.py` - 品質測試
- `view_llm_results.py` - 結果查看
- `llm_stats.py` - LLM 統計
- `review_llm_results.py` - 結果審查

**資料**：
- `data/raw/` - 原始資料（CSV）
- `output/tags.db` - 資料庫（最重要）⭐
- `output/pipeline.log` - 執行日誌

**文檔**（保留最新）：
- `LLM_ENHANCEMENT_FINAL_REPORT.md` - LLM 增強最終報告
- `LLM_SETUP_GUIDE.md` - LLM 設定指南
- `INTEGRATION_SUMMARY.md` - 整合總結

---

### 🗑️ 可刪除的檔案

**舊的測試腳本**（已完成任務）：
- `test_deepseek_api.py`
- `test_qwen_classifier.py`
- `test_20_tags.py`
- `test_classifier.py`
- `text_batch_test.py`
- `comprehensive_db_test.py`
- `check_real_tags.py`
- `real_world_usage_test.py`
- `final_validation.py`

**舊的分析腳本**（已完成分析）：
- `analyze_data.py`
- `explain_coverage_difference.py`
- `low_frequency_tag_analysis.py`
- `llm_candidate_analysis.py`
- `verify_background_fix.py`
- `verify_frequency_impact.py`
- `generate_detailed_stats.py`
- `update_env_model.py`

**舊的配置/腳本**（已被新版取代）：
- `deepseek_config.py` - 被 llm_config.py 取代
- `deepseek_batch_classifier.py` - 被 qwen_classifier.py 取代
- `run_llm_enhancement.py` - 互動式版本（可選保留）

**舊的報告文檔**（歷史記錄）：
- `PHASE1_COMPLETION_SUMMARY.md`
- `PHASE2_IMPROVEMENT_REPORT.md`
- `PHASE2_RULE_ENHANCEMENT_PLAN.md`
- `PHASE2.5_FINAL_REPORT.md`
- `PHASE2.6_ACHIEVEMENT_REPORT.md`
- `PHASE2.6_EXECUTIVE_SUMMARY.md`
- `ACCURACY_AND_IMPROVEMENT_PLAN.md`
- `CREATIVE_VALUE_ENHANCEMENT_PLAN.md`
- `DEEPSEEK_EXECUTION_PLAN.md`
- `REAL_WORLD_VALUE_ASSESSMENT.md`
- `BUGFIX_REPORT.md`
- `FINAL_REPORT.md`
- `IMPLEMENTATION_COMPLETED.md`
- `IMPLEMENTATION_SUMMARY.md`
- `SQL_TEST_FINAL_SUMMARY.md`
- `coverage_visualization.md`

**舊的輸出檔案**：
- `output/DATA_ANALYSIS.md`
- `output/FINAL_SUMMARY.txt`
- `output/IMPLEMENTATION_SUMMARY.md`
- `output/llm_candidates.txt`
- `output/classification_report.txt` - 可保留作為參考
- `analysis_result.txt`

**其他**：
- `QUICKSTART.md` - 可整合到 README
- `LLM_ENHANCEMENT_SUMMARY.txt` - 簡化版，可選刪除

---

## 📋 清理建議

### 方案 A：激進清理（推薦）
刪除所有舊的測試、分析腳本和報告，只保留核心程式和最新文檔。

**保留檔案數**: ~25 個
**刪除檔案數**: ~45 個

### 方案 B：保守清理
保留一些有用的測試腳本和關鍵報告。

**保留檔案數**: ~35 個
**刪除檔案數**: ~35 個

### 方案 C：建立歷史目錄
將舊檔案移到 `archive/` 目錄而非刪除。

**保留檔案數**: 全部
**組織方式**: 分類到子目錄

---

## 🎯 建議的最終結構

```
stage1/
├── config.py
├── data_rules.py
├── run_pipeline.py
├── requirements.txt
├── README.md
│
├── llm_config.py
├── qwen_classifier.py
├── migrate_db_for_llm.py
├── run_llm_auto.py
│
├── quick_stats.py
├── test_classification_quality.py
├── view_llm_results.py
├── llm_stats.py
├── review_llm_results.py
│
├── src/
│   └── classifier/
│       ├── categories.py
│       ├── rule_classifier.py
│       └── rules/
│
├── data/
│   └── raw/
│       └── *.csv
│
├── output/
│   ├── tags.db ⭐
│   ├── pipeline.log
│   └── classification_report.txt
│
└── docs/
    ├── LLM_ENHANCEMENT_FINAL_REPORT.md
    ├── LLM_SETUP_GUIDE.md
    ├── INTEGRATION_SUMMARY.md
    └── archive/
        └── (舊報告)
```

---

## ✅ 執行步驟

1. 建立 `docs/` 和 `docs/archive/` 目錄
2. 移動最新文檔到 `docs/`
3. 移動舊報告到 `docs/archive/`
4. 刪除舊的測試和分析腳本
5. 清理 `__pycache__` 目錄
6. 更新 README 反映新結構

---

選擇您偏好的方案，我將執行清理！

