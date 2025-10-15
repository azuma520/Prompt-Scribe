# 🚀 Plan C 快速開始指南

> 從 90% 到 96% 覆蓋率的完整執行方案

---

## ⚡ 5 分鐘開始

### 1. 檢查環境

```bash
cd stage1

# 檢查配置
python llm_config.py

# 查看當前狀態
python quick_stats.py
```

### 2. 一鍵執行

```bash
# 啟動完整流程
python execute_plan_c.py
```

就這麼簡單！腳本會自動：
- ✅ 檢查環境
- ✅ 顯示當前統計
- ✅ 確認執行
- ✅ 依序執行 Phase 1 和 Phase 2
- ✅ 生成所有報告

---

## 📋 分階段執行

如果想要更細緻的控制：

### Phase 1: 中頻標籤 (90% → 91.5%)

```bash
python run_plan_c_phase1.py
```

**預計**: 2.5-3 小時，$0.16

### Phase 2: 低頻標籤 (91.5% → 96%)

```bash
python run_plan_c_phase2.py
```

**預計**: 10-11 小時，$0.72

---

## 📊 監控進度

### 實時監控

```bash
# 終端 1: 執行任務
python execute_plan_c.py

# 終端 2: 實時監控（可選）
python live_monitor.py
```

### 查看報告

```bash
# Phase 1 進度
cat output/PLAN_C_PHASE1_PROGRESS.md

# Phase 2 進度
cat output/PLAN_C_PHASE2_PROGRESS.md

# 品質報告
cat output/QUALITY_REPORT.md

# 檢查點記錄
cat output/CHECKPOINT_LOGS.md
```

---

## 🛠️ 常用命令

### 檢查當前狀態

```bash
python quick_stats.py
```

### 測試單個工具

```bash
# 測試檢查點評估器
python checkpoint_evaluator.py

# 測試批次調整器
python batch_size_adjuster.py

# 測試品質監控
python quality_monitor.py

# 測試規則提取
python auto_rule_extractor.py
```

### 查看幫助

```bash
python run_plan_c_phase1.py --help
python run_plan_c_phase2.py --help
```

---

## 🎯 關鍵里程碑

系統會在達到以下覆蓋率時自動通知：

- **91%**: Phase 1 基本完成
- **92%**: 第一個重要里程碑 🎯
- **93%**: Phase 2 進展良好
- **94%**: 接近目標
- **95%**: 最後衝刺
- **96%**: 🎉 目標達成！

---

## ⚠️ 如果出現問題

### 執行中斷了？

不用擔心！重新運行即可：

```bash
python execute_plan_c.py
```

腳本會自動跳過已處理的標籤。

### 成功率下降？

系統會自動調整批次大小。如果仍有問題：

```bash
# 查看品質報告
cat output/QUALITY_REPORT.md

# 運行品質檢查
python quality_consistency_checker.py
```

### API 限流？

編輯 Phase 配置文件，增加延遲時間。

---

## 📁 重要文件

| 文件 | 說明 |
|------|------|
| `execute_plan_c.py` | 主執行器（推薦） |
| `run_plan_c_phase1.py` | Phase 1 執行器 |
| `run_plan_c_phase2.py` | Phase 2 執行器 |
| `PLAN_C_SPECIFICATION.md` | 完整規格文檔 |
| `PLAN_C_IMPLEMENTATION.md` | 詳細實施指南 |

---

## 🎉 達成 96% 後

```bash
# 1. 生成最終報告
cat output/96_PERCENT_ACHIEVEMENT.md

# 2. 運行品質檢查
python quality_consistency_checker.py

# 3. 備份數據
cp output/tags.db output/tags_96percent_backup.db

# 4. 提交到 Git
git add stage1/output/
git commit -m "🎉 達成 Plan C：96%+ 覆蓋率"
```

---

## 💡 小提示

1. **時間安排**: Phase 2 需要 10+ 小時，建議隔夜執行
2. **監控**: 可以開兩個終端，一個執行，一個監控
3. **中斷恢復**: 隨時可以中斷，重新執行會自動繼續
4. **成本控制**: 系統會自動追蹤成本，預計不超過 $1
5. **品質優先**: 如果成功率 < 85%，系統會自動調整

---

## 📞 需要幫助？

1. **查看日誌**: `output/plan_c_phase*.log`
2. **查看文檔**: `PLAN_C_IMPLEMENTATION.md`（詳細指南）
3. **運行診斷**: `python comprehensive_testing.py`

---

## 🏁 準備好了嗎？

```bash
python execute_plan_c.py
```

讓我們開始達成 96% 覆蓋率的目標！🚀

---

**創建日期**: 2025-10-13  
**預期完成**: 2-3 天  
**最終目標**: 96.63% 覆蓋率 ✨

