# 資料庫品質測試 - 任務清單

**功能**: 標籤分類資料庫的全面品質驗證與測試  
**規格**: [db-quality-test-spec.md](../specs/db-quality-test-spec.md)  
**計劃**: [db-quality-test-plan.md](../plans/db-quality-test-plan.md)  
**創建日期**: 2025-10-13  
**狀態**: 待執行 ⏳

---

## 📊 任務總覽

| 任務組 | 任務數 | 狀態 | 預計時間 | 實際時間 |
|--------|--------|------|---------|---------|
| A: 核心框架 | 2 | ⏳ 待執行 | 75 分鐘 | - |
| B: 測試場景 | 5 | ⏳ 待執行 | 240 分鐘 | - |
| C: 報告文檔 | 3 | ⏳ 待執行 | 95 分鐘 | - |
| **總計** | **10** | **0/10 完成** | **6.8 小時** | **-** |

---

## 任務組 A: 核心框架（P0）

### T001: 創建基礎架構 ⏳

**優先級**: P0  
**預計時間**: 30 分鐘  
**依賴**: 無

**目標**: 建立測試框架的基礎結構

**具體任務**:
- [ ] 創建 `test_scenarios/` 目錄
- [ ] 創建 `test_scenarios/__init__.py`
- [ ] 創建 `test_scenarios/base.py` 基類
- [ ] 定義 `TestScenario` 數據類
- [ ] 定義 `TestResult` 數據類
- [ ] 定義 `QualityIssue` 數據類
- [ ] 定義 `BaseTestScenario` 抽象基類

**交付物**:
- `test_scenarios/base.py` (約 150 行)

**驗收標準**:
- [ ] 所有數據類正確定義
- [ ] 基類提供必要的抽象方法
- [ ] 可被其他模組 import

---

### T002: 實現測試執行引擎 ⏳

**優先級**: P0  
**預計時間**: 45 分鐘  
**依賴**: T001

**目標**: 建立主測試腳本和執行邏輯

**具體任務**:
- [ ] 創建 `db_quality_test.py` 主腳本
- [ ] 實現 `DatabaseQualityTest` 類別
- [ ] 實現 `run_all_tests()` 方法
- [ ] 實現 `run_scenario()` 方法
- [ ] 實現命令行參數解析
- [ ] 實現 Unicode 安全輸出
- [ ] 實現錯誤處理和日誌記錄

**交付物**:
- `db_quality_test.py` (約 200 行)

**驗收標準**:
- [ ] 可成功連接資料庫
- [ ] 可載入所有測試場景
- [ ] 可執行測試並捕獲結果
- [ ] 錯誤不中斷執行流程

---

## 任務組 B: 測試場景實施（P0）

### T003: 實施完整性測試（A1-A3）⏳

**優先級**: P0  
**預計時間**: 60 分鐘  
**依賴**: T001, T002

**目標**: 實現 A 組所有測試場景

**具體任務**:
- [ ] 創建 `test_scenarios/completeness_tests.py`
- [ ] 實現 A1: 主分類覆蓋度測試
  - [ ] SQL 查詢執行
  - [ ] 結果驗證（17 個分類檢查）
  - [ ] 分布合理性檢查
- [ ] 實現 A2: 頻率段覆蓋度測試
  - [ ] SQL 查詢執行
  - [ ] 8 個頻率段覆蓋率計算
  - [ ] 目標達成驗證
- [ ] 實現 A3: Danbooru 轉換完整性測試
  - [ ] SQL 查詢執行
  - [ ] 5 種分類轉換驗證
  - [ ] 對應關係正確性檢查

**交付物**:
- `test_scenarios/completeness_tests.py` (約 250 行)

**驗收標準**:
- [ ] 3 個場景都能成功執行
- [ ] 返回正確的測試結果
- [ ] 能識別覆蓋率不足問題

---

### T004: 實施準確性測試（B1-B3）⏳

**優先級**: P0  
**預計時間**: 60 分鐘  
**依賴**: T001, T002

**目標**: 實現 B 組所有測試場景

**具體任務**:
- [ ] 創建 `test_scenarios/accuracy_tests.py`
- [ ] 實現 B1: 副分類邏輯準確性
  - [ ] 眼睛標籤檢查
  - [ ] 頭髮標籤檢查
  - [ ] 誤分類案例識別
