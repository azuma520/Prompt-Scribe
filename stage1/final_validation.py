#!/usr/bin/env python3
"""最終驗證報告"""

import sqlite3

conn = sqlite3.connect('output/tags.db')

print("=" * 80)
print("Danbooru 標籤管線 Phase 1 - 最終驗證報告")
print("=" * 80)

# 基本統計
print("\n### 資料庫統計")
total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
general_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE danbooru_cat = 0').fetchone()[0]
other_tags = total_tags - general_tags

print(f"  總標籤數: {total_tags:,}")
print(f"  一般標籤 (danbooru_cat=0): {general_tags:,}")
print(f"  其他類別: {other_tags:,}")

# 主分類覆蓋率
classified = conn.execute("""
    SELECT COUNT(*) FROM tags_final 
    WHERE danbooru_cat = 0 AND main_category IS NOT NULL
""").fetchone()[0]
overall_coverage = (classified / general_tags * 100) if general_tags > 0 else 0

print(f"\n### 主分類覆蓋率")
print(f"  已分類: {classified:,}/{general_tags:,}")
print(f"  覆蓋率: {overall_coverage:.1f}%")

# TOP 標籤覆蓋率
for top_n in [10, 30, 50, 100]:
    top_tags = conn.execute(f"""
        SELECT name, main_category
        FROM tags_final
        WHERE danbooru_cat = 0 AND post_count > 0
        ORDER BY post_count DESC
        LIMIT {top_n}
    """).fetchall()
    
    classified_count = sum(1 for _, cat in top_tags if cat is not None)
    coverage = (classified_count / top_n * 100) if top_n > 0 else 0
    print(f"  TOP {top_n:3} 高頻標籤: {classified_count:3}/{top_n:3} ({coverage:5.1f}%)")

# 加權覆蓋率（按使用頻率加權）
print(f"\n### 加權覆蓋率（按 post_count 加權）")
total_usage = conn.execute("""
    SELECT SUM(post_count) 
    FROM tags_final 
    WHERE danbooru_cat = 0
""").fetchone()[0]

classified_usage = conn.execute("""
    SELECT SUM(post_count)
    FROM tags_final
    WHERE danbooru_cat = 0 AND main_category IS NOT NULL
""").fetchone()[0]

weighted_coverage = (classified_usage / total_usage * 100) if total_usage > 0 else 0
print(f"  已分類標籤的總使用次數: {classified_usage:,}")
print(f"  所有標籤的總使用次數: {total_usage:,}")
print(f"  加權覆蓋率: {weighted_coverage:.1f}%")

# 性能指標
print(f"\n### 性能指標")
raw_count = conn.execute('SELECT COUNT(*) FROM tags_raw').fetchone()[0]
final_count = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
print(f"  原始記錄數: {raw_count:,}")
print(f"  唯一標籤數: {final_count:,}")
print(f"  去重率: {(raw_count - final_count) / raw_count * 100:.1f}%")

# 資料品質
print(f"\n### 資料品質檢查")
# 唯一性
dup_check = conn.execute("""
    SELECT COUNT(*), COUNT(DISTINCT name) FROM tags_final
""").fetchone()
uniqueness_pass = dup_check[0] == dup_check[1]
print(f"  唯一性: {'[PASS]' if uniqueness_pass else '[FAIL]'}")

# 完整性
null_check = conn.execute("""
    SELECT COUNT(*) FROM tags_final
    WHERE name IS NULL OR danbooru_cat IS NULL
""").fetchone()[0]
completeness_pass = null_check == 0
print(f"  完整性: {'[PASS]' if completeness_pass else '[FAIL]'}")

# 一致性
sum_raw = conn.execute("SELECT SUM(post_count) FROM tags_raw").fetchone()[0] or 0
sum_final = conn.execute("SELECT SUM(post_count) FROM tags_final").fetchone()[0] or 0
consistency_pass = sum_raw == sum_final
print(f"  一致性: {'[PASS]' if consistency_pass else '[FAIL]'} (raw={sum_raw:,}, final={sum_final:,})")

print("\n" + "=" * 80)
all_passed = uniqueness_pass and completeness_pass and consistency_pass
if all_passed:
    print("[SUCCESS] 所有驗證通過！")
else:
    print("[WARNING] 部分驗證未通過")
print("=" * 80)

conn.close()

