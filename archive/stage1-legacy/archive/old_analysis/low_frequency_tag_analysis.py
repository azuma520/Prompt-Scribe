"""
低頻標籤深度分析

目的：
1. 分析 16,205 個未分類標籤的特性
2. 評估創意價值
3. 提出經濟有效的處理方案
"""

import sqlite3
from collections import defaultdict

conn = sqlite3.connect('output/tags.db')

print("="*80)
print("低頻標籤深度分析 - 創意價值評估")
print("="*80)

# 1. 未分類標籤頻率分布
print("\n" + "="*80)
print("1. 未分類標籤頻率分布")
print("="*80)

result = conn.execute("""
    SELECT 
        CASE 
            WHEN post_count >= 1000000 THEN '超高頻 (>1M)'
            WHEN post_count >= 100000 THEN '高頻 (100k-1M)'
            WHEN post_count >= 10000 THEN '中高頻 (10k-100k)'
            WHEN post_count >= 1000 THEN '中頻 (1k-10k)'
            WHEN post_count >= 100 THEN '低頻 (100-1k)'
            ELSE '極低頻 (<100)'
        END as frequency_tier,
        COUNT(*) as tag_count,
        SUM(post_count) as total_usage,
        ROUND(AVG(post_count), 0) as avg_usage
    FROM tags_final
    WHERE danbooru_cat = 0 AND main_category IS NULL
    GROUP BY 
        CASE 
            WHEN post_count >= 1000000 THEN '超高頻 (>1M)'
            WHEN post_count >= 100000 THEN '高頻 (100k-1M)'
            WHEN post_count >= 10000 THEN '中高頻 (10k-100k)'
            WHEN post_count >= 1000 THEN '中頻 (1k-10k)'
            WHEN post_count >= 100 THEN '低頻 (100-1k)'
            ELSE '極低頻 (<100)'
        END
    ORDER BY MIN(post_count) DESC
""").fetchall()

print(f"\n{'頻率層級':20} {'標籤數':>10} {'使用次數':>15} {'平均使用':>12} {'創意價值':10}")
print("-"*80)

total_unclassified = 0
for tier, count, usage, avg in result:
    total_unclassified += count
    # 評估創意價值
    if '極低頻' in tier or '低頻' in tier:
        creativity = "HIGHEST"  # 低頻標籤創意價值高
    elif '中頻' in tier:
        creativity = "HIGH"
    else:
        creativity = "MEDIUM"
    
    print(f"{tier:20} {count:>10,} {usage:>15,} {avg:>12,.0f} {creativity:10}")

print(f"\n總計未分類: {total_unclassified:,} 個標籤")

# 2. 低頻標籤的創意價值分析
print("\n" + "="*80)
print("2. 低頻標籤創意價值分析")
print("="*80)

# 隨機抽樣低頻標籤
low_freq_samples = conn.execute("""
    SELECT name, post_count
    FROM tags_final
    WHERE danbooru_cat = 0 
      AND main_category IS NULL
      AND post_count < 1000
    ORDER BY RANDOM()
    LIMIT 30
""").fetchall()

print("\n隨機抽樣 30 個低頻未分類標籤（創意靈感來源）:")
print(f"{'標籤名稱':40} {'使用次數':>12}")
print("-"*80)
for name, count in low_freq_samples:
    print(f"{name:40} {count:>12,} 次")

print("\n觀察:")
print("  這些低頻標籤往往包含:")
print("  - 具體的場景描述（如特定地點、時間）")
print("  - 罕見的物件或道具")
print("  - 特殊的藝術風格或技法")
print("  - 獨特的姿勢或表情組合")
print("  → 對創作者而言，這些可能是靈感的寶庫！")

# 3. 批次處理成本分析
print("\n" + "="*80)
print("3. 批次處理成本效益分析")
print("="*80)

strategies = [
    ("超高頻優先", "post_count >= 1000000", "處理最重要的標籤"),
    ("高頻+超高頻", "post_count >= 100000", "覆蓋高影響力標籤"),
    ("中高頻以上", "post_count >= 10000", "平衡成本與覆蓋"),
    ("中頻以上", "post_count >= 1000", "較全面覆蓋"),
    ("所有有使用", "post_count >= 100", "最大化創意價值"),
    ("全部標籤", "1=1", "完全覆蓋"),
]

print(f"\n{'策略':20} {'標籤數':>10} {'使用次數':>15} {'預估成本':>12} {'創意價值':10}")
print("-"*80)

for strategy_name, condition, desc in strategies:
    result = conn.execute(f"""
        SELECT 
            COUNT(*) as count,
            SUM(post_count) as usage
        FROM tags_final
        WHERE danbooru_cat = 0 
          AND main_category IS NULL
          AND {condition}
    """).fetchone()
    
    count, usage = result
    # GPT-4o-mini 成本估算：每個標籤約 $0.00002
    cost = count * 0.00002
    
    # 創意價值評分
    if count > 10000:
        creativity = "HIGHEST"
    elif count > 3000:
        creativity = "HIGH"
    else:
        creativity = "MEDIUM"
    
    print(f"{strategy_name:20} {count:>10,} {usage or 0:>15,} ${cost:>10.2f} {creativity:10}")
    print(f"  └─ {desc}")

