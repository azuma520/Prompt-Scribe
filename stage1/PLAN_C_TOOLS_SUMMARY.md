# 🛠️ Plan C 工具總覽

**創建日期**: 2025-10-13  
**狀態**: ✅ 全部就緒

---

## 📦 已創建的工具

### 核心執行腳本

| 文件 | 功能 | 狀態 |
|------|------|------|
| `execute_plan_c.py` | **主執行器** - 一鍵啟動完整流程 | ✅ |
| `run_plan_c_phase1.py` | Phase 1 執行器（中頻標籤 10K-100K） | ✅ |
| `run_plan_c_phase2.py` | Phase 2 執行器（低頻標籤 1K-10K） | ✅ |

### 輔助工具模組

| 文件 | 功能 | 狀態 |
|------|------|------|
| `checkpoint_evaluator.py` | 檢查點評估器 - 評估進度和品質 | ✅ |
| `batch_size_adjuster.py` | 批次大小動態調整器 | ✅ |
| `quality_monitor.py` | 品質監控器 - 實時監控處理品質 | ✅ |
| `auto_rule_extractor.py` | 規則自動提取器 | ✅ |
| `progress_reporter.py` | 進度報告生成器 | ✅ |

### 更新的現有文件

| 文件 | 更新內容 | 狀態 |
|------|----------|------|
| `optimized_llm_classifier.py` | 添加低頻標籤專用提示詞支持 | ✅ |

### 文檔文件

| 文件 | 說明 | 狀態 |
|------|------|------|
| `PLAN_C_SPECIFICATION.md` | 完整規格文檔（已存在） | ✅ |
| `PLAN_C_IMPLEMENTATION.md` | 詳細實施指南 | ✅ |
| `PLAN_C_QUICKSTART.md` | 快速開始指南 | ✅ |
| `PLAN_C_TOOLS_SUMMARY.md` | 本文檔 - 工具總覽 | ✅ |

---

## 🔍 工具詳細說明

### 1. execute_plan_c.py

**主執行器** - 推薦使用

**功能**:
- 環境檢查
- 統計顯示
- 確認執行
- 自動執行 Phase 1 & 2
- 生成最終總結

**使用**:
```bash
python execute_plan_c.py
```

**特點**:
- 智能跳過已完成階段
- 支持中斷恢復
- 全程引導式操作

---

### 2. run_plan_c_phase1.py

**Phase 1 執行器** - 中頻標籤處理

**處理範圍**:
- 50K-100K: 1 個標籤
- 30K-50K: ~298 個標籤
- 20K-30K: ~425 個標籤
- 10K-20K: ~905 個標籤

**參數**:
- `--phases N [N...]`: 指定執行的 phase (0-3)
- `--dry-run`: 測試運行

**使用示例**:
```bash
# 執行所有
python run_plan_c_phase1.py

# 只執行特定 phase
python run_plan_c_phase1.py --phases 1 2

# 測試運行
python run_plan_c_phase1.py --dry-run
```

**輸出**:
- 日誌: `output/plan_c_phase1.log`
- 進度報告: `output/PLAN_C_PHASE1_PROGRESS.md`
- 最終報告: `output/PLAN_C_PHASE1_FINAL_REPORT.md`

---

### 3. run_plan_c_phase2.py

**Phase 2 執行器** - 低頻標籤處理

**處理範圍**:
- 5K-10K: ~2,000 個標籤
- 3K-5K: ~2,000 個標籤
- 1K-3K: ~3,159 個標籤

**特殊功能**:
- 使用低頻標籤專用提示詞
- 自動標記低信心度標籤
- 每 500 個標籤提取規則

**參數**:
- `--phases N [N...]`: 指定執行的 phase (0-2)
- `--dry-run`: 測試運行

**使用示例**:
```bash
# 執行所有
python run_plan_c_phase2.py

# 分批執行
python run_plan_c_phase2.py --phases 0  # 5K-10K
python run_plan_c_phase2.py --phases 1  # 3K-5K
python run_plan_c_phase2.py --phases 2  # 1K-3K
```

**輸出**:
- 日誌: `output/plan_c_phase2.log`
- 進度報告: `output/PLAN_C_PHASE2_PROGRESS.md`
- 規則提取: `output/RULE_EXTRACTION_LOG.md`
- 規則代碼: `output/extracted_rules.py`

---

### 4. checkpoint_evaluator.py

**檢查點評估器**

