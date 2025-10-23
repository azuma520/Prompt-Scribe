# Phase 2: 規則法完善分類系統計劃

**建立日期：** 2025-10-09  
**目標：** 提高資料庫分類深度與廣度  
**方法：** 規則擴展（零成本）

---

## 📊 當前狀態分析（基於測試結果）

### 整體數據
- **總標籤數**: 140,782 個
- **已分類**: 119,088 個 (84.59%)
  - Danbooru 直接分類: 110,000 個 (78.13%)
  - 規則分類器: 9,088 個 (6.46%)
- **未分類**: 21,694 個 (15.41%)

### danbooru_cat=0 (一般標籤) 分析
- **總數**: 30,782 個
- **已分類**: 9,088 個 (29.52%)
- **未分類**: 21,694 個 (70.48%)

### 未分類標籤按頻率分層
| 頻率層級 | 標籤數 | 總使用次數 | 優先級 |
|---------|--------|-----------|--------|
| 超高頻 (>1M) | 57 | 110,767,084 | ⭐⭐⭐⭐⭐ |
| 高頻 (100k-1M) | 629 | 172,716,108 | ⭐⭐⭐⭐⭐ |
| 中高頻 (10k-100k) | 2,427 | 76,476,308 | ⭐⭐⭐⭐ |
| 中頻 (1k-10k) | 6,012 | 20,367,912 | ⭐⭐⭐ |
| 低頻 (<1k) | 12,569 | 4,290,716 | ⭐⭐ |

---

## 🎯 Phase 2 目標

### 數量目標
- **當前覆蓋率**: 29.52% (danbooru_cat=0)
- **目標覆蓋率**: 45-50%
- **需新增覆蓋**: 約 4,000-5,000 個標籤

### 質量目標
- TOP 100 高頻標籤覆蓋率達 90%+
- 超高頻標籤 (>1M) 覆蓋率達 90%+
- 保持分類準確率 ≥ 95%

### 深度目標
- 現有主分類副分類覆蓋率達 60%+
- 新增 2 個主分類 (ADULT_CONTENT, THEME_CONCEPT)
- 擴展副分類覆蓋至更細緻層級

---

## 📋 未分類高價值標籤分析

### TOP 30 未分類標籤（使用次數 > 1.7M）

#### 1. 服裝類 (CLOTHING) - 可用規則擴展
```
thighhighs      4,667,380  ✅ 高優先級
underwear       3,175,044  ✅ 高優先級
panties         2,589,748  ✅ 高優先級
pantyhose       2,115,692  ✅ 高優先級
frills          1,985,204  ✅ 高優先級
open_clothes    1,974,736  ✅ 高優先級
necktie         1,772,468  ✅ 高優先級
```

#### 2. 身體部位 (BODY_PARTS) - 需新增副分類
```
navel           4,611,288  ✅ 高優先級
cleavage        4,010,592  ✅ 高優先級
nipples         3,319,508  ⚠️ 成人內容
collarbone      3,155,440  ✅ 高優先級
ass             2,368,452  ⚠️ 成人內容
thighs          2,259,292  ✅ 高優先級
teeth           1,968,724  ✅ 中優先級
```

#### 3. 頭髮配飾類 (HAIR/ACCESSORIES) - 可用規則擴展
```
ahoge           2,595,080  ✅ 高優先級
sidelocks       2,450,480  ✅ 高優先級
hairband        1,893,300  ✅ 高優先級
tail            3,137,868  ⚠️ 可能是動物特徵或髮型
```

#### 4. 配飾類 (ACCESSORIES) - 可用規則擴展
```
jewelry         4,253,336  ✅ 高優先級
earrings        2,233,540  ✅ 高優先級
```

#### 5. 表情類 (EXPRESSION) - 可用規則擴展
```
:d              2,198,840  ✅ 高優先級
sweat           2,091,908  ✅ 高優先級
```

#### 6. 成人內容 (ADULT_CONTENT) - 需新增主分類
```
hetero          2,173,164  ⚠️ 性行為
censored        1,825,292  ⚠️ 審查相關
```