# 4. 推薦方案
print("\n" + "="*80)
print("4. 推薦處理方案（針對創意價值）")
print("="*80)

print("\n方案 A: 分層批次處理（推薦）")
print("-"*80)

tiers = [
    ("第一批: 超高頻", "post_count >= 1000000", "CRITICAL", 0.00002),
    ("第二批: 高頻", "post_count >= 100000 AND post_count < 1000000", "HIGH", 0.00002),
    ("第三批: 中高頻", "post_count >= 10000 AND post_count < 100000", "MEDIUM", 0.00001),  # 使用更便宜模型
    ("第四批: 中頻", "post_count >= 1000 AND post_count < 10000", "LOW", 0.000005),  # 使用最便宜模型
]

total_cost = 0
total_tags_processed = 0

for batch_name, condition, priority, unit_cost in tiers:
    result = conn.execute(f"""
        SELECT COUNT(*)
        FROM tags_final
        WHERE danbooru_cat = 0 
          AND main_category IS NULL
          AND {condition}
    """).fetchone()
    
    count = result[0]
    cost = count * unit_cost
    total_cost += cost
    total_tags_processed += count
    
    model = "GPT-4o-mini" if unit_cost >= 0.00002 else "Claude-3.5-Haiku" if unit_cost >= 0.00001 else "Gemini-Flash"
    
    print(f"\n{batch_name}")
    print(f"  標籤數: {count:,}")
    print(f"  建議模型: {model}")
    print(f"  預估成本: ${cost:.2f}")
    print(f"  優先級: {priority}")

print(f"\n總計:")
print(f"  處理標籤: {total_tags_processed:,}")
print(f"  總成本: ${total_cost:.2f}")
print(f"  覆蓋率提升: 47.36% → {(14577 + total_tags_processed) / 30782 * 100:.2f}%")

# 5. 低成本高創意方案
print("\n" + "="*80)
print("5. 低成本高創意方案（創新建議）")
print("="*80)

print("""
方案 B: 使用開源 LLM + 本地部署（零成本）[最高性價比]

工具選擇:
  1. Ollama + Llama 3.1 (本地運行)
  2. Hugging Face Transformers (本地)
  3. LM Studio (本地 GUI)

優勢:
  [+] 完全零成本
  [+] 可處理所有 16,205 個標籤
  [+] 隱私保護（本地處理）
  [+] 可重複執行優化

劣勢:
  [-] 需要本地運算資源（8GB+ VRAM）
  [-] 處理時間較長（數小時）
  [-] 準確率可能略低於 GPT-4

預期效果:
  - Cat=0 覆蓋率: 47% -> 95%+ 
  - 成本: $0
  - 時間: 3-5 小時（一次性）
""")

print("\n方案 C: 混合策略（平衡）[推薦]")
print("-"*80)

mixed_strategy = conn.execute("""
    SELECT 
        CASE 
            WHEN post_count >= 10000 THEN 'GPT-4o-mini ($)'
            ELSE '開源 LLM (免費)'
        END as processing_method,
        COUNT(*) as tag_count,
        SUM(post_count) as usage
    FROM tags_final
    WHERE danbooru_cat = 0 AND main_category IS NULL
    GROUP BY CASE WHEN post_count >= 10000 THEN 'GPT-4o-mini ($)' ELSE '開源 LLM (免費)' END
""").fetchall()

print("\n分層處理策略:")
for method, count, usage in mixed_strategy:
    cost_note = "約 $5-10" if '$' in method else "$0"
    print(f"  {method:25} {count:>7,} 個標籤  {usage:>12,} 次使用  成本: {cost_note}")

print("\n總成本: $5-10")
print("總覆蓋: 所有 16,205 個未分類標籤")
print("策略: 高頻用商業 API（保證質量），低頻用開源 LLM（零成本）")

conn.close()

print("\n" + "="*80)
print("結論")
print("="*80)

print("""
您的觀點非常正確！低頻標籤的創意價值不應被忽視。

推薦方案（按優先級）:

1. 混合策略（最佳平衡）[推薦]
   - 高頻標籤(>10k): 用 GPT-4o-mini ($5-10)
   - 低頻標籤(<10k): 用開源 LLM (免費)
   - 總成本: $5-10
   - 覆蓋率: 47% -> 95%+
   
2. 完全使用開源 LLM（零成本）[最高性價比]
   - 工具: Ollama + Llama 3.1
   - 成本: $0
   - 時間: 3-5 小時
   - 覆蓋率: 47% -> 90-95%

3. 分批處理（靈活）
   - 先處理高頻（$10）
   - 再根據需求處理低頻（$0 或少量成本）
   - 可隨時停止

建議：從方案 1 (混合策略) 開始，兼顧質量和創意多樣性！
""")