- [ ] 實現 B2: 信心度分布驗證
  - [ ] 各主分類信心度統計
  - [ ] 整體信心度分布
  - [ ] 低信心度標籤識別
- [ ] 實現 B3: 邊界案例處理
  - [ ] 複合標籤檢查
  - [ ] NULL 字符串檢查
  - [ ] 成人內容分類檢查
  - [ ] 極低信心度檢查

**交付物**:
- `test_scenarios/accuracy_tests.py` (約 300 行)

**驗收標準**:
- [ ] 3 個場景都能成功執行
- [ ] 能準確識別誤分類
- [ ] 能計算準確率

---

### T005: 實施一致性測試（C1-C2）⏳

**優先級**: P0  
**預計時間**: 45 分鐘  
**依賴**: T001, T002

**目標**: 實現 C 組所有測試場景

**具體任務**:
- [ ] 創建 `test_scenarios/consistency_tests.py`
- [ ] 實現 C1: 同類標籤一致性
  - [ ] 眼睛標籤一致性檢查（使用 CTE）
  - [ ] 頭髮標籤一致性檢查
  - [ ] 服裝標籤一致性檢查
  - [ ] 不一致案例識別
- [ ] 實現 C2: 分類來源品質對比
  - [ ] 各來源品質統計
  - [ ] LLM vs 規則品質對比
  - [ ] 品質穩定性分析

**交付物**:
- `test_scenarios/consistency_tests.py` (約 250 行)

**驗收標準**:
- [ ] CTE 查詢正確執行
- [ ] 一致性百分比計算正確
- [ ] 能識別不一致模式

---

### T006: 實施性能測試（D1）⏳

**優先級**: P0  
**預計時間**: 30 分鐘  
**依賴**: T001, T002

**目標**: 實現性能測試場景

**具體任務**:
- [ ] 創建 `test_scenarios/performance_tests.py`
- [ ] 實現 D1: 複雜查詢效率測試
  - [ ] 單條件查詢性能測量
  - [ ] 多條件組合查詢測量
  - [ ] 聚合查詢性能測量
  - [ ] 全文搜索性能測量
  - [ ] EXPLAIN QUERY PLAN 分析
- [ ] 實現性能計時函數
- [ ] 實現查詢計劃解析

**交付物**:
- `test_scenarios/performance_tests.py` (約 150 行)

**驗收標準**:
- [ ] 準確測量查詢時間
- [ ] 能解析查詢計劃
- [ ] 能判斷是否使用索引

---

### T007: 實施應用測試（E1）⏳

**優先級**: P0  
**預計時間**: 45 分鐘  
**依賴**: T001, T002

**目標**: 實現實際應用場景測試

**具體任務**:
- [ ] 創建 `test_scenarios/application_tests.py`
- [ ] 實現 E1: Prompt 生成流程驗證
  - [ ] Step 1: 角色數量查詢
  - [ ] Step 2: 髮型髮色查詢
  - [ ] Step 3: 服裝配飾查詢
  - [ ] Step 4: 姿態表情查詢
  - [ ] Step 5: 場景環境查詢
  - [ ] Step 6: 藝術風格查詢
  - [ ] 綜合統計分析
- [ ] 驗證每個維度選項充足性
- [ ] 生成示例 Prompt

**交付物**:
- `test_scenarios/application_tests.py` (約 200 行)

**驗收標準**:
- [ ] 6 個步驟都成功執行
- [ ] 每個維度有足夠選項
- [ ] 能生成合理的 Prompt 示例

---

## 任務組 C: 報告與文檔（P1）

### T008: 實施報告生成 ⏳

**優先級**: P1  
**預計時間**: 45 分鐘  
**依賴**: T003-T007

**目標**: 建立完整的報告生成系統

**具體任務**:
- [ ] 創建 `report_generator.py`
- [ ] 實現 `ReportGenerator` 類別
- [ ] 實現 Markdown 報告生成
  - [ ] 執行摘要部分
  - [ ] 詳細結果部分
  - [ ] 問題總結部分
  - [ ] 表格格式化
- [ ] 實現 JSON 報告生成
- [ ] 實現報告模板系統

**交付物**:
- `report_generator.py` (約 250 行)

