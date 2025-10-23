#!/usr/bin/env python3
"""
LLM 分類統計
"""

import sqlite3

conn = sqlite3.connect('output/tags.db')

# 總數
total = conn.execute('SELECT COUNT(*) FROM tags_final WHERE classification_source = "qwen3_80b"').fetchone()[0]
print("="*80)
print(f"LLM 分類標籤總數: {total}")
print("="*80)

# 按主分類統計
print("\n主分類分布:")
by_cat = conn.execute('''
    SELECT main_category, COUNT(*) as count
    FROM tags_final 
    WHERE classification_source = "qwen3_80b"
    GROUP BY main_category 
    ORDER BY count DESC
''').fetchall()

for cat, count in by_cat:
    print(f"  {cat}: {count}")

# 按副分類統計
print("\n副分類分布:")
by_sub = conn.execute('''
    SELECT sub_category, COUNT(*) as count
    FROM tags_final 
    WHERE classification_source = "qwen3_80b"
    AND sub_category IS NOT NULL
    GROUP BY sub_category 
    ORDER BY count DESC
''').fetchall()

for sub, count in by_sub:
    print(f"  {sub}: {count}")

# 影響的使用次數
usage = conn.execute('SELECT SUM(post_count) FROM tags_final WHERE classification_source = "qwen3_80b"').fetchone()[0]
print(f"\n影響使用次數: {usage:,}")

# 平均置信度
avg_conf, min_conf, max_conf = conn.execute('''
    SELECT 
        AVG(classification_confidence),
        MIN(classification_confidence),
        MAX(classification_confidence)
    FROM tags_final 
    WHERE classification_source = "qwen3_80b"
''').fetchone()

print(f"\n置信度統計:")
print(f"  平均: {avg_conf:.3f}")
print(f"  最低: {min_conf:.3f}")
print(f"  最高: {max_conf:.3f}")

# 整體統計
print("\n" + "="*80)
print("整體覆蓋率")
print("="*80)

total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
classified = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
coverage = classified / total_tags * 100

print(f"總標籤數: {total_tags:,}")
print(f"已分類: {classified:,}")
print(f"覆蓋率: {coverage:.2f}%")

# danbooru_cat=0 覆蓋率
cat0_total = conn.execute('SELECT COUNT(*) FROM tags_final WHERE danbooru_cat = 0').fetchone()[0]
cat0_classified = conn.execute('SELECT COUNT(*) FROM tags_final WHERE danbooru_cat = 0 AND main_category IS NOT NULL').fetchone()[0]
cat0_coverage = cat0_classified / cat0_total * 100

print(f"\ndanbooru_cat=0 覆蓋率:")
print(f"  總數: {cat0_total:,}")
print(f"  已分類: {cat0_classified:,}")
print(f"  覆蓋率: {cat0_coverage:.2f}%")

conn.close()

