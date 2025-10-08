# 規格文件：Danbooru 標籤資料管線

**規格編號 (Spec ID):** SPEC-2025-001

**版本 (Version):** 1.0.0

**狀態 (Status):** Draft

**作者 (Author):** Prompt-Scribe Team

**建立日期 (Created):** 2025-10-08

**最後更新 (Last Updated):** 2025-10-08

---

## 憲法符合性檢查 (Constitution Compliance Check)

- [x] 符合「兩階段混合式架構」原則 - **本規格屬於階段一：本地資料管線**
- [x] 符合「LLM 職責分離」原則 - 語意分類使用資料層 LLM，所有推理結果將被記錄
- [x] 符合「規格驅動開發」原則 - 本規格將在批准後才開始實作
- [x] 符合「資料優先」原則 - 資料模型、驗證邏輯已明確定義
- [x] 符合「模組化與可讀性」原則 - 管線設計清晰、職責單一

---

## 1. 概述 (Overview)

### 1.1 目標 (Objective)

建立一個自動化的資料處理管線，讀取多個原始的 **Danbooru** 繪圖標籤 CSV 檔案，將其處理成一個單一、乾淨、經過語意豐富化的 SQLite 資料庫檔案 (`tags.db`)。此檔案將作為整個專案的「黃金資料資產」。

**Danbooru 背景說明：**
Danbooru 是一個知名的圖像標籤平台，使用數字分類系統來組織標籤：
- `0`: 一般標籤 (General) - 描述圖像內容、風格、元素等
- `1`: 藝術家標籤 (Artist)
- `3`: 版權標籤 (Copyright)
- `4`: 角色標籤 (Character)
- `5`: 元標籤 (Meta)

本專案的核心價值在於為 `danbooru_cat = 0` 的一般標籤建立更精細的自訂分類系統。

### 1.2 範圍 (Scope)

**包含 (In Scope):**
- 自動載入 `/data` 目錄下所有 Danbooru 標籤 CSV 檔案
- 資料清理、合併與去重複處理
- 為一般類別標籤進行語意分類（使用資料層 LLM）
- 產出結構化的 SQLite 資料庫 (`tags.db`)
- 完整的資料驗證與品質保證機制
- LLM 推理結果的完整記錄

**不包含 (Out of Scope):**
- 圖像檔案的處理（僅處理標籤文字資料）
- 與 Danbooru API 的即時同步
- Web UI 或互動式介面（本階段為純資料處理）
- 雲端部署（屬於階段二）

### 1.3 架構階段定位 (Architecture Stage)

- [x] 階段一：本地資料管線
- [ ] 階段二：雲端應用後端
- [ ] 跨階段（需說明如何解耦）

**說明：** 本規格完全屬於階段一，所有處理在本地完成，產出可攜式的 SQLite 檔案。

---

## 2. 需求 (Requirements)

### 2.1 功能需求 (Functional Requirements)

| ID | 需求描述 | 優先級 | 驗收標準 |
|----|----------|--------|----------|
| FR-01 | 系統能讀取 `/data` 目錄下所有 `.csv` 檔案 | High | 所有 CSV 檔案被成功載入，無遺漏 |
| FR-02 | 系統能處理 CSV 欄位不一致的情況 | High | 不同欄位結構的 CSV 都能被正確解析 |
| FR-03 | 系統將原始資料載入臨時表 `tags_raw` | High | `tags_raw` 表包含所有原始記錄 |
| FR-04 | 系統對 `name` 相同的標籤進行合併去重 | High | 最終表中 `name` 欄位無重複值 |
| FR-05 | 系統對數值欄位（如 `post_count`）進行聚合 | Medium | 合併後的 `post_count` 為所有來源的總和 |
| FR-06 | 系統為 `danbooru_cat=0` 的標籤生成 `custom_cat` | High | 顯著比例的一般標籤有自訂分類 |
| FR-07 | 系統產出 `/output/tags.db` SQLite 檔案 | High | 檔案成功建立且可被 SQLite 工具開啟 |
| FR-08 | 最終表 `tags_final` 包含所有必要欄位 | High | Schema 符合定義（見下方資料模型） |
| FR-09 | 所有 LLM 推理結果被完整記錄 | High | `llm_inference_log` 表包含所有 API 呼叫記錄 |