**驗收標準**:
- [ ] Markdown 格式正確
- [ ] 表格對齊美觀
- [ ] JSON 格式有效
- [ ] 支持中文輸出

---

### T009: 實施問題分析 ⏳

**優先級**: P1  
**預計時間**: 30 分鐘  
**依賴**: T003-T007

**目標**: 建立問題識別和建議生成機制

**具體任務**:
- [ ] 實現問題收集邏輯
- [ ] 實現問題優先級排序
  - [ ] P0: 必須修復（如覆蓋率不達標）
  - [ ] P1: 建議修復（如低信心度）
  - [ ] P2: 可選優化（如性能優化）
- [ ] 實現修復建議生成
  - [ ] 基於問題類型的建議模板
  - [ ] 具體的 SQL 修復語句
  - [ ] 優先級和影響評估
- [ ] 生成問題清單文檔
- [ ] 生成修復建議文檔

**交付物**:
- 問題分析邏輯（集成在主腳本）
- `output/QUALITY_ISSUES.md`
- `output/FIX_RECOMMENDATIONS.md`

**驗收標準**:
- [ ] 問題按優先級正確排序
- [ ] 每個問題都有修復建議
- [ ] 建議具體且可執行

---

### T010: 創建使用文檔 ⏳

**優先級**: P1  
**預計時間**: 20 分鐘  
**依賴**: T001-T009

**目標**: 提供完整的使用指南

**具體任務**:
- [ ] 創建 `DB_QUALITY_TEST_QUICKSTART.md`
- [ ] 撰寫快速開始指南
  - [ ] 環境要求
  - [ ] 執行步驟
  - [ ] 命令行參數說明
- [ ] 撰寫輸出解讀指南
  - [ ] 報告結構說明
  - [ ] 狀態含義解釋
  - [ ] 問題優先級說明
- [ ] 撰寫常見問題解答
- [ ] 提供使用示例

**交付物**:
- `DB_QUALITY_TEST_QUICKSTART.md`

**驗收標準**:
- [ ] 新用戶可根據文檔成功執行
- [ ] 涵蓋所有使用場景
- [ ] 包含實際輸出示例

---

## 執行計劃

### 第一天（核心開發）

**上午** (2 小時):
- T001: 創建基礎架構 (30 分鐘)
- T002: 實現測試執行引擎 (45 分鐘)
- 測試: 驗證框架可用 (15 分鐘)

**下午** (2 小時):
- T003: 實施完整性測試 (60 分鐘)
- T004: 實施準確性測試（部分）(60 分鐘)

**晚上** (1 小時):
- T004: 實施準確性測試（完成）(30 分鐘)
- T005: 實施一致性測試（開始）(30 分鐘)

---

### 第二天（測試實施）

**上午** (2 小時):
- T005: 實施一致性測試（完成）(15 分鐘)
- T006: 實施性能測試 (30 分鐘)
- T007: 實施應用測試 (45 分鐘)
- 整合測試: 運行所有場景 (30 分鐘)

**下午** (1.5 小時):
- T008: 實施報告生成 (45 分鐘)
- T009: 實施問題分析 (30 分鐘)
- T010: 創建使用文檔 (20 分鐘)

**完成**: 執行完整測試，生成報告

---

## 詳細任務規格

### T001 詳細規格

**檔案**: `test_scenarios/base.py`

**類別定義**:

```python
@dataclass
class TestScenario:
    id: str
    name: str
    dimension: str
    description: str
    sql_queries: List[str]
    success_criteria: Dict
    priority: str

@dataclass
class TestResult:
    scenario_id: str
    status: str  # PASS/FAIL/WARN/ERROR
    execution_time: float
    query_results: List[Dict]
    issues: List['QualityIssue']
    metrics: Dict
    timestamp: str
    error: str = ""

@dataclass
class QualityIssue:
    issue_type: str
    severity: str  # P0/P1/P2
    description: str
    affected_tags: List[str]
    recommendation: str
    scenario_id: str

class BaseTestScenario(ABC):
    @property
    @abstractmethod
    def scenario_id(self) -> str: ...
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @abstractmethod
    def execute(self, cursor: sqlite3.Cursor) -> TestResult: ...
    
    @abstractmethod
    def validate_results(self, query_results: List[Dict]) 
        -> Tuple[bool, List[QualityIssue]]: ...
```

---

### T002 詳細規格

