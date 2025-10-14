# 📋 Plan C 實施計畫 - 完整執行指南

**版本**: v1.0  
**創建日期**: 2025-10-13  
**狀態**: ✅ 準備就緒  
**基於**: [PLAN_C_SPECIFICATION.md](./PLAN_C_SPECIFICATION.md)

---

## 🎯 快速開始

### 準備檢查清單

- [ ] Python 3.8+ 已安裝
- [ ] 所有依賴已安裝 (`pip install -r requirements.txt`)
- [ ] 資料庫文件存在 (`output/tags.db`)
- [ ] API Key 已設置（`.env` 文件中）
- [ ] 當前覆蓋率 >= 90%

### 驗證環境

```bash
cd stage1

# 1. 檢查 Python 版本
python --version

# 2. 驗證 LLM 配置
python llm_config.py

# 3. 檢查當前統計
python quick_stats.py

# 4. 測試工具
python checkpoint_evaluator.py
python batch_size_adjuster.py
python quality_monitor.py
```

---

## 🚀 執行流程

### Phase 1: 中頻標籤處理 (10K-100K)

**目標**: 91.5% 覆蓋率  
**預計時間**: 2.5-3 小時  
**預計成本**: $0.16

#### 啟動 Phase 1

```bash
# 執行所有 Phase 1 階段
python run_plan_c_phase1.py

# 或分階段執行
python run_plan_c_phase1.py --phases 0 1 2  # 執行特定 phase
```

#### Phase 1 包含的階段

| Phase | 頻率範圍 | 標籤數 | 批次大小 | 預計時間 |
|-------|---------|--------|---------|---------|
| 1-1 | 50K-100K | 1 | 20 | 1 分鐘 |
| 1-2 | 30K-50K | ~298 | 20 | 30 分鐘 |
| 1-3 | 20K-30K | ~425 | 15 | 45 分鐘 |
| 1-4 | 10K-20K | ~905 | 15 | 90 分鐘 |

#### 檢查點

- **檢查點 1**: Phase 1-2 完成後
  - 檢查成功率 >= 90%
  - 檢查平均信心度 >= 0.80
  
- **檢查點 2**: Phase 1-3 完成後
  - 覆蓋率應達到 ~91%
  - 生成進度報告

- **檢查點 3**: Phase 1 全部完成
  - 生成最終報告
  - 準備 Phase 2

#### 監控命令

```bash
# 即時監控（另一個終端）
python live_monitor.py

# 查看進度報告
cat output/PLAN_C_PHASE1_PROGRESS.md

# 查看檢查點日誌
cat output/CHECKPOINT_LOGS.md

# 查看品質報告
cat output/QUALITY_REPORT.md
```

---

### Phase 2: 低頻標籤處理 (1K-10K)

**目標**: 96.63% 覆蓋率  
**預計時間**: 10-11 小時  
**預計成本**: $0.72

#### 啟動 Phase 2

```bash
# 執行所有 Phase 2 階段
python run_plan_c_phase2.py

# 或分階段執行
python run_plan_c_phase2.py --phases 0  # 只執行 5K-10K
python run_plan_c_phase2.py --phases 1  # 只執行 3K-5K
python run_plan_c_phase2.py --phases 2  # 只執行 1K-3K
```

#### Phase 2 包含的階段

| Phase | 頻率範圍 | 預計標籤數 | 批次大小 | 預計時間 |
|-------|---------|-----------|---------|---------|
| 2-1 | 5K-10K | ~2,000 | 12 | 2.5 小時 |
| 2-2 | 3K-5K | ~2,000 | 12 | 3 小時 |
| 2-3 | 1K-3K | ~3,159 | 10 | 5 小時 |

#### 特殊處理

Phase 2 使用**低頻標籤專用提示詞**，包含：

- 更寬鬆的信心度閾值 (0.60+)
- 特殊標籤處理指南
- 日文詞彙和遊戲特定標籤處理
- 自動標記低信心度標籤

#### 檢查點

- 每處理 300 個標籤進行一次檢查點評估
- 每處理 500 個標籤提取一次規則模式
- 實時生成進度報告

#### 監控命令

```bash
# 查看 Phase 2 進度
cat output/PLAN_C_PHASE2_PROGRESS.md

# 查看規則提取日誌
cat output/RULE_EXTRACTION_LOG.md

# 查看提取的 Python 規則
cat output/extracted_rules.py
```

---

## 📊 工具說明

### 1. 執行腳本

#### `run_plan_c_phase1.py`
中頻標籤處理執行器

**參數**:
- `--phases N [N...]`: 指定要執行的 phase (0-3)
- `--dry-run`: 測試運行，不更新數據庫

