# 實際使用場景測試 - 準確率分析與精進方案

**測試日期：** 2025-10-09  
**測試方法：** SQL 實際使用場景模擬  
**資料庫版本：** Phase 2.5

---

## 🎯 測試總結

### 測試場景覆蓋
- ✅ 場景 1: 內容創作者搜索標籤
- ✅ 場景 2: 內容過濾和分類
- ✅ 場景 3: 標籤推薦系統
- ✅ 場景 4: 數據質量檢查
- ✅ 場景 5: 分類錯誤檢測
- ✅ 場景 6: LLM 候選標籤識別

### 測試結果
- **測試成功率**: 14/14 (100%)
- **發現問題數**: 27 個
- **LLM 候選標籤**: 126 個

---

## ❌ 發現的主要問題

### 問題 1: Background 標籤嚴重誤分類 ⭐⭐⭐⭐⭐

**嚴重程度**: CRITICAL  
**影響範圍**: 20 個高頻 background 標籤

**誤分類案例**:
- `simple_background` (18.2M 使用) → 誤分為 CHARACTER_RELATED / BODY_PARTS
- `white_background` (15.0M 使用) → 誤分為 CHARACTER_RELATED / BODY_PARTS
- `grey_background` (2.6M 使用) → 誤分為 CHARACTER_RELATED / BODY_PARTS

**原因**: 
- `_body_parts_keywords` 包含 'back'
- 'background' 包含 'back' 導致誤匹配

**影響**:
- 合計影響 **43M+ 使用次數**
- 佔總使用量 **3.6%**
- 嚴重影響推薦系統準確性

**修復方案**: ✅ 已修復
- 在 `_is_body_parts()` 方法中添加排除邏輯
- 需重新運行管線

### 問題 2: 副分類覆蓋不足

**低副分類覆蓋率的主分類**:
| 主分類 | 副分類覆蓋率 | 問題 |
|--------|-------------|------|
| ART_STYLE | 0% | 無副分類定義 |
| COMPOSITION | 0% | 無副分類定義 |
| ENVIRONMENT | 0% | 無副分類定義 |
| OBJECTS | 0% | 無副分類定義 |
| VISUAL_EFFECTS | 0% | 無副分類定義 |

**影響**: 
- 這些分類的標籤無法進行精細篩選
- 推薦系統功能受限

**建議**: 
- 可選擇性添加副分類（非緊急）
- 優先處理高頻標籤覆蓋

### 問題 3: 推薦系統盲區

**影響統計**:
- 高頻未分類標籤: 50 個（post_count > 1,000）
- 影響使用次數: **122.3M 次**
- 佔總使用量: **10.29%**

**影響**:
- 推薦系統無法推薦這些高頻標籤
- 影響用戶體驗

---

## 📊 LLM 候選標籤深度分析

### 分類分析結果

#### 可用規則擴展處理: 58 個標籤 (54.7%)

| 類別 | 數量 | 使用次數 | TOP 標籤 |
|------|------|---------|---------|
| **CLOTHING** | 29 | 63.0M | open_clothes, choker, belt, serafuku, hood |
| **BODY_PARTS** | 17 | 37.0M | pointy_ears, tongue, fang, midriff, armpits |
| **OBJECTS** | 4 | 9.4M | speech_bubble, halo, star_(symbol) |
| **EXPRESSION** | 2 | 4.4M | sweatdrop, arm_up |
| **ACCESSORIES** | 2 | 3.9M | nail_polish, wrist_cuffs |
| **TECHNICAL** | 3 | 6.9M | twitter_username, english_text, dated |
| **ART_STYLE** | 1 | 1.4M | border |

**小計**: 
- 標籤數: 58 個
- 使用次數: **125.9M**
- 佔候選標籤使用量: **65.6%**

#### 真正需要 LLM 處理: 48 個標籤 (45.3%)

**特徵**: 語意複雜、難以用關鍵字規則處理

**TOP 20 需要 LLM 的標籤**:
1. virtual_youtuber (3.9M) - 概念性標籤
2. hair_over_one_eye (2.5M) - 複雜髮型描述
3. off_shoulder (2.4M) - 服裝狀態（已在規則中但未匹配）
4. character_name (2.0M) - 元數據
5. two_side_up (1.7M) - 髮型
6. v (1.5M) - 手勢符號
7. wet (1.5M) - 狀態描述
8. loli (1.5M) - 角色類型
9. maid (1.5M) - 職業/服裝
10. no_humans (1.5M) - 場景特徵
11. pokemon_(creature) (1.5M) - 特殊類別
12. pillow (1.4M) - 家具
13. thigh_strap (1.4M) - 服裝配件
14. ascot (1.4M) - 領飾
15. head_tilt (1.4M) - 頭部姿勢
... (還有 33 個)

