# 開發計畫：Danbooru 標籤資料管線 - Phase 1 (純規則式分類)

**計畫編號 (Plan ID):** PLAN-2025-001-PHASE1

**版本 (Version):** 1.1.0

**狀態 (Status):** Planning

**計畫負責人 (Owner):** Prompt-Scribe Team

**建立日期 (Created):** 2025-10-08

**最後更新 (Last Updated):** 2025-10-08

**預計開始 (Start Date):** 2025-10-08

**預計完成 (Target Date):** 2025-10-15

---

## 憲法符合性檢查 (Constitution Compliance Check)

- [x] 計畫遵循「兩階段混合式架構」（本計畫專注於階段一：本地資料管線）
- [x] 計畫遵循「LLM 職責分離」（Phase 1 不使用資料層 LLM，僅使用規則式分類）
- [x] 計畫遵循「規格驅動開發」（基於 SPEC-2025-001）
- [x] 計畫遵循「資料優先」（資料清洗與驗證是核心任務）
- [x] 計畫考慮「模組化與可讀性」（簡單腳本架構，職責清晰）

---

## 1. 計畫概述 (Overview)

### 1.1 目標 (Objectives)

**主要目標：**
- 建立一個完全本地、不依賴 LLM 的資料處理管線
- 使用規則式方法對 Danbooru 標籤進行主分類 (main_category) 和副分類 (sub_category)
- 產出結構化的 SQLite 資料庫 (`tags.db`)，包含清洗、合併、分類後的標籤資料
- 實現 ≥ 90% 的主分類覆蓋率（針對 `danbooru_cat=0` 的一般標籤）

**成功指標 (Success Metrics):**
- 所有 CSV 檔案成功載入，無遺漏
- 標籤名稱 (`name`) 完全去重，無重複值
- 主分類覆蓋率 ≥ 90%
- 副分類覆蓋率 ≥ 40%（針對高價值主分類）
- 處理 10 萬筆標籤資料在 5 分鐘內完成
- 所有資料驗證規則通過

### 1.2 背景與動機 (Background and Motivation)

根據 SPEC-2025-001，原始規格包含 LLM 語意分類功能。然而，為了：
1. **降低初期開發複雜度**：規則式分類可快速實現並驗證資料管線
2. **減少外部依賴**：不依賴 LLM API，避免成本、限流和網路連線問題
3. **建立基準線 (Baseline)**：規則式分類結果可作為未來 LLM 分類的對照組
4. **階段性實作**：先完成資料管線核心功能，再逐步添加 LLM 增強

本計畫將專注於建立一個**純 Python、純規則式**的分類系統，並預留未來擴展 LLM 的接口。

### 1.3 範圍 (Scope)

**包含 (In Scope):**
- 讀取 `/data/raw` 目錄下所有 CSV 檔案
- 資料清洗、標準化與驗證
- 合併與去重複處理（按 `name` 聚合）
- 規則式分類邏輯（基於關鍵字字典）
  - 主分類 (main_category)：9 個頂層類別
  - 副分類 (sub_category)：針對 CHARACTER_RELATED 和 ACTION_POSE
- 產出 SQLite 資料庫 (`/output/tags.db`)
- 完整的資料驗證與品質檢查
- 分類統計報告

**不包含 (Out of Scope):**
- LLM API 整合（留待 Phase 2）
- 圖像檔案處理
- Web UI 或互動介面
- 雲端部署（屬於階段二）
- `llm_inference_log` 表（Phase 1 不使用 LLM）

---

## 2. 架構分階段規劃 (Architecture-Stage Planning)

### 2.1 階段一：本地資料管線工作 (Stage 1: Local Data Pipeline)

**工作項目：**
- [x] 建立專案基礎結構
- [ ] 實作 CSV 載入模組
- [ ] 實作資料驗證模組
- [ ] 實作合併去重模組
- [ ] 實作規則式分類模組（核心）
- [ ] 實作資料品質驗證模組
- [ ] 整合完整管線
- [ ] 撰寫測試
- [ ] 產生分類統計報告

