# Phase 2 更新策略：基於 Danbooru 分類整合後的新格局

**計畫編號：** PLAN-2025-003-PHASE2-UPDATED  
**版本：** 1.0.0  
**規劃日期：** 2025-10-09  
**狀態：** Planning  
**前置完成：** Phase 1 + Danbooru 分類整合

---

## 🎉 重大突破：格局已變

### Phase 1 原始成果 vs 整合後成果

| 指標 | Phase 1 原始 | Danbooru 整合後 | 提升 |
|------|-------------|----------------|------|
| **整體覆蓋率** | 29.5% | **84.6%** | **+55.1%** 🚀 |
| 已分類標籤數 | 9,088 | **119,088** | **+110,000** |
| 未分類標籤數 | 21,694 | **21,694** | 0 (同樣的) |
| 分類來源 | 規則 100% | 規則 7.6% + Danbooru 92.4% | 混合 |

### 關鍵發現

✅ **Danbooru 分類整合已解決大部分問題**
- CHARACTER（角色）：40,931 個 ✅
- COPYRIGHT（版權作品）：9,478 個 ✅
- ARTIST（藝術家）：59,201 個 ✅

❗ **剩餘未分類的 21,694 個標籤都是 `danbooru_cat=0`（一般標籤）**
- 這些才是真正需要 Phase 2 處理的對象
- 佔總標籤數的 15.4%

---

## 📊 剩餘未分類標籤深度分析

### 數量與頻率分布

```sql
-- 查詢剩餘未分類標籤的頻率分布
SELECT 
    CASE 
        WHEN post_count >= 1000000 THEN '超高頻 (>1M)'
        WHEN post_count >= 100000 THEN '高頻 (100k-1M)'
        WHEN post_count >= 10000 THEN '中高頻 (10k-100k)'
        WHEN post_count >= 1000 THEN '中頻 (1k-10k)'
        WHEN post_count >= 100 THEN '低頻 (100-1k)'
        ELSE '極低頻 (<100)'
    END as freq_tier,
    COUNT(*) as tag_count,
    SUM(post_count) as total_usage
FROM tags_final
WHERE danbooru_cat = 0 
  AND main_category IS NULL
GROUP BY freq_tier;
```

**預估分布：**（基於昨天的分析）

| 頻率層級 | 標籤數（估計） | 總使用次數 | 優先級 | 建議策略 |
|----------|---------------|-----------|--------|---------|
| 超高頻 (>1M) | ~20 | ~30M | 🔴 最高 | 手動 + 規則 |
| 高頻 (100k-1M) | ~300 | ~100M | 🟠 高 | 規則 + LLM |
| 中高頻 (10k-100k) | ~1,000 | ~50M | 🟡 中 | LLM |
| 中頻 (1k-10k) | ~3,500 | ~20M | 🟢 低 | 選擇性 LLM |
| 低頻 (<1k) | ~17,000 | ~5M | ⚪ 極低 | 忽略 |

### TOP 20 未分類高頻標籤（已知）

1. **thighhighs** (2,333,690) - 服裝/腿部
2. **navel** (2,305,644) - 身體特徵
3. **jewelry** (2,126,668) - 配飾
4. **cleavage** (2,005,296) - 身體特徵
5. **nipples** (1,659,754) - 身體特徵
6. **underwear** (1,587,522) - 服裝
7. **collarbone** (1,577,720) - 身體特徵
8. **tail** (1,568,934) - 身體特徵/動物
9. **ahoge** (1,297,540) - 髮型
10. **panties** (1,294,874) - 服裝
11. **sidelocks** (1,225,240) - 髮型
12. **ass** (1,184,226) - 身體特徵
13. **thighs** (1,129,646) - 身體特徵
14. **earrings** (1,116,770) - 配飾
15. **:d** (1,099,420) - 表情
16. **hetero** (1,086,582) - 關係/場景
17. **comic** (1,078,462) - 媒體類型
18. **pantyhose** (1,057,846) - 服裝
19. **sweat** (1,045,954) - 視覺效果
20. **greyscale** (1,002,774) - 視覺效果

---

## 🎯 Phase 2 更新目標

### 修訂後的目標