**小計**:
- 標籤數: 48 個
- 使用次數: **66.0M**
- 佔候選標籤使用量: **34.4%**

---

## 🎯 精進方案（三階段推薦）

### 階段 2.6: 緊急修復 + 快速規則擴展 ⭐⭐⭐⭐⭐

**優先級**: CRITICAL  
**時間**: 1-2 小時  
**成本**: $0

#### A. 緊急修復 (立即執行)
- ✅ 已修復 background 誤分類
- 需重新運行管線驗證

#### B. 快速規則擴展 (58 個標籤)
添加以下關鍵字到現有規則：

**CLOTHING** (29 個標籤 → +63M 使用次數):
```python
# 服裝配件和細節
'choker', 'belt', 'hood', 'collar', 'serafuku', 'vest', 'sweater',
'apron', 'leotard', 'crop_top', 'sailor_collar', 'japanese_clothes',
'strapless', 'fur_trim', 'clothing_cutout', 'see-through',
'striped_clothes', 'off_shoulder', 'clothes_lift'
```

**BODY_PARTS** (17 個標籤 → +37M 使用次數):
```python
# 身體部位擴展
'pointy_ears', 'tongue', 'fang', 'fangs', 'midriff', 'armpits',
'mole', 'fingernails', 'eyelashes', 'toes', 'facial_mark',
'tongue_out', 'abs', 'eyebrows', 'cameltoe'
```

**ACCESSORIES** (2 個標籤 → +3.9M 使用次數):
```python
'nail_polish', 'wrist_cuffs', 'wristband'
```

**EXPRESSION** (2 個標籤 → +4.4M 使用次數):
```python
'sweatdrop', 'arm_up', 'happy'
```

**OBJECTS** (4 個標籤 → +9.4M 使用次數):
```python
'speech_bubble', 'halo', 'star', 'symbol'
```

**TECHNICAL** (3 個標籤 → +6.9M 使用次數):
```python
'twitter_username', 'english_text', 'dated', 'character_name'
```

**預期效果**:
- danbooru_cat=0 覆蓋率: 41.59% → **55-60%**
- 新增覆蓋: **+58 個標籤**
- 新增使用次數: **+125.9M**
- 成本: **$0**

### 階段 3: 選擇性 LLM 增強 ⭐⭐⭐⭐

**優先級**: HIGH  
**時間**: 1 天  
**成本**: $5-10

#### 僅處理 48 個真正需要 LLM 的標籤

**分批處理策略**:
1. **Batch 1**: 超高頻標籤 (>2M 使用) - 5 個標籤
   - virtual_youtuber, hair_over_one_eye, off_shoulder, character_name, two_side_up
   
2. **Batch 2**: 高頻標籤 (1M-2M 使用) - 43 個標籤
   - 其餘 43 個標籤

**LLM Prompt 設計**:
```
你是一個專業的 Danbooru 標籤分類專家。

標籤: {tag_name}
使用次數: {post_count}

請將此標籤分類到以下主分類之一：
- CHARACTER_RELATED: 人物相關（外觀、服裝、身體特徵）
- ACTION_POSE: 動作姿態（姿勢、表情）
- OBJECTS: 物件道具
- ENVIRONMENT: 場景環境
- COMPOSITION: 構圖技法
- VISUAL_EFFECTS: 視覺效果
- ART_STYLE: 藝術風格
- ADULT_CONTENT: 成人內容
- THEME_CONCEPT: 主題概念
- TECHNICAL: 技術標籤

如果屬於 CHARACTER_RELATED 或 ACTION_POSE，請提供副分類。

請以 JSON 格式回答：
{
  "main_category": "...",
  "sub_category": "..." (可選),
  "confidence": 0.0-1.0,
  "reason": "簡短說明"
}
```

**預期效果**:
- 覆蓋率: 55-60% → **65-70%**
- 成本: **$2-5**
- LLM 調用: 48 次

### 階段 4: 高頻標籤全覆蓋 (可選) ⭐⭐⭐

**優先級**: MEDIUM  
**時間**: 1-2 天  
**成本**: $10-20

#### 處理所有 post_count > 100k 的未分類標籤

