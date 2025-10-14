import sqlite3

db_path = 'stage1/output/tags.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 總記錄數
cursor.execute('SELECT COUNT(*) FROM tags_final')
total_records = cursor.fetchone()[0]
print(f'總記錄數: {total_records:,}')

# 已分類記錄數
cursor.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL')
classified_records = cursor.fetchone()[0]
print(f'已分類記錄數: {classified_records:,}')

# 覆蓋率
coverage = (classified_records / total_records) * 100 if total_records > 0 else 0
print(f'覆蓋率: {coverage:.2f}%')

# 前10大主分類
print('\n前10大主分類:')
cursor.execute('''
    SELECT main_category, COUNT(*) as count
    FROM tags_final
    WHERE main_category IS NOT NULL
    GROUP BY main_category
    ORDER BY count DESC
    LIMIT 10
''')
for cat, count in cursor.fetchall():
    percentage = (count / classified_records) * 100
    print(f'  {cat:30} {count:,} 筆 ({percentage:.2f}%)')

# 檢查 CSV 導出的數據
print('\n檢查 CSV 導出檔案:')
import os
csv_path = 'stage1/output/tags_final.csv'
if os.path.exists(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_lines = sum(1 for _ in f) - 1  # 減去標題行
    print(f'CSV 檔案記錄數: {csv_lines:,}')
else:
    print('CSV 檔案不存在')

conn.close()