| 指標 | 當前 | 目標 | 提升 | 策略 |
|------|------|------|------|------|
| **整體覆蓋率** | 84.6% | **90-95%** | +5.4-10.4% | 規則擴展為主 |
| **一般標籤覆蓋率** | 29.5% | **70-80%** | +40.5-50.5% | 規則 + LLM |
| **加權覆蓋率** | ~85% | **95%+** | +10% | 高頻優先 |
| **未分類標籤** | 21,694 | **<7,000** | -14,000+ | 階梯處理 |

### 成本重估

**原估計（基於 29.5%）：**
- 需要 LLM 處理：~15,000 個標籤
- 預估成本：$30-70

**新估計（基於 84.6%）：**
- 需要 LLM 處理：~4,500 個標籤（中高頻以上）
- 預估成本：**$15-30** ✅ 大幅降低！

---

## 🚀 Phase 2 階梯式執行計畫

### 階段 2A：規則擴展（高價值、零成本）

**時程：** Day 1-2  
**成本：** $0  
**預期提升：** +15-20% 覆蓋率（達到 90%+）

#### 具體任務

**Day 1：快速勝利 - 添加明顯規則**

```python
# 服裝配件（新增到 CLOTHING）
clothing_additions = [
    'thighhighs', 'pantyhose', 'underwear', 'panties',
    'bra', 'bikini', 'swimsuit', 
    'stockings', 'legwear', 'footwear',
]

# 身體特徵（新增 BODY_FEATURES 副分類）
body_features = [
    'navel', 'cleavage', 'collarbone', 'nipples',
    'ass', 'thighs', 'breasts', 'chest',
    'stomach', 'waist', 'hips', 'legs',
]

# 配飾（新增到 OBJECTS 或 CHARACTER_RELATED）
accessories = [
    'jewelry', 'earrings', 'necklace', 'bracelet',
    'ring', 'piercing', 'accessory',
]

# 視覺效果（新增到 VISUAL_EFFECTS）
visual_effects = [
    'greyscale', 'monochrome', 'sepia',
    'blurry', 'motion_blur', 'depth_of_field',
    'chromatic_aberration', 'film_grain',
]

# 媒體類型（新增到 TECHNICAL）
media_types = [
    'comic', 'manga', 'sketch', 'lineart',
    'rough', 'animated', 'gif',
]
```

**Day 2：副分類擴展**

1. **新增 `BODY_FEATURES` 副分類到 `CHARACTER_RELATED`**
   ```python
   SUB_CATEGORIES = {
       'CHARACTER_RELATED': {
           'CLOTHING': '服裝',
           'HAIR': '頭髮',
           'CHARACTER_COUNT': '角色數量',
           'BODY_FEATURES': '身體特徵',  # 新增
       }
   }
   ```

2. **新增 `ACCESSORIES` 副分類**
   ```python
   SUB_CATEGORIES = {
       'CHARACTER_RELATED': {
           # ... 現有
           'ACCESSORIES': '配飾',  # 新增
       }
   }
   ```

3. **更新分類邏輯**
   - 優先級調整
   - 避免衝突
   - 測試驗證

**預期成果：**
- 覆蓋率：84.6% → **90-92%** ✅
- 新分類標籤：~7,500 個
- 剩餘未分類：~14,000 個

---

### 階段 2B：LLM 高頻標籤處理（選擇性）

**時程：** Day 3-5  
**成本：** $10-20  
**預期提升：** +3-5% 覆蓋率（達到 93-97%）

#### 執行條件（決策點）

**如果 2A 達到 90%+：** ✅ 可選，根據需求決定  
**如果 2A 低於 90%：** ⚠️ 必須執行

#### 目標標籤

```sql
-- 剩餘的高頻未分類標籤
SELECT name, post_count
FROM tags_final
WHERE danbooru_cat = 0 
  AND main_category IS NULL
  AND post_count > 10000
ORDER BY post_count DESC;
```

預估：~1,000-2,000 個標籤

#### LLM 配置

**模型選擇：**
- 主要：GPT-4o-mini（平衡成本與質量）
- 備選：GPT-3.5-turbo（如預算緊張）

**Prompt 設計：**