**數量**: 
- 超高頻 (>1M): 106 個
- 高頻 (100k-1M): 約 200 個
- **總計**: 約 300 個標籤

**預期效果**:
- 覆蓋率: 65-70% → **75-80%**
- 成本: **$10-20**

---

## 🔧 立即執行計劃

### 步驟 1: 修復 Background 誤分類 (已完成)

**修改文件**: `stage1/src/classifier/rules/character_sub_rules.py`

```python
def _is_body_parts(self, tag: str) -> bool:
    """判斷是否為身體部位"""
    # 排除誤判：background 不是 body parts
    if 'background' in tag:
        return False
    # ... 其餘邏輯
```

**驗證**: 重新運行管線

### 步驟 2: 快速規則擴展（建議優先執行）

**優先擴展清單** (按影響力排序):

#### 2.1 CLOTHING 擴展 (最高優先級)
需添加 29 個標籤，影響 63M 使用次數

```python
# stage1/src/classifier/rules/character_sub_rules.py
CLOTHING_KEYWORDS_QUICK_EXPANSION = {
    # 服裝配件 (超高頻)
    'choker', 'belt', 'hood', 'collar', 'vest', 'sweater', 'apron',
    'serafuku', 'sailor_collar', 'crop_top', 'leotard',
    
    # 服裝類型
    'japanese_clothes', 'japanese', 'obi', 'military',
    
    # 鞋類
    'footwear', 'black_footwear', 'sandals', 'heels', 'high_heels',
    
    # 服裝細節
    'fur_trim', 'striped_clothes', 'strapless',
    
    # 服裝狀態
    'clothing_cutout', 'see-through', 'clothes_lift'
}
```

#### 2.2 BODY_PARTS 擴展
需添加 17 個標籤，影響 37M 使用次數

```python
# 已包含基本關鍵字，需添加：
BODY_PARTS_QUICK_EXPANSION = {
    # 動物特徵
    'pointy_ears', 'rabbit_ears', 'fox_ears', 'horse_ears',
    'fang', 'fangs',
    
    # 身體細節
    'tongue_out', 'midriff', 'armpits', 'mole', 
    'fingernails', 'eyelashes', 'abs', 'toes',
    'facial_mark', 'eyebrows', 'v-shaped_eyebrows',
    'mole_under_eye', 'cameltoe', 'underboob', 'sideboob'
}
```

#### 2.3 ACCESSORIES 擴展
需添加 2 個標籤，影響 3.9M 使用次數

```python
ACCESSORIES_QUICK_EXPANSION = {
    'nail_polish', 'wrist_cuffs', 'wristband'
}
```

#### 2.4 TECHNICAL 擴展
需添加 3 個標籤，影響 6.9M 使用次數

```python
# stage1/src/classifier/rules/main_category_rules.py
TECHNICAL_QUICK_EXPANSION = {
    'twitter_username', 'username', 'english_text', 
    'dated', 'character_name', 'copyright_name'
}
```

#### 2.5 OBJECTS 擴展
需添加 4 個標籤，影響 9.4M 使用次數

```python
OBJECTS_QUICK_EXPANSION = {
    'speech_bubble', 'halo', 'star', 'symbol',
    'symbol-shaped_pupils', 'stuffed_toy'
}
```

**預期效果**:
- 新增覆蓋: **+58 個標籤**
- 新增使用次數: **+125.9M**
- 覆蓋率提升: 41.59% → **55-60%**

### 步驟 3: LLM 處理剩餘 48 個標籤

**真正需要 LLM 的標籤** (無法用簡單規則處理):

```
virtual_youtuber, hair_over_one_eye, two_side_up, v (手勢),
wet, loli, maid, no_humans, pokemon_(creature), pillow,
thigh_strap, ascot, head_tilt, sash, lips, cosplay,
tattoo, zettai_ryouiki, petals, profile, blood,
kneehighs, shiny_skin, makeup, mask, hug, expressionless,
bell, hair_intakes, skindentation, saliva, highleg,
scar, siblings, fruit, piercing, frown, leaf,
one_side_up, soles, chain, beret
```

**成本估算**:
- 標籤數: 48 個
- 預估成本: **$2-5**
- 預期覆蓋率提升: +3-5%

---

## 📈 預期成效總覽

### 如果執行完整計劃 (階段 2.6 + 階段 3)

