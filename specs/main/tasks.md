# 任務清單：Danbooru 標籤資料管線 - Phase 1

**任務清單編號 (Tasks ID):** TASKS-2025-001-PHASE1

**關聯計畫 (Related Plan):** PLAN-2025-001-PHASE1

**關聯規格 (Related Specs):** SPEC-2025-001

**負責人 (Owner):** AI Agent (Cursor)

**建立日期 (Created):** 2025-10-08

**最後更新 (Last Updated):** 2025-10-08

---

## 憲法符合性提醒 (Constitution Compliance Reminder)

執行任務時，請持續檢查：
- ✅ 任務屬於階段一：本地資料管線
- ✅ Phase 1 不使用資料層 LLM（僅使用規則式分類）
- ✅ 實作基於已審核的規格（SPEC-2025-001）
- ✅ 資料品質任務優先處理（資料優先原則）
- ✅ 程式碼保持簡單清晰（函式式風格，避免過度設計）

---

## 任務狀態標籤說明 (Task Status Labels)

- **[ ]** 未開始 (Not Started)
- **[>]** 進行中 (In Progress)
- **[✓]** 已完成 (Completed)
- **[!]** 受阻 (Blocked)
- **[?]** 待確認 (Pending Clarification)
- **[-]** 已取消 (Cancelled)
- **[P]** 可並行執行 (Parallelizable)

---

## 實作策略 (Implementation Strategy)

### MVP 優先原則
本任務清單按照「可獨立交付」原則組織，每個 Phase 完成後都能產出可驗證的增量價值：
- **Phase 1 (Setup)**: 建立專案基礎，完成後可執行基本腳本
- **Phase 2 (Foundation)**: 建立核心分類邏輯，完成後可手動測試分類功能
- **Phase 3-6**: 每個 Phase 對應一個完整的功能模組，獨立可測試
- **Phase 7 (Integration)**: 整合所有模組，產出完整管線

### 建議 MVP 範圍
- **最小可行產品 (MVP)**: Phase 1 + Phase 2 + Phase 3
  - 可完成：載入單個 CSV → 套用規則分類 → 顯示結果
  - 交付時間：約 1-2 天

---

## Phase 1: 專案基礎設定 (Project Setup)

**目標：** 建立專案結構與配置，確保開發環境就緒

**獨立測試標準：**
- [ ] 執行 `python run_pipeline.py --help` 顯示幫助訊息
- [ ] 配置檔案可被正確讀取
- [ ] 目錄結構符合設計

---

### T001: 建立專案目錄結構 [P]

- **描述：** 建立 Phase 1 所需的完整目錄結構
- **規格依據：** PLAN-2025-001-PHASE1, Section 10.1
- **優先級：** High
- **預估時間：** 0.5 小時
- **相依任務：** 無
- **驗收標準：**
  - `stage1/run_pipeline.py` 檔案存在（空白或骨架）
  - `stage1/config.py` 檔案存在
  - `stage1/data_rules.py` 檔案存在
  - `stage1/src/` 目錄存在
  - `stage1/output/` 目錄存在
  - `stage1/tests/` 目錄存在
- **技術細節：**
  - 主要檔案：`stage1/` 目錄下所有結構
  - 語言：Python 3.11+
- **備註：** 保持簡單的扁平結構，避免過度設計

---

### T002: 建立配置檔案 (config.py) [P]

- **描述：** 定義所有可配置的參數，包括路徑、資料庫名稱等
- **規格依據：** PLAN-2025-001-PHASE1, Task A2
- **優先級：** High
- **預估時間：** 0.5 小時
- **相依任務：** T001
- **驗收標準：**
  - 定義 `DATA_DIR`（輸入資料目錄）
  - 定義 `OUTPUT_DIR`（輸出目錄）
  - 定義 `DB_PATH`（資料庫完整路徑）
  - 定義 `LOG_LEVEL`（日誌層級）
  - 所有路徑使用 `pathlib.Path`
  - 可被其他模組正確 import
- **技術細節：**
  - 主要檔案：`stage1/config.py`
  - 使用 pathlib 而非字串路徑
  - 範例內容：
    ```python
    from pathlib import Path
    
    # 專案根目錄
    PROJECT_ROOT = Path(__file__).parent
    
    # 資料目錄
    DATA_DIR = PROJECT_ROOT / 'data' / 'raw'
    OUTPUT_DIR = PROJECT_ROOT / 'output'
    
    # 資料庫路徑
    DB_PATH = OUTPUT_DIR / 'tags.db'
    
    # 日誌設定
    LOG_LEVEL = 'INFO'
    ```
- **備註：** 確保所有路徑在 Windows 和 Linux 都能正常運作

---

### T003: 設定日誌系統 [P]