```python
PHASE2_CLASSIFICATION_PROMPT = """
你是 Danbooru 標籤分類專家。請將以下標籤分類到 12 個主分類之一。

## 12 個主分類

**內容維度：**
1. CHARACTER_RELATED - 人物相關（外觀特徵、服裝、配飾）
   - 副分類：CLOTHING, HAIR, BODY_FEATURES, ACCESSORIES, CHARACTER_COUNT
2. CHARACTER - 角色名稱（具體角色）
3. OBJECTS - 物件道具
4. ENVIRONMENT - 場景環境

**表現維度：**
5. COMPOSITION - 構圖技法
6. VISUAL_EFFECTS - 視覺效果
7. ART_STYLE - 藝術風格
8. ACTION_POSE - 動作姿態
   - 副分類：POSE, EXPRESSION

**元資訊維度：**
9. COPYRIGHT - 版權作品
10. ARTIST - 藝術家
11. QUALITY - 品質等級
12. TECHNICAL - 技術規格

## 分類規則

- 按優先級：QUALITY > TECHNICAL > CHARACTER > COPYRIGHT > ARTIST > ...
- CHARACTER_RELATED 包含身體特徵（navel, cleavage）、服裝（thighhighs）、配飾（jewelry）
- 身體特徵屬於 CHARACTER_RELATED.BODY_FEATURES
- 模糊表情符號（:d, :o）屬於 ACTION_POSE.EXPRESSION

## 待分類標籤

{tag_list}

## 輸出格式（JSON）

[
    {
        "tag": "thighhighs",
        "main_category": "CHARACTER_RELATED",
        "sub_category": "CLOTHING",
        "confidence": 0.95,
        "reasoning": "腿部服裝"
    }
]
"""
```

#### 批次處理策略

```python
# batch_llm_processor.py

def process_unclassified_batch(
    tags: List[str],
    batch_size: int = 50,
    model: str = "gpt-4o-mini"
) -> List[dict]:
    """
    批次處理未分類標籤
    """
    results = []
    
    for i in range(0, len(tags), batch_size):
        batch = tags[i:i+batch_size]
        
        # 調用 LLM
        response = call_openai_api(
            model=model,
            prompt=PHASE2_CLASSIFICATION_PROMPT.format(
                tag_list=", ".join(batch)
            ),
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        # 解析結果
        parsed = parse_llm_response(response)
        
        # 記錄推理
        log_llm_inference(
            batch=batch,
            model=model,
            response=response,
            parsed_results=parsed
        )
        
        results.extend(parsed)
        
        # 成本控制：實時監控
        current_cost = calculate_cost(response)
        if get_total_cost() > MAX_BUDGET:
            logging.warning("達到預算上限，停止處理")
            break
    
    return results
```

---

### 階段 2C：中頻標籤處理（可選）

**時程：** Day 6-8  
**成本：** $10-20  
**預期提升：** +2-3% 覆蓋率（達到 95-99%）

#### 執行條件

**只在以下情況執行：**
- 2A + 2B 後覆蓋率 < 95%
- 且有預算和時間
- 且確實需要更高覆蓋率

#### 目標

```sql
SELECT COUNT(*) 
FROM tags_final
WHERE danbooru_cat = 0 
  AND main_category IS NULL
  AND post_count BETWEEN 1000 AND 10000;
```

預估：~3,500 個標籤

#### 策略

- 使用更便宜的 GPT-3.5-turbo
- 更大的批次（100 個/次）
- 只處理非專有名詞
- confidence < 0.7 跳過

---

## 📊 Phase 2 完整時程與里程碑

### Week 1：規則擴展（必做）

| Day | 任務 | 產出 | 成功標準 |
|-----|------|------|---------|
| **Day 1** | 分析未分類標籤<br>添加明顯規則 | 200+ 新關鍵字 | 通過測試 |
| **Day 2** | 新增副分類<br>驗證改進 | 覆蓋率報告 | 覆蓋率 ≥ 90% |

**Milestone 1：** 達到 90% 整體覆蓋率 ✅

### Week 2：LLM 整合（選擇性）