**產出物：**
- `tags.db`：包含 `tags_raw`、`tags_final` 資料表
- 處理腳本：`run_pipeline.py`
- 規則字典：`data_rules.py`
- 配置檔案：`config.py`
- 分類報告：`classification_report.txt`

**技術棧：**
- Python 3.11+
- SQLite (內建 `sqlite3` 模組)
- pandas 2.0+ (CSV 處理)
- 標準函式庫：pathlib, json, logging, datetime

### 2.2 階段二：雲端應用後端工作 (Stage 2: Cloud Application Backend)

**不在本計畫範圍內**（將在後續計畫中規劃）

### 2.3 階段相依性 (Stage Dependencies)

```
Phase 1 (規則式分類) → 產出 tags.db → Phase 2 (LLM 增強) → 階段二 (雲端部署)
```

---

## 3. 規格與實作對應 (Spec-to-Implementation Mapping)

| 規格文件 | 對應工作項目 | 負責人 | 狀態 |
|----------|--------------|--------|------|
| SPEC-2025-001, FR-01 | CSV 載入模組 | AI Agent | 未開始 |
| SPEC-2025-001, FR-02 | 欄位映射與容錯處理 | AI Agent | 未開始 |
| SPEC-2025-001, FR-03 | `tags_raw` 表建立 | AI Agent | 未開始 |
| SPEC-2025-001, FR-04 | 合併去重邏輯 | AI Agent | 未開始 |
| SPEC-2025-001, FR-06 | 規則式分類邏輯 | AI Agent | 未開始 |
| SPEC-2025-001, FR-07 | SQLite 資料庫產出 | AI Agent | 未開始 |
| SPEC-2025-001, FR-08 | `tags_final` Schema | AI Agent | 未開始 |
| SPEC-2025-001, NFR-01 | 效能優化 | AI Agent | 未開始 |

---

## 4. 任務分解 (Task Breakdown)

### 4.1 第一階段任務

#### 任務組 A：專案基礎設定

- **任務 A1：建立專案結構**
  - **預估時間：** 1 小時
  - **優先級：** High
  - **相依任務：** 無
  - **驗收標準：** 
    - `run_pipeline.py` 檔案存在
    - `data_rules.py` 檔案存在
    - `config.py` 檔案存在
    - `/output` 目錄存在

- **任務 A2：定義配置檔 (`config.py`)**
  - **預估時間：** 0.5 小時
  - **優先級：** High
  - **相依任務：** A1
  - **驗收標準：** 
    - 定義資料目錄路徑
    - 定義輸出目錄路徑
    - 定義資料庫檔案名稱

#### 任務組 B：規則式分類核心

- **任務 B1：建立分類規則字典 (`data_rules.py`)**
  - **預估時間：** 4 小時
  - **優先級：** High
  - **相依任務：** A2
  - **驗收標準：** 
    - 定義 9 個主分類的關鍵字列表
    - 定義 CHARACTER_RELATED 副分類關鍵字（CLOTHING, HAIR, CHARACTER_COUNT）
    - 定義 ACTION_POSE 副分類關鍵字（POSE, EXPRESSION）
    - 關鍵字列表經過人工審查與測試
  - **內容要點：**
    ```python
    # 主分類關鍵字字典
    MAIN_CATEGORY_RULES = {
        'CHARACTER_RELATED': [...],
        'OBJECTS': [...],
        'ENVIRONMENT': [...],
        'COMPOSITION': [...],
        'VISUAL_EFFECTS': [...],
        'ART_STYLE': [...],
        'ACTION_POSE': [...],
        'QUALITY': [...],
        'TECHNICAL': [...],
    }
    
    # 副分類關鍵字字典
    SUB_CATEGORY_RULES = {
        'CHARACTER_RELATED': {
            'CLOTHING': [...],
            'HAIR': [...],
            'CHARACTER_COUNT': [...],
        },
        'ACTION_POSE': {
            'POSE': [...],
            'EXPRESSION': [...],
        }
    }
    ```

