# Stage 1 優化計畫

## 📊 現狀分析

### 當前成果
- **總覆蓋率**: 88.57% (124,691/140,782)
- **LLM 處理**: 114 個超高頻標籤，成功率 100%
- **平均信心度**: 0.937 (優秀)

### 剩餘機會
- **未分類標籤**: 16,091 個，總使用 4.4 億次
- **高價值目標**: 999 個中高頻標籤 (100K-1M)

---

## 🎯 優化策略

### 階段 1: 規則擴展 (預估提升 2-3%)

#### 1.1 服裝配件規則擴展
**目標**: 處理服裝相關的高頻標籤

**新增規則模式**:
```python
# 服裝配件
'polka_dot': 'CHARACTER_RELATED/CLOTHING',
'fishnets': 'CHARACTER_RELATED/CLOTHING', 
'loafers': 'CHARACTER_RELATED/CLOTHING',
'veil': 'CHARACTER_RELATED/CLOTHING',
'bandaid': 'CHARACTER_RELATED/CLOTHING',
'brooch': 'CHARACTER_RELATED/ACCESSORIES',
'single_thighhigh': 'CHARACTER_RELATED/CLOTHING',
'lipstick': 'CHARACTER_RELATED/COSMETICS',
```

**預估影響**: 8 個標籤，約 800 萬次使用

#### 1.2 身體部位規則擴展
**目標**: 完善身體相關標籤分類

**新增規則模式**:
```python
# 身體部位和特徵
'eyewear_on_head': 'CHARACTER_RELATED/BODY_PARTS',
'shaded_face': 'CHARACTER_RELATED/BODY_PARTS',
'tan': 'CHARACTER_RELATED/BODY_PARTS',
'extra_ears': 'CHARACTER_RELATED/BODY_PARTS',
```

**預估影響**: 4 個標籤，約 370 萬次使用

#### 1.3 動作姿態規則擴展
**目標**: 處理動作相關標籤

**新增規則模式**:
```python
# 動作姿態
'bent_over': 'ACTION_POSE/BODY_POSE',
'all_fours': 'ACTION_POSE/BODY_POSE',
'kiss': 'ACTION_POSE/GESTURE',
'staff': 'ACTION_POSE/PROPS',
```

**預估影響**: 4 個標籤，約 380 萬次使用

#### 1.4 技術規格規則擴展
**目標**: 處理技術相關標籤

**新增規則模式**:
```python
# 技術規格
'goggles': 'TECHNICAL/EQUIPMENT',
'letterboxed': 'TECHNICAL/FRAMING',
'bondage': 'ADULT_CONTENT/EXPLICIT_BODY',
'otoko_no_ko': 'THEME_CONCEPT/CONCEPT',
```

**預估影響**: 4 個標籤，約 370 萬次使用

### 階段 2: LLM 批量處理 (預估提升 3-4%)

#### 2.1 中高頻標籤處理
**目標**: 999 個標籤 (100K-1M 使用)

**處理策略**:
- 批量大小: 50 個標籤/批次
- 預估批次: 20 批次
- 預估成本: $0.03-0.05
- 預估時間: 10-15 分鐘

**預期成果**:
- 處理 999 個標籤
- 總使用次數: 3.1 億次
- 覆蓋率提升: +3-4%

#### 2.2 品質控制
- 信心度閾值: 0.8
- 低信心度標籤手動審查
- 一致性檢查

### 階段 3: 副分類系統擴展 (預估提升 1-2%)

#### 3.1 新增副分類
```python
# 新增副分類
'COSMETICS': '化妝品',
'PROPS': '道具',
'EQUIPMENT': '裝備',
'CONCEPT': '概念',
```

#### 3.2 副分類規則擴展
- 為現有標籤補充副分類
- 提高分類細緻度

---

## 📈 預期成果

### 覆蓋率提升預估
| 階段 | 提升幅度 | 累計覆蓋率 | 新增標籤數 |
|------|----------|------------|------------|
| 當前 | - | 88.57% | - |
| 規則擴展 | +2.5% | 91.07% | ~500 |
| LLM 處理 | +3.5% | 94.57% | ~900 |
| 副分類擴展 | +1.0% | 95.57% | - |
| **總計** | **+7.0%** | **95.57%** | **~1,400** |

### 成本效益分析
- **規則擴展**: 免費，開發時間 2-3 小時
- **LLM 處理**: $0.05，處理時間 15 分鐘
- **總投資**: <$0.10，總時間 <4 小時
- **ROI**: 極高，覆蓋率從 88.57% 提升至 95.57%

---

## 🚀 執行計畫

### 第 1 週: 規則擴展
1. 實施服裝配件規則
2. 實施身體部位規則  
3. 實施動作姿態規則
4. 實施技術規格規則
5. 測試和驗證

### 第 2 週: LLM 批量處理
1. 準備中高頻標籤列表
2. 執行 LLM 批量分類
3. 品質審查和修正
4. 結果整合

### 第 3 週: 副分類擴展
1. 新增副分類定義
2. 擴展現有標籤的副分類
3. 系統優化和測試

---

## 🎯 成功指標

- **覆蓋率**: 從 88.57% 提升至 95%+
- **處理標籤**: 新增 1,400+ 個分類標籤
- **使用次數**: 新增 3.5+ 億次使用覆蓋
- **品質**: 平均信心度維持 0.9+
- **成本**: 總投資 <$0.10

這個優化計畫將使您的分類系統達到業界領先的 95%+ 覆蓋率！
