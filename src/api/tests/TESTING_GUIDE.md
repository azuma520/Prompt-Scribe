# 🧪 測試執行指南

## 📋 目錄

1. [快速開始](#快速開始)
2. [測試類型](#測試類型)
3. [執行測試](#執行測試)
4. [測試結果解讀](#測試結果解讀)
5. [常見問題](#常見問題)

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
cd src/api
pip install -r requirements.txt
pip install -r tests/requirements-test.txt
```

### 2. 運行快速測試

```bash
# Linux/Mac
chmod +x tests/run_tests.sh
./tests/run_tests.sh quick

# Windows
.\tests\run_tests.ps1 quick
```

---

## 📊 測試類型

### 1️⃣ 快取測試 (`test_cache.py`)
**不需要資料庫連接** ✅

```bash
pytest tests/test_cache.py -v -s
```

**測試內容**:
- 快取統計功能
- 快取鍵生成
- TTL 過期機制
- 併發安全性
- 效能提升驗證

**預期結果**:
```
快取效能測試:
無快取時間: 103.45ms
有快取時間: 0.12ms
速度提升: 862.1x
```

### 2️⃣ 批量查詢測試 (`test_batch_queries.py`)
**需要 Supabase 連接** ⚠️

```bash
# 配置 .env 後執行
pytest tests/test_batch_queries.py -v -s
```

**測試內容**:
- 批量標籤查詢
- 分頁查詢效能
- 批量搜尋
- LLM 批量推薦
- 資料一致性

**預期結果**:
```
批量查詢平均時間: 245.67ms/查詢
批量推薦平均時間: 398.23ms/查詢
```

### 3️⃣ 負載測試 (`test_load_performance.py`)
**可選 Supabase 連接** 

```bash
pytest tests/test_load_performance.py -v -s
```

**測試內容**:
- 基礎負載測試（100 請求）
- 併發請求測試（20 併發）
- 持續負載測試（10 秒）
- 記憶體使用測試

**預期結果**:
```
併發測試:
併發數: 20
成功率: 100%
平均響應時間: 18.23ms
P95: 45.12ms
```

---

## 🎯 執行測試

### 方式 1: 使用測試腳本（推薦）

#### Linux/Mac
```bash
./tests/run_tests.sh [選項]

選項:
  quick    - 快速測試（不需資料庫）
  cache    - 快取功能測試
  batch    - 批量查詢測試
  load     - 負載測試
  coverage - 生成覆蓋率報告
  all      - 所有測試（預設）
```

#### Windows
```powershell
.\tests\run_tests.ps1 [選項]
```

### 方式 2: 使用 pytest 直接執行

#### 運行單一測試檔案
```bash
pytest tests/test_cache.py -v
```

#### 運行單一測試類別
```bash
pytest tests/test_cache.py::TestCacheStats -v
```

#### 運行單一測試方法
```bash
pytest tests/test_cache.py::TestCacheStats::test_initial_state -v
```

#### 運行所有測試
```bash
pytest tests/ -v
```

#### 顯示詳細輸出
```bash
pytest tests/ -v -s
```

#### 並行執行（加速）
```bash
pytest tests/ -v -n 4
```

#### 生成覆蓋率報告
```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

#### 只運行不需要資料庫的測試
```bash
pytest tests/ -v -m "not skip"
```

---

## 📈 測試結果解讀

### 成功的測試輸出

```
tests/test_cache.py::TestCacheStats::test_initial_state PASSED   [10%]
tests/test_cache.py::TestCacheStats::test_record_hit PASSED      [20%]
tests/test_cache.py::TestCacheStats::test_hit_rate PASSED        [30%]

=== 快取測試結果 ===
無快取時間: 103.45ms
有快取時間: 0.12ms
速度提升: 862.1x ✨

==================== 30 passed in 2.34s ====================
```

### 跳過的測試輸出

```
tests/test_batch_queries.py::test_batch_query SKIPPED          [需要 Supabase 連接]
```

**說明**: 這些測試需要實際的 Supabase 連接。配置 `.env` 檔案並移除 `@pytest.mark.skip` 裝飾器後可執行。

### 失敗的測試輸出

```
tests/test_cache.py::test_cache_hit FAILED                     [40%]
AssertionError: assert 2 == 1
```

**處理方式**: 查看錯誤訊息，修復問題後重新執行。

---

## 🎯 效能基準

以下是預期的測試效能指標：

| 測試類型 | 預期時間 | 備註 |
|---------|---------|------|
| 快取測試 | < 5 秒 | 全部通過 |
| 批量查詢測試 | 10-30 秒 | 需資料庫 |
| 負載測試 | 15-45 秒 | 含持續負載 |
| 完整測試套件 | 1-2 分鐘 | 包含所有測試 |

---

## ❓ 常見問題

### Q1: 如何跳過需要資料庫的測試？

**A**: 使用快速測試模式：
```bash
./tests/run_tests.sh quick
```

或使用 pytest 標記：
```bash
pytest tests/ -v -m "not skip"
```

### Q2: 測試顯示「需要 Supabase 連接」怎麼辦？

**A**: 有兩個選項：

1. **配置 Supabase（推薦）**:
   ```bash
   cp .env.example .env
   # 編輯 .env 填入 Supabase 憑證
   ```

2. **只運行不需要資料庫的測試**:
   ```bash
   pytest tests/test_cache.py -v
   ```

### Q3: 如何查看測試覆蓋率？

**A**: 
```bash
# 生成覆蓋率報告
pytest tests/ --cov=. --cov-report=html

# 在瀏覽器中查看
# Windows
start htmlcov/index.html

# Linux/Mac
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html       # Mac
```

### Q4: 負載測試太慢怎麼辦？

**A**: 可以調整測試參數或跳過：

```python
# 修改 test_load_performance.py 中的參數
num_requests = 50  # 減少請求數
duration_seconds = 5  # 減少測試時長
```

### Q5: 測試失敗如何除錯？

**A**: 使用詳細輸出和 pdb：
```bash
# 顯示詳細輸出
pytest tests/ -v -s --tb=long

# 失敗時進入除錯器
pytest tests/ --pdb

# 只運行失敗的測試
pytest tests/ --lf
```

### Q6: 如何測試單一功能？

**A**: 
```bash
# 只測試快取統計
pytest tests/test_cache.py::TestCacheStats -v

# 只測試併發請求
pytest tests/test_load_performance.py::TestConcurrentRequests -v
```

### Q7: 測試記憶體洩漏？

**A**: 
```bash
# 需要安裝 psutil
pip install psutil

# 運行記憶體測試
pytest tests/test_load_performance.py::TestMemoryAndResourceUsage -v -s
```

---

## 🔧 進階用法

### 並行測試（加速執行）

```bash
# 使用 4 個並行程序
pytest tests/ -v -n 4

# 自動選擇程序數
pytest tests/ -v -n auto
```

### 測試特定標記

```bash
# 只運行慢速測試
pytest tests/ -v -m slow

# 排除慢速測試
pytest tests/ -v -m "not slow"
```

### 生成 JUnit XML 報告

```bash
pytest tests/ --junitxml=test-results.xml
```

### 持續監控模式

```bash
# 文件變更時自動重新測試
pytest-watch tests/
```

---

## 📝 最佳實踐

1. **開發前先運行快速測試**
   ```bash
   ./tests/run_tests.sh quick
   ```

2. **提交前運行完整測試**
   ```bash
   pytest tests/ -v
   ```

3. **定期檢查覆蓋率**
   ```bash
   ./tests/run_tests.sh coverage
   ```

4. **負載測試定期執行**
   ```bash
   # 每週執行一次
   ./tests/run_tests.sh load
   ```

5. **使用測試專用資料庫**
   - 避免影響生產資料
   - 建立測試專用 Supabase 專案

---

## 🎉 測試完成檢查清單

- [ ] 所有快取測試通過
- [ ] 批量查詢測試通過（如有資料庫）
- [ ] 負載測試顯示合理效能
- [ ] 覆蓋率 > 80%
- [ ] 無明顯效能瓶頸
- [ ] 文檔更新完成

---

**更新日期**: 2025-10-15  
**版本**: 1.0.0  
**維護者**: Prompt-Scribe Team

