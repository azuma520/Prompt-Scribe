# 研究與技術決策：Danbooru 標籤管線 Phase 1

**文件編號 (Doc ID):** RESEARCH-2025-001-PHASE1

**版本 (Version):** 1.0.0

**建立日期 (Created):** 2025-10-08

**最後更新 (Last Updated):** 2025-10-08

---

## 1. 執行摘要 (Executive Summary)

本文件記錄 Phase 1 (純規則式分類) 的所有技術決策、研究發現和替代方案評估。主要決策包括：

1. **不使用 LLM 進行分類**：改採純規則式 (rule-based) 方法
2. **簡化專案結構**：以腳本為核心，不使用複雜的物件導向設計
3. **使用 Python 內建 `sqlite3`**：不依賴第三方 ORM
4. **階段性實作副分類**：優先實作高價值分類

---

## 2. 核心技術決策 (Key Technical Decisions)

### 2.1 決策：不使用 LLM API 進行分類

**決策內容 (Decision):**
Phase 1 完全不使用任何 LLM API (OpenAI, Anthropic 等)，改採基於關鍵字字典的規則式分類。

**理由 (Rationale):**
1. **降低初期複雜度**
   - LLM 整合需要處理 API 金鑰管理、錯誤重試、限流處理等複雜邏輯
   - 規則式分類邏輯簡單、可預測、易於除錯
   
2. **成本考量**
   - 10 萬筆標籤的 LLM 分類成本約 $50-200 (依模型而定)
   - 規則式分類完全免費
   
3. **速度優勢**
   - 規則式分類可在數秒內完成 10 萬筆
   - LLM API 即使批次處理也需要數小時
   
4. **建立基準線**
   - 規則式分類結果可作為未來 LLM 分類的對照組
   - 可量化 LLM 帶來的改善幅度
   
5. **離線可用**
   - 不依賴網路連線
   - 不受 API 服務中斷影響

**替代方案 (Alternatives Considered):**
- ❌ **OpenAI GPT-4 Turbo**: 成本高、需網路、限流問題
- ❌ **Anthropic Claude 3**: 同上
- ❌ **本地 LLM (Ollama)**: 需額外安裝、推理速度慢、品質不確定
- ✅ **規則式分類**: 簡單、快速、免費、可控

**風險與緩解 (Risks and Mitigations):**
- **風險**: 規則覆蓋率可能不足
  - **緩解**: 持續優化關鍵字字典，目標主分類覆蓋率 ≥ 90%
- **風險**: 規則式分類無法處理複雜語意
  - **緩解**: Phase 2 將引入 LLM 作為補充

---

### 2.2 決策：簡化專案結構

**決策內容 (Decision):**
採用「三檔案結構」：
- `run_pipeline.py`: 主執行腳本
- `data_rules.py`: 規則字典
- `config.py`: 配置檔案

不使用複雜的物件導向設計 (如 `LLMClassifier` 抽象基類、策略模式等)。

**理由 (Rationale):**
1. **符合使用者要求**
   - 使用者明確要求「保持簡單，以腳本為核心」
   - 不需要 `LLMClassifier` 等抽象設計
   
2. **可讀性優先**
   - 新手也能快速理解程式碼流程
   - 函式式風格比物件導向更直觀（針對此任務）
   
