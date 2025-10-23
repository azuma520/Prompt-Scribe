import sqlite3

conn = sqlite3.connect('output/tags.db')

print("="*80)
print("未分類標籤頻率與實際影響分析")
print("="*80)

# 查詢各頻率層級
tiers = [
    ("超高頻 (>1M)", 1000000, 999999999),
    ("高頻 (100k-1M)", 100000, 999999),
    ("中高頻 (10k-100k)", 10000, 99999),
    ("中頻 (1k-10k)", 1000, 9999),
    ("低頻 (<1k)", 0, 999),
]

print(f"\n{'頻率層級':20} {'標籤數':>8} {'使用次數':>15} {'佔比':>8} {'創意價值':12} {'實際價值':12}")
print("-"*90)

total_tags = 0
total_usage = 0

for name, min_count, max_count in tiers:
    result = conn.execute(f"""
        SELECT COUNT(*), SUM(post_count)
        FROM tags_final
        WHERE danbooru_cat = 0 
          AND main_category IS NULL
          AND post_count >= {min_count} 
          AND post_count <= {max_count}
    """).fetchone()
    
    count = result[0]
    usage = result[1] or 0
    percentage = usage / 636189872 * 100 if usage else 0
    
    total_tags += count
    total_usage += usage
    
    # 創意價值評估
    if '低頻' in name:
        creativity = "HIGHEST"
        real_value = "LOWEST"
    elif '中頻' in name:
        creativity = "HIGH"
        real_value = "LOW"
    elif '中高頻' in name:
        creativity = "MEDIUM"
        real_value = "MEDIUM"
    else:
        creativity = "LOW"
        real_value = "HIGHEST"
    
    print(f"{name:20} {count:>8,} {usage:>15,} {percentage:>7.2f}% {creativity:12} {real_value:12}")

print("-"*90)
print(f"{'合計':20} {total_tags:>8,} {total_usage:>15,} {total_usage/636189872*100:>7.2f}%")

print("\n" + "="*80)
print("關鍵發現")
print("="*80)

print(f"""
1. 低頻標籤 (<1k) 的實際影響:
   - 標籤數量比例: {conn.execute('SELECT COUNT(*) FROM tags_final WHERE danbooru_cat=0 AND main_category IS NULL AND post_count < 1000').fetchone()[0] / total_tags * 100:.1f}%
   - 使用量佔比: {conn.execute('SELECT SUM(post_count) FROM tags_final WHERE danbooru_cat=0 AND main_category IS NULL AND post_count < 1000').fetchone()[0] / total_usage * 100:.1f}%
   
2. 創意價值 vs 實際影響的矛盾:
   - 創意價值: 低頻標籤最高（獨特、罕見）
   - 實際影響: 低頻標籤最低（使用量 <0.5%）

3. 投資回報率分析:
   - 處理超高頻 114 個: 影響 30.6% 未分類使用量
   - 處理高頻 999 個: 影響 49.0% 未分類使用量  
   - 處理中高頻 3,120 個: 影響 16.0% 未分類使用量
   - 處理中頻 7,228 個: 影響 3.9% 未分類使用量
   - 處理低頻 4,744 個: 影響 0.5% 未分類使用量 [WARNING]
""")

# 計算達到不同覆蓋率目標所需處理的標籤數
print("\n" + "="*80)
print("達成不同目標所需處理的標籤數")
print("="*80)

targets = [
    (50, "及格線"),
    (60, "良好"),
    (70, "優秀"),
    (80, "卓越"),
    (90, "近乎完美"),
]

current_classified = 14577
current_total = 30782

print(f"\n{'目標覆蓋率':15} {'需已分類':>12} {'需新增':>10} {'約需處理':20} {'預估成本':12}")
print("-"*80)

for target_pct, desc in targets:
    need_classified = int(current_total * target_pct / 100)
    need_new = max(0, need_classified - current_classified)
    
    # 估算需要處理哪些層級
    if need_new <= 114:
        processing = "超高頻"
    elif need_new <= 1113:
        processing = "超高頻+高頻"
    elif need_new <= 4233:
        processing = ">10k 全部"
    elif need_new <= 11461:
        processing = ">1k 全部"
    else:
        processing = "所有標籤"
    
    # 成本估算
    if need_new <= 1113:
        cost = "$2-5"
    elif need_new <= 4233:
        cost = "$5-10"
    elif need_new <= 11461:
        cost = "$10-20"
    else:
        cost = "$20-50"
    
    print(f"{target_pct}% ({desc:8}) {need_classified:>12,} {need_new:>10,} {processing:20} {cost:12}")

conn.close()

print("\n" + "="*80)
print("結論與建議")
print("="*80)

print("""
基於 Sequential Thinking 分析：

真實場景價值評估:
  [HIGH] 超高頻+高頻標籤 (1,113個): 價值極高
     - 影響 79.6% 未分類使用量
     - 成本 $2-5
     - 強烈建議處理

  [MEDIUM] 中高頻標籤 (3,120個): 價值中等
     - 影響額外 16.0% 使用量
     - 成本 $5-10
     - 建議處理（性價比尚可）

  [LOW] 中頻標籤 (7,228個): 價值較低
     - 影響僅 3.9% 使用量
     - 大量標籤，投入產出比低
     - 可選處理

  [VERY_LOW] 低頻標籤 (4,744個): 實際價值很低
     - 影響僅 0.5% 使用量
     - 雖有「創意價值」但實際使用率極低
     - 不建議預先處理

推薦方案（修正）:
  
  方案 1: 處理 >10k 標籤 (4,233個)
    - 成本: $5-10
    - Cat=0 覆蓋率: 47% -> 60-65%
    - 影響: 95.6% 未分類使用量
    - 評價: [BEST] 性價比最高
  
  方案 2: 處理 >100k 標籤 (1,113個)
    - 成本: $2-5
    - Cat=0 覆蓋率: 47% -> 51-52%
    - 影響: 79.6% 未分類使用量
    - 評價: [GOOD] 快速見效
  
  方案 3: 採用「按需分類」
    - 當用戶首次使用某個低頻標籤時，即時調用 LLM 分類
    - 避免預先處理可能永遠不會被使用的標籤
    - 長期零成本增長
    - 評價: [SMART] 最智能

結論: 低頻標籤的「創意價值」在理論上存在，但在實際使用場景中
價值有限。建議優先處理中高頻以上標籤（>10k），對低頻標籤採用
按需處理策略。
""")

