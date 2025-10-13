# 資料庫品質測試 - 實施計劃

**功能**: 標籤分類資料庫的全面品質驗證與測試  
**規格文檔**: [db-quality-test-spec.md](../specs/db-quality-test-spec.md)  
**版本**: v1.0  
**創建日期**: 2025-10-13  
**分支**: feature/phase1-danbooru-integration-and-bugfix  
**狀態**: 計劃中 📋

---

## 📋 目錄

1. [技術背景](#技術背景)
2. [憲章檢查](#憲章檢查)
3. [Phase 0: 研究與設計](#phase-0-研究與設計)
4. [Phase 1: 數據模型與合約](#phase-1-數據模型與合約)
5. [Phase 2: 實施任務](#phase-2-實施任務)
6. [驗證與測試](#驗證與測試)

---

## 技術背景

### 現有技術棧

**已確定**:
- **資料庫**: SQLite3 (tags.db)
- **資料表**: tags_final
- **程式語言**: Python 3.8+
- **SQL 引擎**: sqlite3 (Python 標準庫)
- **報告格式**: Markdown
- **執行環境**: Windows 10, PowerShell

**架構**:
```
測試架構:
├── 資料庫層: SQLite3 (tags.db)
├── 查詢層: Python sqlite3
├── 測試邏輯: 10 個測試場景
├── 報告生成: Markdown + 可選 JSON
└── 執行介面: CLI (命令行)
```

### 技術約束

1. **SQLite3 版本**: 需確認是否支持 CTE (3.8.3+) 和窗口函數 (3.25.0+)
2. **字符編碼**: Windows cp950 編碼問題需處理
3. **查詢性能**: 14 萬行數據，需考慮索引
4. **內存限制**: 避免一次性加載大量數據

### 依賴項

**外部依賴**:
- Python 3.8+
- sqlite3 (標準庫)
- 可選: pandas (用於數據分析和報告美化)

**內部依賴**:
- `output/tags.db`: Plan C Phase 3 完成後的資料庫
- `config.py`: 配置文件
- 現有工具: `quality_consistency_checker.py`, `check_db_status.py`

---

## 憲章檢查

### 專案架構一致性

**遵循現有模式** ✅:
- 測試腳本放在 `stage1/` 根目錄
- 報告輸出到 `stage1/output/`
- 使用現有的 `config.py` 配置
- 保持與其他工具（如 `quality_monitor.py`）的命名一致性

**代碼風格** ✅:
- 使用 UTF-8 編碼
- 遵循 PEP 8 規範
- 使用 Type Hints
- 完整的文檔字符串

**錯誤處理** ✅:
- 使用 logging 模組記錄
- 優雅的錯誤處理（不中斷測試流程）
- 提供清晰的錯誤訊息

### 與現有代碼整合

**可重用現有工具**:
- `quality_monitor.py`: QualityMonitor 類別
- `check_db_status.py`: 資料庫狀態檢查邏輯
- `config.py`: DB_PATH, OUTPUT_DIR 配置

**新增工具**:
- `db_quality_test.py`: 主測試腳本（新建）
- `test_scenarios/`: 測試場景模組目錄（新建）

---

## Phase 0: 研究與設計

### 研究任務

#### R1: SQLite3 版本確認
**問題**: 確認當前 SQLite3 版本是否支持所需功能

**研究內容**:
- 檢查 SQLite3 版本
- 確認 CTE (WITH 子句) 支持
- 確認 GROUP_CONCAT 函數
- 確認查詢性能基準

**決策**:
```python
import sqlite3
print(f"SQLite version: {sqlite3.sqlite_version}")
# 預期: 3.8.3+ (支持 CTE)
```

**結論**: 
- 使用 CTE 進行複雜查詢
- 避免窗口函數（可能不支持）
- 使用標準 SQL 聚合函數

---

#### R2: 測試框架選擇
**問題**: 選擇合適的測試組織結構

**選項評估**:

| 方案 | 優點 | 缺點 | 決策 |
|------|------|------|------|
| 單一腳本 | 簡單易用 | 難以維護、擴展 | ❌ |
| 模組化設計 | 易維護、可擴展 | 稍複雜 | ✅ 採用 |
| 使用 pytest | 標準框架 | 過度設計 | ❌ |

**決策**: 採用模組化設計
```
db_quality_test.py (主腳本)
test_scenarios/
  ├── __init__.py
  ├── completeness_tests.py  (A1-A3)
  ├── accuracy_tests.py      (B1-B3)
  ├── consistency_tests.py   (C1-C2)
  ├── performance_tests.py   (D1)
  └── application_tests.py   (E1)
```

---

#### R3: 報告生成策略
**問題**: 如何生成清晰、專業的測試報告

**決策**:
- **主報告**: Markdown 格式（易讀、可版本控制）
- **數據輸出**: 可選 JSON 格式（機器可讀）
- **結構**: 遵循規格中的報告範例結構
- **圖表**: 使用 ASCII 表格（跨平台兼容）

**工具**:
```python
class ReportGenerator:
    def generate_markdown_report(self, results: Dict) -> str
    def generate_json_report(self, results: Dict) -> str
    def format_table(self, data: List[Dict]) -> str
```

---

#### R4: 性能測試方法
**問題**: 如何準確測量查詢性能

**決策**:
- 使用 `time.perf_counter()` 測量執行時間
- 執行 3 次取平均值（排除首次冷啟動）
- 使用 `EXPLAIN QUERY PLAN` 分析查詢計劃
- 記錄是否使用索引

**實現**:
```python
import time
def measure_query_performance(cursor, sql: str, runs: int = 3) -> float:
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        cursor.execute(sql)
        cursor.fetchall()
        times.append(time.perf_counter() - start)
    return sum(times[1:]) / (runs - 1)  # 排除第一次
```

---

### 研究總結

| 研究項目 | 決策 | 理由 |
|---------|------|------|
| SQLite 版本 | 使用 3.8.3+ 功能 | 支持 CTE，滿足需求 |
| 測試框架 | 模組化設計 | 易維護和擴展 |
| 報告格式 | Markdown + JSON | 人機兼顧 |
| 性能測量 | perf_counter + 平均 | 準確可靠 |

---

## Phase 1: 數據模型與合約

### 數據模型

#### 實體 1: TestScenario（測試場景）

**屬性**:
```python
@dataclass
class TestScenario:
    """測試場景數據模型"""
    id: str                    # 場景 ID (如 'A1', 'B2')
    name: str                  # 場景名稱
    dimension: str             # 測試維度 (Completeness/Accuracy/...)
    description: str           # 測試描述
    sql_queries: List[str]     # SQL 查詢列表
    success_criteria: Dict     # 成功標準
    priority: str              # 優先級 (P0/P1/P2)
```

**示例**:
```python
TestScenario(
    id='A1',
    name='主分類覆蓋度測試',
    dimension='Completeness',
    description='驗證所有主分類都有合理的標籤分布',
    sql_queries=[
        "SELECT main_category, COUNT(*) as tag_count FROM tags_final..."
    ],
    success_criteria={
        'all_categories_exist': True,
        'min_categories': 17,
        'distribution_balanced': True
    },
    priority='P0'
)
```

---

#### 實體 2: TestResult（測試結果）

**屬性**:
```python
@dataclass
class TestResult:
    """測試結果數據模型"""
    scenario_id: str           # 關聯的場景 ID
    status: str                # 狀態 (PASS/FAIL/WARN)
    execution_time: float      # 執行時間（秒）
    query_results: List[Dict]  # 查詢結果
    issues: List[Dict]         # 發現的問題
    metrics: Dict              # 測試指標
    timestamp: str             # 執行時間戳
```

**狀態定義**:
- `PASS`: 所有成功標準都滿足
- `WARN`: 大部分滿足，有小問題
- `FAIL`: 未滿足關鍵成功標準

---

#### 實體 3: QualityIssue（品質問題）

**屬性**:
```python
@dataclass
class QualityIssue:
    """品質問題數據模型"""
    issue_type: str            # 問題類型
    severity: str              # 嚴重程度 (P0/P1/P2)
    description: str           # 問題描述
    affected_tags: List[str]   # 受影響的標籤
    recommendation: str        # 修復建議
    scenario_id: str           # 發現問題的場景
```

**問題類型**:
- `MISSING_COVERAGE`: 覆蓋率不足
- `MISCLASSIFICATION`: 誤分類
- `INCONSISTENCY`: 分類不一致
- `LOW_CONFIDENCE`: 信心度過低
- `NULL_STRING`: NULL 字符串問題
- `PERFORMANCE`: 性能問題

---

### API 合約

#### 合約 1: 測試執行介面

```python
class DatabaseQualityTest:
    """資料庫品質測試主類別"""
    
    def __init__(self, db_path: str):
        """初始化測試器
        
        Args:
            db_path: 資料庫路徑
        """
    
    def run_all_tests(self) -> Dict[str, TestResult]:
        """執行所有測試場景
        
        Returns:
            場景 ID -> 測試結果的字典
        """
    
    def run_scenario(self, scenario_id: str) -> TestResult:
        """執行單一測試場景
        
        Args:
            scenario_id: 場景 ID (如 'A1', 'B2')
            
        Returns:
            測試結果
        """
    
    def generate_report(self, results: Dict[str, TestResult], 
                       output_path: str) -> None:
        """生成測試報告
        
        Args:
            results: 測試結果字典
            output_path: 報告輸出路徑
        """
```

---

#### 合約 2: 測試場景介面

```python
class BaseTestScenario(ABC):
    """測試場景基類"""
    
    @property
    @abstractmethod
    def scenario_id(self) -> str:
        """場景 ID"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """場景名稱"""
    
    @abstractmethod
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試
        
        Args:
            cursor: 資料庫游標
            
        Returns:
            測試結果
        """
    
    @abstractmethod
    def validate_results(self, query_results: List[Dict]) -> Tuple[bool, List[QualityIssue]]:
        """驗證測試結果
        
        Args:
            query_results: 查詢結果
            
        Returns:
            (是否通過, 問題清單)
        """
```

---

#### 合約 3: 報告生成介面

```python
class ReportGenerator:
    """測試報告生成器"""
    
    def __init__(self, template_path: str = None):
        """初始化報告生成器
        
        Args:
            template_path: 報告模板路徑（可選）
        """
    
    def generate_markdown_report(self, 
                                 results: Dict[str, TestResult],
                                 issues: List[QualityIssue],
                                 output_path: str) -> None:
        """生成 Markdown 格式報告
        
        Args:
            results: 測試結果
            issues: 品質問題清單
            output_path: 輸出路徑
        """
    
    def generate_json_report(self, 
                            results: Dict[str, TestResult],
                            output_path: str) -> None:
        """生成 JSON 格式報告
        
        Args:
            results: 測試結果
            output_path: 輸出路徑
        """
    
    def generate_summary(self, results: Dict[str, TestResult]) -> Dict:
        """生成執行摘要
        
        Args:
            results: 測試結果
            
        Returns:
            摘要統計
        """
```

---

## Phase 0: 研究與設計

### 技術決策

#### 決策 1: 模組化測試架構

**決定**: 採用模組化設計，每個測試維度一個模組

**理由**:
- 易於維護和擴展
- 符合單一職責原則
- 便於單獨執行特定測試
- 代碼組織清晰

**替代方案**:
- 單一腳本: 過於龐大，難以維護
- pytest 框架: 過度設計，增加依賴

---

#### 決策 2: 錯誤處理策略

**決定**: 繼續執行策略（Continue on Error）

**理由**:
- 一個場景失敗不應中斷其他測試
- 需要獲得完整的測試結果
- 便於識別所有問題

**實現**:
```python
for scenario in scenarios:
    try:
        result = scenario.execute(cursor)
        results[scenario.id] = result
    except Exception as e:
        logger.error(f"場景 {scenario.id} 執行失敗: {e}")
        results[scenario.id] = TestResult(
            scenario_id=scenario.id,
            status='ERROR',
            error=str(e)
        )
        continue  # 繼續執行下一個場景
```

---

#### 決策 3: Unicode 編碼處理

**決定**: 使用 UTF-8 文件輸出，終端輸出移除特殊字符

**理由**:
- Windows PowerShell 使用 cp950 編碼
- 報告文件使用 UTF-8 保證完整性
- 終端輸出使用 ASCII 兼容字符

**實現**:
```python
# 文件輸出：UTF-8
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

# 終端輸出：移除 Emoji
def safe_print(text: str):
    # 移除或替換 Emoji 和特殊 Unicode
    safe_text = text.encode('ascii', 'ignore').decode('ascii')
    print(safe_text)
```

---

#### 決策 4: 性能測試基準

**決定**: 使用絕對時間和相對查詢計劃

**理由**:
- 絕對時間受硬件影響，但提供實際參考
- EXPLAIN QUERY PLAN 驗證索引使用
- 兩者結合提供全面的性能分析

**基準值**:
- 單條件查詢: <100ms
- 複雜查詢: <200ms
- 全文搜索: <500ms

---

### 研究文檔

所有技術決策已明確，無需額外研究。

---

## Phase 1: 數據模型與合約

### 核心數據模型

已在上面定義：
- `TestScenario`: 測試場景
- `TestResult`: 測試結果
- `QualityIssue`: 品質問題

### 檔案結構

```
stage1/
├── db_quality_test.py              ← 主執行腳本
├── test_scenarios/                 ← 測試場景模組
│   ├── __init__.py
│   ├── base.py                     ← 基類定義
│   ├── completeness_tests.py       ← A1-A3
│   ├── accuracy_tests.py           ← B1-B3
│   ├── consistency_tests.py        ← C1-C2
│   ├── performance_tests.py        ← D1
│   └── application_tests.py        ← E1
├── report_generator.py             ← 報告生成器
└── output/
    ├── DB_QUALITY_TEST_REPORT.md   ← 主報告
    ├── QUALITY_ISSUES.md           ← 問題清單
    ├── FIX_RECOMMENDATIONS.md      ← 修復建議
    └── test_results.json           ← JSON 數據（可選）
```

---

## Phase 2: 實施任務

### 任務分解

#### 任務組 A: 核心框架（優先級 P0）

**T001: 創建基礎架構** ⏳
- 時間: 30 分鐘
- 輸出: 
  - `test_scenarios/base.py`: 基類定義
  - `db_quality_test.py`: 主腳本框架
  - `report_generator.py`: 報告生成器

**T002: 實現測試執行引擎** ⏳
- 時間: 45 分鐘
- 輸出:
  - 測試場景載入機制
  - 測試執行邏輯
  - 錯誤處理和日誌記錄

---

#### 任務組 B: 測試場景實施（優先級 P0）

**T003: 實施完整性測試（A1-A3）** ⏳
- 時間: 60 分鐘
- 輸出: `test_scenarios/completeness_tests.py`
- 場景:
  - A1: 主分類覆蓋度
  - A2: 頻率段覆蓋度
  - A3: Danbooru 轉換完整性

**T004: 實施準確性測試（B1-B3）** ⏳
- 時間: 60 分鐘
- 輸出: `test_scenarios/accuracy_tests.py`
- 場景:
  - B1: 副分類邏輯準確性
  - B2: 信心度分布驗證
  - B3: 邊界案例處理

**T005: 實施一致性測試（C1-C2）** ⏳
- 時間: 45 分鐘
- 輸出: `test_scenarios/consistency_tests.py`
- 場景:
  - C1: 同類標籤一致性
  - C2: 分類來源品質對比

**T006: 實施性能測試（D1）** ⏳
- 時間: 30 分鐘
- 輸出: `test_scenarios/performance_tests.py`
- 場景:
  - D1: 複雜查詢效率測試

**T007: 實施應用測試（E1）** ⏳
- 時間: 45 分鐘
- 輸出: `test_scenarios/application_tests.py`
- 場景:
  - E1: Prompt 生成流程驗證

---

#### 任務組 C: 報告與文檔（優先級 P1）

**T008: 實施報告生成** ⏳
- 時間: 45 分鐘
- 輸出: 完整的報告生成邏輯
- 功能:
  - Markdown 報告生成
  - JSON 數據導出
  - 執行摘要生成

**T009: 實施問題分析** ⏳
- 時間: 30 分鐘
- 輸出: 問題識別和建議生成
- 功能:
  - 問題優先級排序
  - 修復建議生成
  - 問題清單格式化

**T010: 創建使用文檔** ⏳
- 時間: 20 分鐘
- 輸出: `DB_QUALITY_TEST_QUICKSTART.md`
- 內容:
  - 快速開始指南
  - 命令行參數說明
  - 輸出解讀指南

---

### 實施時間表

| 任務組 | 任務數 | 預計時間 | 優先級 |
|--------|--------|---------|--------|
| A: 核心框架 | 2 | 75 分鐘 | P0 |
| B: 測試場景 | 5 | 240 分鐘 | P0 |
| C: 報告文檔 | 3 | 95 分鐘 | P1 |
| **總計** | **10** | **6.8 小時** | - |

**建議執行順序**: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010

---

## 驗證與測試

### 單元測試計劃

雖然這是測試工具本身，仍需要驗證：

1. **SQL 語法驗證**:
   - 手動執行所有 SQL 查詢確保無語法錯誤
   - 驗證查詢返回預期的數據結構

2. **邊界條件測試**:
   - 空資料庫測試
   - 部分缺失欄位測試
   - 特殊字符標籤測試

3. **報告格式驗證**:
   - 驗證 Markdown 格式正確
   - 驗證表格對齊
   - 驗證中文顯示

### 整合測試

1. **端到端測試**:
   ```bash
   python db_quality_test.py --all
   ```
   - 驗證所有場景順利執行
   - 驗證報告成功生成
   - 驗證問題正確識別

2. **單場景測試**:
   ```bash
   python db_quality_test.py --scenario A1
   ```
   - 驗證單獨執行功能
   - 驗證結果正確性

---

## 快速開始指南（草稿）

### 安裝

無需額外安裝，使用 Python 標準庫。

### 執行

```bash
# 執行所有測試
python db_quality_test.py

# 執行特定維度
python db_quality_test.py --dimension Completeness

# 執行特定場景
python db_quality_test.py --scenario A1

# 生成 JSON 報告
python db_quality_test.py --format json

# 詳細模式
python db_quality_test.py --verbose
```

### 查看結果

```bash
# 主報告
cat output/DB_QUALITY_TEST_REPORT.md

# 問題清單
cat output/QUALITY_ISSUES.md

# 修復建議
cat output/FIX_RECOMMENDATIONS.md
```

---

## 里程碑與交付

### 里程碑 M1: 核心框架完成
- **時間**: Day 1（2 小時）
- **交付**: 基礎架構、測試引擎、報告生成器
- **驗證**: 能執行簡單的測試查詢

### 里程碑 M2: 所有測試場景實施
- **時間**: Day 2（4 小時）
- **交付**: 10 個測試場景全部實現
- **驗證**: 每個場景單獨執行成功

### 里程碑 M3: 完整測試執行
- **時間**: Day 2-3（1 小時）
- **交付**: 完整測試報告、問題清單、修復建議
- **驗證**: 所有交付物符合規格要求

---

## 附錄

### A. 技術棧總結

| 類別 | 技術 | 用途 |
|------|------|------|
| 資料庫 | SQLite3 | 數據存儲 |
| 程式語言 | Python 3.8+ | 測試腳本 |
| SQL 引擎 | sqlite3 (stdlib) | 查詢執行 |
| 報告格式 | Markdown | 人類可讀報告 |
| 數據格式 | JSON (可選) | 機器可讀數據 |
| 日誌 | logging (stdlib) | 執行日誌 |

### B. 代碼風格指南

- 遵循 PEP 8
- 使用 Type Hints
- 完整的 Docstrings (Google 風格)
- 函數長度 <50 行
- 單一職責原則

### C. 命名規範

- 模組: `snake_case.py`
- 類別: `PascalCase`
- 函數: `snake_case()`
- 常數: `UPPER_CASE`
- 私有: `_leading_underscore`

---

**計劃版本**: v1.0  
**最後更新**: 2025-10-13  
**下一步**: 開始實施任務 T001  
**準備狀態**: ✅ 計劃完成，可開始開發

