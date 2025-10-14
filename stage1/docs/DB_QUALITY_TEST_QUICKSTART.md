# 資料庫品質測試 - 快速開始指南

**版本**: v1.0  
**創建日期**: 2025-10-13  
**適用於**: Plan C Phase 3 完成後的資料庫驗證

---

## 📋 目錄

1. [環境要求](#環境要求)
2. [快速開始](#快速開始)
3. [使用說明](#使用說明)
4. [輸出解讀](#輸出解讀)
5. [常見問題](#常見問題)

---

## 環境要求

### 必需
- **Python**: 3.8+
- **SQLite3**: 3.8.3+（Python 標準庫）
- **資料庫**: `output/tags.db`（Plan C Phase 3 完成後）

### 可選
- **Pandas**: 用於進階數據分析（非必需）

### 確認環境
```bash
# 檢查 Python 版本
python --version  # 應該 >= 3.8

# 檢查 SQLite3 版本
python -c "import sqlite3; print(f'SQLite: {sqlite3.sqlite_version}')"  # 應該 >= 3.8.3

# 確認資料庫存在
ls output/tags.db
```

---

## 快速開始

### 1. 執行所有測試（推薦）

```bash
cd stage1
python db_quality_test.py
```

**預期輸出**:
```
2025-10-13 15:00:00 - INFO - 載入測試場景...
2025-10-13 15:00:00 - INFO - 成功載入 10 個測試場景
2025-10-13 15:00:00 - INFO - ================================================================================
2025-10-13 15:00:00 - INFO - 開始執行資料庫品質測試
2025-10-13 15:00:00 - INFO - ================================================================================

[1/10] 執行場景 A1: 主分類覆蓋度測試
------------------------------------------------------------
結果: [PASS] (執行時間: 0.052s)

[... 其他場景 ...]

================================================================================
所有測試執行完成
================================================================================

生成測試報告...
Markdown 報告已生成: output/DB_QUALITY_TEST_REPORT.md

================================================================================
測試摘要
================================================================================
總場景: 10
通過: 8
警告: 1
失敗: 1
錯誤: 0
總問題數: 5
執行時間: 2.34 秒
================================================================================
```

### 2. 查看測試報告

```bash
# Windows
type output\DB_QUALITY_TEST_REPORT.md

# Linux/Mac
cat output/DB_QUALITY_TEST_REPORT.md
```

---

## 使用說明

### 執行模式

#### 模式 1: 執行所有測試（默認）
```bash
python db_quality_test.py
```

#### 模式 2: 執行特定場景
```bash
# 執行單一場景
python db_quality_test.py --scenario A1

# 場景 ID:
# A1: 主分類覆蓋度
# A2: 頻率段覆蓋度
# A3: Danbooru 轉換
# B1: 副分類準確性
# B2: 信心度分布
# B3: 邊界案例
# C1: 模式一致性
# C2: 來源品質
# D1: 查詢性能
# E1: Prompt 生成
```

#### 模式 3: 執行特定維度
```bash
# 只執行完整性測試
python db_quality_test.py --dimension Completeness

# 維度選項:
# Completeness: 完整性測試 (A1-A3)
# Accuracy: 準確性測試 (B1-B3)
# Consistency: 一致性測試 (C1-C2)
# Performance: 性能測試 (D1)
# Application: 應用測試 (E1)
```

### 報告格式

#### Markdown 報告（默認）
```bash
python db_quality_test.py --format markdown
```
輸出: `output/DB_QUALITY_TEST_REPORT.md`

#### JSON 報告
```bash
python db_quality_test.py --format json
```
輸出: `output/test_results.json`

#### 同時生成兩種格式
```bash
python db_quality_test.py --format both
```

### 其他選項

```bash
# 詳細輸出模式
python db_quality_test.py --verbose

# 指定資料庫路徑
python db_quality_test.py --db /path/to/tags.db

# 指定輸出目錄
python db_quality_test.py --output /path/to/output
```

---

## 輸出解讀

### 測試狀態

| 狀態 | 圖標 | 含義 |
|------|------|------|
| **PASS** | ✅ | 所有成功標準都滿足 |
| **WARN** | ⚠️ | 大部分滿足，有小問題（P2 級別） |
| **FAIL** | ❌ | 未滿足關鍵成功標準（P0/P1 問題） |
| **ERROR** | 🔴 | 執行時發生錯誤 |

### 問題嚴重程度

| 級別 | 含義 | 建議 |
|------|------|------|
| **P0** | 必須修復 | 阻礙 Stage 2 進行 |
| **P1** | 建議修復 | 應該在 Stage 2 前處理 |
| **P2** | 可選優化 | 可以在後續改進 |

### 報告結構

```markdown
# 資料庫品質測試報告

## 執行摘要
- 整體測試結果統計

## 詳細結果
### A 組: 數據完整性
#### A1: 主分類覆蓋度 ✅
- 狀態、執行時間、關鍵指標、發現問題

[... 其他場景 ...]

## 問題總結
### P0 問題（必須修復）
1. [場景 ID] 問題描述
   - 受影響標籤
   - 修復建議

### P1 問題（建議修復）
...

## 修復建議
- 具體的修復步驟和建議
```

---

## 常見問題

### Q1: Unicode 編碼錯誤
**問題**: `UnicodeEncodeError: 'cp950' codec can't encode character...`

**解決方案**:
```bash
# 方法 1: 重定向輸出到文件
python db_quality_test.py > test_output.txt

# 方法 2: 只看報告文件（不看終端輸出）
python db_quality_test.py
type output\DB_QUALITY_TEST_REPORT.md
```

### Q2: 找不到資料庫文件
**問題**: `FileNotFoundError: 資料庫文件不存在`

**解決方案**:
```bash
# 確認當前目錄
pwd  # 應該在 stage1/

# 確認資料庫存在
ls output/tags.db

# 或指定完整路徑
python db_quality_test.py --db D:\Prompt-Scribe\stage1\output\tags.db
```

### Q3: 測試場景未載入
**問題**: `未找到任何測試場景`

**解決方案**:
```bash
# 確認測試模組存在
ls test_scenarios/

# 應該包含:
# - __init__.py
# - base.py
# - completeness_tests.py
# - accuracy_tests.py
# - consistency_tests.py
# - performance_tests.py
# - application_tests.py
```

### Q4: CTE 不支持錯誤
**問題**: `near "WITH": syntax error`

**解決方案**:
- 升級 SQLite3 到 3.8.3+
- 或修改查詢移除 WITH 子句

### Q5: 如何只測試覆蓋率？
**答案**:
```bash
python db_quality_test.py --dimension Completeness
```

---

## 進階使用

### 自動化執行
```bash
# 創建批次腳本
cat > run_db_test.bat << EOF
@echo off
cd stage1
python db_quality_test.py --format both
type output\DB_QUALITY_TEST_REPORT.md
pause
EOF

# 執行
run_db_test.bat
```

### 定期監控
```bash
# 每次優化後執行
python db_quality_test.py
git add output/DB_QUALITY_TEST_REPORT.md
git commit -m "test: Update quality test results"
```

### 整合到工作流
```bash
# Stage 2 前的檢查
if python db_quality_test.py; then
    echo "品質檢查通過，可以進入 Stage 2"
else
    echo "品質檢查未通過，請檢查報告"
    exit 1
fi
```

---

## 測試場景說明

### A 組: 數據完整性
- **A1**: 所有 17 個主分類都有標籤嗎？
- **A2**: 各頻率段覆蓋率達標嗎？
- **A3**: Danbooru 分類正確轉換了嗎？

### B 組: 分類準確性
- **B1**: 副分類邏輯正確嗎？（眼睛在 BODY_PARTS，頭髮在 HAIR）
- **B2**: 信心度分布合理嗎？
- **B3**: 邊界案例處理正確嗎？（NULL、成人內容）

### C 組: 數據一致性
- **C1**: 相似標籤分類一致嗎？（所有 *_eyes 都同分類）
- **C2**: 不同分類來源品質穩定嗎？

### D 組: 查詢性能
- **D1**: 查詢速度滿足實時需求嗎？

### E 組: 實際應用
- **E1**: 能支持完整的 Prompt 生成嗎？

---

## 快速故障排除

| 問題 | 可能原因 | 解決方案 |
|------|---------|---------|
| 找不到模組 | Python 路徑問題 | 確保在 stage1/ 目錄執行 |
| 編碼錯誤 | Windows cp950 編碼 | 查看文件報告，不看終端 |
| 查詢超時 | 資料庫過大 | 正常現象，等待完成 |
| 報告未生成 | 執行失敗 | 檢查錯誤訊息，修復後重試 |

---

## 下一步

執行測試後：

1. **查看報告**: `output/DB_QUALITY_TEST_REPORT.md`
2. **檢查問題**: 查看 P0/P1 問題清單
3. **執行修復**: 根據建議修復問題
4. **重新測試**: 確認修復效果
5. **進入 Stage 2**: 品質驗證通過後

---

**文檔版本**: v1.0  
**最後更新**: 2025-10-13  
**維護者**: Prompt-Scribe Team  
**支持**: 查看 `.specify/specs/db-quality-test-spec.md` 獲取完整規格

