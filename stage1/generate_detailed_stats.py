#!/usr/bin/env python3
"""生成詳細統計數據"""

import sqlite3
import pandas as pd

conn = sqlite3.connect('output/tags.db')

print("=" * 80)
print("詳細數據分析 - 用於 Phase 2 規劃")
print("=" * 80)

# 1. 按使用頻率分層
print("\n### 1. 按使用頻率分層統計")
result = conn.execute("""
    SELECT 
        CASE 
            WHEN post_count = 0 THEN '0_零使用'
            WHEN post_count < 100 THEN '1_極低頻(<100)'
            WHEN post_count < 1000 THEN '2_低頻(100-1k)'
            WHEN post_count < 10000 THEN '3_中頻(1k-10k)'
            WHEN post_count < 100000 THEN '4_中高頻(10k-100k)'
            WHEN post_count < 1000000 THEN '5_高頻(100k-1M)'
            ELSE '6_超高頻(>1M)'
        END as freq_tier,
        COUNT(*) as total_tags,
        SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified,
        ROUND(AVG(CASE WHEN main_category IS NOT NULL THEN 1.0 ELSE 0.0 END) * 100, 1) as coverage_pct,
        SUM(post_count) as total_usage
    FROM tags_final
    WHERE danbooru_cat = 0
    GROUP BY freq_tier
    ORDER BY freq_tier
""").fetchall()

print(f"{'頻率層級':<20} {'標籤數':>10} {'已分類':>10} {'覆蓋率':>10} {'總使用次數':>15}")
print("-" * 80)
for tier, total, classified, coverage, usage in result:
    tier_name = tier.split('_')[1]
    print(f"{tier_name:<20} {total:>10,} {classified:>10,} {coverage:>9.1f}% {usage:>15,}")

# 2. 未分類高價值標籤 TOP 50
print("\n### 2. 未分類高價值標籤 TOP 50")
unclassified_high_freq = conn.execute("""
    SELECT name, post_count
    FROM tags_final
    WHERE danbooru_cat = 0 
      AND main_category IS NULL
      AND post_count > 0
    ORDER BY post_count DESC
    LIMIT 50
""").fetchall()

print(f"{'標籤名稱':<30} {'使用次數':>15}")
print("-" * 50)
for name, count in unclassified_high_freq[:20]:
    print(f"{name:<30} {count:>15,}")
print(f"... 還有 {len(unclassified_high_freq)-20} 個")

# 3. 各主分類的覆蓋情況
print("\n### 3. 各主分類統計")
result = conn.execute("""
    SELECT 
        main_category,
        COUNT(*) as tag_count,
        SUM(post_count) as total_usage,
        COUNT(DISTINCT sub_category) as sub_cat_count
    FROM tags_final
    WHERE main_category IS NOT NULL
    GROUP BY main_category
    ORDER BY tag_count DESC
""").fetchall()

print(f"{'主分類':<25} {'標籤數':>10} {'總使用次數':>15} {'副分類數':>10}")
print("-" * 70)
for cat, count, usage, sub_count in result:
    print(f"{cat:<25} {count:>10,} {usage:>15,} {sub_count:>10}")

# 4. LLM 優化目標標籤數量預估
print("\n### 4. LLM 優化目標預估")
targets = [
    ('post_count > 10000', '高頻標籤'),
    ('post_count > 1000', '中高頻標籤'),
    ('post_count > 100', '中頻以上標籤'),
    ('post_count > 0', '所有有使用的標籤'),
]

for condition, desc in targets:
    count = conn.execute(f"""
        SELECT COUNT(*) 
        FROM tags_final
        WHERE danbooru_cat = 0 
          AND main_category IS NULL
          AND {condition}
    """).fetchone()[0]
    print(f"  {desc:<25} 未分類數：{count:>8,} 個")

# 5. 成本估算
print("\n### 5. Phase 2 成本估算（不同策略）")
all_unclassified = conn.execute("""
    SELECT COUNT(*) 
    FROM tags_final
    WHERE danbooru_cat = 0 AND main_category IS NULL AND post_count > 0
""").fetchone()[0]

# GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
# 假設每個標籤平均 20 tokens input, 10 tokens output
tokens_per_tag = 30
cost_per_million = 0.15 * 0.66 + 0.60 * 0.33  # 加權平均

for target_count in [500, 2000, 5000, 11000, all_unclassified]:
    if target_count <= all_unclassified:
        estimated_cost = (target_count * tokens_per_tag / 1_000_000) * cost_per_million
        print(f"  處理 {target_count:>6,} 個標籤：約 ${estimated_cost:>6.2f}")

print("\n### 6. 建議的優化順序")
print("  1. [零成本] 擴展規則庫 → 覆蓋率 +10-15%")
print("  2. [低成本] LLM 處理 TOP 500 → 覆蓋率 +5-10%")
print("  3. [中成本] LLM 處理 post_count > 1000 → 覆蓋率 +10-15%")
print("  4. [可選] 全量 LLM → 覆蓋率 +30-40%")

conn.close()

print("\n" + "=" * 80)
print("數據分析完成！詳見 output/DATA_ANALYSIS.md")
print("=" * 80)

