# 資料模型：Danbooru 標籤管線 Phase 1

**文件編號 (Doc ID):** DATA-MODEL-2025-001-PHASE1

**版本 (Version):** 1.0.0

**建立日期 (Created):** 2025-10-08

**最後更新 (Last Updated):** 2025-10-08

---

## 1. 概述 (Overview)

本文件定義 Phase 1 (純規則式分類) 的完整資料模型，包括：
- 輸入資料格式 (CSV)
- 中間資料表 (`tags_raw`)
- 最終資料表 (`tags_final`)
- 資料驗證規則
- 資料流向與轉換邏輯

---

## 2. 輸入資料格式 (Input Data Format)

### 2.1 CSV 檔案結構

**檔案位置:** `stage1/data/raw/*.csv`

**必要欄位:**
| 欄位名稱 | 資料型別 | 說明 | 範例 |
|----------|----------|------|------|
| `name` | str | 標籤名稱 | `school_uniform` |
| `category` 或 `danbooru_cat` | int | Danbooru 分類 ID (0-5) | `0` |

**可選欄位:**
| 欄位名稱 | 資料型別 | 說明 | 預設值 |
|----------|----------|------|--------|
| `post_count` | int | 使用此標籤的貼文數量 | `0` |

**Danbooru 分類對照表:**
| ID | 類別名稱 | 說明 |
|----|----------|------|
| 0 | General | 一般標籤（內容描述） |
| 1 | Artist | 藝術家標籤 |
| 3 | Copyright | 版權標籤 |
| 4 | Character | 角色標籤 |
| 5 | Meta | 元標籤 |

### 2.2 CSV 範例

```csv
name,category,post_count
school_uniform,0,15234
from_above,0,8921
1girl,0,123456
hatsune_miku,4,98765
anime,0,5432
```

### 2.3 資料品質要求

**驗證規則:**
1. `name` 不可為空
2. `name` 長度在 1-200 字元之間
3. `category` 必須在 0-5 範圍內
4. `post_count` 必須 ≥ 0

**容錯處理:**
- 欄位名稱大小寫不敏感（`Category` → `category`）
- 支援欄位別名（`tag` → `name`, `count` → `post_count`）
- 缺失的 `post_count` 預設為 0
- 無效記錄記錄至日誌並跳過

---

## 3. 資料表結構 (Database Schema)

### 3.1 tags_raw (原始資料表)

**用途:** 儲存所有來源檔案的原始記錄，保留完整追溯性。

**Schema:**
```sql
CREATE TABLE tags_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,           -- 來源檔案名稱
    name TEXT NOT NULL,                  -- 標籤名稱
    danbooru_cat INTEGER,                -- Danbooru 原始分類 (0-5)
    post_count INTEGER DEFAULT 0,        -- 使用次數
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_tags_raw_name ON tags_raw(name);
CREATE INDEX idx_tags_raw_cat ON tags_raw(danbooru_cat);
CREATE INDEX idx_tags_raw_source ON tags_raw(source_file);
```

**欄位說明:**
| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| `id` | INTEGER | PRIMARY KEY | 自動遞增 ID |
| `source_file` | TEXT | NOT NULL | CSV 檔案名稱，如 `danbooru.csv` |
| `name` | TEXT | NOT NULL | 標籤名稱，未標準化 |
| `danbooru_cat` | INTEGER | - | Danbooru 分類，可為 NULL |
| `post_count` | INTEGER | DEFAULT 0 | 使用次數 |
| `loaded_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 載入時間 |

**範例資料:**
```
id | source_file      | name            | danbooru_cat | post_count | loaded_at
---|------------------|-----------------|--------------|------------|---------------------
1  | danbooru.csv     | school_uniform  | 0            | 15234      | 2025-10-08 10:00:00
2  | e621.csv         | school_uniform  | 0            | 3421       | 2025-10-08 10:00:05
3  | danbooru.csv     | from_above      | 0            | 8921       | 2025-10-08 10:00:00
```

---

### 3.2 tags_final (最終資料表)

**用途:** 儲存合併、去重、分類後的最終標籤資料，作為黃金資料資產。

**Schema:**
```sql
CREATE TABLE tags_final (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,           -- 標籤名稱（唯一）
    danbooru_cat INTEGER NOT NULL,       -- Danbooru 原始分類 (0-5)
    
    -- 階層式分類欄位
    main_category TEXT,                  -- 主分類（9 選 1 或 NULL）
    sub_category TEXT,                   -- 副分類（可選）
    
    -- 統計欄位
    post_count INTEGER DEFAULT 0,        -- 合併後的總使用次數
    source_count INTEGER DEFAULT 1,      -- 來源檔案數量
    
    -- 時間戳記
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 約束
    CHECK (danbooru_cat BETWEEN 0 AND 5),
    CHECK (post_count >= 0),
    CHECK (source_count >= 1)
);