### 2.2 非功能需求 (Non-Functional Requirements)

| ID | 類別 | 需求描述 | 標準 |
|----|------|----------|------|
| NFR-01 | 效能 (Performance) | 處理 10 萬筆標籤資料 | < 30 分鐘（不含 LLM API 呼叫） |
| NFR-02 | 效能 (Performance) | LLM API 呼叫效率 | 支援批次處理，含重試機制 |
| NFR-03 | 可靠性 (Reliability) | 資料完整性 | 無資料遺失，所有輸入記錄可追溯 |
| NFR-04 | 可靠性 (Reliability) | 錯誤處理 | 處理失敗時保留錯誤日誌與部分結果 |
| NFR-05 | 可維護性 (Maintainability) | 程式碼模組化 | 每個處理步驟為獨立函式/類別 |
| NFR-06 | 可維護性 (Maintainability) | 日誌記錄 | 詳細的處理日誌，包含每階段統計 |
| NFR-07 | 可擴展性 (Scalability) | 支援新欄位 | 可輕鬆新增欄位而不破壞現有流程 |

---

## 3. 資料模型 (Data Model)

### 3.1 資料結構

#### 3.1.1 輸入資料格式（CSV）

**預期的 CSV 欄位（可能因來源而異）：**
```python
# 標準欄位
name: str           # 標籤名稱（必須）
category: int       # Danbooru 分類 ID（0-5）
post_count: int     # 使用此標籤的貼文數量
```

#### 3.1.2 原始資料表 (tags_raw)

```sql
CREATE TABLE tags_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,           -- 來源檔案名稱
    name TEXT NOT NULL,                  -- 標籤名稱
    danbooru_cat INTEGER,                -- Danbooru 原始分類
    post_count INTEGER DEFAULT 0,        -- 使用次數
    raw_data TEXT,                       -- 原始 JSON（保留完整記錄）
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tags_raw_name ON tags_raw(name);
CREATE INDEX idx_tags_raw_cat ON tags_raw(danbooru_cat);
```

#### 3.1.3 最終資料表 (tags_final)

**設計理念：階段性副分類架構**

採用「主分類 + 副分類」的階層式設計：
- **主分類（必填）**：9 個頂層類別，使用規則分類，覆蓋率目標 ≥ 90%
- **副分類（可選）**：針對高價值主分類添加細分，階段性實作

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TagFinal:
    """最終標籤資料模型"""
    id: int                              # 唯一識別碼
    name: str                            # 標籤名稱（唯一）
    danbooru_cat: int                    # Danbooru 原始分類 (0-5)
    
    # 階層式分類欄位
    main_category: str                   # 主分類（必填，9 選 1）
    sub_category: Optional[str]          # 副分類（可選，階段性添加）
    
    # 其他欄位
    post_count: int                      # 合併後的總使用次數
    source_count: int                    # 來源檔案數量
    name_zh: Optional[str]               # 中文名稱（可選，未來使用）
    created_at: datetime                 # 建立時間
    updated_at: datetime                 # 最後更新時間
```

**主分類列表（9 個）：**

```python
MAIN_CATEGORIES = {
    # 內容維度
    'CHARACTER_RELATED': '人物相關',
    'OBJECTS': '物件道具',
    'ENVIRONMENT': '場景環境',
    
    # 表現維度
    'COMPOSITION': '構圖技法',
    'VISUAL_EFFECTS': '視覺效果',
    'ART_STYLE': '藝術風格',
    'ACTION_POSE': '動作姿態',
    
    # 元資訊維度
    'QUALITY': '品質等級',
    'TECHNICAL': '技術規格',
}
```

**階段 1 副分類（僅針對高價值主分類）：**

```python
# CHARACTER_RELATED 的副分類（優先實作）
CHARACTER_RELATED_SUB = {
    'CLOTHING': '服裝',           # 優先級：高
    'HAIR': '頭髮',               # 優先級：高
    'CHARACTER_COUNT': '角色數量', # 優先級：中
    'BODY_FEATURES': '身體特徵',   # 優先級：低（可選）
}