- **任務 B2：實作分類函式**
  - **預估時間：** 3 小時
  - **優先級：** High
  - **相依任務：** B1
  - **驗收標準：** 
    - `classify_tag(tag_name: str) -> tuple[str, Optional[str]]` 函式正常運作
    - 支援模糊匹配（部分字串匹配）
    - 支援多規則優先級判斷
    - 100 個測試案例通過
  - **函式邏輯：**
    1. 標準化標籤名稱（小寫、去空白）
    2. 遍歷主分類規則，找到第一個匹配的關鍵字
    3. 如果主分類有副分類規則，繼續匹配副分類
    4. 返回 `(main_category, sub_category)`

#### 任務組 C：資料載入與驗證

- **任務 C1：實作 CSV 載入函式**
  - **預估時間：** 2 小時
  - **優先級：** High
  - **相依任務：** A2
  - **驗收標準：** 
    - 成功讀取所有 `.csv` 檔案
    - 處理欄位名稱不一致（`category` vs `danbooru_cat`）
    - 處理缺失欄位（提供預設值）
    - 記錄每個檔案的載入統計

- **任務 C2：實作資料驗證邏輯**
  - **預估時間：** 2 小時
  - **優先級：** High
  - **相依任務：** C1
  - **驗收標準：** 
    - 驗證 `name` 不為空
    - 驗證 `category` 在 0-5 範圍內
    - 驗證 `post_count` 非負數
    - 無效記錄被記錄並跳過

- **任務 C3：建立 `tags_raw` 資料表**
  - **預估時間：** 1 小時
  - **優先級：** High
  - **相依任務：** C2
  - **驗收標準：** 
    - 資料表 Schema 符合 SPEC-2025-001
    - 所有有效記錄成功插入
    - 索引正確建立

#### 任務組 D：合併去重與分類

- **任務 D1：實作合併去重邏輯**
  - **預估時間：** 2 小時
  - **優先級：** High
  - **相依任務：** C3
  - **驗收標準：** 
    - 相同 `name` 的記錄被合併
    - `post_count` 正確加總
    - `source_count` 正確計算
    - 保留 `danbooru_cat`（選擇出現次數最多的值）

- **任務 D2：套用分類規則**
  - **預估時間：** 2 小時
  - **優先級：** High
  - **相依任務：** B2, D1
  - **驗收標準：** 
    - 對所有 `danbooru_cat=0` 的標籤執行分類
    - 主分類覆蓋率 ≥ 90%
    - 副分類覆蓋率 ≥ 40%
    - 未分類的標籤 `main_category` 設為 NULL

- **任務 D3：建立 `tags_final` 資料表**
  - **預估時間：** 1.5 小時
  - **優先級：** High
  - **相依任務：** D2
  - **驗收標準：** 
    - 資料表 Schema 符合 SPEC-2025-001（不包含 LLM 相關欄位）
    - 所有記錄成功插入
    - 索引與約束正確建立
    - 全文搜尋索引建立

#### 任務組 E：品質保證與驗證

- **任務 E1：實作資料品質檢查**
  - **預估時間：** 2 小時
  - **優先級：** High
  - **相依任務：** D3
  - **驗收標準：** 
    - 唯一性檢查通過
    - 完整性檢查通過
    - 一致性檢查通過
    - 覆蓋率檢查通過

- **任務 E2：產生分類統計報告**
  - **預估時間：** 1.5 小時
  - **優先級：** Medium
  - **相依任務：** E1
  - **驗收標準：** 
    - 報告包含：總標籤數、主分類分佈、副分類分佈
    - 報告包含：覆蓋率統計、TOP 未分類標籤
    - 報告儲存至 `/output/classification_report.txt`

#### 任務組 F：整合與測試

- **任務 F1：整合完整管線 (`run_pipeline.py`)**
  - **預估時間：** 2 小時
  - **優先級：** High
  - **相依任務：** E2
  - **驗收標準：** 
    - 一個指令完成所有處理步驟
    - 提供進度條顯示
    - 錯誤處理完善
    - 記錄詳細日誌

