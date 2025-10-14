# 資料模型設計：SQLite 遷移至 Supabase

**專案：** PLAN-2025-004  
**建立日期：** 2025-10-14  
**版本：** 1.0.0

---

## 概述

本文件定義 Supabase 資料庫的完整資料模型，包含表結構、關聯關係、索引設計和驗證規則。

---

## 1. 實體定義 (Entity Definitions)

### 1.1 標籤實體 (Tag Entity)

**實體名稱：** tags_final

**用途：** 儲存所有標籤的基本資訊和分類資料

**資料來源：** 階段一產出的 `tags.db` 中的 `tags_final` 表

#### 欄位定義

| 欄位名稱 | 資料型別 | 必填 | 唯一 | 預設值 | 說明 |
|---------|---------|------|------|--------|------|
| id | TEXT | ✅ | ✅ | UUID | 主鍵，唯一識別標籤 |
| name | TEXT | ✅ | ✅ | - | 標籤名稱（英文，小寫，底線分隔） |
| danbooru_cat | INTEGER | ✅ | ❌ | - | Danbooru 原始分類（0-5） |
| post_count | INTEGER | ✅ | ❌ | 0 | 使用次數（越高表示越常用） |
| main_category | TEXT | ❌ | ❌ | NULL | 主分類（14 個類別之一） |
| sub_category | TEXT | ❌ | ❌ | NULL | 副分類（依主分類而定） |
| confidence | REAL | ❌ | ❌ | NULL | 分類信心度（0.0-1.0） |
| classification_source | TEXT | ❌ | ❌ | NULL | 分類來源（rule / llm / manual） |
| created_at | TIMESTAMP | ✅ | ❌ | NOW() | 記錄建立時間 |
| updated_at | TIMESTAMP | ✅ | ❌ | NOW() | 記錄更新時間 |

#### 約束條件

```sql
-- 主鍵約束
PRIMARY KEY (id)

-- 唯一性約束
UNIQUE (name)

-- 檢查約束
CHECK (danbooru_cat >= 0 AND danbooru_cat <= 5)
CHECK (post_count >= 0)
CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0))
CHECK (classification_source IN ('rule', 'llm', 'manual', NULL))
```

#### Danbooru 分類對照

| danbooru_cat | 說明 | 處理方式 |
|-------------|------|---------|
| 0 | 一般標籤 | 需要分類至 14 個主分類 |
| 1 | 藝術家 | 直接映射至 ARTIST |
| 3 | 版權作品 | 直接映射至 COPYRIGHT |
| 4 | 角色 | 直接映射至 CHARACTER |
| 5 | 元資訊 | 映射至 TECHNICAL / QUALITY |

#### 範例資料

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "school_uniform",
  "danbooru_cat": 0,
  "post_count": 15234,
  "main_category": "CHARACTER_RELATED",
  "sub_category": "CLOTHING",
  "confidence": 0.95,
  "classification_source": "rule",
  "created_at": "2025-10-14T10:00:00Z",
  "updated_at": "2025-10-14T10:00:00Z"
}
```

---

### 1.2 向量嵌入實體 (Tag Embedding Entity)

**實體名稱：** tag_embeddings

**用途：** 儲存標籤的向量表示，用於語意搜尋

**資料來源：** 透過 OpenAI Embeddings API 生成

#### 欄位定義

| 欄位名稱 | 資料型別 | 必填 | 唯一 | 預設值 | 說明 |
|---------|---------|------|------|--------|------|
| id | SERIAL | ✅ | ✅ | AUTO | 主鍵，自動遞增 |
| tag_name | TEXT | ✅ | ✅ | - | 標籤名稱（外鍵至 tags_final.name） |
| embedding | VECTOR(1536) | ✅ | ❌ | - | 1536 維向量 |
| model | TEXT | ✅ | ❌ | 'text-embedding-3-small' | 使用的嵌入模型 |
| created_at | TIMESTAMP | ✅ | ❌ | NOW() | 記錄建立時間 |

#### 約束條件

```sql
-- 主鍵約束
PRIMARY KEY (id)

-- 唯一性約束
UNIQUE (tag_name)

-- 外鍵約束
FOREIGN KEY (tag_name) REFERENCES tags_final(name) ON DELETE CASCADE