-- 索引
CREATE UNIQUE INDEX idx_tags_final_name ON tags_final(name);
CREATE INDEX idx_tags_final_danbooru_cat ON tags_final(danbooru_cat);
CREATE INDEX idx_tags_final_main_cat ON tags_final(main_category);
CREATE INDEX idx_tags_final_sub_cat ON tags_final(sub_category);
CREATE INDEX idx_tags_final_main_sub ON tags_final(main_category, sub_category);
CREATE INDEX idx_tags_final_post_count ON tags_final(post_count DESC);

-- 全文搜尋索引 (FTS5)
CREATE VIRTUAL TABLE tags_search USING fts5(
    name, 
    main_category,
    sub_category,
    content='tags_final',
    content_rowid='id'
);
```

**欄位說明:**
| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| `id` | INTEGER | PRIMARY KEY | 自動遞增 ID |
| `name` | TEXT | NOT NULL UNIQUE | 標籤名稱（唯一），標準化後 |
| `danbooru_cat` | INTEGER | NOT NULL, CHECK | Danbooru 分類 (0-5) |
| `main_category` | TEXT | - | 主分類，可為 NULL（未分類） |
| `sub_category` | TEXT | - | 副分類，可為 NULL |
| `post_count` | INTEGER | DEFAULT 0, CHECK | 所有來源的 post_count 總和 |
| `source_count` | INTEGER | DEFAULT 1, CHECK | 出現在幾個來源檔案中 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 建立時間 |

**範例資料:**
```
id | name            | danbooru_cat | main_category      | sub_category    | post_count | source_count
---|-----------------|--------------|--------------------|-----------------|-----------:|------------:
1  | school_uniform  | 0            | CHARACTER_RELATED  | CLOTHING        |     18655  |           2
2  | from_above      | 0            | COMPOSITION        | NULL            |      8921  |           1
3  | 1girl           | 0            | CHARACTER_RELATED  | CHARACTER_COUNT |    123456  |           1
4  | smile           | 0            | ACTION_POSE        | EXPRESSION      |     56789  |           1
5  | indoors         | 0            | ENVIRONMENT        | NULL            |     34567  |           1
6  | anime           | 0            | ART_STYLE          | NULL            |      5432  |           1
```

---

## 4. 分類系統 (Classification System)

### 4.1 主分類 (Main Categories)

**9 個頂層類別:**

| 代碼 | 中文名稱 | 英文名稱 | 說明 | 範例標籤 |
|------|----------|----------|------|----------|
| QUALITY | 品質等級 | Quality | 圖像品質描述 | `masterpiece`, `best_quality` |
| TECHNICAL | 技術規格 | Technical | 技術性描述 | `monochrome`, `censored`, `animated` |
| ART_STYLE | 藝術風格 | Art Style | 藝術風格與媒材 | `anime`, `realistic`, `watercolor` |
| COMPOSITION | 構圖技法 | Composition | 鏡頭與構圖 | `from_above`, `close-up`, `portrait` |
| VISUAL_EFFECTS | 視覺效果 | Visual Effects | 光影與特效 | `bloom`, `lens_flare`, `depth_of_field` |
| CHARACTER_RELATED | 人物相關 | Character Related | 人物外觀、服裝 | `1girl`, `school_uniform`, `long_hair` |
| ACTION_POSE | 動作姿態 | Action & Pose | 動作、姿勢、表情 | `sitting`, `smile`, `running` |
| OBJECTS | 物件道具 | Objects | 物件與道具 | `sword`, `flower`, `book` |
| ENVIRONMENT | 場景環境 | Environment | 場景與環境 | `indoors`, `outdoors`, `sky` |

**優先級順序:** QUALITY > TECHNICAL > ART_STYLE > COMPOSITION > VISUAL_EFFECTS > CHARACTER_RELATED > ACTION_POSE > OBJECTS > ENVIRONMENT

### 4.2 副分類 (Sub-Categories)

**Phase 1 實作範圍:**

#### CHARACTER_RELATED 副分類

| 代碼 | 中文名稱 | 說明 | 範例標籤 |
|------|----------|------|----------|
| CLOTHING | 服裝 | 服裝類型 | `school_uniform`, `dress`, `shirt` |
| HAIR | 頭髮 | 髮型、髮色 | `long_hair`, `ponytail`, `blonde_hair` |
| CHARACTER_COUNT | 角色數量 | 角色數量描述 | `solo`, `1girl`, `2girls`, `multiple_girls` |

#### ACTION_POSE 副分類

| 代碼 | 中文名稱 | 說明 | 範例標籤 |
|------|----------|------|----------|
| POSE | 姿勢 | 身體姿勢 | `sitting`, `standing`, `lying`, `kneeling` |
| EXPRESSION | 表情 | 面部表情 | `smile`, `blush`, `angry`, `crying` |

**未來擴展:** 其他主分類的副分類將在後續階段按需添加。

---

## 5. 資料流向 (Data Flow)

### 5.1 整體流程圖

```
┌─────────────────┐
│  CSV 檔案們     │
│  (data/raw/)    │
└────────┬────────┘
         │ 載入
         ↓