- **任務 F2：撰寫單元測試**
  - **預估時間：** 4 小時
  - **優先級：** High
  - **相依任務：** F1
  - **驗收標準：** 
    - 測試覆蓋率 ≥ 80%
    - 關鍵函式有完整測試案例
    - 所有測試通過

- **任務 F3：端到端測試**
  - **預估時間：** 2 小時
  - **優先級：** High
  - **相依任務：** F2
  - **驗收標準：** 
    - 使用真實資料測試完整管線
    - 產出的 `tags.db` 可被 SQLite 工具開啟
    - 所有驗收標準通過

---

## 5. 時程規劃 (Timeline)

### 5.1 里程碑 (Milestones)

| 里程碑 | 日期 | 交付物 | 狀態 |
|--------|------|--------|------|
| M1: 規則字典完成 | 2025-10-09 | `data_rules.py` | 未開始 |
| M2: 分類邏輯完成 | 2025-10-10 | 分類函式 + 測試 | 未開始 |
| M3: 資料載入完成 | 2025-10-11 | CSV → tags_raw | 未開始 |
| M4: 管線整合完成 | 2025-10-13 | `run_pipeline.py` | 未開始 |
| M5: 測試與驗證完成 | 2025-10-14 | 測試報告 | 未開始 |
| M6: Phase 1 完成 | 2025-10-15 | `tags.db` + 文件 | 未開始 |

### 5.2 甘特圖 (Gantt Chart)

```
任務        | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 | Day 7 |
-----------|-------|-------|-------|-------|-------|-------|-------|
任務組 A    | ████  |       |       |       |       |       |       |
任務組 B    | ████  | ████  |       |       |       |       |       |
任務組 C    |       | ████  | ████  |       |       |       |       |
任務組 D    |       |       | ████  | ████  |       |       |       |
任務組 E    |       |       |       | ████  | ████  |       |       |
任務組 F    |       |       |       |       | ████  | ████  | ████  |
```

---

## 6. 資源規劃 (Resource Planning)

### 6.1 人力資源

| 角色 | 人員 | 分配時間 | 主要任務 |
|------|------|----------|----------|
| 開發者 | AI Agent (Cursor) | 100% | 所有程式碼實作 |
| 審查者 | 使用者 | 按需 | 規則字典審查、測試驗證 |

### 6.2 技術資源

- **開發環境：** Windows 10, Python 3.11+, VS Code/Cursor
- **雲端資源：** 無（完全本地執行）
- **第三方服務：** 無

### 6.3 預算 (Budget)

| 項目 | 預估成本 | 備註 |
|------|----------|------|
| 開發成本 | $0 | 本地開發 |
| LLM API | $0 | Phase 1 不使用 |
| 雲端服務 | $0 | 本地執行 |
| **總計** | **$0** | |

---

## 7. 風險管理 (Risk Management)

| 風險 | 可能性 | 影響 | 緩解策略 | 負責人 |
|------|--------|------|----------|--------|
| CSV 格式不一致 | High | Medium | 實作彈性欄位映射與驗證 | AI Agent |
| 規則覆蓋率不足 | Medium | High | 持續優化關鍵字字典，分析未分類標籤 | 使用者 + AI Agent |
| 效能問題（大資料量） | Low | Medium | 使用批次處理與索引優化 | AI Agent |
| 關鍵字衝突（同一標籤匹配多個分類） | Medium | Medium | 定義優先級規則，記錄衝突案例 | AI Agent |
| 測試資料不足 | Low | High | 使用真實資料的子集進行測試 | AI Agent |

---

## 8. 品質保證 (Quality Assurance)

### 8.1 測試計畫

- **單元測試：** 
  - 分類函式測試（100+ 案例）
  - 資料驗證測試
  - 合併去重測試
  - 覆蓋率目標：≥ 80%

- **整合測試：** 
  - CSV 載入 → 分類 → 資料庫產出
  - 使用測試資料集（1000 筆）

- **端到端測試：** 
  - 使用真實資料（全量或 10% 取樣）
  - 驗證所有驗收標準

- **效能測試：** 
  - 10 萬筆標籤處理時間 < 5 分鐘
  - 記憶體使用 < 2GB

