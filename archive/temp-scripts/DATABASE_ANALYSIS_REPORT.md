# 📊 現有資料庫分析報告

**日期**: 2025-10-21  
**資料來源**: Supabase - tags_final 表  
**分析目的**: 評估如何整合 Inspire Agent

---

## 🔍 實際發現

### 1. 表結構（tags_final）

**實際欄位：**
```
- id (int) - 主鍵
- name (str) - 標籤名稱 ✅
- main_category (str) - 主分類 ✅
- sub_category (str) - 子分類 ✅
- post_count (int) - 使用次數 ✅
- confidence (float) - 分類信心度 ✅
- classification_source (str) - 分類來源
- danbooru_cat (int) - Danbooru 原始分類
- embedding (vector) - 嵌入向量
- created_at (timestamp)
- updated_at (timestamp)
```

**不存在的欄位（需要添加）：**
```
❌ aliases - 別名列表
❌ conflicts - 衝突標籤
❌ nsfw_level - 內容分級
❌ category - Inspire 類別系統
```

---

### 2. 資料統計

**總標籤數：** 140,782 個 ✅

**流行度分佈：**
```
>= 10,000 posts:  15,620 tags (11.10%)
>= 5,000 posts:   25,349 tags (18.01%)
>= 1,000 posts:   78,475 tags (55.74%) ← 超過半數！
>= 500 posts:    121,257 tags (86.13%)
>= 100 posts:    140,782 tags (100.00%)
```

**關鍵發現：**
- ✅ 55% 標籤有 >= 1000 使用次數（品質很高！）
- ✅ 流行度資料完整（可直接用於熱門池）
- ✅ 無垃圾資料（最低 100 posts）

**TOP 10 最熱門標籤：**
```
1. 1girl              - 96,138,304 posts
2. highres            - 84,099,120 posts
3. solo               - 80,015,264 posts
4. long_hair          - 69,611,888 posts
5. breasts            - 55,027,424 posts ← NSFW 內容存在
6. looking_at_viewer  - 53,051,552 posts
7. blush              - 47,084,672 posts
8. smile              - 45,982,240 posts
9. open_mouth         - 37,854,480 posts
10. short_hair        - 36,185,728 posts
```

---

### 3. 分類系統（main_category）

**現有分類：**
- ACTION_POSE（至少有這個）
- NULL（4,841 個標籤未分類，佔 3.44%）

**問題：**
- ⚠️ 只看到 1 個分類樣本
- ⚠️ 需要查詢完整的分類列表
- ⚠️ 可能分類不完整或命名不符合 Inspire 需求

---

### 4. 向量嵌入（tag_embeddings）

**現狀：**
- ❌ 表存在但**完全是空的**（0 coverage）
- ❌ 語義搜尋**暫時不可用**

**影響：**
- MVP 階段必須用關鍵字搜尋
- 語義搜尋需要離線批量生成 embeddings

---

## 📋 Inspire 需求 vs 現有資料對比

| Inspire 需求 | 現有資料 | 狀態 | 行動 |
|-------------|---------|------|------|
| **標籤名稱** | `name` | ✅ 直接可用 | 無需改動 |
| **流行度** | `post_count` | ✅ 完整（140K） | 無需改動 |
| **分類系統** | `main_category` | ⚠️ 存在但需映射 | 需要映射邏輯 |
| **別名** | 不存在 | ❌ 缺失 | 可選（手動或從外部來源） |
| **衝突檢測** | 不存在 | ❌ 缺失 | 可選（規則或統計） |
| **NSFW 分級** | 不存在 | ❌ 缺失 | **P0 必須添加** |
| **語義搜尋** | embedding 空 | ❌ 不可用 | P1（離線生成） |

---

## 💡 關鍵洞察

### 發現 1: 資料品質非常高 ⭐⭐⭐⭐⭐

```
✅ 140K+ 標籤（豐富）
✅ 55% >= 1000 posts（高品質）
✅ 流行度完整（可靠排序）
✅ 已有分類系統（雖需映射）
```

**結論：** 現有資料足以支撐 Inspire MVP！

---

### 發現 2: 語義搜尋暫時不可用

```
❌ tag_embeddings 表是空的
❌ 無法進行向量相似度搜尋
```

**影響：**
- MVP 必須用關鍵字搜尋（ILIKE）
- 這與我們的 Day 3 計劃一致 ✅

**解決方案：**
- Week 1: 用關鍵字搜尋
- Week 2-3: 離線生成 embeddings

---

### 發現 3: 分類系統需要調查

```
⚠️ 只看到 ACTION_POSE 一個分類
⚠️ 3.44% 標籤未分類（NULL）
```

**需要確認：**
- 完整的分類列表是什麼？
- 如何映射到 Inspire 的 9 個類別？

---

### 發現 4: NSFW 內容確實存在 ⚠️

```
TOP 5 包含 "breasts"（55M posts）
確實有敏感內容
```

**結論：** P0 安全過濾**絕對必要**！

---

## 🎯 修正後的整合策略