-- 檢查約束
CHECK (model IN ('text-embedding-3-small', 'text-embedding-3-large'))
```

#### 範例資料

```json
{
  "id": 1,
  "tag_name": "school_uniform",
  "embedding": [0.012, -0.034, 0.056, ..., 0.089],  // 1536 個浮點數
  "model": "text-embedding-3-small",
  "created_at": "2025-10-14T12:00:00Z"
}
```

---

### 1.3 遷移日誌實體 (Migration Log Entity)

**實體名稱：** migration_log

**用途：** 記錄遷移過程中的所有操作，用於審計和除錯

**資料來源：** 遷移工具自動生成

#### 欄位定義

| 欄位名稱 | 資料型別 | 必填 | 唯一 | 預設值 | 說明 |
|---------|---------|------|------|--------|------|
| id | SERIAL | ✅ | ✅ | AUTO | 主鍵，自動遞增 |
| migration_batch | TEXT | ✅ | ❌ | - | 遷移批次識別碼 |
| operation | TEXT | ✅ | ❌ | - | 操作類型 |
| records_affected | INTEGER | ✅ | ❌ | 0 | 影響的記錄數 |
| status | TEXT | ✅ | ❌ | - | 狀態（success / failed / pending） |
| error_message | TEXT | ❌ | ❌ | NULL | 錯誤訊息（若失敗） |
| started_at | TIMESTAMP | ✅ | ❌ | - | 操作開始時間 |
| completed_at | TIMESTAMP | ❌ | ❌ | NULL | 操作完成時間 |
| duration_seconds | REAL | ❌ | ❌ | NULL | 執行時間（秒） |

#### 約束條件

```sql
-- 主鍵約束
PRIMARY KEY (id)

-- 檢查約束
CHECK (status IN ('success', 'failed', 'pending'))
CHECK (records_affected >= 0)
CHECK (duration_seconds IS NULL OR duration_seconds >= 0)
```

#### 操作類型

| operation | 說明 |
|-----------|------|
| create_schema | 建立資料庫結構 |
| upload_batch | 批次上傳資料 |
| generate_embeddings | 生成向量嵌入 |
| create_index | 建立索引 |
| validate_data | 驗證資料完整性 |
| api_call | LLM API 呼叫 |

#### 範例資料

```json
{
  "id": 1,
  "migration_batch": "batch_001",
  "operation": "upload_batch",
  "records_affected": 500,
  "status": "success",
  "error_message": null,
  "started_at": "2025-10-14T10:00:00Z",
  "completed_at": "2025-10-14T10:00:12Z",
  "duration_seconds": 12.5
}
```

---

## 2. 實體關聯圖 (Entity Relationship Diagram)

```
┌─────────────────┐
│   tags_final    │
│─────────────────│
│ id (PK)         │
│ name (UK)       │
│ danbooru_cat    │
│ post_count      │
│ main_category   │
│ sub_category    │
│ confidence      │
│ ...             │
└─────────────────┘
         │ 1
         │
         │ 1:1
         │
         ▼
┌─────────────────┐
│ tag_embeddings  │
│─────────────────│
│ id (PK)         │
│ tag_name (FK)   │◄──────── references tags_final.name
│ embedding       │
│ model           │
│ ...             │
└─────────────────┘


┌─────────────────┐
│ migration_log   │
│─────────────────│
│ id (PK)         │
│ operation       │
│ status          │
│ ...             │
└─────────────────┘
  (獨立表，用於審計)
```

**關聯說明：**

1. **tags_final ↔ tag_embeddings**：一對一關係
   - 每個標籤最多有一個向量嵌入
   - 透過 `tag_name` 欄位連結
   - 使用 ON DELETE CASCADE，刪除標籤時自動刪除其向量

2. **migration_log**：獨立表
   - 不與其他表建立外鍵關聯
   - 純審計用途

---

## 3. 索引設計 (Index Design)

### 3.1 tags_final 表索引

```sql
-- 主鍵索引（自動建立）
-- PRIMARY KEY (id)

-- 唯一索引（自動建立）
-- UNIQUE (name)

-- 查詢優化索引
CREATE INDEX idx_tags_main_category 
ON tags_final(main_category)
WHERE main_category IS NOT NULL;

CREATE INDEX idx_tags_sub_category 
ON tags_final(sub_category)
WHERE sub_category IS NOT NULL;

CREATE INDEX idx_tags_post_count 
ON tags_final(post_count DESC);

CREATE INDEX idx_tags_confidence 
ON tags_final(confidence DESC)
WHERE confidence IS NOT NULL;

CREATE INDEX idx_tags_danbooru_cat 
ON tags_final(danbooru_cat);

-- 複合索引（支援常見查詢模式）
CREATE INDEX idx_tags_category_count 
ON tags_final(main_category, post_count DESC)
WHERE main_category IS NOT NULL;

CREATE INDEX idx_tags_source_confidence 
ON tags_final(classification_source, confidence DESC)
WHERE classification_source IS NOT NULL;
```

**索引使用場景：**

| 索引 | 查詢模式 | 預期效能提升 |
|------|---------|-------------|
| idx_tags_main_category | 按分類篩選 | 50-100x |
| idx_tags_post_count | 按熱度排序 | 20-50x |
| idx_tags_category_count | 分類內排序 | 10-30x |

### 3.2 tag_embeddings 表索引

```sql
-- 主鍵索引（自動建立）
-- PRIMARY KEY (id)

