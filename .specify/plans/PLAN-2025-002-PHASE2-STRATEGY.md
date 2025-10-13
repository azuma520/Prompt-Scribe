# Phase 2 策略規劃：基於 Phase 1 數據分析

**規劃日期：** 2025-10-08  
**數據基礎：** Phase 1 實作成果  
**規劃目標：** 將覆蓋率從 29.5% 提升至 90%+

---

## 📊 一、Phase 1 客觀數據總結

### 1.1 核心成就

| 指標 | 數值 | 評級 |
|------|------|------|
| **TOP 30 覆蓋率** | **100.0%** | ⭐⭐⭐⭐⭐ 完美 |
| **加權覆蓋率** | **62.1%** | ⭐⭐⭐⭐⭐ 卓越 |
| 整體覆蓋率 | 29.5% | ⭐⭐ 待改進 |
| 處理速度 | 5.3 秒 | ⭐⭐⭐⭐⭐ 極快 |
| 資料品質 | 100% 通過 | ⭐⭐⭐⭐⭐ 完美 |

### 1.2 關鍵數據洞察

**頻率分層分析（揭示規則式分類的特性）**

| 頻率層級 | 標籤數 | 已分類 | 覆蓋率 | 洞察 |
|----------|--------|--------|--------|------|
| 超高頻 (>1M) | 90 | 70 | **77.8%** | ✅ 規則式擅長領域 |
| 高頻 (100k-1M) | 651 | 296 | **45.5%** | ⚠️ 改進空間大 |
| 中高頻 (10k-100k) | 2,667 | 988 | 37.0% | ⚠️ LLM 機會區 |
| 中頻 (1k-10k) | 6,936 | 2,186 | 31.5% | ⚠️ LLM 機會區 |
| 低頻 (100-1k) | 14,130 | 3,961 | 28.0% | 📊 長尾區域 |
| 極低頻 (<100) | 6,308 | 1,587 | 25.2% | 📊 長尾區域 |

**發現：**
- 越高頻的標籤，規則式分類效果越好（77.8%）
- 中頻標籤（1k-100k）是 **LLM 的最佳施力點**
- 低頻標籤（<1k）成本效益低，可考慮不處理

### 1.3 未分類高價值標籤（優化目標）

**TOP 20 未分類高頻標籤：**
1. thighhighs (2,333,690) - 服裝/腿部
2. navel (2,305,644) - 身體特徵
3. jewelry (2,126,668) - 配飾
4. cleavage (2,005,296) - 身體特徵
5. nipples (1,659,754) - 身體特徵
6. underwear (1,587,522) - 服裝
7. collarbone (1,577,720) - 身體特徵
8. tail (1,568,934) - 身體特徵/動物
9. ahoge (1,297,540) - 髮型
10. panties (1,294,874) - 服裝
... 等共 21,694 個未分類標籤

**特徵分析：**
- 大多是具體、細節的描述
- 規則式分類難以窮舉
- **非常適合 LLM 語意理解**

---

## 🎯 二、Phase 2 目標設定

### 2.1 量化目標

| 目標 | 當前 | 目標 | 提升 |
|------|------|------|------|
| **整體覆蓋率** | 29.5% | **90%+** | +60.5% |
| TOP 30 覆蓋率 | 100% | 100% | 維持 |
| 加權覆蓋率 | 62.1% | 85%+ | +22.9% |
| 副分類覆蓋率 | 46.2% | 70%+ | +23.8% |

### 2.2 質量目標

- 分類準確率：≥ 85%（人工抽樣驗證）
- LLM 推理記錄：100%（所有調用都記錄）
- API 成功率：≥ 95%（含重試機制）
- 成本控制：< $100

### 2.3 非功能目標

- 處理時間：< 30 分鐘（含 LLM 調用）
- 可降級運行：API 失敗時使用規則式
- 完整記錄：所有 LLM 決策可追溯
- 可重現性：相同輸入產生相同結果

