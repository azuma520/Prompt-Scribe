import sqlite3

conn = sqlite3.connect('output/tags.db')

# danbooru_cat=0 統計
result = conn.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified
    FROM tags_final 
    WHERE danbooru_cat = 0
""").fetchone()

total = result[0]
classified = result[1]

print("="*60)
print("danbooru_cat=0 (一般標籤) 覆蓋率")
print("="*60)
print(f"總數: {total:,}")
print(f"已分類: {classified:,}")
print(f"覆蓋率: {classified/total*100:.2f}%")
print(f"未分類: {total-classified:,}")

# 整體統計
result2 = conn.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified
    FROM tags_final
""").fetchone()

print("\n" + "="*60)
print("整體覆蓋率")
print("="*60)
print(f"總數: {result2[0]:,}")
print(f"已分類: {result2[1]:,}")
print(f"覆蓋率: {result2[1]/result2[0]*100:.2f}%")

# 規則分類器統計
result3 = conn.execute("""
    SELECT COUNT(*) 
    FROM tags_final 
    WHERE danbooru_cat = 0 AND main_category IS NOT NULL
""").fetchone()

print("\n" + "="*60)
print("規則分類器效能")
print("="*60)
print(f"規則分類標籤數: {result3[0]:,}")

conn.close()