| Day | 任務 | 產出 | 成功標準 |
|-----|------|------|---------|
| **Day 3** | LLM 模組開發<br>Prompt 設計 | LLM 分類器 | API 測試通過 |
| **Day 4** | 高頻標籤批次處理 | 1,000-2,000 個分類 | 準確率 ≥ 85% |
| **Day 5** | 驗證與優化 | 最終報告 | 覆蓋率 ≥ 93% |

**Milestone 2：** 達到 93-97% 覆蓋率 ✅

### Week 3：可選深化

**只在需要時執行：**
- Day 6-8：中頻標籤 LLM 處理
- Day 9-10：最終優化與文檔

**Milestone 3：** 達到 95-99% 覆蓋率（可選）

---

## 💰 更新的成本效益分析

### 成本大幅降低

| 方案 | 原估計（29.5%基礎） | 新估計（84.6%基礎） | 降幅 |
|------|-------------------|-------------------|------|
| 規則擴展 (2A) | $0 | $0 | - |
| LLM 高頻 (2B) | $10-20 | $10-15 | -25% |
| LLM 中頻 (2C) | $30-50 | $10-20 | -60% |
| **總計（90% 目標）** | **$40-70** | **$0-15** | **-78%** 🎉 |
| **總計（95% 目標）** | **$70-120** | **$10-35** | **-71%** 🎉 |

### ROI 分析

| 投資 | 產出 | ROI |
|------|------|-----|
| 2A：2 天工作 | 覆蓋率 +5-8%（達到 90%） | ⭐⭐⭐⭐⭐ 極高 |
| 2B：3 天工作 + $10-15 | 覆蓋率 +3-5%（達到 93-95%） | ⭐⭐⭐⭐ 高 |
| 2C：3 天工作 + $10-20 | 覆蓋率 +2-3%（達到 95-97%） | ⭐⭐⭐ 中等 |

---

## 🎯 推薦執行方案

### 方案 A：保守型（推薦）✅

**執行：** 僅 2A（規則擴展）  
**時程：** 2 天  
**成本：** $0  
**產出：** 90-92% 覆蓋率

**適合：**
- 預算有限
- 時間緊張
- 90% 覆蓋率已滿足需求

### 方案 B：平衡型

**執行：** 2A + 2B  
**時程：** 5 天  
**成本：** $10-15  
**產出：** 93-95% 覆蓋率

**適合：**
- 追求更高質量
- 有合理預算
- 想處理所有高頻標籤

### 方案 C：完美型

**執行：** 2A + 2B + 2C  
**時程：** 8-10 天  
**成本：** $20-35  
**產出：** 95-99% 覆蓋率

**適合：**
- 追求極致覆蓋率
- 預算充足
- 有充足時間

---

## 🔬 技術實作要點

### 1. 規則擴展最佳實踐

```python
# src/classifier/rules/character_sub_rules.py

# 新增身體特徵副分類
def _is_body_features(self, tag: str) -> bool:
    """判斷是否為身體特徵"""
    body_keywords = {
        'navel', 'belly', 'stomach', 'abs',
        'cleavage', 'chest', 'breasts', 'bust',
        'collarbone', 'neck', 'shoulders',
        'nipples', 'areola',
        'ass', 'butt', 'buttocks',
        'thighs', 'legs', 'feet',
        'arms', 'hands', 'fingers',
        'back', 'spine', 'waist', 'hips',
    }
    
    # 解剖相關後綴
    if tag.endswith('_anatomy') or '_muscle' in tag:
        return True
    
    return any(word in tag for word in body_keywords)

# 更新分類優先級
def classify(self, tag_name: str) -> Optional[str]:
    # 優先級 1：角色數量
    if self._is_character_count(tag_name):
        return 'CHARACTER_COUNT'
    
    # 優先級 2：服裝
    if self._is_clothing(tag_name):
        return 'CLOTHING'
    
    # 優先級 3：頭髮
    if self._is_hair(tag_name):
        return 'HAIR'
    
    # 優先級 4：身體特徵（新增）
    if self._is_body_features(tag_name):
        return 'BODY_FEATURES'
    
    # 優先級 5：配飾（新增）
    if self._is_accessories(tag_name):
        return 'ACCESSORIES'
    
    return None
```

### 2. LLM 整合架構

