# 分類層級系統設計文檔

## 設計日期
2025-10-13

## 設計目標
實現**分類層級系統 (Classification Hierarchy)**，允許標籤擁有主分類和次要分類，以解決分類邊界模糊的問題。

---

## 📋 核心概念

### 方案 B: 分類層級

```
標籤分類結構：
├── 主分類 (Primary Category) - 必填
│   └── 主副分類 (Primary Sub-category) - 可選
└── 次要分類 (Secondary Category) - 可選
    └── 次要副分類 (Secondary Sub-category) - 可選
```

### 設計原則

1. **主分類優先**: 用於基本篩選和主要特徵識別
2. **次要分類補充**: 提供額外的分類維度和檢索能力
3. **保持向後兼容**: 不影響現有的單一分類標籤
4. **信心度分離**: 主分類和次要分類各有獨立的信心度

---

## 🗄️ 數據庫架構設計

### 現有架構
```sql
CREATE TABLE tags_final (
    name TEXT PRIMARY KEY,
    danbooru_cat INTEGER,
    post_count INTEGER,
    main_category TEXT,
    sub_category TEXT,
    classification_source TEXT,
    classification_confidence REAL,
    classification_reasoning TEXT,
    classification_timestamp TEXT
);
```

### 擴展架構（向後兼容）
```sql
-- 保留原有欄位作為主分類
-- main_category          -> 主分類
-- sub_category           -> 主副分類
-- classification_confidence -> 主分類信心度

-- 新增欄位用於次要分類
ALTER TABLE tags_final ADD COLUMN secondary_category TEXT;
ALTER TABLE tags_final ADD COLUMN secondary_sub_category TEXT;
ALTER TABLE tags_final ADD COLUMN secondary_confidence REAL;
ALTER TABLE tags_final ADD COLUMN secondary_reasoning TEXT;
```

### 完整架構
```sql
CREATE TABLE tags_final_v2 (
    -- 基本資訊
    name TEXT PRIMARY KEY,
    danbooru_cat INTEGER,
    post_count INTEGER,
    
    -- 主分類（原有）
    main_category TEXT,                    -- 主分類
    sub_category TEXT,                     -- 主副分類
    classification_source TEXT,            -- 分類來源
    classification_confidence REAL,        -- 主分類信心度
    classification_reasoning TEXT,         -- 主分類理由
    classification_timestamp TEXT,         -- 分類時間戳
    
    -- 次要分類（新增）
    secondary_category TEXT,               -- 次要分類
    secondary_sub_category TEXT,           -- 次要副分類
    secondary_confidence REAL,             -- 次要分類信心度
    secondary_reasoning TEXT,              -- 次要分類理由
    
    -- 分類屬性（新增）
    is_ambiguous BOOLEAN DEFAULT 0,        -- 是否為模糊分類標籤
    classification_note TEXT               -- 分類註記
);
```

---

## 🎯 適用場景

### 場景 1: 顏色 + 物品組合

**案例**: `blue_dress`
```json
{
  "name": "blue_dress",
  "primary": {
    "main_category": "CHARACTER_RELATED",
    "sub_category": "CLOTHING",
    "confidence": 0.95,
    "reasoning": "主要描述服裝類型"
  },
  "secondary": {
    "main_category": "VISUAL_EFFECTS",
    "sub_category": "COLORS",
    "confidence": 0.85,
    "reasoning": "顏色屬性提供額外的視覺特徵"
  }
}
```

### 場景 2: 動作 + 構圖

**案例**: `leaning_forward`
```json
{
  "name": "leaning_forward",
  "primary": {
    "main_category": "ACTION_POSE",
    "sub_category": "BODY_POSE",
    "confidence": 0.90,
    "reasoning": "主要描述身體姿勢"
  },
  "secondary": {
    "main_category": "COMPOSITION",
    "sub_category": "PERSPECTIVE",
    "confidence": 0.75,
    "reasoning": "可能影響構圖和透視效果"
  }
}
```

### 場景 3: 角色類型 + 服裝

