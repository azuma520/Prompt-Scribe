# 🧪 Database Testing Suite

完整的 Supabase 資料庫測試套件，用於驗證 Prompt-Scribe 專案的資料庫功能、效能和資料完整性。

## 📋 測試套件概覽

### 🚀 Quick Test (`quick_test.py`)
**用途**: 快速健康檢查，適合日常驗證和 CI/CD 整合  
**執行時間**: ~30 秒  
**測試項目**:
- 資料庫連接測試
- 記錄數量驗證 (140,782 筆)
- 基本查詢功能
- 搜尋效能檢查
- 排序和分頁功能
- 資料完整性基本檢查
- 分類分佈驗證

### 🧪 Comprehensive Test (`test_comprehensive.py`)
**用途**: 全面功能測試，深度驗證所有資料庫功能  
**執行時間**: ~5-10 分鐘  
**測試項目**:
- 基礎功能測試 (連接、CRUD 操作)
- 查詢效能測試 (主鍵、名稱、分類查詢)
- 資料完整性測試 (約束、資料類型、範圍)
- 搜尋功能測試 (文字搜尋、分類搜尋、排序)
- 併發處理測試 (多執行緒查詢)
- 邊界條件測試 (錯誤處理、極限值)

### ⚡ Performance Test (`performance_test.py`)
**用途**: 專業效能測試，評估查詢速度和吞吐量  
**執行時間**: ~3-5 分鐘  
**測試項目**:
- 主鍵查詢效能 (目標: <100ms)
- 名稱搜尋效能 (精確匹配、前綴搜尋)
- 分類查詢效能
- 範圍查詢效能
- 複雜查詢效能 (多條件組合)
- 排序查詢效能
- 聚合查詢效能
- 併發讀取測試 (多執行緒負載)

### 🎯 Test Runner (`test_runner.py`)
**用途**: 統一測試執行器，協調所有測試套件  
**功能**:
- 執行單一或多個測試套件
- 生成綜合報告
- 保存測試結果 (JSON 格式)
- 命令列介面支援

## 🚀 快速開始

### 環境準備

1. **安裝依賴**:
```bash
pip install supabase pytest asyncpg python-dotenv
```

2. **設定環境變數**:
確保 `specs/001-sqlite-ags-db/.env` 檔案包含:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # CRUD 測試需要
```

### 執行測試

#### 快速測試 (推薦日常使用)
```bash
cd tests/database
python quick_test.py
```

#### 完整測試套件
```bash
cd tests/database
python test_runner.py
```

#### 僅執行特定測試
```bash
# 僅快速測試
python test_runner.py --quick-only

# 僅全面測試
python test_runner.py --comprehensive-only