3. **減少過度設計**
   - Phase 1 功能單一，不需要多層抽象
   - YAGNI 原則 (You Aren't Gonna Need It)
   
4. **易於維護**
   - 所有邏輯在單一檔案，方便查找與修改
   - 減少檔案跳轉與抽象層級

**替代方案 (Alternatives Considered):**
- ❌ **物件導向設計 (OOP)**: 過度設計、複雜度高、不符合使用者要求
- ❌ **完整 MVC 架構**: 適合大型專案，此處不需要
- ✅ **腳本式設計**: 簡單、直觀、易於理解

**程式碼範例:**
```python
# run_pipeline.py - 簡單清晰的函式式風格
def main():
    logger.info("開始執行資料管線...")
    
    # 步驟 1: 載入資料
    df = load_csv_files(DATA_DIR)
    
    # 步驟 2: 建立 tags_raw
    create_tags_raw_table(df, DB_PATH)
    
    # 步驟 3: 合併去重
    df_merged = merge_and_deduplicate(DB_PATH)
    
    # 步驟 4: 套用分類
    df_classified = apply_classification(df_merged)
    
    # 步驟 5: 建立 tags_final
    create_tags_final_table(df_classified, DB_PATH)
    
    # 步驟 6: 驗證
    errors = validate_output(DB_PATH)
    
    # 步驟 7: 產生報告
    generate_report(DB_PATH, REPORT_PATH)
    
    logger.info("管線執行完成！")
```

---

### 2.3 決策：使用 Python 內建 `sqlite3` 模組

**決策內容 (Decision):**
使用 Python 內建的 `sqlite3` 模組，不使用 `sqlite-utils` 或 ORM (如 SQLAlchemy)。

**理由 (Rationale):**
1. **零依賴**
   - `sqlite3` 是 Python 標準函式庫，無需安裝
   - 減少專案依賴複雜度
   
2. **效能優勢**
   - 直接執行 SQL，無中間層開銷
   - 適合大量資料插入與查詢
   
3. **學習價值**
   - 直接使用 SQL，更接近資料庫本質
   - 提升 SQL 技能
   
4. **靈活性**
   - 可執行任意複雜的 SQL 查詢
   - 不受 ORM 限制

**替代方案 (Alternatives Considered):**
- ❌ **sqlite-utils**: 高層 API 方便，但增加依賴
- ❌ **SQLAlchemy**: 功能強大但過度複雜，學習成本高
- ❌ **Pandas.to_sql**: 方便但效能較差，缺乏細粒度控制
- ✅ **Python sqlite3**: 零依賴、高效能、靈活

**實作範例:**
```python
import sqlite3

def create_tags_final_table(df, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 建立表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags_final (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            danbooru_cat INTEGER NOT NULL,
            main_category TEXT,
            sub_category TEXT,
            post_count INTEGER DEFAULT 0,
            source_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (danbooru_cat BETWEEN 0 AND 5)
        )
    """)
    
    # 批次插入
    df.to_sql('tags_final', conn, if_exists='append', index=False)
    
    # 建立索引
    cursor.execute("CREATE UNIQUE INDEX idx_name ON tags_final(name)")
    
    conn.commit()
    conn.close()
```

---

### 2.4 決策：階段性實作副分類

**決策內容 (Decision):**
Phase 1 僅針對 `CHARACTER_RELATED` 和 `ACTION_POSE` 實作副分類，其他主分類暫不添加副分類。

**理由 (Rationale):**
1. **價值優先**
   - `CHARACTER_RELATED` 是最常用的主分類（約佔 40-50%）
   - 副分類可顯著提升此類標籤的可用性
   
2. **語意混雜問題**
   - `ACTION_POSE` 同時包含動作 (sitting) 和表情 (smile)
   - 副分類可解決此混雜
   
3. **降低初期工作量**
   - 減少需要定義的關鍵字數量
   - 專注於高價值分類
   
4. **可擴展設計**
   - 未來可輕鬆添加其他副分類
   - Schema 已預留 `sub_category` 欄位

**優先級排序:**
1. **高優先級 (Phase 1 實作):**
   - CHARACTER_RELATED: CLOTHING, HAIR, CHARACTER_COUNT
   - ACTION_POSE: POSE, EXPRESSION

2. **中優先級 (Phase 2 考慮):**
   - OBJECTS: WEAPON, FURNITURE, ACCESSORY
   - ENVIRONMENT: INDOOR, OUTDOOR, NATURAL

3. **低優先級 (按需添加):**
   - VISUAL_EFFECTS: LIGHTING, COLOR_EFFECT
   - ART_STYLE: 2D_STYLE, 3D_STYLE

**替代方案 (Alternatives Considered):**
- ❌ **全部實作**: 工作量大、初期價值不明確
- ❌ **完全不實作**: 無法解決語意混雜問題
- ✅ **階段性實作**: 平衡價值與工作量

---

### 2.5 決策：使用關鍵字列表而非正規表達式

**決策內容 (Decision):**
分類規則使用簡單的「字串包含」匹配，而非正規表達式 (regex)。

**理由 (Rationale):**
1. **可讀性**
   - 關鍵字列表更直觀，易於維護
   - 非技術人員也能理解與編輯
   
2. **效能**
   - 字串包含比 regex 匹配更快
   - 處理 10 萬筆標籤速度優勢明顯
   
3. **足夠應付大多數情況**
   - Danbooru 標籤通常是簡單字串（如 `school_uniform`）
   - 不需要複雜的模式匹配
   
4. **易於除錯**
   - 匹配邏輯清晰，容易追蹤為何某標籤被分類

**實作範例:**
```python
# data_rules.py
MAIN_CATEGORY_RULES = {
    'CHARACTER_RELATED': [
        'girl', 'boy', 'woman', 'man',
        'hair', 'eyes', 'face',
        'dress', 'shirt', 'skirt', 'uniform',
        'solo', '1girl', '2girls', 'multiple_girls'
    ],
    'COMPOSITION': [
        'from_above', 'from_below',
        'close-up', 'wide_shot',
        'portrait', 'dutch_angle',
        'pov', 'first-person'
    ]
}

def classify_tag(tag_name: str) -> Tuple[Optional[str], Optional[str]]:
    tag_lower = tag_name.lower().strip()
    
    # 遍歷主分類規則
    for main_cat, keywords in MAIN_CATEGORY_RULES.items():
        if any(kw in tag_lower for kw in keywords):
            # 找到主分類
            sub_cat = None
            if main_cat in SUB_CATEGORY_RULES:
                # 繼續匹配副分類
                for sub_cat_name, sub_keywords in SUB_CATEGORY_RULES[main_cat].items():
                    if any(kw in tag_lower for kw in sub_keywords):
                        sub_cat = sub_cat_name
                        break
            return (main_cat, sub_cat)
    
    return (None, None)  # 未分類
```

**替代方案 (Alternatives Considered):**
- ❌ **正規表達式**: 效能較差、可讀性低、容易出錯
- ❌ **詞幹分析 (Stemming)**: 增加複雜度、效果提升有限
- ✅ **簡單字串包含**: 快速、簡單、有效

---

### 2.6 決策：分類優先級順序

**決策內容 (Decision):**
主分類按照以下優先級順序匹配（從高到低）：
1. QUALITY
2. TECHNICAL
3. ART_STYLE
4. COMPOSITION
5. VISUAL_EFFECTS
6. CHARACTER_RELATED
7. ACTION_POSE
8. OBJECTS
9. ENVIRONMENT

**理由 (Rationale):**
1. **避免分類衝突**
   - 某些標籤可能匹配多個分類
   - 例如 `anime_style_portrait` 可能匹配 ART_STYLE 和 COMPOSITION
   
2. **語意重要性排序**
   - QUALITY 和 TECHNICAL 是「元屬性」，優先級最高
   - ART_STYLE 是整體風格，優於具體內容
   - COMPOSITION 是技術性描述，優於內容描述
   - CHARACTER/OBJECT/ENVIRONMENT 是具體內容，優先級較低
   
3. **減少歧義**
   - 明確的優先級規則讓分類結果可預測
   - 易於向使用者解釋為何某標籤被分到特定類別

**案例分析:**
```python
# 案例 1: "anime_style_portrait"
# 匹配: ART_STYLE ('anime') 和 COMPOSITION ('portrait')
# 結果: ART_STYLE (優先級 3 > 4)

# 案例 2: "masterpiece_quality_girl"
# 匹配: QUALITY ('masterpiece') 和 CHARACTER_RELATED ('girl')
# 結果: QUALITY (優先級 1 > 6)

# 案例 3: "school_uniform"
# 匹配: CHARACTER_RELATED ('uniform')
# 副分類: CLOTHING ('uniform')
# 結果: CHARACTER_RELATED / CLOTHING
```

**替代方案 (Alternatives Considered):**
- ❌ **隨機順序**: 結果不可預測
- ❌ **按關鍵字長度**: 語意意義不明確
- ✅ **語意重要性順序**: 邏輯清晰、可預測

---

## 3. 技術最佳實踐 (Best Practices)

### 3.1 Python 資料處理

**研究主題:** 如何高效處理大量 CSV 資料

**發現 (Findings):**
1. **Pandas 是最佳選擇**
   - 成熟、穩定、文件完整
   - 處理 10 萬筆標籤速度快（< 1 秒）
   - 提供豐富的資料清洗函式

2. **記憶體優化技巧**
   - 使用 `dtype` 指定欄位類型，減少記憶體使用
   - 不需要的欄位立即 drop
   - 使用 iterator 模式處理超大檔案

3. **批次處理模式**
   ```python
   # 範例：批次插入資料庫
   chunk_size = 1000
   for i in range(0, len(df), chunk_size):
       chunk = df.iloc[i:i+chunk_size]
       chunk.to_sql('tags_final', conn, if_exists='append', index=False)
   ```

### 3.2 SQLite 效能優化

**研究主題:** SQLite 大量資料插入最佳實踐

**發現 (Findings):**
1. **使用交易 (Transaction)**
   ```python
   conn.execute('BEGIN TRANSACTION')
   # ... 多次插入 ...
   conn.execute('COMMIT')
   # 速度提升 10-100 倍
   ```

2. **延遲索引建立**
   - 先插入所有資料
   - 再一次性建立索引
   - 比逐筆插入時維護索引快得多

3. **使用 executemany**
   ```python
   cursor.executemany('INSERT INTO tags VALUES (?, ?, ?)', data_list)
   # 比逐筆 execute 快 5-10 倍
   ```

### 3.3 程式碼品質

**研究主題:** Python 程式碼風格與品質工具

**採用工具:**
1. **Black**: 自動格式化
   - 配置：預設設定即可
   - 執行：`black run_pipeline.py`

2. **Pylint**: 靜態檢查
   - 配置：忽略 C0103 (命名風格) 和 W0511 (TODO)
   - 執行：`pylint run_pipeline.py`

3. **Docstring**: Google 風格
   ```python
   def classify_tag(tag_name: str) -> Tuple[Optional[str], Optional[str]]:
       """根據規則對標籤進行分類。
       
       Args:
           tag_name: 標籤名稱
       
       Returns:
           (main_category, sub_category) 的元組。
           未分類時返回 (None, None)。
       
       Example:
           >>> classify_tag('school_uniform')
           ('CHARACTER_RELATED', 'CLOTHING')
       """
       pass
   ```

---

## 4. 關鍵字字典建立方法 (Keyword Dictionary Creation)

### 4.1 建立流程

**步驟 1: 資料探索**
- 讀取 CSV 檔案，統計最常見的標籤
- 識別明顯屬於某分類的標籤

**步驟 2: 人工標註樣本**
- 隨機抽取 500 筆標籤
- 人工分配至 9 個主分類
- 識別每個分類的典型關鍵字

**步驟 3: 關鍵字擴展**
- 基於樣本標註結果，列出關鍵字
- 考慮同義詞、相關詞
- 考慮常見縮寫與變體

**步驟 4: 迭代驗證**
- 用關鍵字字典對樣本進行分類
- 計算準確率
- 根據錯誤案例調整關鍵字

**步驟 5: 全量測試**
- 對所有資料進行分類
- 檢視未分類標籤
- 持續優化關鍵字

### 4.2 關鍵字選擇原則

1. **高頻優先**: 優先添加高頻標籤的關鍵字
2. **精準性**: 避免過於寬泛的關鍵字（如 'a', 'the'）
3. **覆蓋率**: 目標主分類覆蓋率 ≥ 90%
4. **避免衝突**: 確保關鍵字不會導致大量誤分類

---

## 5. 效能預估 (Performance Estimates)

### 5.1 處理時間預估

**假設:**
- 資料量: 100,000 筆標籤
- 硬體: 中等效能筆電 (i5, 8GB RAM, SSD)

**預估時間:**
| 步驟 | 預估時間 | 說明 |
|------|----------|------|
| CSV 載入 | 5 秒 | Pandas 讀取 |
| 資料驗證 | 10 秒 | 逐筆檢查 |
| 建立 tags_raw | 5 秒 | SQLite 批次插入 |
| 合併去重 | 30 秒 | SQL GROUP BY + 聚合 |
| 分類處理 | 60 秒 | 10 萬次字串匹配 |
| 建立 tags_final | 10 秒 | 批次插入 + 索引 |
| 驗證與報告 | 20 秒 | SQL 查詢 + 統計 |
| **總計** | **~2.5 分鐘** | 遠低於目標 5 分鐘 |

### 5.2 記憶體使用預估

| 資料結構 | 預估記憶體 | 說明 |
|----------|------------|------|
| Pandas DataFrame (10 萬筆) | ~50 MB | 含 5-6 個欄位 |
| 關鍵字字典 | < 1 MB | 約 1000 個關鍵字 |
| SQLite 連線 | ~10 MB | 快取與緩衝 |
| **總計** | **~100 MB** | 遠低於 2GB 限制 |

---

## 6. 潛在問題與解決方案 (Issues and Solutions)

### 6.1 問題：CSV 格式不一致

**問題描述:**
不同來源的 CSV 檔案可能欄位名稱不同：
- 有些使用 `category`，有些使用 `danbooru_cat`
- 有些有 `post_count`，有些沒有

**解決方案:**
```python
def standardize_columns(df):
    """標準化欄位名稱"""
    # 欄位映射
    column_map = {
        'category': 'danbooru_cat',
        'count': 'post_count',
        'tag': 'name'
    }
    df.rename(columns=column_map, inplace=True)
    
    # 補充缺失欄位
    if 'post_count' not in df.columns:
        df['post_count'] = 0
    
    return df
```

### 6.2 問題：關鍵字衝突

**問題描述:**
某些標籤可能匹配多個主分類，例如：
- `anime_portrait`: 匹配 ART_STYLE 和 COMPOSITION

**解決方案:**
- 使用優先級順序（見 2.6）
- 記錄衝突案例至日誌
- 定期審查衝突案例，調整規則

### 6.3 問題：未分類標籤過多

**問題描述:**
如果主分類覆蓋率 < 90%，表示關鍵字字典不夠完善。

**解決方案:**
1. 產生「未分類標籤報告」
2. 按 `post_count` 排序，優先處理高頻標籤
3. 人工審查並添加關鍵字
4. 重新執行管線

---

## 7. 未來擴展路徑 (Future Extensions)

### 7.1 Phase 2: LLM 增強

**目標:**
- 使用 LLM 對規則式分類未覆蓋的標籤進行語意分類
- 建立混合式分類系統（規則優先，LLM 補充）

**技術選型:**
- 主要: OpenAI GPT-4 Turbo
- 備用: Anthropic Claude 3.5
- 本地: Ollama (可選)

**整合點:**
```python
def apply_classification(df):
    # 步驟 1: 規則式分類
    df['main_category'], df['sub_category'] = zip(*df['name'].apply(classify_tag))
    
    # 步驟 2: LLM 補充分類 (Phase 2)
    unclassified = df[df['main_category'].isnull()]
    if not unclassified.empty:
        llm_results = classify_with_llm(unclassified['name'].tolist())
        df.loc[df['main_category'].isnull(), 'main_category'] = llm_results
    
    return df
```

### 7.2 Phase 3: 機器學習分類

**目標:**
- 訓練分類模型（Random Forest, BERT）
- 使用規則式 + LLM 結果作為訓練資料

**潛在價值:**
- 完全離線執行
- 推理速度更快
- 無 API 成本

---

## 8. 參考資料 (References)

### 8.1 技術文件

- [Pandas 官方文件](https://pandas.pydata.org/docs/)
- [Python sqlite3 文件](https://docs.python.org/3/library/sqlite3.html)
- [SQLite 效能優化](https://www.sqlite.org/faq.html#q19)

### 8.2 相關專案

- [Danbooru 標籤系統](https://danbooru.donmai.us/wiki_pages/howto:tag)
- [Booru 標籤規範](https://github.com/booru-tags)

### 8.3 內部文件

- SPEC-2025-001: Danbooru 標籤資料管線規格
- PLAN-2025-001-PHASE1: Phase 1 開發計畫
- Constitution.md: 專案開發憲法

---

**研究文件結束 (End of Research Document)**

**下一步行動:**
1. ✅ 研究完成，所有技術決策已記錄
2. [ ] 開始實作任務組 A（專案基礎設定）
3. [ ] 建立初始關鍵字字典