### 8.2 Code Review 流程

- 所有程式碼必須經過：
  - 自動化 linter 檢查（pylint, black）
  - 單元測試通過
  - 邏輯審查（使用者或 AI 自審）

### 8.3 文件要求

- [x] 程式碼註解完整（docstring）
- [x] README.md 已更新（使用說明）
- [x] 分類規則文件（關鍵字說明）
- [x] 技術決策記錄（選擇規則式分類的原因）

---

## 9. 分類規則設計 (Classification Rules Design)

### 9.1 主分類規則 (Main Category Rules)

**分類邏輯：**
基於關鍵字匹配，優先級從高到低：

1. **QUALITY** (優先級 1 - 最高)
   - 關鍵字：`best_quality`, `masterpiece`, `worst_quality`, `low_quality`, `normal_quality`, `highres`, `absurdres`

2. **TECHNICAL** (優先級 2)
   - 關鍵字：`monochrome`, `greyscale`, `comic`, `animated`, `pixel_art`, `sketch`, `lineart`, `censored`, `uncensored`

3. **ART_STYLE** (優先級 3)
   - 關鍵字：`anime`, `realistic`, `chibi`, `watercolor`, `oil_painting`, `traditional_media`, `manga`, `3d`, `photorealistic`

4. **COMPOSITION** (優先級 4)
   - 關鍵字：`from_above`, `from_below`, `close-up`, `wide_shot`, `portrait`, `dutch_angle`, `pov`, `first-person_view`, `symmetrical`

5. **VISUAL_EFFECTS** (優先級 5)
   - 關鍵字：`lighting`, `bloom`, `lens_flare`, `motion_blur`, `depth_of_field`, `bokeh`, `chromatic_aberration`, `backlight`

6. **CHARACTER_RELATED** (優先級 6)
   - 關鍵字：`girl`, `boy`, `woman`, `man`, `hair`, `eyes`, `dress`, `shirt`, `skirt`, `uniform`, `solo`, `multiple_girls`

7. **ACTION_POSE** (優先級 7)
   - 關鍵字：`sitting`, `standing`, `lying`, `walking`, `running`, `smile`, `blush`, `looking_at_viewer`, `hand_up`, `arms_behind_back`

8. **OBJECTS** (優先級 8)
   - 關鍵字：`weapon`, `sword`, `gun`, `flower`, `book`, `phone`, `computer`, `cup`, `chair`, `table`

9. **ENVIRONMENT** (優先級 9 - 最低)
   - 關鍵字：`indoors`, `outdoors`, `sky`, `cloud`, `tree`, `building`, `street`, `beach`, `mountain`, `forest`

**未匹配處理：**
- 如果標籤不匹配任何關鍵字，`main_category` 設為 `NULL`
- 這些標籤將被記錄於分類報告的「未分類標籤」區段

### 9.2 副分類規則 (Sub-Category Rules)

**CHARACTER_RELATED 副分類：**
- **CLOTHING:** `dress`, `shirt`, `skirt`, `uniform`, `jacket`, `coat`, `pants`, `shorts`, `swimsuit`, `kimono`
- **HAIR:** `hair`, `ponytail`, `twintails`, `braid`, `short_hair`, `long_hair`, `bangs`, `hairband`, `hair_ornament`
- **CHARACTER_COUNT:** `solo`, `2girls`, `3girls`, `multiple_girls`, `multiple_boys`, `1boy`, `1girl`

**ACTION_POSE 副分類：**
- **POSE:** `sitting`, `standing`, `lying`, `kneeling`, `crouching`, `leaning`, `stretching`, `walking`, `running`, `jumping`
- **EXPRESSION:** `smile`, `blush`, `angry`, `sad`, `surprised`, `crying`, `laughing`, `embarrassed`, `smirk`, `serious`

---

## 10. 實作細節 (Implementation Details)

### 10.1 專案結構