```python
# src/llm/classifier.py

class LLMClassifier:
    """LLM 標籤分類器"""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_cost: float = 30.0,
        cache_enabled: bool = True
    ):
        self.model = model
        self.max_cost = max_cost
        self.current_cost = 0.0
        self.cache = {} if cache_enabled else None
    
    def classify_batch(
        self,
        tags: List[str],
        batch_size: int = 50
    ) -> List[ClassificationResult]:
        """批次分類標籤"""
        results = []
        
        for i in range(0, len(tags), batch_size):
            # 成本檢查
            if self.current_cost >= self.max_cost:
                logger.warning("達到成本上限，停止處理")
                break
            
            batch = tags[i:i+batch_size]
            
            # 檢查快取
            cached_results = self._check_cache(batch)
            uncached_tags = [t for t in batch if t not in cached_results]
            
            if uncached_tags:
                # 調用 LLM
                llm_results = self._call_llm(uncached_tags)
                
                # 更新快取
                if self.cache is not None:
                    self._update_cache(llm_results)
                
                results.extend(llm_results)
            
            results.extend(cached_results.values())
        
        return results
    
    def _call_llm(self, tags: List[str]) -> List[ClassificationResult]:
        """調用 LLM API"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": self._format_tags(tags)}
                ],
                temperature=0,
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            
            # 計算成本
            cost = self._calculate_cost(response.usage)
            self.current_cost += cost
            
            # 記錄推理
            self._log_inference(tags, response, cost)
            
            # 解析結果
            return self._parse_response(response)
            
        except Exception as e:
            logger.error(f"LLM 調用失敗: {e}")
            return [ClassificationResult(tag=t, error=str(e)) for t in tags]
```

### 3. 混合式分類整合

```python
# run_pipeline_phase2.py

def classify_tag_hybrid(
    tag: TagRecord,
    use_llm: bool = True,
    llm_classifier: Optional[LLMClassifier] = None
) -> ClassificationResult:
    """
    混合式分類：規則優先，LLM 補充
    """
    # Step 1: 檢查 Danbooru 原始分類
    if tag.danbooru_cat in [1, 3, 4, 5]:
        return classify_by_danbooru_cat(tag)
    
    # Step 2: 規則式分類
    main, sub = rule_classifier.classify(tag.name)
    if main is not None:
        return ClassificationResult(
            tag=tag.name,
            main_category=main,
            sub_category=sub,
            source='rule',
            confidence=1.0
        )
    
    # Step 3: LLM 分類（如果啟用且未達成本上限）
    if use_llm and llm_classifier and llm_classifier.can_process():
        llm_result = llm_classifier.classify_single(tag.name)
        if llm_result.confidence >= 0.7:  # 信心閾值
            return llm_result
    
    # Step 4: 無法分類
    return ClassificationResult(
        tag=tag.name,
        main_category=None,
        sub_category=None,
        source='unclassified',
        confidence=0.0
    )
```

---

## 📋 立即可執行的下一步

### 今日（Day 0）：準備工作

```bash
# 1. 分析剩餘未分類標籤
cd stage1
python generate_detailed_stats.py --focus-unclassified

# 2. 產生高頻未分類清單
python -c "
import sqlite3
conn = sqlite3.connect('output/tags.db')
result = conn.execute('''
    SELECT name, post_count, danbooru_cat
    FROM tags_final
    WHERE danbooru_cat = 0 
      AND main_category IS NULL
      AND post_count > 10000
    ORDER BY post_count DESC
''').fetchall()
print(f'高頻未分類標籤數: {len(result)}')
with open('output/phase2_targets.txt', 'w') as f:
    for name, count, cat in result:
        f.write(f'{name},{count},{cat}\n')
"

# 3. 人工審查 TOP 50
head -n 50 output/phase2_targets.txt
```

### 明日（Day 1）：開始 Phase 2A

**Morning：**
- [ ] 建立 `phase2a_rules_expansion` 分支
- [ ] 分析 TOP 100 未分類標籤
- [ ] 設計新的關鍵字集合

**Afternoon：**
- [ ] 實作 `BODY_FEATURES` 副分類
- [ ] 實作 `ACCESSORIES` 副分類
- [ ] 添加 150-200 個新關鍵字