#### 7. 藝術風格/技術 (ART_STYLE/TECHNICAL)
```
comic           2,156,924  ✅ 可擴展到 ART_STYLE
greyscale       2,005,548  ✅ 可擴展到 ART_STYLE
```

#### 8. 物件類 (OBJECTS)
```
food            1,768,116  ✅ 可擴展
wings           1,745,132  ✅ 可擴展
horns           1,847,764  ✅ 可擴展
```

#### 9. 服裝修飾 (CLOTHING_STATE)
```
alternate_costume 1,712,804  ⚠️ 概念性標籤
```

---

## 🎨 規則擴展計劃

### 階段 1: 擴展現有分類 (預計新增 2,000-2,500 個標籤)

#### 1.1 CHARACTER_RELATED 擴展

**A. 新增 BODY_PARTS 副分類** ⭐ 最高優先級
```python
# stage1/src/classifier/rules/character_sub_rules.py
BODY_PARTS_KEYWORDS = {
    # 軀幹
    'navel', 'collarbone', 'neck', 'shoulder', 'shoulders', 'waist',
    'midriff', 'stomach', 'belly', 'chest', 'torso', 'back',
    
    # 胸部相關（非成人）
    'cleavage', 'breasts', 'small_breasts', 'medium_breasts', 'large_breasts',
    'flat_chest', 'chest',
    
    # 四肢
    'thighs', 'legs', 'leg', 'calves', 'ankles', 'feet', 'foot',
    'arms', 'arm', 'hands', 'hand', 'fingers', 'finger', 'wrist',
    
    # 臀部（非成人）
    'hips', 'butt',
    
    # 臉部細節
    'teeth', 'tooth', 'tongue', 'lips', 'chin', 'cheek', 'cheeks',
    'forehead', 'eyebrows', 'eyebrow', 'eyelashes', 'eyelash',
    
    # 其他
    'skin', 'muscle', 'abs'
}
```

**B. 擴展 CLOTHING 關鍵字** ⭐ 最高優先級
```python
CLOTHING_KEYWORDS_EXPANSION = {
    # 腿部服裝
    'thighhighs', 'pantyhose', 'stockings', 'socks', 'garter_belt', 
    'garter_straps', 'leg_warmers', 'knee_highs',
    
    # 內衣類
    'underwear', 'panties', 'bra', 'lingerie', 'camisole',
    
    # 領飾
    'necktie', 'bowtie', 'choker', 'collar', 'scarf', 'neckwear',
    
    # 服裝狀態
    'open_clothes', 'open_shirt', 'open_jacket', 'unbuttoned',
    'partially_visible', 'torn_clothes',
    
    # 服裝細節
    'frills', 'ruffles', 'lace', 'ribbon', 'ribbons', 'buttons',
    'zipper', 'belt', 'buckle',
    
    # 特定服裝
    'bikini', 'swimsuit', 'school_uniform', 'uniform', 'kimono',
    'apron', 'vest', 'sweater', 'hoodie', 'coat', 'blazer'
}
```

**C. 擴展 HAIR 關鍵字**
```python
HAIR_KEYWORDS_EXPANSION = {
    # 髮型細節
    'ahoge', 'sidelocks', 'hair_strand', 'hair_strands',
    'hair_between_eyes', 'parted_bangs', 'swept_bangs',
    
    # 髮飾
    'hairband', 'hairclip', 'hair_ribbon', 'hair_bow',
    'hair_flower', 'hair_ornament',
    
    # 特殊髮型
    'braided_hair', 'wavy_hair', 'curly_hair', 'straight_hair',
    'messy_hair', 'wet_hair'
}
```

**D. 新增 ACCESSORIES 副分類**
```python
ACCESSORIES_KEYWORDS = {
    # 珠寶
    'jewelry', 'earrings', 'necklace', 'bracelet', 'ring', 'rings',
    'pendant', 'brooch', 'piercing',
    
    # 配飾
    'glasses', 'eyewear', 'sunglasses', 'goggles',
    'watch', 'wristwatch',
    
    # 頭部配飾（非髮飾）
    'tiara', 'crown', 'headband', 'headphones', 'headset'
}
```

