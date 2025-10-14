import csv
import os
import glob

csv_path = 'stage1/output/tags_final_full.csv'
output_dir = 'stage1/output/mini_batches'
batch_size = 500  # 每批 500 筆記錄，更適合 MCP 工具

print('開始生成迷你批次 SQL 文件...')

os.makedirs(output_dir, exist_ok=True)

# 清理舊的批次文件
for old_file in glob.glob(f'{output_dir}/batch_*.sql'):
    os.remove(old_file)

if not os.path.exists(csv_path):
    print(f'錯誤: 找不到 CSV 檔案於 {csv_path}')
    exit(1)

batch_count = 0
total_processed = 0

with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    header = next(csv_reader)  # 跳過標題行
    
    batch_data = []
    
    for row in csv_reader:
        if len(row) != len(header):
            continue
        
        # 處理 NULL 值和字符轉義
        name = row[0].replace("'", "''").replace("\\", "\\\\") if row[0] else ''
        main_category = row[1].replace("'", "''") if row[1] else None
        sub_category = row[2].replace("'", "''") if row[2] else None
        classification_source = row[3].replace("'", "''") if row[3] else None
        classification_confidence = row[4] if row[4] else None
        post_count = row[5] if row[5] else '0'
        
        # 構建 VALUES 子句
        value_str = f"('{name}', "
        value_str += f"'{main_category}'" if main_category else "NULL"
        value_str += ", "
        value_str += f"'{sub_category}'" if sub_category else "NULL"
        value_str += ", "
        value_str += f"'{classification_source}'" if classification_source else "NULL"
        value_str += ", "
        value_str += f"{classification_confidence}" if classification_confidence else "NULL"
        value_str += f", {post_count})"
        
        batch_data.append(value_str)
        
        if len(batch_data) >= batch_size:
            batch_count += 1
            total_processed += len(batch_data)
            
            # 生成批次 SQL 文件
            sql_file = f'{output_dir}/batch_{batch_count:04d}.sql'
            with open(sql_file, 'w', encoding='utf-8') as f:
                values_str = ",\n".join(batch_data)
                sql = f"INSERT INTO tags_final (name, main_category, sub_category, classification_source, classification_confidence, post_count) VALUES\n{values_str};"
                f.write(sql)
            
            if batch_count % 50 == 0:
                print(f'已生成 {batch_count} 個批次 (總計: {total_processed:,} 筆記錄)')
            
            batch_data = []
    
    # 處理剩餘數據
    if batch_data:
        batch_count += 1
        total_processed += len(batch_data)
        
        sql_file = f'{output_dir}/batch_{batch_count:04d}.sql'
        with open(sql_file, 'w', encoding='utf-8') as f:
            values_str = ",\n".join(batch_data)
            sql = f"INSERT INTO tags_final (name, main_category, sub_category, classification_source, classification_confidence, post_count) VALUES\n{values_str};"
            f.write(sql)

print(f'\n迷你批次 SQL 文件生成完成！')
print(f'輸出目錄: {output_dir}')
print(f'總批次數: {batch_count}')
print(f'總記錄數: {total_processed:,}')
print(f'平均每批: {total_processed // batch_count:,} 筆')