```
stage1/
├── run_pipeline.py          # 主執行腳本
├── config.py                # 配置檔案
├── data_rules.py            # 分類規則字典
├── data/
│   └── raw/                 # 輸入 CSV 檔案
├── output/
│   ├── tags.db              # 產出資料庫
│   └── classification_report.txt  # 分類報告
└── tests/
    └── test_classifier.py   # 單元測試
```

### 10.2 核心函式簽名

```python
# run_pipeline.py
def load_csv_files(data_dir: Path) -> pd.DataFrame:
    """載入所有 CSV 檔案到 DataFrame"""
    pass

def create_tags_raw_table(df: pd.DataFrame, db_path: Path):
    """建立 tags_raw 資料表"""
    pass

def merge_and_deduplicate(db_path: Path) -> pd.DataFrame:
    """合併去重處理"""
    pass

def apply_classification(df: pd.DataFrame) -> pd.DataFrame:
    """套用分類規則"""
    pass

def create_tags_final_table(df: pd.DataFrame, db_path: Path):
    """建立 tags_final 資料表"""
    pass

def validate_output(db_path: Path) -> List[str]:
    """驗證輸出資料品質"""
    pass

def generate_report(db_path: Path, output_path: Path):
    """產生分類統計報告"""
    pass

def main():
    """主執行流程"""
    # 1. 載入資料
    # 2. 建立 tags_raw
    # 3. 合併去重
    # 4. 套用分類
    # 5. 建立 tags_final
    # 6. 驗證
    # 7. 產生報告
    pass
```

```python
# data_rules.py
from typing import Optional, Tuple

MAIN_CATEGORY_RULES: Dict[str, List[str]] = {
    'QUALITY': [...],
    'TECHNICAL': [...],
    'ART_STYLE': [...],
    'COMPOSITION': [...],
    'VISUAL_EFFECTS': [...],
    'CHARACTER_RELATED': [...],
    'ACTION_POSE': [...],
    'OBJECTS': [...],
    'ENVIRONMENT': [...],
}

SUB_CATEGORY_RULES: Dict[str, Dict[str, List[str]]] = {
    'CHARACTER_RELATED': {
        'CLOTHING': [...],
        'HAIR': [...],
        'CHARACTER_COUNT': [...],
    },
    'ACTION_POSE': {
        'POSE': [...],
        'EXPRESSION': [...],
    }
}

def classify_tag(tag_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    根據規則對標籤進行分類
    
    Args:
        tag_name: 標籤名稱
    
    Returns:
        (main_category, sub_category)
    """
    pass
```

### 10.3 資料表 Schema（簡化版）

```sql
-- tags_raw 表
CREATE TABLE tags_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    name TEXT NOT NULL,
    danbooru_cat INTEGER,
    post_count INTEGER DEFAULT 0,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- tags_final 表
CREATE TABLE tags_final (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    danbooru_cat INTEGER NOT NULL,
    main_category TEXT,                  -- 可為 NULL（未分類）
    sub_category TEXT,
    post_count INTEGER DEFAULT 0,
    source_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (danbooru_cat BETWEEN 0 AND 5),
    CHECK (post_count >= 0),
    CHECK (source_count >= 1)
);

-- 索引
CREATE UNIQUE INDEX idx_tags_final_name ON tags_final(name);
CREATE INDEX idx_tags_final_main_cat ON tags_final(main_category);
CREATE INDEX idx_tags_final_sub_cat ON tags_final(sub_category);
```

### 10.4 Pandas 最佳實踐（來自官方文檔）

#### 記憶體優化
```python
# 載入 CSV 時指定資料型別，減少記憶體使用
df = pd.read_csv('data.csv', dtype={
    'name': 'string',           # 字串型別
    'danbooru_cat': 'int8',     # 0-5 只需 int8 (1 byte)
    'post_count': 'int32'       # 32-bit 整數足夠
})

# 檢查記憶體使用情況
memory_usage = df.memory_usage(deep=True)
print(f"Total memory: {memory_usage.sum() / 1024**2:.2f} MB")
```