---

## 🚀 三、推薦策略：階梯式混合分類

### 3.1 核心理念

**"規則優先，LLM 補充，成本最優"**

```
標籤輸入
  ↓
[1] 規則式分類 (Phase 1)
  ├─ 已分類 (62.1%) → ✅ 直接使用（零成本）
  └─ 未分類 (37.9%)
       ↓
    [2] 數據清洗
       ├─ 無效標籤 → ❌ 過濾
       ├─ 專有名詞 → 📝 標記但不分類
       └─ 真實標籤 → 繼續
           ↓
        [3] 頻率篩選
           ├─ 高頻 (>10k) → LLM 處理（優先）
           ├─ 中頻 (1k-10k) → LLM 處理（次要）
           └─ 低頻 (<1k) → 跳過或低優先級
               ↓
            [4] LLM 批次分類
               ↓
            [5] 結果驗證與記錄
```

### 3.2 具體實施步驟

#### 階段 2A：數據清洗與規則擴展（1-2 天）

**成本：$0**  
**預期提升：+10-15% 覆蓋率**

1. **過濾無效標籤**
   ```sql
   -- 移除特殊字元標籤
   DELETE FROM tags_final 
   WHERE danbooru_cat = 0 
     AND name REGEXP '^[^a-zA-Z0-9_]+$';
   
   -- 標記專有名詞（不需要分類）
   UPDATE tags_final 
   SET danbooru_cat = 4  -- 標記為角色類
   WHERE name LIKE '%_(%' 
      OR name LIKE '%)%';
   ```

2. **擴展規則庫**
   - 分析 TOP 100-200 未分類標籤
   - 手動添加 100-200 個關鍵字
   - 重點：服裝細節、身體特徵、具體物件

3. **驗證改進**
   - 重新運行管線
   - 預期覆蓋率：29.5% → 40-45%

#### 階段 2B：LLM 高頻標籤處理（2-3 天）

**成本：$10-20**  
**預期提升：+15-20% 覆蓋率**

1. **目標標籤**
   - post_count > 10,000 的未分類標籤
   - 數量：約 2,054 個
   - 特徵：具體、高價值

2. **LLM 配置**
   - 模型：OpenAI GPT-4o-mini
   - 批次大小：100 個/次
   - Prompt 模板：
     ```
     分類以下 Danbooru 圖像標籤到這 9 個類別之一：
     1. CHARACTER_RELATED（人物相關）
     2. OBJECTS（物件道具）
     ...
     
     標籤：{tag_list}
     
     返回 JSON 格式：
     [{"tag": "...", "main_category": "...", "sub_category": "...", "confidence": 0.95}]
     ```

3. **結果處理**
   - 記錄所有 LLM 推理到 `llm_inference_log` 表
   - confidence < 0.7 的標記為低信心
   - 人工抽樣驗證 100 個

#### 階段 2C：LLM 中頻標籤處理（可選，3-5 天）

**成本：$30-50**  
**預期提升：+15-25% 覆蓋率**

1. **目標標籤**
   - 1,000 < post_count < 10,000
   - 數量：約 6,936 個

2. **優化策略**
   - 相似標籤分組批次處理
   - 使用更便宜的模型（GPT-3.5-turbo）
   - 只處理非專有名詞

---

## 💰 四、成本效益分析

### 4.1 策略對比

| 策略 | 處理標籤數 | 預估成本 | 預期覆蓋率 | ROI |
|------|------------|----------|------------|-----|
| **2A: 擴展規則** | +5,000 | $0 | 40-45% | ⭐⭐⭐⭐⭐ |
| **2B: LLM 高頻** | ~2,000 | $10-20 | 55-65% | ⭐⭐⭐⭐⭐ |
| **2C: LLM 中頻** | ~7,000 | $30-50 | 75-85% | ⭐⭐⭐⭐ |
| **2D: LLM 全量** | ~22,000 | $80-150 | 90-95% | ⭐⭐⭐ |

