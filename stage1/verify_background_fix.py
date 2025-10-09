import sqlite3

conn = sqlite3.connect('output/tags.db')

print("="*80)
print("驗證 Background 標籤分類修復")
print("="*80)

results = conn.execute("""
    SELECT name, main_category, sub_category, post_count 
    FROM tags_final 
    WHERE name LIKE '%background%' 
    ORDER BY post_count DESC 
    LIMIT 15
""").fetchall()

print(f"\n找到 {len(results)} 個 background 標籤\n")
print(f"{'標籤名稱':30} {'主分類':20} {'副分類':15} {'使用次數':>12}")
print("-"*80)

correct = 0
total = len(results)

for name, main, sub, count in results:
    status = "[OK]" if main == 'ENVIRONMENT' else "[ERROR]"
    if main == 'ENVIRONMENT':
        correct += 1
    print(f"{status} {name:30} {main or 'NULL':20} {sub or 'NULL':15} {count:>12,}")

print("-"*80)
print(f"\n正確率: {correct}/{total} ({correct/total*100:.1f}%)")
print(f"預期: 所有 background 標籤都應分類為 ENVIRONMENT")

if correct == total:
    print("\n[SUCCESS] Background 標籤全部正確分類！✅")
else:
    print(f"\n[WARNING] 還有 {total-correct} 個 background 標籤分類錯誤")

conn.close()