**檔案**: `db_quality_test.py`

**主類別**:

```python
class DatabaseQualityTest:
    def __init__(self, db_path: str = "output/tags.db"):
        self.db_path = db_path
        self.scenarios: List[BaseTestScenario] = []
        self.results: Dict[str, TestResult] = {}
        
    def load_scenarios(self) -> None:
        """載入所有測試場景"""
        
    def run_all_tests(self) -> Dict[str, TestResult]:
        """執行所有測試"""
        
    def run_scenario(self, scenario_id: str) -> TestResult:
        """執行單一場景"""
        
    def run_dimension(self, dimension: str) -> Dict[str, TestResult]:
        """執行特定維度的所有場景"""
```

**命令行參數**:
```
--all: 執行所有測試（默認）
--scenario <ID>: 執行特定場景（如 A1, B2）
--dimension <NAME>: 執行特定維度（如 Completeness, Accuracy）
--format <FORMAT>: 報告格式（markdown/json/both）
--verbose: 詳細輸出模式
--output <PATH>: 指定輸出目錄（默認 output/）
```

---

### T003-T007 場景實施規格

每個測試場景類別應繼承 `BaseTestScenario` 並實現：

```python
class ScenarioA1_MainCategoryCoverage(BaseTestScenario):
    @property
    def scenario_id(self) -> str:
        return 'A1'
    
    @property
    def name(self) -> str:
        return '主分類覆蓋度測試'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        # 1. 執行 SQL 查詢
        # 2. 獲取結果
        # 3. 驗證結果
        # 4. 返回 TestResult
        
    def validate_results(self, query_results: List[Dict]) 
        -> Tuple[bool, List[QualityIssue]]:
        # 1. 檢查成功標準
        # 2. 識別問題
        # 3. 返回通過狀態和問題清單
```

---

### T008 報告生成規格

**檔案**: `report_generator.py`

**報告結構**:
```markdown
# 資料庫品質測試報告

**執行日期**: 2025-10-13 15:00
**資料庫**: output/tags.db (Plan C Phase 3)
**執行者**: Automated Test

## 📊 執行摘要
- 總場景: 10
- ✅ 通過: 8
- ⚠️ 警告: 1
- ❌ 失敗: 1

## 詳細結果

### A 組: 完整性測試

#### A1: 主分類覆蓋度 ✅
- **狀態**: 通過
- **執行時間**: 0.05 秒
- **主要發現**: 所有 17 個主分類都存在
- **數據**: [表格]

[... 其他場景 ...]

## 問題總結
### P0 問題（必須修復）
1. [場景 B3] 發現 15 個 NULL 字符串標籤
   - 受影響標籤: [清單]
   - 修復建議: 運行 quality_optimizer.py

### P1 問題（建議修復）
...

## 修復建議
...
```

---

## 成功標準

### 開發完成標準
- [ ] 所有 10 個任務完成
- [ ] 代碼通過基本測試
- [ ] 無明顯錯誤或 bug

### 功能驗證標準
- [ ] 能成功執行所有 10 個場景
- [ ] 生成完整的測試報告
- [ ] 識別已知的品質問題
- [ ] 報告格式正確，易於閱讀

### 品質標準
- [ ] 代碼符合 PEP 8
- [ ] 有完整的文檔字符串
- [ ] 錯誤處理完善
- [ ] 日誌記錄清晰

---

## 風險與緩解

| 風險 | 可能性 | 影響 | 緩解措施 |
|------|--------|------|---------|
| CTE 不支持 | 低 | 高 | 檢查版本，提供替代查詢 |
| Unicode 編碼錯誤 | 高 | 低 | 使用 ASCII 輸出，文件用 UTF-8 |
| 查詢超時 | 中 | 中 | 設置超時限制，優化查詢 |
| 開發時間超支 | 中 | 中 | 優先完成 P0 任務 |

---

## 下一步

1. **立即開始**: T001 創建基礎架構
2. **優先順序**: 按 P0 任務順序執行
3. **驗證點**: 每完成一個任務組進行整合測試

**準備狀態**: ✅ 計劃完成，可開始實施！

---

**計劃版本**: v1.0  
**最後更新**: 2025-10-13  
**預計完成**: 2 天（12 小時工作時間）  
**狀態**: 📋 計劃完成，待執行