### 4.2 推薦方案

**方案一：保守型（推薦預算緊張時）**
- 執行：2A + 2B
- 總成本：$10-20
- 預期覆蓋率：55-65%
- 時間：3-5 天

**方案二：平衡型（推薦） ✅**
- 執行：2A + 2B + 2C
- 總成本：$30-50
- 預期覆蓋率：75-85%
- 時間：5-8 天

**方案三：激進型（追求極致）**
- 執行：2A + 2B + 2C + 2D
- 總成本：$80-150
- 預期覆蓋率：90-95%
- 時間：7-10 天

---

## 📋 五、詳細行動計畫

### Phase 2A：數據清洗與規則擴展

**時程：Day 1-2**

```markdown
Day 1：數據清洗
- [ ] 分析 EnglishDictionary.csv 的標籤
- [ ] 建立過濾規則（特殊字元、非圖像詞彙）
- [ ] 標記專有名詞（角色名、系列名）
- [ ] 重新計算基準覆蓋率
- [ ] 產出：cleaned_tags.db

Day 2：規則擴展
- [ ] 分析 TOP 200 未分類標籤
- [ ] 分類為：可添加規則 vs 需要 LLM
- [ ] 添加 100-200 個關鍵字
  - 服裝細節：thighhighs, pantyhose, underwear
  - 身體特徵：navel, cleavage, collarbone, thighs
  - 配飾：jewelry, earrings
  - 姿態：ahoge (髮型)
  - 效果：greyscale, comic, sweat
- [ ] 運行測試，驗證改進
- [ ] 產出：更新的分類器 v1.1
```

### Phase 2B：LLM 高頻標籤處理

**時程：Day 3-5**

```markdown
Day 3：LLM 整合準備
- [ ] 設計 LLM Prompt 模板
- [ ] 實作 API 調用模組（含重試、限流）
- [ ] 建立 llm_inference_log 表
- [ ] 準備測試集（100 個人工標註）

Day 4：批次處理實作
- [ ] 實作批次分類函式（100 個/批）
- [ ] 實作結果解析與驗證
- [ ] 實作 confidence 計算
- [ ] 處理高頻標籤（post_count > 10k）
- [ ] 預估：2,054 個標籤，~21 批次

Day 5：驗證與優化
- [ ] 人工抽樣驗證 100 個
- [ ] 計算準確率
- [ ] 調整 Prompt（如需要）
- [ ] 重新處理低信心標籤
- [ ] 產出：LLM 分類結果 v1.0
```

### Phase 2C：LLM 中頻標籤處理（可選）

**時程：Day 6-8**

```markdown
Day 6-7：中頻標籤處理
- [ ] 處理 1k < post_count < 10k
- [ ] 約 6,936 個標籤，~70 批次
- [ ] 使用更便宜的模型（GPT-3.5-turbo）
- [ ] 實作成本監控

Day 8：整合與驗證
- [ ] 合併規則式 + LLM 結果
- [ ] 計算最終覆蓋率
- [ ] 生成 Phase 2 完成報告
```

---

## 🔬 六、技術實作細節

### 6.1 混合式分類架構

```python
# run_pipeline_phase2.py

def classify_tag_hybrid(tag_name: str, use_llm: bool = True) -> Tuple[str, str, str]:
    """
    混合式分類（規則 + LLM）
    
    Returns:
        (main_category, sub_category, source)
        source: 'rule' or 'llm'
    """
    # Step 1: 規則式分類
    main, sub = classify_tag(tag_name)
    
    if main is not None:
        return (main, sub, 'rule')
    
    # Step 2: LLM 分類（如果啟用）
    if use_llm:
        main, sub, confidence = classify_with_llm(tag_name)
        
        # 記錄 LLM 推理
        log_llm_inference(
            tag_name=tag_name,
            model='gpt-4o-mini',
            result={'main': main, 'sub': sub, 'confidence': confidence}
        )
        
        return (main, sub, 'llm')
    
    return (None, None, 'unclassified')
```