# ACTION_POSE 的副分類（解決語意混雜）
ACTION_POSE_SUB = {
    'POSE': '姿勢',        # sitting, standing
    'EXPRESSION': '表情',  # smile, blush
}

# 其他主分類暫時不添加副分類，按需擴展
```

**分類示例：**

```python
# 完整副分類
{
    'name': 'school_uniform',
    'main_category': 'CHARACTER_RELATED',
    'sub_category': 'CLOTHING'
}

# 只有主分類
{
    'name': 'indoors',
    'main_category': 'ENVIRONMENT',
    'sub_category': None
}

# 表情分類
{
    'name': 'smile',
    'main_category': 'ACTION_POSE',
    'sub_category': 'EXPRESSION'
}
```

**SQL Schema:**
```sql
CREATE TABLE tags_final (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    danbooru_cat INTEGER NOT NULL,
    
    -- 階層式分類欄位
    main_category TEXT NOT NULL,         -- 主分類（必填）
    sub_category TEXT,                   -- 副分類（可選）
    
    -- 其他欄位
    post_count INTEGER DEFAULT 0,
    source_count INTEGER DEFAULT 1,
    name_zh TEXT,                        -- 中文名稱（可選）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 約束
    CHECK (danbooru_cat BETWEEN 0 AND 5),
    CHECK (post_count >= 0),
    CHECK (source_count >= 1)
);

-- 索引設計
CREATE UNIQUE INDEX idx_tags_final_name ON tags_final(name);
CREATE INDEX idx_tags_final_danbooru_cat ON tags_final(danbooru_cat);
CREATE INDEX idx_tags_final_main_cat ON tags_final(main_category);
CREATE INDEX idx_tags_final_sub_cat ON tags_final(sub_category);
CREATE INDEX idx_tags_final_main_sub ON tags_final(main_category, sub_category);

-- 全文搜尋索引
CREATE VIRTUAL TABLE tags_search USING fts5(
    name, 
    main_category,
    sub_category,
    content='tags_final',
    content_rowid='id'
);
```

#### 3.1.4 LLM 推理記錄表 (llm_inference_log)

```sql
CREATE TABLE llm_inference_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL,              -- 被分類的標籤名稱
    model TEXT NOT NULL,                 -- 使用的 LLM 模型
    provider TEXT NOT NULL,              -- 服務提供者 (openai/anthropic)
    prompt_template TEXT NOT NULL,       -- 使用的 prompt 模板
    input_hash TEXT NOT NULL,            -- 輸入內容的 SHA256
    output_category TEXT,                -- LLM 回傳的分類結果
    confidence REAL,                     -- 信心分數（如有）
    raw_response TEXT,                   -- 完整的 API 回應（JSON）
    tokens_used INTEGER,                 -- 使用的 token 數量
    api_cost REAL,                       -- API 呼叫成本（USD）
    latency_ms INTEGER,                  -- 回應延遲（毫秒）
    status TEXT NOT NULL,                -- success/failed/timeout
    error_message TEXT,                  -- 錯誤訊息（如有）
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (tag_name) REFERENCES tags_final(name)
);