**示例**:
```bash
# 執行所有
python run_plan_c_phase1.py

# 只執行 Phase 1-2 和 1-3
python run_plan_c_phase1.py --phases 1 2
```

#### `run_plan_c_phase2.py`
低頻標籤處理執行器

**參數**:
- `--phases N [N...]`: 指定要執行的 phase (0-2)
- `--dry-run`: 測試運行

**示例**:
```bash
# 執行所有
python run_plan_c_phase2.py

# 分批執行
python run_plan_c_phase2.py --phases 0
python run_plan_c_phase2.py --phases 1
python run_plan_c_phase2.py --phases 2
```

### 2. 輔助工具

#### `checkpoint_evaluator.py`
檢查點評估器 - 評估進度和品質

**功能**:
- 成功率評估
- 信心度評估
- 覆蓋率進度
- 成本監控

#### `batch_size_adjuster.py`
批次大小動態調整器

**功能**:
- 根據成功率動態調整批次大小
- 根據頻率範圍推薦參數
- 記錄調整歷史

#### `quality_monitor.py`
品質監控器

**功能**:
- 實時監控批次處理品質
- 檢測異常（null 字符串、低信心度等）
- 生成品質報告

#### `auto_rule_extractor.py`
規則自動提取器

**功能**:
- 從已分類標籤提取後綴規則
- 提取前綴規則
- 提取包含規則
- 生成 Python 代碼

**示例**:
```bash
python auto_rule_extractor.py
```

#### `progress_reporter.py`
進度報告生成器

**功能**:
- 生成 Phase 1/2 進度報告
- 生成最終報告
- 生成里程碑報告（91%, 92%, 96% 等）

### 3. 監控工具

#### `live_monitor.py`
實時進度監控

```bash
python live_monitor.py
```

#### `quick_stats.py`
快速統計查看

```bash
python quick_stats.py
```

---

## 🔍 品質控制

### 自動品質檢查

每個檢查點會執行以下檢查：

1. **成功率檢查**
   - ✅ 優秀: >= 95%
   - ⚠️ 良好: 90-95%
   - 🛑 警告: < 90%

2. **信心度檢查**
   - ✅ 優秀: >= 0.85
   - ⚠️ 良好: 0.75-0.85
   - 🛑 警告: < 0.75

3. **覆蓋率進度**
   - 實際 vs 預期提升
   - 異常檢測

4. **成本控制**
   - 預算使用追蹤
   - 超標預警

### 品質問題處理

如果出現品質警告：

```bash
# 1. 查看詳細品質報告
cat output/QUALITY_REPORT.md

# 2. 查看最近的分類結果
python review_llm_results.py --recent 100

# 3. 檢查特定標籤
python view_llm_results.py --tag "標籤名稱"

# 4. 運行品質一致性檢查
python quality_consistency_checker.py
```

---

## 🎛️ 動態調整

### 批次大小調整

系統會根據成功率自動調整批次大小：

- 成功率 >= 95%: 可以增加批次大小
- 成功率 90-95%: 維持當前批次大小
- 成功率 < 90%: 降低批次大小

### 提示詞優化

如果平均信心度 < 0.75，可以：

1. 分析低信心度標籤的共同特徵
2. 在提示詞中添加針對性說明
3. 使用優化後的提示詞繼續處理

### 成本控制

監控累計成本：

```bash
# 查看預計成本
python -c "from progress_reporter import ProgressReporter; r = ProgressReporter(); print(r.get_overall_stats())"
```

如果預計超出預算：
1. 調整批次大小
2. 縮減處理範圍
3. 暫停並重新評估

---

## 📈 進度追蹤

### 里程碑

系統會在達到以下覆蓋率時自動生成里程碑報告：

- 91%: `output/91_PERCENT_MILESTONE.md`
- 92%: `output/92_PERCENT_ACHIEVEMENT.md` 🎯
- 93%: `output/93_PERCENT_MILESTONE.md`
- 94%: `output/94_PERCENT_MILESTONE.md`
- 95%: `output/95_PERCENT_MILESTONE.md`
- 96%: `output/96_PERCENT_ACHIEVEMENT.md` 🎉

### 報告文件

| 文件 | 描述 | 更新頻率 |
|------|------|---------|
| `PLAN_C_PHASE1_PROGRESS.md` | Phase 1 進度 | 每個檢查點 |
| `PLAN_C_PHASE1_FINAL_REPORT.md` | Phase 1 最終報告 | Phase 1 完成時 |
| `PLAN_C_PHASE2_PROGRESS.md` | Phase 2 進度 | 每個檢查點 |
| `CHECKPOINT_LOGS.md` | 所有檢查點記錄 | 每個檢查點 |
| `QUALITY_REPORT.md` | 品質監控報告 | 即時 |
| `RULE_EXTRACTION_LOG.md` | 規則提取記錄 | 每 500 個標籤 |