### 6.2 LLM Prompt 設計

```python
CLASSIFICATION_PROMPT = """
你是一個 Danbooru 圖像標籤分類專家。請將以下標籤分類到對應的類別。

## 分類系統（9 個主分類）

1. **QUALITY** - 品質等級（masterpiece, best_quality）
2. **TECHNICAL** - 技術規格（highres, 4k）
3. **ART_STYLE** - 藝術風格（anime, realistic）
4. **COMPOSITION** - 構圖技法（from_above, portrait）
5. **VISUAL_EFFECTS** - 視覺效果（lighting, bloom）
6. **CHARACTER_RELATED** - 人物相關（1girl, dress, long_hair）
   - 副分類：CLOTHING（服裝）, HAIR（頭髮）, CHARACTER_COUNT（角色數量）
7. **ACTION_POSE** - 動作姿態（sitting, smile）
   - 副分類：POSE（姿勢）, EXPRESSION（表情）
8. **OBJECTS** - 物件道具（sword, flower）
9. **ENVIRONMENT** - 場景環境（indoors, forest）

## 分類規則

- 按優先級順序：QUALITY > TECHNICAL > ART_STYLE > ... > ENVIRONMENT
- 一個標籤只能屬於一個主分類
- 副分類可選（僅 CHARACTER_RELATED 和 ACTION_POSE）
- 使用 confidence 表示信心度（0-1）

## 待分類標籤

{tag_list}

## 輸出格式（JSON）

[
    {"tag": "thighhighs", "main_category": "CHARACTER_RELATED", "sub_category": "CLOTHING", "confidence": 0.95},
    {"tag": "navel", "main_category": "CHARACTER_RELATED", "sub_category": null, "confidence": 0.90}
]
"""
```

### 6.3 資料庫 Schema 擴展

```sql
-- 新增：LLM 推理記錄表
CREATE TABLE llm_inference_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL,
    model TEXT NOT NULL,          -- 'gpt-4o-mini'
    prompt_hash TEXT,             -- Prompt 的 hash（用於去重）
    input_tokens INTEGER,
    output_tokens INTEGER,
    main_category TEXT,
    sub_category TEXT,
    confidence REAL,
    raw_response TEXT,            -- 完整 LLM 回應
    api_latency REAL,             -- API 延遲（秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_name) REFERENCES tags_final(name)
);

-- 新增：分類來源欄位
ALTER TABLE tags_final ADD COLUMN classification_source TEXT;
-- 值：'rule', 'llm', 'manual'
```

---

## 📊 七、成本詳細預估

### 7.1 OpenAI GPT-4o-mini 定價

- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens

### 7.2 Token 使用預估

**單次批次處理（100 個標籤）：**
- Prompt tokens: ~1,500（系統提示 + 9 個分類說明）
- 標籤 tokens: ~200（100 個標籤，平均 2 tokens/個）
- 輸出 tokens: ~600（100 個標籤的 JSON 回應）
- **總計：~2,300 tokens/批次**

**成本計算：**
```
2,054 個高頻標籤 = 21 批次
21 批次 × 2,300 tokens = 48,300 tokens
成本 = (48,300 × 0.15 + 48,300 × 0.60) / 1,000,000
     = $0.036（約 $0.04）

實際預估（含重試）：$10-20
```

### 7.3 預算分配建議

| 階段 | 目標 | 預算 | 產出 |
|------|------|------|------|
| 2A | 規則擴展 | $0 | 覆蓋率 +10% |
| 2B | 高頻 LLM | $10-20 | 覆蓋率 +20% |
| 2C | 中頻 LLM | $30-50 | 覆蓋率 +25% |
| **總計** | **90% 覆蓋** | **$40-70** | **Phase 2 完成** |

---