**案例**: `witch`
```json
{
  "name": "witch",
  "primary": {
    "main_category": "THEME_CONCEPT",
    "sub_category": "CONCEPT",
    "confidence": 0.85,
    "reasoning": "主要表達角色概念"
  },
  "secondary": {
    "main_category": "CHARACTER_RELATED",
    "sub_category": "CLOTHING",
    "confidence": 0.70,
    "reasoning": "通常伴隨特定服裝風格"
  }
}
```

### 場景 4: 物品 + 用途

**案例**: `sword`
```json
{
  "name": "sword",
  "primary": {
    "main_category": "OBJECTS",
    "sub_category": "WEAPONS",
    "confidence": 0.98,
    "reasoning": "主要是武器物品"
  },
  "secondary": {
    "main_category": "ACTION_POSE",
    "sub_category": "PROPS",
    "confidence": 0.80,
    "reasoning": "經常作為動作道具使用"
  }
}
```

---

## 🔧 實施步驟

### Phase 1: 數據庫遷移（立即）

1. **添加新欄位**
```sql
-- 執行遷移腳本
ALTER TABLE tags_final ADD COLUMN secondary_category TEXT;
ALTER TABLE tags_final ADD COLUMN secondary_sub_category TEXT;
ALTER TABLE tags_final ADD COLUMN secondary_confidence REAL;
ALTER TABLE tags_final ADD COLUMN secondary_reasoning TEXT;
ALTER TABLE tags_final ADD COLUMN is_ambiguous BOOLEAN DEFAULT 0;
ALTER TABLE tags_final ADD COLUMN classification_note TEXT;
```

2. **驗證遷移**
```python
# 檢查新欄位是否正確添加
import sqlite3
conn = sqlite3.connect('output/tags.db')
cursor = conn.cursor()
result = cursor.execute("PRAGMA table_info(tags_final)").fetchall()
for row in result:
    print(row)
```

### Phase 2: 識別模糊分類標籤（1-2 天）

1. **自動識別**
```python
# 識別低信心度標籤
ambiguous_candidates = execute('''
    SELECT name, main_category, sub_category, classification_confidence
    FROM tags_final
    WHERE classification_confidence < 0.85
    AND main_category IS NOT NULL
    ORDER BY post_count DESC
''')
```

2. **人工審核**
   - 審核前 100 個高頻低信心度標籤
   - 判斷是否需要次要分類
   - 標記為 `is_ambiguous = 1`

### Phase 3: 批量添加次要分類（1 周）

1. **創建規則庫**
```python
# 顏色 + 物品規則
COLOR_ITEM_RULES = {
    'pattern': r'(red|blue|green|...)_(dress|shirt|...)',
    'primary': 'CHARACTER_RELATED/CLOTHING',
    'secondary': 'VISUAL_EFFECTS/COLORS'
}

# 動作 + 構圖規則
ACTION_COMPOSITION_RULES = {
    'pattern': r'(leaning|bending|looking)_(forward|back|...)',
    'primary': 'ACTION_POSE/BODY_POSE',
    'secondary': 'COMPOSITION/PERSPECTIVE'
}
```

2. **LLM 輔助分類**
```python
# 優化提示詞以支持次要分類
prompt = f"""
請為標籤提供主分類和可選的次要分類：

標籤: {tag_name}

如果標籤具有多重屬性，請提供：
1. 主分類：最主要的特徵
2. 次要分類：次要但重要的特徵

JSON 格式：
{{
  "primary": {{
    "main_category": "...",
    "sub_category": "...",
    "confidence": 0.95,
    "reasoning": "..."
  }},
  "secondary": {{  // 可選
    "main_category": "...",
    "sub_category": "...",
    "confidence": 0.80,
    "reasoning": "..."
  }}
}}
"""
```

### Phase 4: API 和查詢支持（2 周）

1. **查詢接口**
```python
def search_tags(
    primary_category=None,
    primary_sub_category=None,
    secondary_category=None,
    secondary_sub_category=None,
    include_ambiguous=True
):
    """
    支持多層級分類查詢
    """
    query = "SELECT * FROM tags_final WHERE 1=1"
    params = []
    
    if primary_category:
        query += " AND main_category = ?"
        params.append(primary_category)
    
    if secondary_category:
        query += " AND secondary_category = ?"
        params.append(secondary_category)
    
    if not include_ambiguous:
        query += " AND is_ambiguous = 0"
    
    return execute(query, params)
```

