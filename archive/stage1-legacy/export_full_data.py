import sqlite3
import csv
import os

db_path = 'stage1/output/tags.db'
csv_path = 'stage1/output/tags_final_full.csv'
batch_size = 10000

print('開始導出 SQLite 數據到 CSV...')

os.makedirs(os.path.dirname(csv_path), exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 獲取總記錄數
cursor.execute("SELECT COUNT(*) FROM tags_final")
total_records = cursor.fetchone()[0]
print(f'總記錄數: {total_records:,}')

# 獲取欄位名稱
cursor.execute("SELECT name, main_category, sub_category, classification_source, classification_confidence, post_count FROM tags_final LIMIT 1")
columns = [description[0] for description in cursor.description]

# 導出數據
cursor.execute("SELECT name, main_category, sub_category, classification_source, classification_confidence, post_count FROM tags_final")

with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(columns)  # 寫入標題
    
    exported_count = 0
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        csv_writer.writerows(rows)
        exported_count += len(rows)
        print(f'已導出 {exported_count:,} / {total_records:,} 筆記錄 ({exported_count*100/total_records:.1f}%)')

conn.close()

print(f'\nCSV 檔案導出完成！')
print(f'檔案位置: {csv_path}')
print(f'總共導出: {exported_count:,} 筆記錄')

# 驗證 CSV 檔案
print('\n驗證 CSV 檔案...')
with open(csv_path, 'r', encoding='utf-8') as f:
    csv_lines = sum(1 for _ in f) - 1  # 減去標題行
print(f'CSV 檔案記錄數: {csv_lines:,}')

if csv_lines == total_records:
    print('✓ CSV 導出成功，記錄數匹配！')
else:
    print(f'✗ 警告：記錄數不匹配！SQLite: {total_records:,}, CSV: {csv_lines:,}')

