#!/usr/bin/env python3
"""檢查各頻率範圍的未分類標籤數量"""

import sqlite3

conn = sqlite3.connect('output/tags.db')
cursor = conn.cursor()

ranges = [
    ('50K-100K', 50000, 100000),
    ('30K-50K', 30000, 50000),
    ('20K-30K', 20000, 30000),
    ('10K-20K', 10000, 20000),
    ('5K-10K', 5000, 10000),
    ('3K-5K', 3000, 5000),
    ('1K-3K', 1000, 3000)
]

print("="*50)
print("未分類標籤統計 (按頻率範圍)")
print("="*50)
print(f"{'頻率範圍':<12} {'未分類數量':>10}")
print("-"*50)

total = 0
for name, min_count, max_count in ranges:
    cursor.execute("""
        SELECT COUNT(*) FROM tags_final
        WHERE main_category IS NULL
        AND post_count >= ?
        AND post_count < ?
    """, (min_count, max_count))
    
    count = cursor.fetchone()[0]
    total += count
    print(f"{name:<12} {count:>10,}")

print("-"*50)
print(f"{'總計':<12} {total:>10,}")
print("="*50)

conn.close()