┌─────────────────┐
│   tags_raw      │  ← 原始資料表
│  (保留所有記錄) │
└────────┬────────┘
         │ 合併去重
         ↓
┌─────────────────┐
│  Pandas DF      │  ← 中間處理
│  (去重 + 聚合)  │
└────────┬────────┘
         │ 套用分類規則
         ↓
┌─────────────────┐
│  Pandas DF      │  ← 添加分類欄位
│  (含分類結果)   │
└────────┬────────┘
         │ 寫入資料庫
         ↓
┌─────────────────┐
│  tags_final     │  ← 最終資料表
│  + tags_search  │  ← FTS5 索引
└─────────────────┘
```

### 5.2 詳細轉換步驟

#### 步驟 1: 載入 CSV → tags_raw

**輸入:** CSV 檔案
**輸出:** tags_raw 表
**轉換邏輯:**
```python
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    
    # 標準化欄位名稱
    df = standardize_columns(df)
    
    # 添加來源檔案欄位
    df['source_file'] = csv_file.name
    
    # 資料驗證
    df = validate_records(df)
    
    # 插入資料庫
    df.to_sql('tags_raw', conn, if_exists='append', index=False)
```

**資料變化範例:**
```
CSV:
  name,category,post_count
  school_uniform,0,15234

→ tags_raw:
  id=1, source_file='danbooru.csv', name='school_uniform', 
  danbooru_cat=0, post_count=15234, loaded_at='2025-10-08 10:00:00'
```

#### 步驟 2: tags_raw → 合併去重

**輸入:** tags_raw 表
**輸出:** Pandas DataFrame (去重後)
**轉換邏輯:**
```sql
SELECT 
    name,
    MODE(danbooru_cat) as danbooru_cat,  -- 選擇最常出現的值
    SUM(post_count) as post_count,
    COUNT(DISTINCT source_file) as source_count
FROM tags_raw
GROUP BY name
```

**資料變化範例:**
```
tags_raw:
  name='school_uniform', danbooru_cat=0, post_count=15234, source_file='danbooru.csv'
  name='school_uniform', danbooru_cat=0, post_count=3421,  source_file='e621.csv'

→ DataFrame:
  name='school_uniform', danbooru_cat=0, post_count=18655, source_count=2
```

#### 步驟 3: DataFrame → 套用分類

**輸入:** 去重後的 DataFrame
**輸出:** 添加分類欄位的 DataFrame
**轉換邏輯:**
```python
def apply_classification(df):
    # 對每個 danbooru_cat=0 的標籤進行分類
    mask = df['danbooru_cat'] == 0
    
    # 套用分類函式
    results = df.loc[mask, 'name'].apply(classify_tag)
    df.loc[mask, 'main_category'] = [r[0] for r in results]
    df.loc[mask, 'sub_category'] = [r[1] for r in results]
    
    # 非一般標籤不分類
    df.loc[~mask, 'main_category'] = None
    df.loc[~mask, 'sub_category'] = None
    
    return df
```

**資料變化範例:**
```
Before:
  name='school_uniform', danbooru_cat=0, post_count=18655, source_count=2

→ After:
  name='school_uniform', danbooru_cat=0, post_count=18655, source_count=2,
  main_category='CHARACTER_RELATED', sub_category='CLOTHING'
```

#### 步驟 4: DataFrame → tags_final

**輸入:** 含分類的 DataFrame
**輸出:** tags_final 表
**轉換邏輯:**
```python
df.to_sql('tags_final', conn, if_exists='replace', index=False)

# 建立索引
cursor.execute("CREATE UNIQUE INDEX idx_name ON tags_final(name)")
cursor.execute("CREATE INDEX idx_main_cat ON tags_final(main_category)")
# ... 其他索引
```

---

## 6. 資料驗證規則 (Validation Rules)

### 6.1 輸入驗證 (Input Validation)

**規則:**
1. `name` 不可為空字串
2. `name` 長度在 1-200 字元之間
3. `danbooru_cat` 必須在 0, 1, 3, 4, 5 之中
4. `post_count` 必須 ≥ 0

**實作:**
```python
def validate_record(record):
    errors = []
    
    # 驗證 name
    if not record['name'] or len(record['name'].strip()) == 0:
        errors.append('name 不可為空')
    elif len(record['name']) > 200:
        errors.append('name 過長（> 200 字元）')
    
    # 驗證 category
    if record['danbooru_cat'] not in [0, 1, 3, 4, 5]:
        errors.append(f'無效的 danbooru_cat: {record["danbooru_cat"]}')
    
    # 驗證 post_count
    if record['post_count'] < 0:
        errors.append('post_count 不可為負數')
    
    return len(errors) == 0, errors