-- 唯一索引（自動建立）
-- UNIQUE (tag_name)

-- 向量相似度索引
CREATE INDEX idx_tag_embeddings_vector 
ON tag_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**向量索引配置說明：**
- `lists = 100`：將向量空間分為 100 個區域
- `vector_cosine_ops`：使用餘弦相似度運算子
- 預期查詢時間：< 100ms（10 萬筆資料）

### 3.3 migration_log 表索引

```sql
-- 主鍵索引（自動建立）
-- PRIMARY KEY (id)

-- 查詢優化索引
CREATE INDEX idx_migration_batch 
ON migration_log(migration_batch);

CREATE INDEX idx_migration_status 
ON migration_log(status);

CREATE INDEX idx_migration_time 
ON migration_log(started_at DESC);
```

---

## 4. 資料驗證規則 (Validation Rules)

### 4.1 輸入驗證（遷移時）

```python
from pydantic import BaseModel, Field, validator

class TagInput(BaseModel):
    """標籤輸入資料驗證"""
    
    name: str = Field(..., min_length=1, max_length=200)
    danbooru_cat: int = Field(..., ge=0, le=5)
    post_count: int = Field(default=0, ge=0)
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    classification_source: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        """驗證標籤名稱格式"""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        if not v.replace('_', '').replace('-', '').replace('(', '').replace(')', '').isalnum():
            raise ValueError('Name contains invalid characters')
        return v.lower()
    
    @validator('main_category')
    def validate_main_category(cls, v):
        """驗證主分類"""
        if v is None:
            return v
        VALID_CATEGORIES = [
            'CHARACTER_RELATED', 'CHARACTER', 'OBJECTS', 'ENVIRONMENT',
            'COMPOSITION', 'VISUAL_EFFECTS', 'ART_STYLE', 'ACTION_POSE',
            'COPYRIGHT', 'ARTIST', 'QUALITY', 'TECHNICAL',
            'ADULT_CONTENT', 'THEME_CONCEPT'
        ]
        if v not in VALID_CATEGORIES:
            raise ValueError(f'Invalid main_category: {v}')
        return v
    
    @validator('classification_source')
    def validate_source(cls, v):
        """驗證分類來源"""
        if v is None:
            return v
        if v not in ['rule', 'llm', 'manual']:
            raise ValueError(f'Invalid classification_source: {v}')
        return v
```

### 4.2 輸出驗證（遷移後）

```python
def validate_migrated_data():
    """驗證遷移後的資料完整性"""
    
    # 1. 記錄數量檢查
    assert_record_count_match()
    
    # 2. 資料類型檢查
    assert_all_ids_are_uuid()
    assert_all_post_counts_positive()
    assert_all_confidences_in_range()
    
    # 3. 外鍵完整性檢查
    assert_no_orphaned_embeddings()
    
    # 4. 業務邏輯檢查
    assert_danbooru_cat_mapping()
    assert_confidence_exists_if_classified()
```

### 4.3 一致性規則

| 規則 | 說明 | 驗證方式 |
|------|------|---------|
| R1 | 每個標籤名稱必須唯一 | UNIQUE 約束 |
| R2 | post_count 必須非負 | CHECK 約束 |
| R3 | confidence 在 0-1 範圍內 | CHECK 約束 + Pydantic |
| R4 | 有 main_category 則必須有 confidence | 業務邏輯檢查 |
| R5 | embedding 的 tag_name 必須存在於 tags_final | FOREIGN KEY 約束 |
| R6 | danbooru_cat 在 0-5 範圍內 | CHECK 約束 |

---

## 5. 狀態轉換 (State Transitions)

### 5.1 標籤分類狀態

```
┌─────────────┐
│ Unclassified│ (main_category = NULL)
└──────┬──────┘
       │ 規則式分類 / LLM 分類
       ▼
┌─────────────┐
│  Classified │ (main_category != NULL, confidence > 0)
└──────┬──────┘
       │ 向量生成
       ▼
┌─────────────┐
│  Vectorized │ (有對應的 tag_embedding)
└─────────────┘
```

**狀態查詢：**

```sql
-- 未分類標籤
SELECT COUNT(*) FROM tags_final WHERE main_category IS NULL;

-- 已分類標籤
SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL;

-- 已向量化標籤
SELECT COUNT(*) FROM tags_final t
INNER JOIN tag_embeddings e ON t.name = e.tag_name;
```

### 5.2 遷移狀態