#### 1.2 ACTION_POSE 擴展

**A. 擴展 EXPRESSION 關鍵字**
```python
EXPRESSION_KEYWORDS_EXPANSION = {
    # 表情符號
    ':d', ':o', ':p', ':3', ':<', '>_<', '^_^', ';)', 
    'xd', 'x3',
    
    # 表情狀態
    'sweat', 'sweating', 'tears', 'crying', 'tearing_up',
    'blushing', 'embarrassed', 'nervous', 'shocked',
    'angry', 'annoyed', 'sad', 'happy', 'excited',
    
    # 表情動作
    'wink', 'winking', 'pout', 'pouting', 'smirk', 'smirking',
    'frown', 'frowning', 'grimace'
}
```

**B. 擴展 POSE 關鍵字**
```python
POSE_KEYWORDS_EXPANSION = {
    # 手部動作
    'waving', 'pointing', 'reaching', 'grabbing', 'touching',
    'hand_on_hip', 'hand_on_head', 'hand_to_mouth',
    'arms_crossed', 'arms_up', 'arms_behind_back',
    
    # 身體姿勢
    'leaning', 'leaning_forward', 'leaning_back',
    'kneeling', 'crouching', 'squatting',
    'lying', 'lying_down', 'on_back', 'on_side',
    'bent_over', 'arched_back',
    
    # 腿部姿勢
    'crossed_legs', 'legs_crossed', 'legs_apart',
    'one_knee', 'on_one_knee'
}
```

#### 1.3 OBJECTS 擴展

```python
OBJECTS_KEYWORDS_EXPANSION = {
    # 武器
    'gun', 'pistol', 'rifle', 'weapon', 'knife', 'dagger',
    
    # 食物
    'food', 'drink', 'cup', 'mug', 'glass', 'bottle',
    'plate', 'fork', 'spoon', 'chopsticks',
    'cake', 'dessert', 'fruit', 'apple', 'orange',
    
    # 家具
    'furniture', 'chair', 'table', 'desk', 'bed', 'sofa',
    'window', 'door', 'pillow', 'cushion',
    
    # 動物特徵/配件
    'wings', 'tail', 'horns', 'horn', 'ears', 'animal_ears',
    'cat_ears', 'fox_ears', 'bunny_ears',
    
    # 其他物品
    'umbrella', 'parasol', 'bag', 'purse', 'backpack',
    'book', 'phone', 'smartphone', 'camera'
}
```

#### 1.4 ART_STYLE 擴展

```python
ART_STYLE_KEYWORDS_EXPANSION = {
    # 色彩風格
    'greyscale', 'grayscale', 'monochrome', 'sepia',
    'black_and_white', 'limited_palette',
    
    # 繪畫風格
    'comic', 'manga', 'traditional_media', 'sketch', 'lineart',
    'watercolor', 'oil_painting', 'pencil_drawing',
    
    # 特殊效果
    'pixel_art', 'retro', 'vintage', 'cel_shading'
}
```

#### 1.5 VISUAL_EFFECTS 擴展

```python
VISUAL_EFFECTS_KEYWORDS_EXPANSION = {
    # 光影效果
    'sparkle', 'sparkles', 'glitter', 'shiny', 'shine',
    'glow', 'glowing_eyes', 'light_particles',
    
    # 動態效果
    'motion_blur', 'speed_lines', 'motion_lines',
    'wind', 'falling_leaves', 'falling_petals'
}
```

### 階段 2: 新增主分類 (預計新增 1,500-2,000 個標籤)

#### 2.1 新增 ADULT_CONTENT 主分類 ⚠️

**目的**: 明確標記成人相關內容，便於過濾和管理

**副分類**:
- SEXUAL: 性行為相關
- EXPLICIT_BODY: 裸露身體部位
- SUGGESTIVE: 暗示性內容
- CENSORSHIP: 審查相關