- **描述：** 建立統一的日誌記錄機制
- **規格依據：** SPEC-2025-001, NFR-06
- **優先級：** Medium
- **預估時間：** 1 小時
- **相依任務：** T002
- **驗收標準：**
  - 使用 Python 內建 `logging` 模組
  - 日誌同時輸出到控制台和檔案
  - 日誌格式包含：時間戳、層級、訊息
  - 支援不同層級（DEBUG, INFO, WARNING, ERROR）
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py` 或單獨的 `logger.py`
  - 日誌檔案：`stage1/output/pipeline.log`
  - 範例配置：
    ```python
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('output/pipeline.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    ```
- **備註：** 避免使用第三方日誌套件，保持簡單

---

## Phase 2: 分類規則建立 (Classification Rules - Foundation)

**目標：** 建立規則式分類的核心邏輯與關鍵字字典

**獨立測試標準：**
- [ ] 執行 `python -c "from data_rules import classify_tag; print(classify_tag('school_uniform'))"` 返回正確分類
- [ ] 至少 20 個測試案例通過

**⚠️ 阻塞性說明：** 此 Phase 必須完成後，後續所有標籤分類功能才能運作

---

### T004: 建立主分類關鍵字字典

- **描述：** 定義 9 個主分類的關鍵字列表
- **規格依據：** PLAN-2025-001-PHASE1, Section 9, Task B1
- **優先級：** High
- **預估時間：** 4 小時
- **相依任務：** T001
- **驗收標準：**
  - 定義所有 9 個主分類的關鍵字
  - 每個分類至少包含 20 個關鍵字
  - 關鍵字經過人工審查與測試
  - 關鍵字列表有適當註解說明
- **技術細節：**
  - 主要檔案：`stage1/data_rules.py` 或 `stage1/src/classifier/categories.py`
  - 資料結構：
    ```python
    MAIN_CATEGORY_RULES = {
        'QUALITY': [
            'best_quality', 'masterpiece', 'high_quality',
            'worst_quality', 'low_quality', 'normal_quality',
            'highres', 'absurdres', 'incredibly_absurdres'
        ],
        'TECHNICAL': [
            'monochrome', 'greyscale', 'grayscale',
            'comic', 'animated', 'animation',
            'pixel_art', 'sketch', 'lineart',
            'censored', 'uncensored', 'mosaic_censoring'
        ],
        'ART_STYLE': [
            'anime', 'anime_style', 'manga', 'manga_style',
            'realistic', 'photorealistic', 'semi-realistic',
            'chibi', 'watercolor', 'oil_painting',
            'traditional_media', '3d', 'cg'
        ],
        'COMPOSITION': [
            'from_above', 'from_below', 'from_side',
            'close-up', 'close_up', 'wide_shot',
            'portrait', 'full_body', 'upper_body',
            'dutch_angle', 'pov', 'first-person'
        ],
        'VISUAL_EFFECTS': [
            'lighting', 'bloom', 'lens_flare',
            'motion_blur', 'depth_of_field', 'bokeh',
            'chromatic_aberration', 'backlight', 'rim_lighting'
        ],
        'CHARACTER_RELATED': [
            'girl', 'boy', 'woman', 'man',
            '1girl', '2girls', '3girls', 'multiple_girls',
            '1boy', '2boys', 'multiple_boys', 'solo',
            'hair', 'eyes', 'face', 'body',
            'dress', 'shirt', 'skirt', 'uniform'
        ],
        'ACTION_POSE': [
            'sitting', 'standing', 'lying', 'kneeling',
            'walking', 'running', 'jumping',
            'smile', 'blush', 'angry', 'sad',
            'looking_at_viewer', 'hand_up', 'arms_behind'
        ],
        'OBJECTS': [
            'weapon', 'sword', 'gun', 'knife',
            'flower', 'rose', 'book', 'phone',
            'computer', 'cup', 'chair', 'table'
        ],
        'ENVIRONMENT': [
            'indoors', 'outdoors', 'inside', 'outside',
            'sky', 'cloud', 'tree', 'building',
            'street', 'beach', 'mountain', 'forest'
        ]
    }
    ```
- **備註：** 
  - 關鍵字選擇參考 `stage1/data/raw/` 中的實際標籤
  - 優先覆蓋高頻標籤
  - 考慮同義詞和常見變體（如 `close-up` vs `close_up`）

---

### T005: 建立副分類關鍵字字典

- **描述：** 為 CHARACTER_RELATED 和 ACTION_POSE 定義副分類關鍵字
- **規格依據：** PLAN-2025-001-PHASE1, Section 9.2, Task B1
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T004
- **驗收標準：**
  - CHARACTER_RELATED 包含 3 個副分類（CLOTHING, HAIR, CHARACTER_COUNT）
  - ACTION_POSE 包含 2 個副分類（POSE, EXPRESSION）
  - 每個副分類至少包含 15 個關鍵字
- **技術細節：**
  - 主要檔案：`stage1/data_rules.py` 或 `stage1/src/classifier/categories.py`
  - 資料結構：
    ```python
    SUB_CATEGORY_RULES = {
        'CHARACTER_RELATED': {
            'CLOTHING': [
                'dress', 'shirt', 'skirt', 'uniform',
                'school_uniform', 'jacket', 'coat',
                'pants', 'shorts', 'swimsuit', 'bikini',
                'kimono', 'yukata', 'maid', 'apron'
            ],
            'HAIR': [
                'hair', 'ponytail', 'twintails', 'braid',
                'short_hair', 'long_hair', 'very_long_hair',
                'bangs', 'hairband', 'hair_ornament',
                'blonde_hair', 'black_hair', 'brown_hair'
            ],
            'CHARACTER_COUNT': [
                'solo', '1girl', '1boy',
                '2girls', '2boys', '3girls', '3boys',
                'multiple_girls', 'multiple_boys',
                '4girls', '5girls', '6+girls'
            ]
        },
        'ACTION_POSE': {
            'POSE': [
                'sitting', 'standing', 'lying', 'kneeling',
                'crouching', 'leaning', 'stretching',
                'walking', 'running', 'jumping',
                'arms_up', 'arms_behind', 'hand_on_hip'
            ],
            'EXPRESSION': [
                'smile', 'blush', 'angry', 'sad',
                'surprised', 'crying', 'laughing',
                'embarrassed', 'smirk', 'serious',
                ':)', ':d', ';)', 'open_mouth'
            ]
        }
    }
    ```
- **備註：** 副分類的關鍵字應該是主分類關鍵字的子集或相關詞

---

### T006: 實作分類函式

- **描述：** 實作核心的 `classify_tag()` 函式
- **規格依據：** PLAN-2025-001-PHASE1, Task B2
- **優先級：** High
- **預估時間：** 3 小時
- **相依任務：** T004, T005
- **驗收標準：**
  - `classify_tag(tag_name: str) -> tuple[str | None, str | None]` 函式正常運作
  - 支援部分字串匹配（`'uniform' in 'school_uniform'`）
  - 支援不區分大小寫
  - 按照優先級順序匹配（QUALITY → TECHNICAL → ... → ENVIRONMENT）
  - 未匹配時返回 `(None, None)`
  - 至少 50 個測試案例通過
- **技術細節：**
  - 主要檔案：`stage1/data_rules.py` 或 `stage1/src/classifier/rule_classifier.py`
  - 函式簽名：
    ```python
    def classify_tag(tag_name: str) -> tuple[Optional[str], Optional[str]]:
        """
        根據規則對標籤進行分類
        
        Args:
            tag_name: 標籤名稱
        
        Returns:
            (main_category, sub_category) 的元組
            未分類時返回 (None, None)
        
        Example:
            >>> classify_tag('school_uniform')
            ('CHARACTER_RELATED', 'CLOTHING')
            
            >>> classify_tag('from_above')
            ('COMPOSITION', None)
            
            >>> classify_tag('unknown_tag_xyz')
            (None, None)
        """
        tag_lower = tag_name.lower().strip()
        
        # 依優先級順序遍歷主分類
        priority_order = [
            'QUALITY', 'TECHNICAL', 'ART_STYLE', 
            'COMPOSITION', 'VISUAL_EFFECTS',
            'CHARACTER_RELATED', 'ACTION_POSE', 
            'OBJECTS', 'ENVIRONMENT'
        ]
        
        for main_cat in priority_order:
            keywords = MAIN_CATEGORY_RULES[main_cat]
            if any(kw in tag_lower for kw in keywords):
                # 找到主分類，繼續匹配副分類
                sub_cat = None
                if main_cat in SUB_CATEGORY_RULES:
                    for sub_cat_name, sub_keywords in SUB_CATEGORY_RULES[main_cat].items():
                        if any(kw in tag_lower for kw in sub_keywords):
                            sub_cat = sub_cat_name
                            break
                return (main_cat, sub_cat)
        
        # 未匹配任何分類
        return (None, None)
    ```
- **備註：** 
  - 優先級順序非常重要，不要改變
  - 考慮效能：避免使用正規表達式

---

### T007: 撰寫分類函式單元測試

- **描述：** 為 `classify_tag()` 撰寫完整的單元測試
- **規格依據：** PLAN-2025-001-PHASE1, Task B2
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T006
- **驗收標準：**
  - 至少 100 個測試案例
  - 覆蓋所有 9 個主分類
  - 覆蓋所有 5 個副分類
  - 覆蓋邊界情況（空字串、特殊字元、未匹配）
  - 所有測試通過
- **技術細節：**
  - 測試檔案：`stage1/tests/test_classifier.py` 或 `stage1/test_classifier.py`
  - 測試框架：Python 內建 `unittest` 或 `pytest`
  - 範例測試：
    ```python
    import unittest
    from data_rules import classify_tag
    
    class TestClassifier(unittest.TestCase):
        
        def test_quality_tags(self):
            self.assertEqual(classify_tag('masterpiece'), ('QUALITY', None))
            self.assertEqual(classify_tag('best_quality'), ('QUALITY', None))
        
        def test_character_clothing(self):
            self.assertEqual(classify_tag('school_uniform'), ('CHARACTER_RELATED', 'CLOTHING'))
            self.assertEqual(classify_tag('dress'), ('CHARACTER_RELATED', 'CLOTHING'))
        
        def test_character_hair(self):
            self.assertEqual(classify_tag('long_hair'), ('CHARACTER_RELATED', 'HAIR'))
            self.assertEqual(classify_tag('ponytail'), ('CHARACTER_RELATED', 'HAIR'))
        
        def test_character_count(self):
            self.assertEqual(classify_tag('1girl'), ('CHARACTER_RELATED', 'CHARACTER_COUNT'))
            self.assertEqual(classify_tag('multiple_girls'), ('CHARACTER_RELATED', 'CHARACTER_COUNT'))
        
        def test_action_pose(self):
            self.assertEqual(classify_tag('sitting'), ('ACTION_POSE', 'POSE'))
            self.assertEqual(classify_tag('standing'), ('ACTION_POSE', 'POSE'))
        
        def test_action_expression(self):
            self.assertEqual(classify_tag('smile'), ('ACTION_POSE', 'EXPRESSION'))
            self.assertEqual(classify_tag('blush'), ('ACTION_POSE', 'EXPRESSION'))
        
        def test_composition(self):
            self.assertEqual(classify_tag('from_above'), ('COMPOSITION', None))
            self.assertEqual(classify_tag('close-up'), ('COMPOSITION', None))
        
        def test_environment(self):
            self.assertEqual(classify_tag('indoors'), ('ENVIRONMENT', None))
            self.assertEqual(classify_tag('outdoors'), ('ENVIRONMENT', None))
        
        def test_unmatched(self):
            self.assertEqual(classify_tag('unknown_tag_xyz'), (None, None))
            self.assertEqual(classify_tag(''), (None, None))
        
        def test_case_insensitive(self):
            self.assertEqual(classify_tag('MASTERPIECE'), ('QUALITY', None))
            self.assertEqual(classify_tag('School_Uniform'), ('CHARACTER_RELATED', 'CLOTHING'))
    
    if __name__ == '__main__':
        unittest.main()
    ```
- **備註：** 
  - 測試案例可參考 `stage1/data/raw/` 中的實際標籤
  - 確保測試覆蓋真實使用情境

---

## Phase 3: CSV 資料載入模組 (CSV Loading Module)

**目標：** 實作 CSV 檔案的載入、驗證與 `tags_raw` 表建立

**獨立測試標準：**
- [ ] 執行載入模組後，`tags.db` 中存在 `tags_raw` 表
- [ ] `tags_raw` 表包含所有有效記錄
- [ ] 載入統計資訊正確輸出

**對應用戶故事：** 
- US1: 作為開發者，我需要能夠讀取和驗證所有 CSV 檔案，以便將原始資料載入系統
- 對應 SPEC FR-01, FR-02, FR-03

---

### T008: 實作 CSV 檔案讀取函式

- **描述：** 實作讀取 `/data/raw` 目錄下所有 CSV 檔案的函式
- **規格依據：** SPEC-2025-001, FR-01; PLAN-2025-001-PHASE1, Task C1
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T002
- **驗收標準：**
  - 成功讀取目錄下所有 `.csv` 檔案
  - 處理檔案不存在的情況（記錄警告）
  - 處理空檔案的情況
  - 記錄每個檔案的載入統計（檔名、記錄數）
  - 返回合併後的 DataFrame
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 函式簽名：
    ```python
    def load_csv_files(data_dir: Path) -> pd.DataFrame:
        """
        載入所有 CSV 檔案到 DataFrame
        
        Args:
            data_dir: 資料目錄路徑
        
        Returns:
            合併後的 DataFrame
        
        Raises:
            FileNotFoundError: 目錄不存在
        """
        import pandas as pd
        from pathlib import Path
        import logging
        
        logger = logging.getLogger(__name__)
        
        if not data_dir.exists():
            raise FileNotFoundError(f"資料目錄不存在: {data_dir}")
        
        csv_files = list(data_dir.glob('*.csv'))
        if not csv_files:
            logger.warning(f"目錄中沒有找到 CSV 檔案: {data_dir}")
            return pd.DataFrame()
        
        all_data = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8')
                df['source_file'] = csv_file.name
                all_data.append(df)
                logger.info(f"✓ 載入 {csv_file.name}: {len(df)} 筆記錄")
            except Exception as e:
                logger.error(f"✗ 無法載入 {csv_file.name}: {e}")
        
        if not all_data:
            return pd.DataFrame()
        
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"總計載入: {len(combined_df)} 筆記錄（來自 {len(csv_files)} 個檔案）")
        
        return combined_df
    ```
- **備註：** 
  - 考慮編碼問題（UTF-8, BIG5）
  - 大檔案可考慮使用 `chunksize` 參數

---

### T009: 實作欄位標準化函式 [P]

- **描述：** 處理不同 CSV 檔案的欄位名稱不一致問題
- **規格依據：** SPEC-2025-001, FR-02; PLAN-2025-001-PHASE1, Task C1
- **優先級：** High
- **預估時間：** 1 小時
- **相依任務：** T008
- **驗收標準：**
  - 支援欄位映射（`category` → `danbooru_cat`, `count` → `post_count`）
  - 欄位名稱不區分大小寫
  - 缺失欄位自動補充預設值
  - 記錄欄位轉換訊息
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 函式簽名：
    ```python
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        標準化 DataFrame 欄位名稱
        
        Args:
            df: 原始 DataFrame
        
        Returns:
            標準化後的 DataFrame
        """
        # 欄位映射表
        column_map = {
            'category': 'danbooru_cat',
            'count': 'post_count',
            'tag': 'name',
            'tag_name': 'name'
        }
        
        # 轉換為小寫以不區分大小寫
        df.columns = df.columns.str.lower().str.strip()
        
        # 套用映射
        df.rename(columns=column_map, inplace=True)
        
        # 補充缺失欄位
        if 'post_count' not in df.columns:
            df['post_count'] = 0
        
        if 'danbooru_cat' not in df.columns:
            df['danbooru_cat'] = 0  # 預設為一般標籤
        
        return df
    ```
- **備註：** 此任務可與 T008 並行開發

---

### T010: 實作資料驗證函式 [P]

- **描述：** 驗證每筆記錄的資料有效性
- **規格依據：** SPEC-2025-001, Section 3.3.1; PLAN-2025-001-PHASE1, Task C2
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T009
- **驗收標準：**
  - 驗證 `name` 不為空
  - 驗證 `name` 長度在 1-200 字元
  - 驗證 `danbooru_cat` 在 [0, 1, 3, 4, 5] 範圍內
  - 驗證 `post_count` ≥ 0
  - 無效記錄被記錄並從 DataFrame 中移除
  - 返回驗證統計（有效數、無效數）
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 函式簽名：
    ```python
    def validate_records(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """
        驗證 DataFrame 中的記錄
        
        Args:
            df: 待驗證的 DataFrame
        
        Returns:
            (有效的 DataFrame, 驗證統計字典)
        """
        logger = logging.getLogger(__name__)
        
        original_count = len(df)
        invalid_records = []
        
        # 驗證 name
        mask_name = (df['name'].notna()) & (df['name'].str.strip() != '')
        mask_name &= (df['name'].str.len() >= 1) & (df['name'].str.len() <= 200)
        
        # 驗證 danbooru_cat
        mask_cat = df['danbooru_cat'].isin([0, 1, 3, 4, 5])
        
        # 驗證 post_count
        mask_count = df['post_count'] >= 0
        
        # 合併所有驗證
        valid_mask = mask_name & mask_cat & mask_count
        
        # 記錄無效記錄
        invalid_df = df[~valid_mask]
        if len(invalid_df) > 0:
            logger.warning(f"發現 {len(invalid_df)} 筆無效記錄")
            for idx, row in invalid_df.head(10).iterrows():
                logger.debug(f"  無效記錄: {row.to_dict()}")
        
        valid_df = df[valid_mask].copy()
        
        stats = {
            'original_count': original_count,
            'valid_count': len(valid_df),
            'invalid_count': original_count - len(valid_df)
        }
        
        logger.info(f"驗證完成: {stats['valid_count']}/{stats['original_count']} 筆有效")
        
        return valid_df, stats
    ```
- **備註：** 此任務可與 T009 並行開發

---

### T011: 建立 tags_raw 資料表

- **描述：** 建立 SQLite 資料表並插入原始資料
- **規格依據：** SPEC-2025-001, FR-03; DATA-MODEL-2025-001-PHASE1, Section 3.1
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T010
- **驗收標準：**
  - `tags_raw` 表 Schema 符合 DATA-MODEL-2025-001-PHASE1
  - 所有有效記錄成功插入
  - 索引正確建立（`name`, `danbooru_cat`, `source_file`）
  - 資料庫檔案可被 SQLite 工具開啟
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 函式簽名：
    ```python
    def create_tags_raw_table(df: pd.DataFrame, db_path: Path) -> int:
        """
        建立 tags_raw 資料表並插入資料
        
        Args:
            df: 驗證後的 DataFrame
            db_path: 資料庫檔案路徑
        
        Returns:
            插入的記錄數
        """
        import sqlite3
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 確保輸出目錄存在
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 連接資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 建立表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags_raw (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file TEXT NOT NULL,
                name TEXT NOT NULL,
                danbooru_cat INTEGER,
                post_count INTEGER DEFAULT 0,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入資料
        df_to_insert = df[['source_file', 'name', 'danbooru_cat', 'post_count']].copy()
        df_to_insert.to_sql('tags_raw', conn, if_exists='append', index=False)
        
        # 建立索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_raw_name ON tags_raw(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_raw_cat ON tags_raw(danbooru_cat)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_raw_source ON tags_raw(source_file)")
        
        conn.commit()
        
        # 驗證插入
        count = cursor.execute("SELECT COUNT(*) FROM tags_raw").fetchone()[0]
        logger.info(f"✓ tags_raw 表建立完成: {count} 筆記錄")
        
        conn.close()
        
        return count
    ```
- **備註：** 
  - 使用 Python 內建 `sqlite3` 模組
  - 考慮使用交易加速插入

---

## Phase 4: 資料合併去重模組 (Data Merging & Deduplication)

**目標：** 合併相同標籤的記錄，去除重複

**獨立測試標準：**
- [ ] 執行後，相同 `name` 的記錄被合併為一筆
- [ ] `post_count` 正確加總
- [ ] `source_count` 正確計算

**對應用戶故事：**
- US2: 作為開發者，我需要能夠合併和去重標籤，以便得到唯一的標籤列表
- 對應 SPEC FR-04, FR-05

---

### T012: 實作合併去重邏輯

- **描述：** 對 `tags_raw` 表中相同 `name` 的記錄進行聚合
- **規格依據：** SPEC-2025-001, FR-04, FR-05; PLAN-2025-001-PHASE1, Task D1
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T011
- **驗收標準：**
  - 相同 `name` 的記錄被合併為一筆
  - `post_count` 為所有來源的總和
  - `source_count` 為不同來源檔案的數量
  - `danbooru_cat` 選擇最常出現的值（mode）
  - 返回去重後的 DataFrame
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 函式簽名：
    ```python
    def merge_and_deduplicate(db_path: Path) -> pd.DataFrame:
        """
        合併去重處理
        
        Args:
            db_path: 資料庫檔案路徑
        
        Returns:
            去重後的 DataFrame
        """
        import sqlite3
        import pandas as pd
        import logging
        
        logger = logging.getLogger(__name__)
        
        conn = sqlite3.connect(db_path)
        
        # 使用 SQL 進行聚合
        query = """
        SELECT 
            name,
            danbooru_cat,
            SUM(post_count) as post_count,
            COUNT(DISTINCT source_file) as source_count
        FROM tags_raw
        GROUP BY name, danbooru_cat
        ORDER BY post_count DESC
        """
        
        df_merged = pd.read_sql_query(query, conn)
        
        # 處理同一個 name 有多個 danbooru_cat 的情況
        # 選擇 post_count 最高的那個
        df_merged = df_merged.sort_values('post_count', ascending=False)
        df_merged = df_merged.drop_duplicates(subset=['name'], keep='first')
        
        conn.close()
        
        logger.info(f"合併去重完成: {len(df_merged)} 個唯一標籤")
        
        return df_merged
    ```
- **備註：** 
  - SQL 聚合比 Pandas 操作更高效
  - 確保 `name` 在最終結果中唯一

---

### T013: 撰寫合併去重測試

- **描述：** 驗證合併去重邏輯的正確性
- **規格依據：** PLAN-2025-001-PHASE1, Task D1
- **優先級：** Medium
- **預估時間：** 1.5 小時
- **相依任務：** T012
- **驗收標準：**
  - 測試案例覆蓋：
    - 完全相同的記錄（name, category）
    - 相同 name 但不同 category
    - 相同 name 但不同 source_file
  - 驗證 post_count 正確加總
  - 驗證 source_count 正確計算
- **技術細節：**
  - 測試檔案：`stage1/tests/test_merge.py`
  - 使用記憶體資料庫 `:memory:` 進行測試
  - 範例測試：
    ```python
    import unittest
    import sqlite3
    import pandas as pd
    from pathlib import Path
    
    class TestMergeDedup(unittest.TestCase):
        
        def setUp(self):
            # 建立測試資料庫
            self.db_path = Path(':memory:')
            self.conn = sqlite3.connect(':memory:')
            
            # 建立測試資料
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE tags_raw (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT NOT NULL,
                    name TEXT NOT NULL,
                    danbooru_cat INTEGER,
                    post_count INTEGER DEFAULT 0,
                    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 插入測試資料
            test_data = [
                ('file1.csv', 'school_uniform', 0, 100),
                ('file2.csv', 'school_uniform', 0, 200),
                ('file1.csv', 'smile', 0, 50),
                ('file1.csv', 'artist_name', 1, 30),
            ]
            cursor.executemany(
                "INSERT INTO tags_raw (source_file, name, danbooru_cat, post_count) VALUES (?, ?, ?, ?)",
                test_data
            )
            self.conn.commit()
        
        def test_merge_same_tag(self):
            # 測試相同標籤被合併
            query = """
            SELECT name, SUM(post_count) as total_count, COUNT(DISTINCT source_file) as source_count
            FROM tags_raw
            WHERE name = 'school_uniform'
            GROUP BY name
            """
            result = pd.read_sql_query(query, self.conn)
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result['total_count'].iloc[0], 300)
            self.assertEqual(result['source_count'].iloc[0], 2)
        
        def tearDown(self):
            self.conn.close()
    ```
- **備註：** 測試應該是獨立的，不依賴真實資料

---

## Phase 5: 分類套用模組 (Classification Application)

**目標：** 將規則式分類套用至所有一般標籤

**獨立測試標準：**
- [ ] 所有 `danbooru_cat=0` 的標籤都嘗試分類
- [ ] 主分類覆蓋率 ≥ 90%
- [ ] 副分類覆蓋率 ≥ 40%（針對 CHARACTER_RELATED 和 ACTION_POSE）

**對應用戶故事：**
- US3: 作為開發者，我需要能夠使用規則式方法對標籤進行分類，以便為標籤添加語意分類
- 對應 SPEC FR-06（Phase 1 版本，不使用 LLM）

---

### T014: 實作批次分類函式

- **描述：** 對 DataFrame 中的所有標籤套用分類規則
- **規格依據：** PLAN-2025-001-PHASE1, Task D2
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T006, T012
- **驗收標準：**
  - 對所有 `danbooru_cat=0` 的標籤執行分類
  - 非一般標籤（category != 0）不分類
  - `main_category` 和 `sub_category` 欄位被正確填充
  - 未分類的標籤保持 `None`
  - 記錄分類統計（已分類數、未分類數、覆蓋率）
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 函式簽名：
    ```python
    def apply_classification(df: pd.DataFrame) -> pd.DataFrame:
        """
        套用分類規則至 DataFrame
        
        Args:
            df: 合併去重後的 DataFrame
        
        Returns:
            添加分類欄位的 DataFrame
        """
        from data_rules import classify_tag
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 初始化分類欄位
        df['main_category'] = None
        df['sub_category'] = None
        
        # 只對一般標籤（danbooru_cat=0）進行分類
        mask = df['danbooru_cat'] == 0
        general_tags = df[mask]
        
        logger.info(f"開始分類 {len(general_tags)} 個一般標籤...")
        
        # 套用分類函式
        classifications = general_tags['name'].apply(classify_tag)
        
        # 拆分主分類和副分類
        df.loc[mask, 'main_category'] = [c[0] for c in classifications]
        df.loc[mask, 'sub_category'] = [c[1] for c in classifications]
        
        # 統計覆蓋率
        classified_count = df[mask & df['main_category'].notna()].shape[0]
        total_general = len(general_tags)
        coverage = classified_count / total_general if total_general > 0 else 0
        
        logger.info(f"分類完成:")
        logger.info(f"  已分類: {classified_count}/{total_general} ({coverage:.1%})")
        logger.info(f"  未分類: {total_general - classified_count}")
        
        # 統計副分類覆蓋率
        sub_cat_count = df[mask & df['sub_category'].notna()].shape[0]
        logger.info(f"  副分類: {sub_cat_count} 個標籤有副分類")
        
        return df
    ```
- **備註：** 
  - 考慮使用進度條（tqdm）顯示處理進度
  - 如果資料量大，可考慮批次處理

---

### T015: 生成分類統計報告

- **描述：** 產生詳細的分類統計報告
- **規格依據：** PLAN-2025-001-PHASE1, Task E2
- **優先級：** Medium
- **預估時間：** 2 小時
- **相依任務：** T014
- **驗收標準：**
  - 報告包含：總標籤數、各主分類分佈、副分類分佈
  - 報告包含：覆蓋率統計、TOP 20 未分類標籤
  - 報告儲存至 `output/classification_report.txt`
  - 報告格式清晰易讀
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 函式簽名：
    ```python
    def generate_classification_report(df: pd.DataFrame, output_path: Path):
        """
        產生分類統計報告
        
        Args:
            df: 分類後的 DataFrame
            output_path: 報告輸出路徑
        """
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 確保輸出目錄存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("Danbooru 標籤分類統計報告\n")
            f.write("=" * 80 + "\n\n")
            
            # 總體統計
            total = len(df)
            general_tags = df[df['danbooru_cat'] == 0]
            total_general = len(general_tags)
            
            f.write("## 總體統計\n")
            f.write(f"  總標籤數: {total}\n")
            f.write(f"  一般標籤數 (danbooru_cat=0): {total_general}\n")
            f.write(f"  其他類別標籤數: {total - total_general}\n\n")
            
            # 主分類分佈
            f.write("## 主分類分佈\n")
            main_cat_dist = general_tags['main_category'].value_counts()
            for cat, count in main_cat_dist.items():
                pct = count / total_general * 100
                f.write(f"  {cat}: {count} ({pct:.1f}%)\n")
            
            # 未分類標籤
            unclassified = general_tags[general_tags['main_category'].isna()]
            unclassified_count = len(unclassified)
            f.write(f"  未分類: {unclassified_count} ({unclassified_count/total_general*100:.1f}%)\n\n")
            
            # 覆蓋率
            classified_count = total_general - unclassified_count
            coverage = classified_count / total_general if total_general > 0 else 0
            f.write(f"## 主分類覆蓋率: {coverage:.1%}\n\n")
            
            # 副分類分佈
            f.write("## 副分類分佈\n")
            sub_cat_dist = general_tags[general_tags['sub_category'].notna()]['sub_category'].value_counts()
            for cat, count in sub_cat_dist.items():
                f.write(f"  {cat}: {count}\n")
            f.write("\n")
            
            # TOP 未分類標籤
            f.write("## TOP 20 未分類標籤（按使用次數排序）\n")
            top_unclassified = unclassified.nlargest(20, 'post_count')[['name', 'post_count']]
            for idx, row in top_unclassified.iterrows():
                f.write(f"  {row['name']}: {row['post_count']} 次\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("報告結束\n")
        
        logger.info(f"✓ 分類報告已生成: {output_path}")
    ```
- **備註：** 
  - 報告應該包含足夠資訊用於優化關鍵字字典
  - 考慮添加視覺化圖表（可選）

---

## Phase 6: 最終資料表建立 (Final Table Creation)

**目標：** 建立 `tags_final` 表並完成所有索引

**獨立測試標準：**
- [ ] `tags_final` 表 Schema 符合定義
- [ ] 所有記錄成功插入
- [ ] 所有索引建立完成
- [ ] 全文搜尋索引可用

**對應用戶故事：**
- US4: 作為開發者，我需要能夠產出 SQLite 資料庫，以便保存處理後的標籤資料
- 對應 SPEC FR-07, FR-08

---

### T016: 建立 tags_final 資料表

- **描述：** 建立最終資料表並插入分類後的資料
- **規格依據：** SPEC-2025-001, FR-08; DATA-MODEL-2025-001-PHASE1, Section 3.2
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T014
- **驗收標準：**
  - `tags_final` 表 Schema 符合 DATA-MODEL-2025-001-PHASE1
  - 所有記錄成功插入
  - `name` 欄位唯一性約束生效
  - CHECK 約束正確設定
  - 所有索引建立完成
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 函式簽名：
    ```python
    def create_tags_final_table(df: pd.DataFrame, db_path: Path) -> int:
        """
        建立 tags_final 資料表並插入資料
        
        Args:
            df: 分類後的 DataFrame
            db_path: 資料庫檔案路徑
        
        Returns:
            插入的記錄數
        """
        import sqlite3
        import logging
        
        logger = logging.getLogger(__name__)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 建立表（如果存在則刪除舊表）
        cursor.execute("DROP TABLE IF EXISTS tags_final")
        cursor.execute("""
            CREATE TABLE tags_final (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                danbooru_cat INTEGER NOT NULL,
                
                -- 階層式分類欄位
                main_category TEXT,
                sub_category TEXT,
                
                -- 統計欄位
                post_count INTEGER DEFAULT 0,
                source_count INTEGER DEFAULT 1,
                
                -- 時間戳記
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- 約束
                CHECK (danbooru_cat BETWEEN 0 AND 5),
                CHECK (post_count >= 0),
                CHECK (source_count >= 1)
            )
        """)
        
        # 插入資料
        df_to_insert = df[[
            'name', 'danbooru_cat', 'main_category', 'sub_category',
            'post_count', 'source_count'
        ]].copy()
        
        df_to_insert.to_sql('tags_final', conn, if_exists='append', index=False)
        
        # 建立索引
        logger.info("建立索引...")
        cursor.execute("CREATE UNIQUE INDEX idx_tags_final_name ON tags_final(name)")
        cursor.execute("CREATE INDEX idx_tags_final_danbooru_cat ON tags_final(danbooru_cat)")
        cursor.execute("CREATE INDEX idx_tags_final_main_cat ON tags_final(main_category)")
        cursor.execute("CREATE INDEX idx_tags_final_sub_cat ON tags_final(sub_category)")
        cursor.execute("CREATE INDEX idx_tags_final_main_sub ON tags_final(main_category, sub_category)")
        cursor.execute("CREATE INDEX idx_tags_final_post_count ON tags_final(post_count DESC)")
        
        conn.commit()
        
        # 驗證插入
        count = cursor.execute("SELECT COUNT(*) FROM tags_final").fetchone()[0]
        logger.info(f"✓ tags_final 表建立完成: {count} 筆記錄")
        
        conn.close()
        
        return count
    ```
- **備註：** 
  - 確保 UNIQUE 約束不會導致插入失敗
  - 索引建立順序：先插入資料，再建立索引（更快）

---

### T017: 建立全文搜尋索引 (FTS5) [可選]

- **描述：** 建立 SQLite FTS5 全文搜尋索引
- **規格依據：** DATA-MODEL-2025-001-PHASE1, Section 3.2
- **優先級：** Low
- **預估時間：** 1 小時
- **相依任務：** T016
- **驗收標準：**
  - `tags_search` 虛擬表建立成功
  - FTS5 索引可用於搜尋
  - 搜尋速度快於普通 LIKE 查詢
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - SQL：
    ```sql
    CREATE VIRTUAL TABLE tags_search USING fts5(
        name, 
        main_category,
        sub_category,
        content='tags_final',
        content_rowid='id'
    );
    
    -- 填充 FTS 索引
    INSERT INTO tags_search(tags_search) VALUES('rebuild');
    ```
- **備註：** 
  - FTS5 在大資料量時顯著提升搜尋速度
  - 如果時間緊迫，可跳過此任務

---

## Phase 7: 資料品質驗證與整合 (Data Quality Validation & Integration)

**目標：** 驗證輸出資料品質，整合完整管線

**獨立測試標準：**
- [ ] 所有資料驗證檢查通過
- [ ] 執行 `python run_pipeline.py` 完整流程成功
- [ ] 產出的 `tags.db` 符合所有要求

---

### T018: 實作資料品質驗證函式

- **描述：** 實作完整的資料品質檢查邏輯
- **規格依據：** SPEC-2025-001, Section 3.3; PLAN-2025-001-PHASE1, Task E1
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T016
- **驗收標準：**
  - 唯一性檢查：`name` 無重複
  - 覆蓋率檢查：主分類覆蓋率 ≥ 90%
  - 一致性檢查：`tags_final.post_count` 總和 = `tags_raw.post_count` 總和
  - 完整性檢查：所有 NOT NULL 欄位無 NULL
  - 返回驗證結果清單（通過/失敗）
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 函式簽名：
    ```python
    def validate_output(db_path: Path) -> list[str]:
        """
        驗證輸出資料品質
        
        Args:
            db_path: 資料庫檔案路徑
        
        Returns:
            錯誤列表（空列表表示通過）
        """
        import sqlite3
        import logging
        
        logger = logging.getLogger(__name__)
        errors = []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("開始資料品質驗證...")
        
        # 1. 唯一性檢查
        result = cursor.execute("""
            SELECT COUNT(*), COUNT(DISTINCT name) FROM tags_final
        """).fetchone()
        if result[0] != result[1]:
            errors.append(f"name 有重複值：{result[0] - result[1]} 筆重複")
        else:
            logger.info("✓ 唯一性檢查通過")
        
        # 2. 覆蓋率檢查
        result = cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(main_category) as classified
            FROM tags_final
            WHERE danbooru_cat = 0
        """).fetchone()
        coverage = result[1] / result[0] if result[0] > 0 else 0
        if coverage < 0.9:
            errors.append(f"主分類覆蓋率不足：{coverage:.1%} < 90%")
        else:
            logger.info(f"✓ 覆蓋率檢查通過：{coverage:.1%}")
        
        # 3. 一致性檢查
        sum_raw = cursor.execute("SELECT SUM(post_count) FROM tags_raw").fetchone()[0]
        sum_final = cursor.execute("SELECT SUM(post_count) FROM tags_final").fetchone()[0]
        if sum_raw != sum_final:
            errors.append(f"post_count 不一致：raw={sum_raw}, final={sum_final}")
        else:
            logger.info("✓ 一致性檢查通過")
        
        # 4. 完整性檢查
        null_count = cursor.execute("""
            SELECT COUNT(*) FROM tags_final
            WHERE name IS NULL OR danbooru_cat IS NULL
        """).fetchone()[0]
        if null_count > 0:
            errors.append(f"發現 {null_count} 筆 NULL 在必填欄位")
        else:
            logger.info("✓ 完整性檢查通過")
        
        conn.close()
        
        if errors:
            logger.error(f"驗證失敗：{len(errors)} 個錯誤")
            for error in errors:
                logger.error(f"  - {error}")
        else:
            logger.info("✓ 所有驗證檢查通過！")
        
        return errors
    ```
- **備註：** 驗證邏輯應該嚴格，確保資料品質

---

### T019: 整合完整管線

- **描述：** 整合所有模組，建立完整的執行流程
- **規格依據：** PLAN-2025-001-PHASE1, Task F1
- **優先級：** High
- **預估時間：** 3 小時
- **相依任務：** T003, T007, T011, T014, T016, T018
- **驗收標準：**
  - `python run_pipeline.py` 可一鍵執行完整流程
  - 提供進度顯示與日誌輸出
  - 錯誤處理完善（檔案不存在、資料庫錯誤等）
  - 執行完成後顯示統計摘要
  - 處理 10 萬筆標籤在 5 分鐘內完成
- **技術細節：**
  - 主要檔案：`stage1/run_pipeline.py`
  - 主函式結構：
    ```python
    def main():
        """主執行流程"""
        import logging
        from pathlib import Path
        import time
        
        # 設定日誌
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('output/pipeline.log'),
                logging.StreamHandler()
            ]
        )
        logger = logging.getLogger(__name__)
        
        start_time = time.time()
        
        logger.info("=" * 80)
        logger.info("Danbooru 標籤資料管線 - Phase 1 (純規則式分類)")
        logger.info("=" * 80)
        
        try:
            # 步驟 1: 載入資料
            logger.info("\n[1/7] 載入 CSV 檔案...")
            df = load_csv_files(DATA_DIR)
            
            if df.empty:
                logger.error("沒有載入任何資料，終止執行")
                return
            
            # 步驟 2: 標準化欄位
            logger.info("\n[2/7] 標準化欄位...")
            df = standardize_columns(df)
            
            # 步驟 3: 驗證資料
            logger.info("\n[3/7] 驗證資料...")
            df, stats = validate_records(df)
            
            # 步驟 4: 建立 tags_raw
            logger.info("\n[4/7] 建立 tags_raw 表...")
            create_tags_raw_table(df, DB_PATH)
            
            # 步驟 5: 合併去重
            logger.info("\n[5/7] 合併去重...")
            df_merged = merge_and_deduplicate(DB_PATH)
            
            # 步驟 6: 套用分類
            logger.info("\n[6/7] 套用分類規則...")
            df_classified = apply_classification(df_merged)
            
            # 步驟 7: 建立 tags_final
            logger.info("\n[7/7] 建立 tags_final 表...")
            create_tags_final_table(df_classified, DB_PATH)
            
            # 驗證輸出
            logger.info("\n驗證資料品質...")
            errors = validate_output(DB_PATH)
            
            if errors:
                logger.error("資料驗證失敗！")
                return
            
            # 產生報告
            logger.info("\n產生分類報告...")
            generate_classification_report(df_classified, OUTPUT_DIR / 'classification_report.txt')
            
            # 完成
            elapsed = time.time() - start_time
            logger.info("\n" + "=" * 80)
            logger.info(f"✓ 管線執行完成！耗時: {elapsed:.1f} 秒")
            logger.info(f"✓ 資料庫已產出: {DB_PATH}")
            logger.info(f"✓ 分類報告已產出: {OUTPUT_DIR / 'classification_report.txt'}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.exception(f"管線執行失敗: {e}")
            raise
    
    if __name__ == '__main__':
        main()
    ```
- **備註：** 
  - 提供清晰的進度指示
  - 確保錯誤訊息有幫助性
  - 考慮添加 `--dry-run` 選項（可選）

---

### T020: 端到端測試

- **描述：** 使用真實資料測試完整管線
- **規格依據：** PLAN-2025-001-PHASE1, Task F3
- **優先級：** High
- **預估時間：** 2 小時
- **相依任務：** T019
- **驗收標準：**
  - 使用 `stage1/data/raw/` 中的真實資料
  - 管線成功執行，無錯誤
  - 產出的 `tags.db` 可被 SQLite 工具開啟
  - 所有驗收標準通過（見 PLAN-2025-001-PHASE1, Section 11）
  - 記錄效能指標（處理時間、記憶體使用）
- **技術細節：**
  - 測試檔案：`stage1/tests/test_e2e.py` 或手動測試
  - 測試步驟：
    1. 清空 `output/` 目錄
    2. 執行 `python run_pipeline.py`
    3. 驗證輸出檔案存在
    4. 使用 `sqlite3` 查詢資料庫
    5. 檢查分類報告內容
  - 範例測試：
    ```python
    import unittest
    import subprocess
    from pathlib import Path
    import sqlite3
    
    class TestE2E(unittest.TestCase):
        
        def setUp(self):
            self.output_dir = Path('output')
            self.db_path = self.output_dir / 'tags.db'
            
            # 清空輸出目錄
            if self.db_path.exists():
                self.db_path.unlink()
        
        def test_full_pipeline(self):
            # 執行管線
            result = subprocess.run(
                ['python', 'run_pipeline.py'],
                cwd='stage1',
                capture_output=True,
                text=True
            )
            
            # 驗證執行成功
            self.assertEqual(result.returncode, 0, f"管線執行失敗: {result.stderr}")
            
            # 驗證輸出檔案存在
            self.assertTrue(self.db_path.exists(), "tags.db 未產出")
            
            # 驗證資料庫結構
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 檢查表存在
            tables = cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table'
            """).fetchall()
            table_names = [t[0] for t in tables]
            
            self.assertIn('tags_raw', table_names)
            self.assertIn('tags_final', table_names)
            
            # 檢查資料存在
            count = cursor.execute("SELECT COUNT(*) FROM tags_final").fetchone()[0]
            self.assertGreater(count, 0, "tags_final 表為空")
            
            # 檢查覆蓋率
            result = cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(main_category) as classified
                FROM tags_final
                WHERE danbooru_cat = 0
            """).fetchone()
            coverage = result[1] / result[0] if result[0] > 0 else 0
            self.assertGreaterEqual(coverage, 0.9, f"覆蓋率不足: {coverage:.1%}")
            
            conn.close()
    ```
- **備註：** 
  - E2E 測試應該在乾淨環境中執行
  - 記錄效能指標用於優化

---

## Phase 8: 文件與交付 (Documentation & Delivery)

**目標：** 完成所有文件，準備交付

**獨立測試標準：**
- [ ] README 包含完整使用說明
- [ ] 程式碼註解完整
- [ ] 所有交付物就緒

---

### T021: 撰寫 README 與使用說明

- **描述：** 為 Phase 1 撰寫完整的 README 文件
- **規格依據：** PLAN-2025-001-PHASE1, Task F2
- **優先級：** Medium
- **預估時間：** 2 小時
- **相依任務：** T019
- **驗收標準：**
  - README 包含：專案簡介、安裝步驟、使用方法、輸出說明
  - 提供完整的範例執行流程
  - 說明如何自訂分類規則
  - 包含常見問題解答（FAQ）
- **技術細節：**
  - 主要檔案：`stage1/README.md`
  - 內容結構：
    ```markdown
    # Danbooru 標籤資料管線 - Phase 1
    
    ## 概述
    [專案簡介]
    
    ## 特點
    - 純規則式分類（不依賴 LLM）
    - 9 個主分類 + 5 個副分類
    - 完全離線執行
    - 零 API 成本
    
    ## 安裝
    [Python 版本要求、依賴安裝]
    
    ## 使用方法
    [執行步驟]
    
    ## 輸出說明
    [資料庫結構、欄位說明]
    
    ## 自訂分類規則
    [如何修改 data_rules.py]
    
    ## 效能指標
    [處理時間、覆蓋率目標]
    
    ## 常見問題
    [FAQ]
    
    ## 授權
    [License]
    ```
- **備註：** 文件應該清晰易懂，面向非技術使用者

---

### T022: 程式碼註解與 Docstring

- **描述：** 為所有公開函式添加完整的 docstring
- **規格依據：** PLAN-2025-001-PHASE1, Section 8.3
- **優先級：** Medium
- **預估時間：** 2 小時
- **相依任務：** T019
- **驗收標準：**
  - 所有公開函式有完整的 docstring（Google 風格）
  - Docstring 包含：功能描述、參數說明、返回值、範例
  - 關鍵邏輯有適當的行內註解
  - 使用 `pylint` 檢查無警告
- **技術細節：**
  - 影響檔案：`stage1/run_pipeline.py`, `stage1/data_rules.py`
  - Docstring 風格：Google Style
  - 範例：
    ```python
    def classify_tag(tag_name: str) -> tuple[Optional[str], Optional[str]]:
        """根據規則對標籤進行分類。
        
        使用預定義的關鍵字字典，按照優先級順序匹配標籤名稱，
        並返回對應的主分類和副分類。
        
        Args:
            tag_name: 標籤名稱，例如 'school_uniform'
        
        Returns:
            包含 (主分類, 副分類) 的元組。如果未匹配任何分類，
            返回 (None, None)。
        
        Examples:
            >>> classify_tag('school_uniform')
            ('CHARACTER_RELATED', 'CLOTHING')
            
            >>> classify_tag('from_above')
            ('COMPOSITION', None)
            
            >>> classify_tag('unknown_tag')
            (None, None)
        
        Note:
            - 匹配不區分大小寫
            - 使用部分字串匹配（'uniform' in 'school_uniform'）
            - 按照 QUALITY → TECHNICAL → ... → ENVIRONMENT 的優先級順序
        """
        # 實作...
    ```
- **備註：** 
  - 使用 `black` 格式化程式碼
  - 使用 `pylint` 檢查品質

---

### T023: 更新專案文件

- **描述：** 更新專案層級的文件（quickstart.md 等）
- **規格依據：** 專案結構要求
- **優先級：** Low
- **預估時間：** 1 小時
- **相依任務：** T021
- **驗收標準：**
  - `docs/quickstart.md` 更新 Phase 1 內容
  - 專案 README 添加 Phase 1 狀態
  - 所有連結有效
- **技術細節：**
  - 影響檔案：`docs/quickstart.md`, `README.md`
- **備註：** 確保專案層級文件與 Stage 1 文件一致

---

## 任務統計 (Task Statistics)

- **總任務數：** 23
- **階段一任務：** 23
- **階段二任務：** 0（Phase 1 範圍外）
- **跨階段任務：** 0
- **高優先級任務：** 18
- **中優先級任務：** 4
- **低優先級任務：** 1
- **已完成任務：** 0 (0%)
- **進行中任務：** 0
- **受阻任務：** 0

---

## 依賴關係圖 (Dependency Graph)

```
Phase 1: Setup
  T001 ────┬──> T002 ──> T003
           │
           └──> T004 ──> T005 ──> T006 ──> T007

Phase 2: Foundation (Blocking)
  T006 ──────────────────┐
                         │
Phase 3: CSV Loading     │
  T002 ──> T008 ──> T009 ──> T010 ──> T011
           (並行: T009, T010)           │
                                        │
Phase 4: Merging                        │
  T011 ──> T012 ──> T013                │
                    │                   │
Phase 5: Classification                 │
  T012 ─────────┬────────────────────────
  T006 ─────────┘
                │
  T014 ──> T015 (報告)
    │
Phase 6: Final Table
  T014 ──> T016 ──> T017 (可選)
                │
Phase 7: Integration
  T003 ──┐
  T007 ──┤
  T011 ──┤
  T014 ──├──> T018 ──> T019 ──> T020
  T016 ──┤
  T018 ──┘

Phase 8: Documentation
  T019 ──> T021 ──> T022 ──> T023
```

---

## 並行執行建議 (Parallel Execution Suggestions)

### 第一輪並行（可同時進行）
- **T001**: 建立目錄結構
- **T002**: 建立配置檔案
- 預估時間：0.5 小時

### 第二輪並行（第一輪完成後）
- **T003**: 設定日誌系統
- **T004**: 建立主分類關鍵字字典
- 預估時間：4 小時（以最長者為準）

### 第三輪並行（T004 完成後）
- **T005**: 建立副分類關鍵字字典
- **T008**: 實作 CSV 讀取函式（可同時開始）
- 預估時間：2 小時

### 第四輪並行（T005, T008 完成後）
- **T006**: 實作分類函式
- **T009**: 實作欄位標準化函式 [P]
- **T010**: 實作資料驗證函式 [P]
- 預估時間：3 小時（以 T006 為準）

### 後續串行執行
- **T007** → **T011** → **T012** → **T013** → **T014** → ... → **T020**
- 每個階段依序完成

---

## 里程碑檢查點 (Milestone Checkpoints)

### ✅ Checkpoint 1: 基礎設施就緒
- **完成任務：** T001, T002, T003
- **驗收標準：**
  - [ ] 可執行 `python run_pipeline.py --help`
  - [ ] 配置檔案正確讀取
  - [ ] 日誌正常輸出
- **預估完成日期：** Day 1

### ✅ Checkpoint 2: 分類規則完成（關鍵阻塞點）
- **完成任務：** T004, T005, T006, T007
- **驗收標準：**
  - [ ] 100 個測試案例通過
  - [ ] 主分類覆蓋率預估 ≥ 85%（基於測試案例）
- **預估完成日期：** Day 2
- **⚠️ 阻塞性：** 此檢查點必須通過才能繼續

### ✅ Checkpoint 3: 資料載入完成
- **完成任務：** T008, T009, T010, T011
- **驗收標準：**
  - [ ] `tags_raw` 表包含所有有效記錄
  - [ ] 載入統計正確
- **預估完成日期：** Day 3

### ✅ Checkpoint 4: 分類套用完成
- **完成任務：** T012, T013, T014, T015
- **驗收標準：**
  - [ ] 主分類覆蓋率 ≥ 90%
  - [ ] 副分類覆蓋率 ≥ 40%
  - [ ] 分類報告已產生
- **預估完成日期：** Day 4

### ✅ Checkpoint 5: 管線整合完成
- **完成任務：** T016, T017, T018, T019, T020
- **驗收標準：**
  - [ ] 完整管線可一鍵執行
  - [ ] 所有驗證檢查通過
  - [ ] E2E 測試通過
- **預估完成日期：** Day 6

### ✅ Checkpoint 6: Phase 1 交付
- **完成任務：** T021, T022, T023
- **驗收標準：**
  - [ ] 所有文件完整
  - [ ] 程式碼註解完整
  - [ ] 符合 PLAN-2025-001-PHASE1 的所有完成標準
- **預估完成日期：** Day 7

---

## 受阻任務追蹤 (Blocked Tasks Tracking)

| 任務 ID | 任務標題 | 受阻原因 | 解決方案 | 負責人 | 預計解決日期 |
|---------|----------|----------|----------|--------|--------------|
| _目前無受阻任務_ | - | - | - | - | - |

---

## 實作建議 (Implementation Tips)

### 開發順序建議
1. **先完成 Phase 2（Foundation）**：分類規則是整個系統的核心，應優先完成並充分測試
2. **小步快跑**：每完成一個任務立即測試，不要累積
3. **保持簡單**：避免過度設計，函式式風格優於物件導向
4. **頻繁提交**：每個任務完成後提交 Git

### 除錯建議
- 使用小型測試資料集（100 筆標籤）快速迭代
- 善用日誌記錄關鍵步驟
- SQLite 可使用 `sqlitebrowser` 視覺化檢查

### 效能優化
- 只有在遇到效能問題時才優化
- 優先使用 SQL 聚合而非 Pandas 操作
- 考慮批次處理（如果資料量 > 100 萬筆）

---

## 變更記錄 (Change Log)

| 日期 | 變更內容 | 變更人 |
|------|----------|--------|
| 2025-10-08 | 初始任務清單建立（基於 Phase 1 計劃） | AI Agent |

---

**任務清單結束 (End of Tasks)**

**注意事項：**
1. 請定期更新任務狀態（使用 `[✓]` 標記已完成任務）
2. 遇到受阻情況立即記錄並尋求協助
3. 完成任務後更新驗收標準檢查清單
4. Phase 2 (Foundation) 是關鍵阻塞點，必須優先完成
5. 所有任務完成後進行最終的憲法合規性審查

**下一步行動：**
1. 審查並批准本任務清單
2. 開始執行 Phase 1: Setup（T001-T003）
3. 建立 Git 分支：`git checkout -b feature/phase1-rule-based-classifier`