**Evening：**
- [ ] 運行測試
- [ ] 重新生成分類報告
- [ ] 驗證改進效果

---

## ✅ 決策建議

基於 **Danbooru 分類整合的重大突破**，我的建議：

### 短期（本週）：執行 Phase 2A ✅

**理由：**
1. **零成本，高回報**：預期提升 5-8%，達到 90%+ 覆蓋率
2. **快速驗證**：2 天內完成，立即看到效果
3. **建立基準**：為可能的 LLM 階段提供更好的對照組
4. **風險極低**：純規則擴展，可完全控制

### 中期（評估後）：決定是否需要 Phase 2B

**決策點：**
- **如果 2A 達到 90-92%：** 可能不需要 LLM，直接進入 Stage 2
- **如果 2A 低於 90%：** 考慮執行 2B（成本僅 $10-15）
- **如果追求 95%+：** 執行 2B + 2C

### 長期：Stage 2 開發

一旦 Phase 2 完成（無論是 2A 或 2A+2B），即可開始：
1. Supabase 遷移準備
2. 向量化與語意搜尋
3. API 開發
4. 多使用者支援

---

## 📊 預期成果總覽

### Phase 1 → Phase 2 完整演進

| 階段 | 覆蓋率 | 方法 | 成本 | 時間 |
|------|--------|------|------|------|
| Phase 1 初始 | 29.5% | 純規則 | $0 | 3 天 |
| **+ Danbooru 整合** | **84.6%** | **規則 + Danbooru** | **$0** | **+1 天** |
| + Phase 2A | 90-92% | 規則擴展 | $0 | +2 天 |
| + Phase 2B（可選） | 93-95% | 規則 + LLM | $10-15 | +3 天 |
| + Phase 2C（可選） | 95-99% | 規則 + LLM | $20-35 | +5 天 |

### 最終產出（Phase 2 完成後）

1. **高覆蓋率分類系統**
   - 整體覆蓋率：90-99%
   - 高頻標籤：100% 覆蓋

2. **混合式分類架構**
   - Danbooru 分類：92.4%
   - 規則分類：7.6-15%
   - LLM 分類：0-5%（可選）

3. **完整的資料資產**
   - `tags.db`：包含 140,782 個標籤
   - 12 個主分類 + 多個副分類
   - 完整的分類來源追蹤

4. **可擴展的基礎**
   - 為 Stage 2（雲端）做好準備
   - 支援向量化和語意搜尋
   - 多使用者服務基礎

---

## 🎯 關鍵成功因素

1. **Danbooru 整合是最大贏家**
   - 提供了 110,000 個精確分類
   - 大幅降低了 Phase 2 的工作量和成本

2. **規則優先策略正確**
   - 零成本達到 90%+ 是最優解
   - 只在必要時使用 LLM

3. **階梯式執行降低風險**
   - 先做 2A（零風險）
   - 根據結果決定是否需要 2B/2C

4. **成本控制得當**
   - 原估計 $40-70 → 新估計 $0-35
   - 降低 50-100% 成本

---

**規劃完成日期：** 2025-10-09  
**前置完成：** ✅ Phase 1 + Danbooru 整合  
**下一步：** 明日開始執行 Phase 2A（規則擴展）  
**預期完成：** 2025-10-11（2 天後達到 90%+ 覆蓋率）

---

## 📎 附錄：快速參考

### 命令速查

```bash
# 分析未分類標籤
python generate_detailed_stats.py --focus-unclassified

# 運行 Phase 2A 管道
python run_pipeline.py

# 驗證改進
python final_validation.py

# 查看分類報告
cat output/classification_report.txt

# 檢查高頻標籤
python check_real_tags.py --top 100 --unclassified-only
```

### 文件位置

- 計畫文檔：`.specify/plans/PLAN-2025-003-PHASE2-UPDATED.md`（本文件）
- 原策略：`.specify/plans/PLAN-2025-002-PHASE2-STRATEGY.md`
- Phase 1 計畫：`.specify/plans/PLAN-2025-001-PHASE1.md`
- 整合報告：`stage1/INTEGRATION_SUMMARY.md`
- 修復報告：`stage1/BUGFIX_REPORT.md`

================================================================================