```python
# stage1/src/classifier/rules/main_category_rules.py
ADULT_CONTENT_KEYWORDS = {
    'SEXUAL': {
        'sex', 'hetero', 'yuri', 'yaoi', 'masturbation',
        'oral', 'paizuri', 'handjob', 'footjob'
    },
    'EXPLICIT_BODY': {
        'nipples', 'penis', 'pussy', 'anus', 'nude', 'naked',
        'ass', 'breasts_out', 'topless', 'bottomless'
    },
    'SUGGESTIVE': {
        'sexually_suggestive', 'seductive', 'provocative',
        'bedroom_eyes', 'inviting'
    },
    'CENSORSHIP': {
        'censored', 'uncensored', 'mosaic_censoring',
        'bar_censor', 'convenient_censoring'
    }
}
```

#### 2.2 新增 THEME_CONCEPT 主分類

**目的**: 處理概念性、主題性標籤

**副分類**:
- SEASON: 季節
- HOLIDAY: 節日
- TIME: 時間
- WEATHER: 天氣
- CONCEPT: 抽象概念

```python
THEME_CONCEPT_KEYWORDS = {
    'SEASON': {
        'spring', 'summer', 'autumn', 'fall', 'winter',
        'spring_season', 'summer_season'
    },
    'HOLIDAY': {
        'christmas', 'halloween', 'valentine', 'easter',
        'new_year', 'birthday'
    },
    'TIME': {
        'day', 'night', 'sunset', 'sunrise', 'dawn', 'dusk',
        'morning', 'afternoon', 'evening', 'midnight'
    },
    'WEATHER': {
        'rain', 'raining', 'snow', 'snowing', 'cloudy',
        'sunny', 'storm', 'lightning'
    },
    'CONCEPT': {
        'love', 'friendship', 'battle', 'peace', 'dream',
        'fantasy', 'reality', 'alternate_costume', 'crossover'
    }
}
```

---

## 🔧 實施步驟

### 步驟 1: 備份現有代碼
```bash
cd stage1
git add -A
git commit -m "backup: 保存 Phase 1 完成狀態"
git branch phase1-backup
```

### 步驟 2: 更新分類器代碼

**A. 更新 categories.py**
```python
# 新增主分類
MAIN_CATEGORIES = [
    'CHARACTER_RELATED',
    'ACTION_POSE',
    'ENVIRONMENT',
    'OBJECTS',
    'ART_STYLE',
    'VISUAL_EFFECTS',
    'COMPOSITION',
    'TECHNICAL',
    'QUALITY',
    'ADULT_CONTENT',      # 新增
    'THEME_CONCEPT',      # 新增
    'ARTIST',
    'CHARACTER',
    'COPYRIGHT'
]

# 更新副分類
SUB_CATEGORIES = {
    'CHARACTER_RELATED': [
        'CLOTHING',
        'HAIR',
        'CHARACTER_COUNT',
        'BODY_PARTS',      # 新增
        'ACCESSORIES'      # 新增
    ],
    'ACTION_POSE': [
        'POSE',
        'EXPRESSION',
        'INTERACTION'      # 新增
    ],
    'ADULT_CONTENT': [     # 新增
        'SEXUAL',
        'EXPLICIT_BODY',
        'SUGGESTIVE',
        'CENSORSHIP'
    ],
    'THEME_CONCEPT': [     # 新增
        'SEASON',
        'HOLIDAY',
        'TIME',
        'WEATHER',
        'CONCEPT'
    ]
}
```

**B. 創建新規則檔案**
```bash
# 創建成人內容規則
touch stage1/src/classifier/rules/adult_content_rules.py

# 創建主題概念規則
touch stage1/src/classifier/rules/theme_concept_rules.py

# 創建身體部位規則
touch stage1/src/classifier/rules/body_parts_sub_rules.py
```

### 步驟 3: 實施規則

**優先順序**:
1. ⭐⭐⭐⭐⭐ CHARACTER_RELATED 擴展 (預計 +1,500 標籤)
2. ⭐⭐⭐⭐⭐ ADULT_CONTENT 新增 (預計 +800 標籤)
3. ⭐⭐⭐⭐ ACTION_POSE 擴展 (預計 +600 標籤)
4. ⭐⭐⭐⭐ OBJECTS 擴展 (預計 +400 標籤)
5. ⭐⭐⭐ ART_STYLE 擴展 (預計 +300 標籤)
6. ⭐⭐⭐ THEME_CONCEPT 新增 (預計 +500 標籤)
7. ⭐⭐ VISUAL_EFFECTS 擴展 (預計 +200 標籤)

