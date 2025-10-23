#!/usr/bin/env python3
"""檢查真實高頻標籤"""

import sqlite3

conn = sqlite3.connect('output/tags.db')

print("=" * 80)
print("TOP 30 高頻圖像標籤（post_count > 0）")
print("=" * 80)

result = conn.execute("""
    SELECT name, post_count, main_category, sub_category
    FROM tags_final
    WHERE danbooru_cat = 0 AND post_count > 0
    ORDER BY post_count DESC
    LIMIT 30
""").fetchall()

for name, count, main_cat, sub_cat in result:
    status = "[OK]" if main_cat else "[NO]"
    cat_str = main_cat if main_cat else "未分類"
    if sub_cat:
        cat_str += f" -> {sub_cat}"
    print(f"  {status} {name:30} {count:>12,} 次  {cat_str}")

classified = sum(1 for _, _, cat, _ in result if cat)
print(f"\n覆蓋率: {classified}/{len(result)} ({classified/len(result)*100:.1f}%)")

# 統計有 post_count 的標籤
print("\n" + "=" * 80)
print("有使用次數的標籤統計")
print("=" * 80)

total_with_count = conn.execute("""
    SELECT COUNT(*) FROM tags_final 
    WHERE danbooru_cat = 0 AND post_count > 0
""").fetchone()[0]

classified_with_count = conn.execute("""
    SELECT COUNT(*) FROM tags_final 
    WHERE danbooru_cat = 0 AND post_count > 0 AND main_category IS NOT NULL
""").fetchone()[0]

print(f"有使用次數的標籤: {total_with_count:,}")
print(f"已分類: {classified_with_count:,}")
print(f"覆蓋率: {classified_with_count/total_with_count*100:.1f}%")

conn.close()