CREATE INDEX idx_llm_log_tag ON llm_inference_log(tag_name);
CREATE INDEX idx_llm_log_model ON llm_inference_log(model);
CREATE INDEX idx_llm_log_status ON llm_inference_log(status);
```

### 3.2 資料流向

```
[/data/*.csv] 
    ↓ (載入)
[tags_raw 表] 
    ↓ (合併去重)
[tags_intermediate 表] 
    ↓ (LLM 語意分類)
[tags_final 表] + [llm_inference_log 表]
    ↓ (匯出)
[/output/tags.db]
```

**詳細流程：**
1. **載入階段：** 讀取所有 CSV → 插入 `tags_raw`
2. **合併階段：** `tags_raw` → 去重聚合 → `tags_intermediate`
3. **豐富化階段：** 對 `danbooru_cat=0` 的標籤呼叫 LLM → 更新 `custom_cat`
4. **記錄階段：** 所有 LLM 呼叫 → 記錄至 `llm_inference_log`
5. **最終化階段：** `tags_intermediate` → 驗證 → `tags_final`
6. **匯出階段：** 整個資料庫 → `/output/tags.db`

### 3.3 資料驗證規則

#### 3.3.1 輸入驗證

```python
from pydantic import BaseModel, Field, validator

class TagInput(BaseModel):
    """CSV 輸入資料驗證"""
    name: str = Field(..., min_length=1, max_length=200)
    category: int = Field(..., ge=0, le=5)  # 0-5
    post_count: int = Field(default=0, ge=0)
    
    @validator('name')
    def name_must_be_valid(cls, v):
        v = v.strip().lower()  # 標準化
        if not v:
            raise ValueError('標籤名稱不能為空')
        if len(v) < 1:
            raise ValueError('標籤名稱太短')
        return v
    
    @validator('category')
    def category_must_be_valid(cls, v):
        if v not in [0, 1, 3, 4, 5]:
            raise ValueError(f'無效的 Danbooru 分類: {v}')
        return v
```

#### 3.3.2 輸出驗證

```python
class TagFinalValidator:
    """最終資料驗證"""
    
    @staticmethod
    def validate_uniqueness(db_path: str) -> bool:
        """驗證 name 欄位的唯一性"""
        # SELECT COUNT(*), COUNT(DISTINCT name) FROM tags_final
        # 兩者必須相等
        pass
    
    @staticmethod
    def validate_custom_cat_coverage(db_path: str, min_ratio: float = 0.6) -> bool:
        """驗證 custom_cat 的覆蓋率"""
        # 對於 danbooru_cat=0 的標籤
        # 至少 60% 應該有 custom_cat 值
        pass
    
    @staticmethod
    def validate_data_integrity(db_path: str) -> bool:
        """驗證資料完整性"""
        # 所有 foreign key 都有效
        # 所有 CHECK 約束都滿足
        # 沒有 NULL 在 NOT NULL 欄位
        pass
```

#### 3.3.3 一致性檢查

- **來源追溯：** 每個 `tags_final` 記錄的 `source_count` 應該與 `tags_raw` 中該 `name` 的記錄數一致
- **數量守恆：** `tags_final` 的總 `post_count` 應該等於所有 `tags_raw` 記錄的 `post_count` 總和
- **LLM 記錄完整：** 每個有 `custom_cat` 的標籤應該在 `llm_inference_log` 有對應記錄

---

## 4. 介面定義 (Interface Definition)

### 4.1 主要函式簽名

```python
from pathlib import Path
from typing import List, Dict, Optional

class DanbooruTagsPipeline:
    """Danbooru 標籤資料管線主類別"""
    
    def __init__(
        self,
        data_dir: Path,
        output_dir: Path,
        enable_llm: bool = True,
        llm_provider: str = "openai"
    ):
        """
        初始化管線
        
        Args:
            data_dir: 輸入 CSV 檔案目錄
            output_dir: 輸出資料庫目錄
            enable_llm: 是否啟用 LLM 語意分類
            llm_provider: LLM 服務提供者 (openai/anthropic)
        """
        pass
    
    def run(self) -> Dict[str, any]:
        """
        執行完整管線
        
        Returns:
            處理結果統計資訊
            {
                'total_files_processed': int,
                'total_raw_records': int,
                'total_unique_tags': int,
                'general_tags_count': int,
                'custom_cat_coverage': float,
                'llm_api_calls': int,
                'processing_time_seconds': float
            }
        
        Raises:
            PipelineError: 管線執行失敗
        """
        pass
    
    def load_csv_files(self) -> int:
        """
        載入所有 CSV 檔案到 tags_raw
        
        Returns:
            載入的記錄總數
        """
        pass
    
    def merge_and_deduplicate(self) -> int:
        """
        合併與去重複處理
        
        Returns:
            唯一標籤數量
        """
        pass
    
    def enrich_with_llm(self, batch_size: int = 50) -> Dict[str, int]:
        """
        使用 LLM 進行語意分類
        
        Args:
            batch_size: 批次處理大小
        
        Returns:
            分類統計 {'成功': int, '失敗': int, '跳過': int}
        """
        pass
    
    def validate_output(self) -> List[str]:
        """
        驗證最終輸出
        
        Returns:
            驗證錯誤列表（空列表表示通過）
        """
        pass
```

### 4.2 資料驗證介面

```python
class DataValidator:
    """資料驗證工具類別"""
    
    @staticmethod
    def validate_csv_file(file_path: Path) -> tuple[bool, List[str]]:
        """
        驗證單個 CSV 檔案
        
        Args:
            file_path: CSV 檔案路徑
        
        Returns:
            (是否有效, 錯誤訊息列表)
        """
        pass
    
    @staticmethod
    def validate_tag_record(record: Dict) -> TagInput:
        """
        驗證單筆標籤記錄
        
        Args:
            record: 原始記錄字典
        
        Returns:
            驗證後的 TagInput 物件
        
        Raises:
            ValidationError: 驗證失敗
        """
        pass
```

### 4.3 LLM 整合介面

```python
from abc import ABC, abstractmethod

class LLMClassifier(ABC):
    """LLM 分類器抽象基礎類別"""
    
    @abstractmethod
    def classify_tag(self, tag_name: str) -> tuple[str, float]:
        """
        分類單個標籤
        
        Args:
            tag_name: 標籤名稱
        
        Returns:
            (分類結果, 信心分數)
        """
        pass
    
    @abstractmethod
    def classify_batch(self, tag_names: List[str]) -> List[tuple[str, float]]:
        """
        批次分類標籤
        
        Args:
            tag_names: 標籤名稱列表
        
        Returns:
            分類結果列表
        """
        pass

class OpenAIClassifier(LLMClassifier):
    """OpenAI 分類器實作"""
    pass

class AnthropicClassifier(LLMClassifier):
    """Anthropic 分類器實作"""
    pass
```

### 4.4 相依性 (Dependencies)

**內部相依：**
- 無（這是第一個模組）

**外部相依：**
```txt
# 核心依賴
python>=3.11
pydantic>=2.0.0              # 資料驗證
pandas>=2.0.0                # CSV 處理
sqlite-utils>=3.35.0         # SQLite 操作
loguru>=0.7.0                # 日誌記錄

# LLM 整合
openai>=1.0.0                # OpenAI API
anthropic>=0.7.0             # Anthropic API

# 工具類
python-dotenv>=1.0.0         # 環境變數
tqdm>=4.65.0                 # 進度條
tenacity>=8.2.0              # 重試機制

# 開發依賴
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.7.0
pylint>=2.17.0
```

---

## 5. LLM 使用聲明 (LLM Usage Declaration)

### 5.1 IDE LLM 使用

- [x] 用於程式碼生成輔助
- [x] 用於文件撰寫輔助
- [x] 用於測試案例生成

**說明：** IDE LLM（如 Cursor）僅用於開發階段的程式碼撰寫輔助，不接觸生產資料。

### 5.2 資料層 LLM 使用

- [x] 使用（必須填寫以下資訊）

**用途：** 為 `danbooru_cat=0` 的一般標籤生成精細的語意分類（`custom_cat` 欄位）

**模型選擇：** 
- 主要：OpenAI GPT-4 Turbo
- 備用：Anthropic Claude 3 Opus

**輸入格式：**
```json
{
  "tag_name": "from_above",
  "danbooru_category": 0,
  "post_count": 15234,
  "context": "Danbooru image tagging system"
}
```

**Prompt 模板：**
```
你是一個 Danbooru 標籤分類專家。請將以下標籤分類到最合適的語意類別中。

標籤名稱: {tag_name}
使用次數: {post_count}

可用的分類類別：
- camera_angle: 鏡頭角度
- lighting: 光影效果
- pose: 姿勢動作
- composition: 構圖元素
- style: 風格描述
- emotion: 情緒表達
- object: 物件道具
- environment: 環境場景
- other: 其他

請只回答類別名稱，不需要額外解釋。如果無法確定，回答 "other"。

分類結果:
```

**輸出格式：**
```json
{
  "category": "camera_angle",
  "confidence": 0.95,
  "reasoning": "This tag describes a camera perspective"
}
```

**記錄機制：**
- 所有 LLM API 呼叫都記錄至 `llm_inference_log` 表
- 記錄內容包括：輸入、輸出、模型、參數、時間戳、成本、狀態
- 使用 SHA256 對輸入進行雜湊以保護隱私同時保持可追溯性

**失敗處理：**
1. **重試機制：** 使用 exponential backoff，最多重試 3 次
2. **降級處理：** 如果主要模型失敗，切換至備用模型
3. **預設值：** 如果所有嘗試都失敗，`custom_cat` 設為 `null`，記錄錯誤
4. **限流處理：** 遇到 rate limit 時，自動暫停並等待
5. **成本控制：** 設定單次執行的最大 API 成本上限

**批次處理策略：**
- 每批次 50 個標籤
- 批次間間隔 1 秒（避免限流）
- 使用 async/await 提升效率
- 支援中斷後從上次進度繼續

---

## 6. 測試策略 (Testing Strategy)

### 6.1 單元測試

**測試覆蓋率目標：** ≥ 80%

**關鍵測試案例：**

1. **CSV 載入測試**
   - 測試標準格式 CSV
   - 測試欄位缺失的 CSV
   - 測試空檔案
   - 測試編碼問題（UTF-8, BIG5）

2. **資料驗證測試**
   - 測試有效資料通過驗證
   - 測試無效 category 被拒絕
   - 測試空字串標籤被拒絕
   - 測試負數 post_count 被拒絕

3. **合併去重測試**
   - 測試相同 name 的記錄被合併
   - 測試 post_count 正確加總
   - 測試 source_count 正確計算

4. **LLM 分類測試（使用 Mock）**
   - Mock LLM API 回應
   - 測試成功分類流程
   - 測試失敗重試機制
   - 測試記錄機制

### 6.2 整合測試

**測試案例：**

1. **端到端測試**
   - 準備測試 CSV 檔案（100 筆記錄）
   - 執行完整管線
   - 驗證 tags.db 產出正確
   - 驗證所有表結構正確

2. **真實 LLM API 測試**
   - 使用少量真實資料（10 筆）
   - 測試 OpenAI API 整合
   - 驗證推理記錄完整性

3. **大資料量測試**
   - 測試 10,000 筆標籤處理
   - 驗證效能符合 NFR-01
   - 驗證記憶體使用合理

### 6.3 資料品質測試

**測試腳本：**

```python
def test_data_quality(db_path: Path):
    """資料品質檢查"""
    
    # 1. 唯一性檢查
    assert check_name_uniqueness(db_path)
    
    # 2. 完整性檢查
    assert check_no_missing_required_fields(db_path)
    
    # 3. 一致性檢查
    assert check_post_count_consistency(db_path)
    
    # 4. 覆蓋率檢查
    coverage = check_custom_cat_coverage(db_path)
    assert coverage >= 0.6  # 至少 60%
    
    # 5. LLM 記錄完整性
    assert check_llm_log_completeness(db_path)
```

---

## 7. 實作計畫 (Implementation Plan)

### 7.1 階段劃分

| 階段 | 任務 | 預估時間 | 優先級 |
|------|------|----------|--------|
| 階段 1 | 基礎架構設定（專案結構、依賴安裝） | 4 小時 | High |
| 階段 2 | CSV 載入模組 | 8 小時 | High |
| 階段 3 | 資料驗證模組 | 6 小時 | High |
| 階段 4 | 合併去重模組 | 8 小時 | High |
| 階段 5 | LLM 整合模組（含記錄機制） | 12 小時 | High |
| 階段 6 | 資料品質驗證模組 | 6 小時 | High |
| 階段 7 | 主管線整合 | 6 小時 | High |
| 階段 8 | 測試撰寫 | 10 小時 | High |
| 階段 9 | 文件與範例 | 4 小時 | Medium |
| **總計** | | **64 小時** | |

### 7.2 風險與對策

| 風險 | 可能性 | 影響程度 | 對策 |
|------|--------|----------|------|
| CSV 格式不一致導致載入失敗 | High | Medium | 實作彈性的欄位映射機制 |
| LLM API 限流影響處理速度 | Medium | High | 實作批次處理與自動限速 |
| LLM API 成本超出預算 | Medium | Medium | 設定成本上限，支援本地模型 |
| 大資料量造成記憶體不足 | Low | High | 使用串流處理，分批載入 |
| 資料品質問題（髒資料） | Medium | Medium | 強化驗證邏輯，記錄問題資料 |

---

## 8. 驗收標準 (Acceptance Criteria)

- [x] 執行完畢後，`/output/tags.db` 檔案被成功建立
- [x] `tags.db` 可被 SQLite 工具正常開啟
- [x] `tags.db` 中存在 `tags_final` 資料表，且 schema 符合定義
- [x] `tags_final` 資料表中的 `name` 欄位沒有任何重複值
- [x] 所有 `danbooru_cat` 值都在 0-5 範圍內
- [x] `danbooru_cat=0` 的標籤中，至少 60% 有非空的 `custom_cat` 值
- [x] `llm_inference_log` 表存在且包含所有 LLM API 呼叫記錄
- [x] 每個有 `custom_cat` 的標籤在 `llm_inference_log` 都有對應記錄
- [x] 所有單元測試通過，覆蓋率 ≥ 80%
- [x] 整合測試通過（包含真實 LLM API 測試）
- [x] 處理 10 萬筆資料在 30 分鐘內完成（不含 LLM）
- [x] 程式碼通過 pylint 檢查，無重大警告
- [x] 文件完整（README、API 文件、使用範例）

---

## 9. 變更記錄 (Change Log)

| 版本 | 日期 | 變更內容 | 作者 |
|------|------|----------|------|
| 1.0.0 | 2025-10-08 | 初始版本 - Danbooru 標籤資料管線規格 | Prompt-Scribe Team |

---

## 10. 參考資料 (References)

### 10.1 外部參考
- [Danbooru 標籤系統文件](https://danbooru.donmai.us/wiki_pages/howto:tag)
- [Danbooru 標籤分類說明](https://danbooru.donmai.us/wiki_pages/howto:tag#tag-types)
- [OpenAI API 文件](https://platform.openai.com/docs)
- [Anthropic API 文件](https://docs.anthropic.com/)

### 10.2 內部參考
- [專案開發憲法](../../.specify/memory/constitution.md)
- [階段一 README](../../stage1/README.md)

### 10.3 相關決策
- **ADR-001**：選擇 SQLite 作為階段一的資料庫（可攜性、無依賴）
- **ADR-002**：選擇 GPT-4 Turbo 作為主要 LLM（平衡成本與準確度）
- **ADR-003**：使用批次處理降低 API 呼叫次數

---

**規格結束 (End of Specification)**

**下一步行動：**
1. 規格審查與批准
2. 建立對應的開發計畫 (`/speckit.plan`)
3. 建立詳細任務清單 (`/speckit.tasks`)
4. 開始實作