```

### 6.2 輸出驗證 (Output Validation)

**規則:**
1. **唯一性:** `tags_final.name` 無重複值
2. **覆蓋率:** 主分類覆蓋率 ≥ 90% (針對 `danbooru_cat=0`)
3. **一致性:** `tags_final.post_count` 總和 = `tags_raw.post_count` 總和
4. **完整性:** 所有 NOT NULL 欄位無 NULL 值

**實作:**
```python
def validate_output(db_path):
    conn = sqlite3.connect(db_path)
    errors = []
    
    # 檢查唯一性
    result = conn.execute("""
        SELECT COUNT(*), COUNT(DISTINCT name) FROM tags_final
    """).fetchone()
    if result[0] != result[1]:
        errors.append(f'name 有重複值：{result[0] - result[1]} 筆')
    
    # 檢查覆蓋率
    result = conn.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(main_category) as classified
        FROM tags_final
        WHERE danbooru_cat = 0
    """).fetchone()
    coverage = result[1] / result[0] if result[0] > 0 else 0
    if coverage < 0.9:
        errors.append(f'主分類覆蓋率不足：{coverage:.1%} < 90%')
    
    # 檢查一致性
    sum_raw = conn.execute("SELECT SUM(post_count) FROM tags_raw").fetchone()[0]
    sum_final = conn.execute("SELECT SUM(post_count) FROM tags_final").fetchone()[0]
    if sum_raw != sum_final:
        errors.append(f'post_count 不一致：raw={sum_raw}, final={sum_final}')
    
    conn.close()
    return errors
```

---

## 7. 查詢範例 (Query Examples)

### 7.1 基本查詢

```sql
-- 查詢所有服裝相關標籤
SELECT name, post_count
FROM tags_final
WHERE main_category = 'CHARACTER_RELATED' 
  AND sub_category = 'CLOTHING'
ORDER BY post_count DESC
LIMIT 100;

-- 查詢未分類的高頻標籤
SELECT name, post_count
FROM tags_final
WHERE danbooru_cat = 0 
  AND main_category IS NULL
ORDER BY post_count DESC
LIMIT 50;

-- 統計各主分類的標籤數量
SELECT 
    main_category,
    COUNT(*) as tag_count,
    SUM(post_count) as total_usage
FROM tags_final
WHERE danbooru_cat = 0
GROUP BY main_category
ORDER BY tag_count DESC;
```

### 7.2 全文搜尋

```sql
-- 使用 FTS5 搜尋標籤
SELECT 
    tf.name, 
    tf.main_category, 
    tf.sub_category, 
    tf.post_count
FROM tags_search ts
JOIN tags_final tf ON ts.rowid = tf.id
WHERE tags_search MATCH 'uniform'
ORDER BY tf.post_count DESC;
```

### 7.3 分類統計

```sql
-- 主分類與副分類的分佈
SELECT 
    main_category,
    sub_category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tags_final WHERE danbooru_cat = 0), 2) as percentage
FROM tags_final
WHERE danbooru_cat = 0
GROUP BY main_category, sub_category
ORDER BY count DESC;
```

---

## 8. 效能考量 (Performance Considerations)

### 8.1 索引策略

**必要索引:**
- `tags_final.name` (UNIQUE): 確保唯一性，加速查詢
- `tags_final.main_category`: 加速分類過濾
- `tags_final.post_count DESC`: 加速排序

**可選索引:**
- `tags_final.(main_category, sub_category)`: 複合索引，加速階層查詢

### 8.2 資料量預估

| 項目 | 預估值 | 說明 |
|------|--------|------|
| 原始記錄數 (tags_raw) | 150,000 | 多個來源有重複 |
| 唯一標籤數 (tags_final) | 100,000 | 去重後 |
| 資料庫檔案大小 | ~50 MB | 含索引 |
| 查詢速度 | < 100 ms | 索引查詢 |

---

## 9. 變更記錄 (Change Log)

| 版本 | 日期 | 變更內容 | 作者 |
|------|------|----------|------|
| 1.0.0 | 2025-10-08 | 初始版本 - Phase 1 資料模型 | Prompt-Scribe Team |

---

**資料模型文件結束 (End of Data Model Document)**