# 僅效能測試
python test_runner.py --performance-only
```

#### 保存結果到檔案
```bash
python test_runner.py --output my_test_results.json
```

## 📊 測試結果解讀

### 成功標準

#### 功能性測試
- ✅ 所有基本 CRUD 操作成功
- ✅ 查詢結果準確性 100%
- ✅ 資料完整性驗證通過
- ✅ 記錄數量匹配 (140,782 筆)

#### 效能標準
- ✅ 主鍵查詢: < 100ms
- ✅ 名稱搜尋: < 200ms
- ✅ 複雜查詢: < 500ms
- ✅ 併發支援: 10+ 同時用戶
- ✅ 成功率: > 95%

#### 資料完整性標準
- ✅ 無空值在必填欄位
- ✅ 資料類型正確
- ✅ 數值範圍合理
- ✅ 唯一約束有效

### 結果狀態

- **🎉 ALL TESTS PASSED**: 資料庫完全健康，可用於生產環境
- **⚠️ SOME TESTS FAILED**: 需要檢查失敗的測試並修復問題
- **❌ CRITICAL ERROR**: 嚴重問題，需要立即處理

## 🔧 故障排除

### 常見問題

#### 1. 連接失敗
```
❌ Database Connection: Connection failed
```
**解決方案**:
- 檢查 `SUPABASE_URL` 和 `SUPABASE_ANON_KEY`
- 確認網路連接
- 驗證 Supabase 專案狀態

#### 2. 記錄數量不匹配
```
❌ Record Count: Expected: 140782, Got: 0
```
**解決方案**:
- 確認資料遷移已完成
- 檢查資料表名稱 (`tags_final`)
- 驗證 RLS 政策設定

#### 3. CRUD 操作失敗
```
❌ CRUD Operations: Service role key required
```
**解決方案**:
- 設定 `SUPABASE_SERVICE_ROLE_KEY`
- 確認服務角色金鑰權限
- 檢查 RLS 政策

#### 4. 效能測試失敗
```
❌ Performance: Slow response (>500ms)
```
**解決方案**:
- 檢查網路延遲
- 確認資料庫索引
- 考慮升級 Supabase 方案

### 調試技巧

1. **啟用詳細輸出**:
```bash
python test_runner.py --verbose
```

2. **檢查環境變數**:
```bash
python -c "import os; print('URL:', os.getenv('SUPABASE_URL')); print('KEY:', os.getenv('SUPABASE_ANON_KEY')[:20] + '...' if os.getenv('SUPABASE_ANON_KEY') else None)"
```

3. **測試單一功能**:
```python
from tests.database.quick_test import QuickDatabaseTest
test = QuickDatabaseTest()
test.test_connection()  # 測試特定功能
```

## 📈 效能基準

### 查詢效能目標

| 查詢類型 | 目標響應時間 | 可接受範圍 |
|----------|-------------|-----------|
| 主鍵查詢 | < 50ms | < 100ms |
| 名稱精確匹配 | < 100ms | < 200ms |
| 前綴搜尋 | < 200ms | < 300ms |
| 分類查詢 | < 150ms | < 250ms |
| 範圍查詢 | < 300ms | < 500ms |
| 複雜查詢 | < 400ms | < 600ms |
| 排序查詢 | < 250ms | < 400ms |

### 吞吐量目標

| 測試類型 | 目標 QPS | 最低要求 |
|----------|----------|----------|
| 簡單查詢 | > 100 | > 50 |
| 複雜查詢 | > 20 | > 10 |
| 併發讀取 | > 50 | > 25 |

## 🔄 持續整合

### GitHub Actions 範例

```yaml
name: Database Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run database tests
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        run: python tests/database/test_runner.py --quick-only
```

### 定期監控

建議設定定期執行測試:
- **每日**: 快速測試 (`quick_test.py`)
- **每週**: 全面測試 (`test_comprehensive.py`)
- **每月**: 效能測試 (`performance_test.py`)

## 📝 測試報告範例

```
🎯 Database Test Runner Starting...
📅 Timestamp: 2025-01-14 15:30:45
🌐 Supabase URL: https://fumuvmbhmmzkenizksyq.supabase.co

🚀 Running Quick Database Test...
✅ Testing Database Connection... PASS (45.2ms)
✅ Testing Record Count... PASS (123.7ms)
✅ Testing Basic Queries... PASS (89.3ms)
✅ Testing Search Performance... PASS (234.1ms)
✅ Testing Sorting & Pagination... PASS (156.8ms)
✅ Testing Data Integrity... PASS (78.9ms)
✅ Testing Category Distribution... PASS (201.4ms)

📊 Test Results:
   Total Tests: 7
   Passed: 7 ✅
   Failed: 0 ❌
   Success Rate: 100.0%

🎉 All tests passed! Database is healthy.

📊 FINAL DATABASE TEST REPORT
🎉 Overall Status: ALL TESTS PASSED
📈 Test Suites: 1/1 passed

🚀 Quick Test: ✅ PASS
   Individual Tests: 7/7 passed

💡 Recommendations:
   🎉 Database is performing excellently!
   ✅ All systems are ready for production use
   📈 Consider implementing monitoring for ongoing health checks

🏁 Database Testing Complete - 2025-01-14 15:31:02
💾 Test results saved to: database_test_results_20250114_153102.json
```

## 🤝 貢獻指南

### 新增測試

1. **新增測試案例**:
```python
def test_new_functionality(self) -> bool:
    """Test description"""
    start_time = time.time()
    try:
        # 測試邏輯
        result = self.client.table('tags_final').select('*').execute()
        success = len(result.data) > 0
        
        duration_ms = (time.time() - start_time) * 1000
        self.log_result("New Functionality", success, duration_ms)
        return success
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        self.log_result("New Functionality", False, duration_ms, error=str(e))
        return False
```

2. **更新測試套件**:
在相應的測試類別中加入新的測試方法，並在 `run_all_tests` 中調用。

3. **更新文檔**:
更新此 README 和測試場景文檔。

### 測試最佳實踐

- **獨立性**: 每個測試應該獨立運行
- **可重複性**: 測試結果應該一致
- **清理**: 測試後清理測試資料
- **錯誤處理**: 妥善處理異常情況
- **效能**: 避免過度耗時的測試

## 📚 相關文檔

- [測試場景設計](database_test_scenarios.md)
- [Supabase 官方文檔](https://supabase.com/docs)
- [PostgreSQL 效能調優](https://www.postgresql.org/docs/current/performance-tips.html)
- [專案主要文檔](../../README.md)
