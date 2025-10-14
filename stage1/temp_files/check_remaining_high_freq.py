#!/usr/bin/env python3
"""
檢查剩餘的高頻未分類標籤
"""

import sqlite3

conn = sqlite3.connect('output/tags.db')

tags = conn.execute('''
    SELECT name, post_count
    FROM tags_final 
    WHERE danbooru_cat = 0 
    AND main_category IS NULL
    AND post_count >= 100000
    ORDER BY post_count DESC
''').fetchall()

print("="*80)
print(f"剩餘高頻未分類標籤 (>=100K): {len(tags)} 個")
print("="*80)

total_usage = 0
for i, (name, usage) in enumerate(tags, 1):
    print(f"{i:2}. {name:30} {usage:,} 次")
    total_usage += usage

print(f"\n總使用次數: {total_usage:,}")
print(f"平均使用次數: {total_usage//len(tags):,}" if tags else "N/A")

conn.close()