**功能**:
- 成功率評估（優秀 >= 95%, 良好 90-95%, 警告 < 90%）
- 信心度評估（優秀 >= 0.85, 良好 0.75-0.85, 警告 < 0.75）
- 覆蓋率進度追蹤
- 成本狀態監控

**自動觸發**: 每處理 300 個標籤

**輸出**: `output/CHECKPOINT_LOGS.md`

**獨立測試**:
```bash
python checkpoint_evaluator.py
```

---

### 5. batch_size_adjuster.py

**批次大小動態調整器**

**功能**:
- 根據成功率動態調整批次大小
- 提供頻率範圍推薦參數
- 記錄調整歷史

**調整策略**:
- 成功率 >= 95%: 可增加批次大小
- 成功率 90-95%: 維持當前
- 成功率 < 90%: 降低批次大小

**獨立測試**:
```bash
python batch_size_adjuster.py
```

---

### 6. quality_monitor.py

**品質監控器**

**功能**:
- 記錄批次處理品質
- 檢測異常（低成功率、低信心度、null 字符串等）
- 生成品質報告
- 檢查信心度分布

**異常檢測**:
- 成功率 < 80%
- 平均信心度 < 0.70
- null 字符串分類
- 分類過度集中

**輸出**: `output/QUALITY_REPORT.md`

**獨立測試**:
```bash
python quality_monitor.py
```

---

### 7. auto_rule_extractor.py

**規則自動提取器**

**功能**:
- 提取後綴規則（如 _hair, _eyes）
- 提取前綴規則（如 red_, blue_）
- 提取包含規則（如包含 girl, sword）
- 生成 Python 規則代碼

**提取條件**:
- 最少 5 個相同模式
- 信心度 >= 0.95
- 分類一致性 >= 90%

**輸出**:
- 報告: `output/RULE_EXTRACTION_LOG.md`
- 代碼: `output/extracted_rules.py`

**獨立執行**:
```bash
python auto_rule_extractor.py
```

---

### 8. progress_reporter.py

**進度報告生成器**

**功能**:
- 生成 Phase 1/2 進度報告
- 生成最終報告
- 生成里程碑報告（91%, 92%, 96% 等）
- 提供整體統計

**自動生成報告**:
- 每個檢查點
- Phase 完成時
- 達到里程碑時

**報告文件**:
- `PLAN_C_PHASE1_PROGRESS.md`
- `PLAN_C_PHASE1_FINAL_REPORT.md`
- `PLAN_C_PHASE2_PROGRESS.md`
- `XX_PERCENT_MILESTONE.md`

---

### 9. optimized_llm_classifier.py (更新)

**LLM 分類器** - 添加低頻標籤支持

**新功能**:
- `use_low_freq_prompt` 參數
- 低頻標籤專用提示詞
- 更寬鬆的信心度標準（0.60+）
- 特殊標籤處理指南

**使用**:
```python
# 標準模式（中高頻標籤）
classifier = OptimizedLLMClassifier()

# 低頻模式
classifier = OptimizedLLMClassifier(use_low_freq_prompt=True)
```

**低頻提示詞特點**:
- 處理高度特殊化標籤
- 文化和語境依賴標籤
- 遊戲/動漫特定標籤
- 模糊語義標籤

---

## 📊 生成的報告文件

### 進度報告

| 文件 | 生成時機 | 內容 |
|------|----------|------|
| `PLAN_C_PHASE1_PROGRESS.md` | Phase 1 檢查點 | Phase 1 進度和統計 |
| `PLAN_C_PHASE1_FINAL_REPORT.md` | Phase 1 完成 | Phase 1 完整報告 |
| `PLAN_C_PHASE2_PROGRESS.md` | Phase 2 檢查點 | Phase 2 進度和統計 |
| `CHECKPOINT_LOGS.md` | 每個檢查點 | 所有檢查點記錄 |

### 品質報告

| 文件 | 生成時機 | 內容 |
|------|----------|------|
| `QUALITY_REPORT.md` | 即時更新 | 品質監控詳情 |
| `RULE_EXTRACTION_LOG.md` | 每 500 個標籤 | 規則提取記錄 |
| `extracted_rules.py` | 規則提取時 | Python 規則代碼 |

### 里程碑報告