### 策略 A: 最小改動方案（推薦）⭐⭐⭐⭐⭐

**原則：** 充分利用現有資料，最小化 Schema 變更

#### 1. 不添加新欄位到 tags_final

**理由：**
- ✅ 避免修改生產表
- ✅ 降低風險
- ✅ 快速上線

#### 2. 用現有欄位 + 應用層邏輯

```python
# Category 映射（程式碼層）
CATEGORY_MAPPING = {
    "ACTION_POSE": "ACTION",
    "CHARACTER": "CHARACTER",
    "APPEARANCE": "APPEARANCE",
    # ... 完整映射待補充
}

# Aliases（手動維護小清單）
TAG_ALIASES = {
    "longhair": "long_hair",
    "1girls": "1girl",
    # ... 常見錯誤映射
}

# Conflicts（規則檢測）
CONFLICT_RULES = [
    ("long_hair", "short_hair"),
    ("1girl", "no_humans"),
    # ... 明顯衝突
]

# NSFW 檢測（關鍵字）
NSFW_KEYWORDS = ["nsfw", "nude", "breasts", "explicit", ...]
BLOCKED_KEYWORDS = ["loli", "shota", "child", ...]
```

**優點：**
- ✅ 零 Schema 變更
- ✅ 立即可用
- ✅ 靈活調整

**缺點：**
- ⚠️ 無法基於資料庫統計衝突
- ⚠️ 需要手動維護列表

---

### 策略 B: 建立輔助表方案（中庸）⭐⭐⭐⭐

**原則：** 不動 tags_final，建立輔助表

#### 1. tags_final 保持不變

**完全不碰** ✅

#### 2. 創建輔助表

```sql
-- 新表 1: tag_metadata (Inspire 擴展資料)
CREATE TABLE tag_metadata (
    tag_name TEXT PRIMARY KEY,  -- 參考 tags_final.name
    inspire_category TEXT,       -- CHARACTER, SCENE, MOOD...
    aliases TEXT[],
    conflicts TEXT[],
    nsfw_level TEXT DEFAULT 'all-ages',
    
    FOREIGN KEY (tag_name) REFERENCES tags_final(name)
);

-- 新表 2: inspire_sessions（業務資料）
CREATE TABLE inspire_sessions (...);
```

**優點：**
- ✅ tags_final 零改動
- ✅ 可以慢慢填充輔助資料
- ✅ 失敗可直接刪除輔助表

**缺點：**
- ⚠️ 需要維護兩個表的一致性
- ⚠️ 查詢需要 JOIN

---

### 策略 C: 完整擴展方案（之前的方案）⭐⭐⭐

**原則：** ALTER TABLE 添加欄位

#### 優點
- ✅ 查詢簡單（不需要 JOIN）
- ✅ 資料集中

#### 缺點
- ⚠️ 修改生產表（有風險）
- ⚠️ 回退較複雜

---

## 🎯 我的建議

### 推薦：混合策略（最穩健）

```
階段 1（Week 1 MVP）：策略 A（應用層）
├─ 用現有欄位（name, post_count, main_category）
├─ 程式碼中維護映射和規則
├─ 只建 inspire_sessions 表（業務資料）
└─ 零風險，快速上線

階段 2（Week 2-3 優化）：策略 B（輔助表）
├─ 創建 tag_metadata（擴展資料）
├─ 逐步填充 aliases, conflicts
└─ 不影響現有系統

階段 3（未來）：評估是否需要策略 C
└─ 如果輔助表證明有效，再考慮整合到 tags_final
```

---

## 📋 需要進一步調查的問題

### Q1: main_category 完整列表是什麼？

**已知：** ACTION_POSE, NULL（3.44%）  
**需要：** 查詢所有不同的 main_category 值

```sql
SELECT DISTINCT main_category, COUNT(*) 
FROM tags_final 
GROUP BY main_category 
ORDER BY COUNT(*) DESC;
```

---

### Q2: sub_category 的資料是什麼？

**已知：** EXPRESSION（範例）  
**需要：** 了解完整的 sub_category 系統

---

### Q3: 如何識別 NSFW 內容？

**已知：** "breasts" 在 TOP 5  
**需要：** 
- 有沒有現成的 NSFW 標記？
- 還是需要關鍵字規則？

---

## 🚀 立即行動建議

### 行動 1: 完成資料庫深入分析（30 分鐘）

**需要查詢：**
1. 完整的 main_category 列表
2. sub_category 樣本
3. TOP 100 熱門標籤（檢查 NSFW）
4. 是否有任何現有的 NSFW 標記

**我創建查詢腳本：**
```python
# 查詢完整分類
# 檢查現有資料品質
# 評估需要哪些補充
```

---

### 行動 2: 基於分析結果制定最小改動方案

**等分析完成後決定：**
- 用策略 A（應用層）？
- 用策略 B（輔助表）？
- 還是策略 C（擴展原表）？

---

**我現在應該創建更深入的分析腳本，還是你想先手動查詢資料庫？** 🤔