### 步驟 4: 測試驗證

```bash
# 運行分類管線
python run_pipeline.py

# 檢查高頻標籤覆蓋率
python check_real_tags.py

# 運行全面測試
python comprehensive_db_test.py

# 查看改進報告
python generate_comparison_report.py
```

### 步驟 5: 評估效果

**預期結果**:
- danbooru_cat=0 覆蓋率: 29.52% → **45-50%**
- TOP 100 高頻標籤覆蓋率: 75% → **90%+**
- 超高頻標籤 (>1M) 覆蓋率: 67.2% → **90%+**
- 新增已分類標籤: **+4,000-5,000 個**

---

## 📊 預期成效矩陣

| 指標 | Phase 1 | Phase 2 目標 | 提升幅度 |
|------|---------|-------------|---------|
| danbooru_cat=0 覆蓋率 | 29.52% | 45-50% | +15-20% |
| 超高頻標籤覆蓋率 | 67.2% | 90%+ | +23%+ |
| 高頻標籤覆蓋率 | 41.5% | 70%+ | +28%+ |
| TOP 100 覆蓋率 | 75% | 90%+ | +15%+ |
| 已分類標籤數 | 9,088 | 13,000-14,000 | +43-54% |
| 主分類數量 | 9 | 11 | +2 |
| 副分類數量 | 5 | 13 | +8 |
| 成本 | $0 | $0 | $0 |
| 開發時間 | - | 1-2 天 | - |

---

## ⚠️ 注意事項

### 1. 成人內容處理
- 明確標記但不排除
- 建立清晰的分類界線
- 便於後續過濾和管理

### 2. 分類優先級
- 高頻標籤優先
- 通用關鍵字優先
- 避免過度細分

### 3. 規則衝突處理
- ADULT_CONTENT 優先級應高於其他分類
- 確保規則優先級邏輯正確
- 測試邊界情況

### 4. 效能考量
- 擴展規則不應影響處理速度
- 目標: 保持在 10 秒內完成
- 監控記憶體使用

---

## 📅 實施時程

### Day 1: 準備與實施（4-6 小時）
- [ ] 09:00-10:00 備份代碼，建立分支
- [ ] 10:00-12:00 實施 CHARACTER_RELATED 擴展
- [ ] 13:00-14:00 實施 ADULT_CONTENT 新分類
- [ ] 14:00-15:30 實施 ACTION_POSE 擴展
- [ ] 15:30-17:00 實施其他分類擴展

### Day 2: 測試與優化（3-4 小時）
- [ ] 09:00-10:00 運行測試套件
- [ ] 10:00-11:30 分析測試結果，調整規則
- [ ] 11:30-12:30 生成對比報告
- [ ] 13:00-14:00 文件整理與提交

---

## 🎯 成功標準

### 必達目標
- ✅ danbooru_cat=0 覆蓋率達到 45%
- ✅ TOP 100 高頻標籤覆蓋率達到 90%
- ✅ 處理速度保持在 10 秒內
- ✅ 無分類錯誤增加

### 挑戰目標
- ⭐ danbooru_cat=0 覆蓋率達到 50%
- ⭐ 超高頻標籤覆蓋率達到 95%
- ⭐ 新增主分類完整實施
- ⭐ 副分類覆蓋率達到 60%

---

## 📝 後續工作

### Phase 2.5: LLM 補充（可選）
如果規則擴展後仍有重要標籤未覆蓋，可考慮：
- 使用 LLM 處理剩餘高頻未分類標籤（post_count > 10,000）
- 預估成本: $10-20
- 預期覆蓋率: 50% → 70%+

### Phase 3: 持續優化
- 定期分析新出現的高頻標籤
- 根據使用數據調整規則優先級
- 建立自動化監控機制

---

**計劃建立完成，等待執行！** 🚀