## 🎯 八、里程碑與驗收標準

### Milestone 1：數據清洗完成（Week 1）
- [ ] 無效標籤過濾完成
- [ ] 規則庫擴展至 200+ 關鍵字
- [ ] 覆蓋率達到 40-45%
- [ ] 測試通過率維持 100%

### Milestone 2：LLM 高頻處理完成（Week 2）
- [ ] llm_inference_log 表建立
- [ ] 2,054 個高頻標籤 LLM 分類完成
- [ ] 覆蓋率達到 55-65%
- [ ] 準確率 ≥ 85%（人工驗證）

### Milestone 3：Phase 2 完成（Week 3-4）
- [ ] 中頻標籤 LLM 處理完成
- [ ] 覆蓋率達到 75-90%
- [ ] 完整的混合式分類系統
- [ ] 所有 LLM 調用都有記錄

---

## 🚧 九、風險與緩解

### 9.1 技術風險

| 風險 | 影響 | 緩解策略 |
|------|------|----------|
| LLM API 限流 | High | 實作重試機制、降低批次大小 |
| LLM 分類錯誤 | Medium | 人工驗證、confidence 閾值過濾 |
| 成本超支 | Medium | 實作成本監控、設定預算上限 |
| API 服務中斷 | Low | 降級至規則式分類 |

### 9.2 質量風險

| 風險 | 影響 | 緩解策略 |
|------|------|----------|
| LLM 不一致性 | Medium | 固定 temperature=0, 使用 JSON mode |
| 分類不準確 | High | 人工抽樣驗證、建立黃金測試集 |
| 規則衝突 | Low | LLM 使用相同優先級順序 |

---

## 📈 十、成功指標（Phase 2）

### 10.1 核心指標

| 指標 | 目標 | 測量方法 |
|------|------|----------|
| 整體覆蓋率 | ≥ 90% | `SELECT COUNT(main_category IS NOT NULL) / COUNT(*)` |
| 加權覆蓋率 | ≥ 85% | 按 post_count 加權計算 |
| 分類準確率 | ≥ 85% | 人工驗證 100 個抽樣 |
| LLM 成本 | < $100 | 記錄所有 API 調用成本 |
| 處理時間 | < 30 分鐘 | 端到端測試 |

### 10.2 質量指標

| 指標 | 目標 | 測量方法 |
|------|------|----------|
| 記錄完整性 | 100% | 所有 LLM 調用都有 log |
| 可重現性 | 100% | 相同輸入產生相同結果 |
| 降級可用性 | 100% | API 失敗時仍能運行 |

---

## 🎬 十一、立即可執行的下一步

### 本週行動（優先級排序）

**1. 分析未分類高頻標籤（1 小時）**
```bash
cd stage1
python -c "
import sqlite3
conn = sqlite3.connect('output/tags.db')
result = conn.execute('''
    SELECT name, post_count
    FROM tags_final
    WHERE danbooru_cat = 0 AND main_category IS NULL AND post_count > 10000
    ORDER BY post_count DESC
    LIMIT 100
''').fetchall()
with open('output/high_freq_unclassified.txt', 'w') as f:
    for name, count in result:
        f.write(f'{name},{count}\n')
print(f'已輸出 {len(result)} 個高頻未分類標籤')
conn.close()
"
```

**2. 手動審查並分類（2-3 小時）**
- 開啟 `output/high_freq_unclassified.txt`
- 人工判斷每個標籤應屬於哪個分類
- 識別可添加的關鍵字

**3. 擴展規則庫（1-2 小時）**
- 在 `src/classifier/rules/*.py` 添加關鍵字
- 運行測試驗證
- 重新運行管線

**4. 評估改進效果（30 分鐘）**
```bash
python final_validation.py
python check_real_tags.py
```

### 下週行動

**5. 準備 LLM 整合**
- 選擇 LLM 提供商並申請 API key
- 實作 LLM 調用模組
- 建立測試集