| 指標 | 當前 (Phase 2.5) | 預期 (完成後) | 提升 |
|------|-----------------|--------------|------|
| 整體覆蓋率 | 87.23% | **90-92%** | +3-5% ✅ |
| danbooru_cat=0 覆蓋率 | 41.59% | **65-70%** | +23-28% ⭐⭐⭐⭐⭐ |
| 規則分類器 | 12,800 | **13,700-14,000** | +900-1,200 ⭐⭐⭐⭐⭐ |
| 推薦系統盲區 | 10.29% | **<3%** | -7% ⭐⭐⭐⭐⭐ |
| 總成本 | $0 | **$2-5** | 極低成本 ✅ |

---

## 🚀 推薦執行順序

### 立即執行 (今天)

1. **修復 Background 誤分類** (10分鐘)
   - ✅ 已修復代碼
   - 重新運行管線
   - 驗證修復效果

2. **快速規則擴展** (1-2 小時)
   - 添加 58 個高頻標籤的規則
   - 重新運行管線
   - 預期覆蓋率提升到 55-60%

3. **驗證效果** (30 分鐘)
   - 運行實際使用場景測試
   - 確認誤分類已修復
   - 統計改進效果

### 明天執行

4. **設計 LLM Prompt** (1 小時)
   - 測試 Prompt 效果
   - 優化分類準確率

5. **LLM 批次處理** (2-3 小時)
   - 處理剩餘 48 個標籤
   - 人工審查結果
   - 整合到數據庫

6. **最終驗證** (1 小時)
   - 完整測試
   - 生成最終報告
   - 準備發布

---

## 💰 成本效益分析

### 方案對比

| 方案 | 時間 | 成本 | 覆蓋率 | ROI |
|------|------|------|--------|-----|
| **僅修復 + 規則擴展** | 2小時 | $0 | 55-60% | ⭐⭐⭐⭐⭐ |
| **+ LLM (48個標籤)** | 1天 | $2-5 | 65-70% | ⭐⭐⭐⭐⭐ |
| **+ LLM (全部高頻)** | 2天 | $15-25 | 75-80% | ⭐⭐⭐⭐ |

### 推薦：混合方案

**階段 2.6**: 修復 + 規則擴展 ($0, 2小時)  
**階段 3**: LLM 處理 48 個標籤 ($2-5, 3小時)

**總投入**: 
- 時間: 5 小時
- 成本: **$2-5**

**總收益**:
- 覆蓋率: 41.59% → **65-70%** (+23-28%)
- 推薦系統可用標籤: +106 個高頻標籤
- 誤分類修復: 20+ 個 background 標籤

---

## ⚠️ 發現的其他次要問題

### 1. 副分類覆蓋不完整
- OBJECTS, ENVIRONMENT, ART_STYLE 等無副分類
- 影響: 中等（可用性降低，但不影響基本功能）
- 建議: 可選擇性添加，非緊急

### 2. 特殊字符處理
- 部分特殊字符標籤未分類 (如 'v', '-')
- 影響: 低（使用量小）
- 建議: 可忽略或低優先級處理

### 3. 邊界情況
- 一些標籤在多個分類邊界（如 'maid' 可能是職業或服裝）
- 影響: 低（數量少）
- 建議: LLM 處理或人工審查

---

## ✅ 結論與建議

### 當前狀態評估
- ✅ **基礎扎實**: 87.23% 覆蓋率
- ⚠️ **存在誤分類**: background 系列 (已修復)
- ⚠️ **推薦系統盲區**: 10.29% 高頻標籤未覆蓋
- ✅ **分類體系完整**: 11 個主分類、16 個副分類

### 建議執行順序

1. **立即執行** (必須):
   - 重新運行管線（驗證 background 修復）
   - 快速規則擴展（58 個標籤）
   - 預期達成: 55-60% 覆蓋率

2. **明天執行** (強烈建議):
   - LLM 處理 48 個真正需要的標籤
   - 預期達成: 65-70% 覆蓋率

3. **可選** (根據需求):
   - 全量 LLM 處理高頻標籤
   - 預期達成: 75-80% 覆蓋率

### 預期最終成果

**如果執行階段 2.6 + 階段 3**:
- ✅ 覆蓋率達到 **65-70%**
- ✅ 推薦系統盲區降到 **<5%**
- ✅ 修復所有已知誤分類
- ✅ 總成本僅 **$2-5**
- ✅ 時間投入僅 **5 小時**

**性價比極高！強烈建議執行！** 🎯

---

**報告完成日期：** 2025-10-09  
**下一步行動：** 立即修復誤分類並執行快速規則擴展

================================================================================