#### 批次處理（適用於超大檔案）
```python
# 如果資料量超過 100 萬筆，可使用批次處理
def process_large_csv(file_path, chunksize=50000):
    """批次處理大型 CSV 檔案"""
    chunks = []
    for chunk in pd.read_csv(file_path, chunksize=chunksize):
        # 處理每個批次
        processed_chunk = process_chunk(chunk)
        chunks.append(processed_chunk)
    
    # 合併所有批次
    return pd.concat(chunks, ignore_index=True)

# 或直接寫入資料庫，避免記憶體累積
def process_to_db(file_path, db_conn, chunksize=50000):
    """批次讀取並直接寫入資料庫"""
    for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunksize)):
        chunk.to_sql('tags_raw', db_conn, 
                     if_exists='append', index=False)
        print(f"Processed chunk {i+1}")
```

#### 快速型別檢查
```python
# 快速檢查 CSV 檔案的資料型別
def inspect_csv_dtypes(file_path):
    """檢查 CSV 前 1000 筆的資料型別"""
    for chunk in pd.read_csv(file_path, chunksize=1000):
        print(chunk.dtypes)
        print(f"\nMemory usage:\n{chunk.memory_usage(deep=True)}")
        break  # 只看第一批
```

#### SQLite 批次插入優化
```python
# 使用交易加速插入
import sqlite3

def bulk_insert_optimized(df, db_path, table_name):
    """優化的批次插入"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 開始交易
    cursor.execute('BEGIN TRANSACTION')
    
    try:
        # 批次插入（比逐筆快 10-100 倍）
        df.to_sql(table_name, conn, if_exists='append', 
                  index=False, method='multi')
        
        # 提交交易
        conn.commit()
        print(f"✓ Inserted {len(df)} rows successfully")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error: {e}")
        raise
    finally:
        conn.close()
```

**注意事項:**
- 一般情況（< 100 萬筆）使用基本方法即可
- 只有在遇到效能問題時才需要使用這些優化技巧
- 記憶體優化和批次處理在 Phase 1 可能不需要，但預留以備不時之需

---

## 11. 完成標準 (Completion Criteria)

- [ ] 所有任務組完成
- [ ] `run_pipeline.py` 可成功執行
- [ ] 產出的 `tags.db` 可被 SQLite 工具開啟
- [ ] `tags_final` 表中 `name` 無重複值
- [ ] 主分類覆蓋率 ≥ 90%（針對 `danbooru_cat=0`）
- [ ] 副分類覆蓋率 ≥ 40%（針對 CHARACTER_RELATED 和 ACTION_POSE）
- [ ] 所有單元測試通過，覆蓋率 ≥ 80%
- [ ] 端到端測試通過
- [ ] 效能測試達標（10 萬筆 < 5 分鐘）
- [ ] 分類報告成功產生
- [ ] 所有資料驗證通過
- [ ] 文件完整（README、程式碼註解、分類規則說明）

---

## 12. 後續行動 (Follow-up Actions)

### 12.1 Phase 1 完成後

- 分析未分類標籤，優化關鍵字字典
- 收集使用者回饋，調整分類規則
- 準備 Phase 2 計畫（LLM 增強）

### 12.2 Phase 2 規劃（未來）

- 整合 LLM API 進行語意分類
- 建立 `llm_inference_log` 表
- 對比規則式與 LLM 分類結果
- 建立混合式分類策略（規則優先，LLM 補充）

---

## 13. 變更記錄 (Change Log)

| 版本 | 日期 | 變更內容 | 原因 | 批准人 |
|------|------|----------|------|--------|
| 1.0.0 | 2025-10-08 | 初始版本 - Phase 1 純規則式分類計畫 | 降低初期複雜度，快速建立基準線 | Prompt-Scribe Team |
| 1.1.0 | 2025-10-08 | 添加 Pandas 最佳實踐區段 (10.4) | 整合官方文檔的效能優化技巧 | Prompt-Scribe Team |

---

**計畫結束 (End of Plan)**

**下一步行動：**
1. ✅ 計畫已完成
2. [ ] 開始實作任務組 A（專案基礎設定）
3. [ ] 建立 `/speckit.tasks` 任務清單（可選）