---

## ⚠️ 故障排除

### 常見問題

#### 1. API 限流

**症狀**: 請求頻繁失敗，返回 429 錯誤

**解決**:
```bash
# 增加延遲時間（修改 PHASES 配置中的 delay 參數）
# 或手動在執行時增加延遲
```

#### 2. 成功率下降

**症狀**: 成功率 < 85%

**解決**:
1. 檢查最近失敗的標籤
2. 降低批次大小
3. 調整提示詞
4. 暫停後重新開始

#### 3. JSON 解析錯誤

**症狀**: 頻繁出現 JSON 解析失敗

**解決**:
- 檢查 LLM 響應格式
- 增加重試次數
- 檢查 API 配置

#### 4. 數據庫鎖定

**症狀**: 數據庫更新失敗

**解決**:
```bash
# 關閉其他訪問數據庫的進程
# 檢查數據庫文件權限
```

### 緊急中斷恢復

如果執行過程中斷：

1. 檢查當前覆蓋率:
```bash
python quick_stats.py
```

2. 查看最後的檢查點:
```bash
tail -50 output/CHECKPOINT_LOGS.md
```

3. 繼續執行:
   - Phase 1 未完成: `python run_plan_c_phase1.py`
   - Phase 1 完成，Phase 2 未完成: `python run_plan_c_phase2.py`

系統會自動跳過已分類的標籤。

---

## ✅ 驗收標準

### Phase 1 完成標準

- [ ] 覆蓋率 >= 91.5%
- [ ] 中頻標籤 (10K-100K) 處理完成
- [ ] 平均成功率 >= 90%
- [ ] 平均信心度 >= 0.80
- [ ] 生成 Phase 1 最終報告

### Phase 2 完成標準

- [ ] 覆蓋率 >= 96%
- [ ] 低頻標籤 (1K-10K) 處理完成
- [ ] 平均成功率 >= 85%
- [ ] 平均信心度 >= 0.75
- [ ] 生成 96% 達成報告

### 整體 Plan C 完成標準

- [ ] 覆蓋率 >= 96.00%
- [ ] 總處理標籤 >= 8,500 個
- [ ] 總成本 <= $1.00
- [ ] 無重大品質問題
- [ ] 所有報告文檔已生成
- [ ] 規則已提取並驗證

---

## 📝 後續步驟

Phase 2 完成後：

### 1. 品質審查 (Day 4-5)

```bash
# 審查低信心度標籤
python -c "
import sqlite3
conn = sqlite3.connect('output/tags.db')
cursor = conn.cursor()
cursor.execute('''
SELECT name, main_category, sub_category, classification_confidence
FROM tags_final
WHERE classification_confidence < 0.75
AND classification_reasoning LIKE '%需審查%'
ORDER BY post_count DESC
LIMIT 100
''')
for row in cursor.fetchall():
    print(row)
"
```

### 2. 一致性檢查

```bash
python quality_consistency_checker.py
python fix_consistency_issues.py  # 如果有問題
```

### 3. 次要分類添加

識別需要次要分類的標籤：
- 顏色組合標籤
- 多重屬性標籤

### 4. 準備 Stage 2

- 驗證所有分類數據
- 導出最終數據集
- 準備向量化處理

---

## 🎉 成功慶祝

當達到 96% 覆蓋率時：

1. **生成最終統計報告**
```bash
python final_stats_generator.py
python coverage_breakdown.py
```

2. **備份數據**
```bash
cp output/tags.db output/tags_96percent_$(date +%Y%m%d).db
```

3. **提交到 Git**
```bash
git add stage1/output/tags.db
git add stage1/output/*.md
git commit -m "🎉 達成 Plan C 目標：96%+ 覆蓋率"
```

4. **準備慶祝！** 🎊

---

## 📞 支持

如果遇到問題：

1. 查看日誌文件: `output/plan_c_phase*.log`
2. 檢查品質報告: `output/QUALITY_REPORT.md`
3. 查看檢查點記錄: `output/CHECKPOINT_LOGS.md`
4. 運行診斷工具: `python comprehensive_testing.py`

---

**最後更新**: 2025-10-13  
**狀態**: ✅ 所有工具已就緒，可以開始執行  
**下一步**: 運行 `python run_plan_c_phase1.py` 🚀