```
┌─────────────┐
│   Pending   │ (遷移開始前)
└──────┬──────┘
       │ 開始遷移
       ▼
┌─────────────┐
│ In Progress │ (批次上傳中)
└──────┬──────┘
       │ 完成所有批次
       ▼
┌─────────────┐
│  Completed  │ (資料驗證通過)
└─────────────┘
```

---

## 6. 資料統計 (Data Statistics)

### 6.1 預期資料量

| 表 | 記錄數 | 單筆大小 | 總大小 |
|----|--------|---------|--------|
| tags_final | 140,782 | ~500 bytes | ~70 MB |
| tag_embeddings | 139,374 (99%) | ~6 KB | ~845 MB |
| migration_log | ~300 | ~200 bytes | ~60 KB |
| **總計** | | | **~915 MB** |

### 6.2 分類分佈（預期）

| main_category | 標籤數 | 百分比 |
|--------------|--------|--------|
| CHARACTER_RELATED | 45,231 | 32.1% |
| ENVIRONMENT | 12,567 | 8.9% |
| ACTION_POSE | 18,934 | 13.4% |
| COMPOSITION | 8,421 | 6.0% |
| 其他 | 55,629 | 39.6% |

---

## 7. 資料生命週期 (Data Lifecycle)

### 7.1 資料建立

```python
# 1. 從 SQLite 讀取
tag_data = read_from_sqlite(tag_name)

# 2. 轉換格式
transformed_data = transform_to_supabase_format(tag_data)

# 3. 驗證資料
validated_data = validate_tag_input(transformed_data)

# 4. 插入 Supabase
supabase.table('tags_final').insert(validated_data).execute()
```

### 7.2 向量生成

```python
# 1. 取得標籤名稱
tags = get_tags_without_embeddings()

# 2. 批次呼叫 API
embeddings = openai.embeddings.create(
    input=[tag.name for tag in tags],
    model="text-embedding-3-small"
)

# 3. 儲存向量
for tag, emb in zip(tags, embeddings.data):
    supabase.table('tag_embeddings').insert({
        'tag_name': tag.name,
        'embedding': emb.embedding,
        'model': 'text-embedding-3-small'
    }).execute()
```

### 7.3 資料查詢

```python
# 基本查詢
tags = supabase.table('tags_final').select('*').eq('main_category', 'CHARACTER_RELATED').execute()

# 語意搜尋
similar_tags = supabase.rpc('search_similar_tags', {
    'query_text': 'school uniform',
    'match_threshold': 0.7,
    'match_count': 10
}).execute()
```

### 7.4 資料更新

**本專案不涉及資料更新**，因為：
1. 資料為單向遷移（SQLite → Supabase）
2. 階段二不修改階段一的產出
3. 未來的更新應在階段一進行，然後重新遷移

---

## 8. 效能考量 (Performance Considerations)

### 8.1 查詢效能目標

| 查詢類型 | 目標延遲 | 優化策略 |
|---------|---------|---------|
| 按名稱查詢 | < 100ms | name 欄位唯一索引 |
| 按分類篩選 | < 500ms | main_category 索引 |
| 熱度排序 | < 1s | post_count 降序索引 |
| 語意搜尋 | < 3s | ivfflat 向量索引 |

### 8.2 儲存空間優化

- ✅ 使用 VECTOR(1536) 而非 TEXT：節省 ~40% 空間
- ✅ 只為有值的欄位建立索引（使用 WHERE 條件）
- ✅ 壓縮日誌表（定期歸檔舊記錄）

### 8.3 記憶體使用

- tags_final 表：~70 MB 記憶體
- tag_embeddings 表：~845 MB 記憶體
- 索引：~200 MB 記憶體
- **總計**：~1.1 GB（在 Supabase Free Tier 限制內）

---

## 9. 備份與恢復 (Backup and Recovery)

### 9.1 備份策略

1. **Supabase 自動備份**：每日自動備份（保留 7 天）
2. **本地 SQLite 保留**：`tags.db` 作為永久備份
3. **遷移日誌**：記錄所有操作，可用於審計

### 9.2 恢復流程

```bash
# 1. 清空目標表
truncate table tags_final cascade;
truncate table tag_embeddings cascade;
truncate table migration_log cascade;

# 2. 重新執行遷移
python migrate_to_supabase.py --source tags.db

# 3. 驗證資料
python validate_migration.py
```

---

## 10. 附錄：SQL Schema 完整腳本

參見：[contracts/database_schema.sql](./contracts/database_schema.sql)

---

**文件狀態：** ✅ 完成  
**最後更新：** 2025-10-14  
**審查狀態：** 待審查  
**對應規格：** SPEC-2025-002  
**對應計畫：** PLAN-2025-004

