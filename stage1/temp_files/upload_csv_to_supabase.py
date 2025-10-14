import csv
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv('stage1/.env')

def upload_csv_to_supabase():
    """將 CSV 數據上傳到 Supabase"""
    
    csv_file = 'stage1/tags_data.csv'
    
    if not os.path.exists(csv_file):
        print(f"錯誤: CSV 文件不存在 {csv_file}")
        return
    
    print(f"開始上傳 CSV 數據...")
    
    # 讀取 CSV 並準備 SQL 插入語句
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # 準備批量插入數據
        batch_size = 100
        batch_data = []
        total_processed = 0
        
        for row in reader:
            # 準備插入數據
            values = [
                row['name'],
                row['main_category'] if row['main_category'] else None,
                row['sub_category'] if row['sub_category'] else None,
                row['classification_source'] if row['classification_source'] else None,
                float(row['classification_confidence']) if row['classification_confidence'] else None,
                int(row['post_count']) if row['post_count'] else 0
            ]
            
            batch_data.append(values)
            
            # 當批次滿了或到文件末尾時，執行插入
            if len(batch_data) >= batch_size:
                insert_batch(batch_data)
                total_processed += len(batch_data)
                print(f"已處理 {total_processed:,} 筆記錄")
                batch_data = []
        
        # 處理剩餘數據
        if batch_data:
            insert_batch(batch_data)
            total_processed += len(batch_data)
            print(f"已處理 {total_processed:,} 筆記錄")
    
    print(f"數據上傳完成！總計 {total_processed:,} 筆記錄")

def insert_batch(batch_data):
    """插入一批數據到 Supabase"""
    
    # 準備 SQL 語句
    sql_template = """
    INSERT INTO tags_final (name, main_category, sub_category, 
                          classification_source, classification_confidence, post_count)
    VALUES 
    """
    
    # 構建 VALUES 部分
    values_list = []
    for row in batch_data:
        values = f"('{row[0].replace("'", "''")}', "
        values += f"{f"'{row[1].replace("'", "''")}'" if row[1] else 'NULL'}, "
        values += f"{f"'{row[2].replace("'", "''")}'" if row[2] else 'NULL'}, "
        values += f"{f"'{row[3].replace("'", "''")}'" if row[3] else 'NULL'}, "
        values += f"{row[4] if row[4] is not None else 'NULL'}, "
        values += f"{row[5]})"
        values_list.append(values)
    
    # 完整的 SQL 語句
    full_sql = sql_template + ",\n".join(values_list) + """
    ON CONFLICT (name) DO UPDATE SET
        main_category = EXCLUDED.main_category,
        sub_category = EXCLUDED.sub_category,
        classification_source = EXCLUDED.classification_source,
        classification_confidence = EXCLUDED.classification_confidence,
        post_count = EXCLUDED.post_count,
        updated_at = CURRENT_TIMESTAMP;
    """
    
    # 將 SQL 寫入文件供 MCP 使用
    with open('stage1/batch_insert.sql', 'w', encoding='utf-8') as f:
        f.write(full_sql)
    
    print(f"批次 SQL 已準備好，包含 {len(batch_data)} 筆記錄")

if __name__ == '__main__':
    upload_csv_to_supabase()