**6. 開發 Phase 2 管線**
- 整合混合式分類邏輯
- 實作批次處理
- 建立 LLM 記錄系統

---

## 📚 十二、參考資料與工具

### 數據分析工具（已完成）
- `final_validation.py` - 最終驗證
- `check_real_tags.py` - 高頻標籤檢查
- `generate_detailed_stats.py` - 詳細統計
- `output/DATA_ANALYSIS.md` - 本文件

### 下一階段需要的工具
- [ ] `filter_invalid_tags.py` - 過濾無效標籤
- [ ] `expand_rules.py` - 規則擴展工具
- [ ] `llm_classifier.py` - LLM 分類模組
- [ ] `batch_processor.py` - 批次處理器
- [ ] `cost_monitor.py` - 成本監控

---

## ✅ 十三、決策建議

基於客觀數據分析，我的建議：

### 短期（立即執行）
✅ **採用策略 2A（規則擴展）**
- 零成本
- 1-2 天完成
- 預期提升至 40-45% 覆蓋率
- 為 LLM 階段建立更好基準

### 中期（下週開始）
✅ **採用策略 2B（LLM 高頻）**
- 成本 $10-20（可接受）
- 2-3 天完成
- 預期達到 55-65% 覆蓋率
- 覆蓋最重要的未分類標籤

### 長期（評估後決定）
❓ **考慮策略 2C（LLM 中頻）**
- 根據 2B 的效果決定
- 如果 2B 達到 60%+，可能不需要 2C
- 如果需要 90% 覆蓋率，則執行 2C

---

## 📊 十四、關鍵數據表格

### Phase 1 vs Phase 2 預期對比

| 指標 | Phase 1 | Phase 2 預期 | 提升 |
|------|---------|--------------|------|
| 整體覆蓋率 | 29.5% | 75-90% | +45-60% |
| 加權覆蓋率 | 62.1% | 85-95% | +23-33% |
| 已分類標籤數 | 9,088 | 23,000-27,000 | +14k-18k |
| 處理時間 | 5.3 秒 | 5-30 分鐘 | - |
| 總成本 | $0 | $30-70 | +$30-70 |

### 不同頻率層級的優化潛力

| 頻率層級 | 標籤數 | Phase 1 覆蓋 | 優化目標 | 方法 |
|----------|--------|--------------|----------|------|
| 超高頻 (>1M) | 90 | 77.8% | 95%+ | 規則擴展 |
| 高頻 (100k-1M) | 651 | 45.5% | 85%+ | 規則+LLM |
| 中高頻 (10k-100k) | 2,667 | 37.0% | 75%+ | LLM 為主 |
| 中頻 (1k-10k) | 6,936 | 31.5% | 60%+ | 選擇性 LLM |
| 低頻 (<1k) | 20,438 | 27.0% | 30-40% | 不優化 |

---

## 🎯 十五、最終建議

基於**客觀數據分析**，建議採取以下策略：

### 推薦路徑：階梯式優化 ✅

**Week 1: Phase 2A（規則擴展）**
- 投入：2 天，$0
- 產出：40-45% 覆蓋率
- 價值：快速勝利，零成本

**Week 2-3: Phase 2B（LLM 高頻）**
- 投入：3-5 天，$10-20
- 產出：55-65% 覆蓋率
- 價值：高價值標籤全覆蓋

**Week 3-4: 評估與決策**
- 如果需要 90% 覆蓋率 → 執行 Phase 2C
- 如果 60% 足夠 → 進入 Stage 2 開發

### 成功的關鍵

1. **數據驅動**：基於實際數據，不憑感覺
2. **成本控制**：階梯式投入，及時止損
3. **質量優先**：準確率 > 覆蓋率
4. **記錄完整**：所有決策可追溯

---

**規劃完成日期：** 2025-10-08  
**下一步：** 批准策略並開始執行 Phase 2A

================================================================================

