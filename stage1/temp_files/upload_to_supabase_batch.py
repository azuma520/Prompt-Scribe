import csv
import os

csv_path = 'stage1/output/tags_final_full.csv'
batch_size = 100  # 每批處理 100 筆記錄

print('開始批量上傳數據到 Supabase...')

if not os.path.exists(csv_path):
    print(f'錯誤: 找不到 CSV 檔案於 {csv_path}')
    exit(1)

# 讀取 CSV 並生成 SQL 批次
batch_count = 0
total_processed = 0

with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    header = next(csv_reader)  # 跳過標題行
    
    batch_data = []
    
    for row in csv_reader:
        if len(row) != len(header):
            print(f'警告: 跳過格式不正確的行: {row}')
            continue
        
        # 處理 NULL 值和字符轉義
        name = row[0].replace("'", "''") if row[0] else ''
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
            sql_file = f'stage1/output/batch_{batch_count:04d}.sql'
            with open(sql_file, 'w', encoding='utf-8') as f:
                values_str = ",\n".join(batch_data)
                sql = f"INSERT INTO tags_final (name, main_category, sub_category, classification_source, classification_confidence, post_count) VALUES\n{values_str};"
                f.write(sql)
            
            print(f'批次 {batch_count} 已生成: {len(batch_data)} 筆記錄 (總計: {total_processed:,})')
            batch_data = []
    
    # 處理剩餘數據
    if batch_data:
        batch_count += 1
        total_processed += len(batch_data)
        
        sql_file = f'stage1/output/batch_{batch_count:04d}.sql'
        with open(sql_file, 'w', encoding='utf-8') as f:
            values_str = ",\n".join(batch_data)
            sql = f"INSERT INTO tags_final (name, main_category, sub_category, classification_source, classification_confidence, post_count) VALUES\n{values_str};"
            f.write(sql)
        
        print(f'批次 {batch_count} 已生成: {len(batch_data)} 筆記錄 (總計: {total_processed:,})')

print(f'\nSQL 批次文件生成完成！')
print(f'總批次數: {batch_count}')
print(f'總記錄數: {total_processed:,}')
print(f'\n請使用 MCP execute_sql 工具逐批執行這些 SQL 文件')