2. **統計接口**
```python
def get_classification_stats():
    """
    獲取分類統計，包括次要分類
    """
    return {
        'primary_distribution': count_by_category('main_category'),
        'secondary_distribution': count_by_category('secondary_category'),
        'ambiguous_count': count_ambiguous_tags(),
        'dual_classified': count_dual_classified_tags()
    }
```

---

## 📊 預期效果

### 量化指標

| 指標 | 預期值 |
|------|--------|
| 擁有次要分類的標籤數 | 500-1,000 個 |
| 模糊分類標籤標記數 | 100-200 個 |
| 分類精確度提升 | +5% |
| 檢索相關性提升 | +10% |

### 質化改進

1. **更精確的檢索**
   - 用戶可以同時按主分類和次要分類篩選
   - 例如：找出所有「服裝 + 藍色」的標籤

2. **更好的分類理解**
   - 明確標示標籤的多重屬性
   - 減少分類爭議

3. **更靈活的擴展**
   - 未來可以添加第三、第四分類
   - 支持複雜的分類關係

---

## ⚠️ 注意事項

### 不要過度使用

```
❌ 錯誤：為所有標籤都添加次要分類
✅ 正確：只為真正具有多重屬性的標籤添加次要分類

例如：
- "dress" 不需要次要分類 (單一屬性)
- "blue_dress" 適合次要分類 (顏色 + 服裝)
```

### 保持簡潔

```
❌ 錯誤：添加 3-4 個分類
✅ 正確：最多 2 個分類（主 + 次要）

複雜度管理：
- 主分類：必填
- 次要分類：選填，且僅在確實有價值時使用
- 信心度閾值：次要分類信心度應 >= 0.70
```

### 向後兼容

```
✅ 確保：
- 現有查詢不受影響
- 默認查詢使用主分類
- 次要分類作為可選增強功能
```

---

## 🚀 未來擴展

### 分類權重系統

```python
# 為不同分類賦予權重
tag_classification = {
    "name": "blue_dress",
    "classifications": [
        {
            "category": "CHARACTER_RELATED/CLOTHING",
            "weight": 0.7,  # 主要屬性
            "confidence": 0.95
        },
        {
            "category": "VISUAL_EFFECTS/COLORS",
            "weight": 0.3,  # 次要屬性
            "confidence": 0.85
        }
    ]
}
```

### 分類關係圖譜

```
建立分類之間的關係網絡：
- 互補關係：服裝 + 顏色
- 包含關係：動作 ⊃ 手勢
- 衝突關係：室內 ⊗ 室外
```

### 上下文相關分類

```python
# 根據查詢上下文動態調整分類權重
def contextual_classification(tag, context):
    if context == "character_design":
        # 優先顯示人物相關分類
        return prioritize(tag, "CHARACTER_RELATED")
    elif context == "scene_composition":
        # 優先顯示構圖相關分類
        return prioritize(tag, "COMPOSITION")
```

---

## 📝 實施時間表

| 階段 | 時間 | 任務 |
|------|------|------|
| **Phase 1** | 立即 | 數據庫遷移 |
| **Phase 2** | 1-2 天 | 識別模糊標籤 |
| **Phase 3** | 1 周 | 添加次要分類 |
| **Phase 4** | 2 周 | API 和查詢支持 |
| **Phase 5** | 持續 | 優化和擴展 |

**總計**: 約 3-4 週完成基礎實施

---

## ✅ 驗收標準

1. ✅ 數據庫成功遷移，無數據丟失
2. ✅ 至少 500 個標籤擁有次要分類
3. ✅ 查詢 API 正常工作
4. ✅ 向後兼容性測試通過
5. ✅ 文檔完整，包含使用範例

---

## 📚 參考資料

- [Danbooru Tag Categories](https://danbooru.donmai.us/wiki_pages/howto:tag)
- [Multi-label Classification Best Practices](https://scikit-learn.org/stable/modules/multiclass.html)
- [Hierarchical Classification Systems](https://en.wikipedia.org/wiki/Hierarchical_classification)

---

**文檔版本**: v1.0  
**最後更新**: 2025-10-13  
**狀態**: 設計階段 → 待實施