| 文件 | 觸發條件 | 意義 |
|------|----------|------|
| `91_PERCENT_MILESTONE.md` | 覆蓋率 >= 91% | Phase 1 基本完成 |
| `92_PERCENT_ACHIEVEMENT.md` | 覆蓋率 >= 92% | 第一個重要里程碑 🎯 |
| `96_PERCENT_ACHIEVEMENT.md` | 覆蓋率 >= 96% | 🎉 目標達成！ |

---

## ✅ 準備檢查清單

在開始執行前，請確認：

### 環境準備

- [ ] Python 3.8+ 已安裝
- [ ] 所有依賴已安裝 (`pip install -r requirements.txt`)
- [ ] 數據庫文件存在 (`output/tags.db`)
- [ ] 有足夠的磁盤空間（至少 1GB）

### 配置檢查

- [ ] API Key 已設置（`.env` 文件）
- [ ] LLM 配置驗證通過 (`python llm_config.py`)
- [ ] 當前覆蓋率 >= 90% (`python quick_stats.py`)

### 文件檢查

- [ ] 所有執行腳本已創建
- [ ] 所有輔助工具已創建
- [ ] 所有文檔已創建

### 測試驗證

```bash
# 運行所有工具測試
python checkpoint_evaluator.py
python batch_size_adjuster.py
python quality_monitor.py
python auto_rule_extractor.py

# 查看幫助
python execute_plan_c.py --help
python run_plan_c_phase1.py --help
python run_plan_c_phase2.py --help
```

---

## 🚀 執行建議

### 推薦方式 1: 一鍵執行

```bash
python execute_plan_c.py
```

**適合**: 首次執行，想要全自動流程

### 推薦方式 2: 分階段執行

```bash
# 先執行 Phase 1
python run_plan_c_phase1.py

# Phase 1 完成後，執行 Phase 2
python run_plan_c_phase2.py
```

**適合**: 想要更多控制，分多天執行

### 推薦方式 3: 更細緻控制

```bash
# Phase 1 分批執行
python run_plan_c_phase1.py --phases 0 1  # 先執行前兩個
python run_plan_c_phase1.py --phases 2 3  # 再執行後兩個

# Phase 2 分批執行
python run_plan_c_phase2.py --phases 0  # 5K-10K
# ... 檢查結果 ...
python run_plan_c_phase2.py --phases 1  # 3K-5K
# ... 檢查結果 ...
python run_plan_c_phase2.py --phases 2  # 1K-3K
```

**適合**: 謹慎執行，每步都要檢查

---

## 📞 故障排除

### 工具無法導入

**問題**: `ModuleNotFoundError`

**解決**:
```bash
# 確保在 stage1 目錄
cd stage1

# 安裝依賴
pip install -r requirements.txt
```

### API 錯誤

**問題**: API Key 無效或限流

**解決**:
1. 檢查 `.env` 文件中的 API Key
2. 運行 `python llm_config.py` 驗證
3. 增加延遲時間（編輯 Phase 配置中的 `delay` 參數）

### 數據庫錯誤

**問題**: 無法訪問數據庫

**解決**:
```bash
# 檢查文件是否存在
ls -lh output/tags.db

# 檢查權限
chmod 644 output/tags.db

# 關閉其他訪問數據庫的進程
```

---

## 🎯 成功指標

### Phase 1 完成

- ✅ 覆蓋率 >= 91.5%
- ✅ 平均成功率 >= 90%
- ✅ 平均信心度 >= 0.80
- ✅ 成本 <= $0.20

### Phase 2 完成

- ✅ 覆蓋率 >= 96.0%
- ✅ 平均成功率 >= 85%
- ✅ 平均信心度 >= 0.75
- ✅ 成本 <= $1.00

### 整體完成

- ✅ 覆蓋率 >= 96.00%
- ✅ 處理標籤 >= 8,500 個
- ✅ 總成本 <= $1.00
- ✅ 無重大品質問題

---

## 📚 相關文檔

- [PLAN_C_SPECIFICATION.md](./PLAN_C_SPECIFICATION.md) - 完整規格文檔
- [PLAN_C_IMPLEMENTATION.md](./PLAN_C_IMPLEMENTATION.md) - 詳細實施指南
- [PLAN_C_QUICKSTART.md](./PLAN_C_QUICKSTART.md) - 快速開始指南

---

## 🎉 準備就緒！

所有工具已創建並測試完成，可以開始執行 Plan C！

```bash
python execute_plan_c.py
```

祝執行順利！🚀

---

**創建日期**: 2025-10-13  
**工具版本**: v1.0  
**狀態**: ✅ 全部就緒

