import csv
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv('stage1/.env')

def batch_insert_supabase():
    """批量插入數據到 Supabase"""
    
    csv_file = 'stage1/tags_data.csv'
    
    if not os.path.exists(csv_file):
        print(f"錯誤: CSV 文件不存在 {csv_file}")
        return
    
    print(f"開始批量插入數據...")
    
    # 讀取 CSV 並準備 SQL 插入語句
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # 準備批量插入數據
        batch_size = 50  # 減少批次大小以避免 SQL 過長
        batch_data = []
        total_processed = 0
        batch_num = 1
        
        # 跳過前 46 筆已插入的記錄
        for i, row in enumerate(reader):
            if i < 46:  # 跳過前 46 筆
                continue
                
            # 準備插入數據
            values = f"('{row['name'].replace("'", "''")}', "
            values += f"{f"'{row['main_category'].replace("'", "''")}'" if row['main_category'] else 'NULL'}, "
            values += f"{f"'{row['sub_category'].replace("'", "''")}'" if row['sub_category'] else 'NULL'}, "
            values += f"{f"'{row['classification_source'].replace("'", "''")}'" if row['classification_source'] else 'NULL'}, "
            values += f"{row['classification_confidence'] if row['classification_confidence'] else 'NULL'}, "
            values += f"{row['post_count'] if row['post_count'] else 0})"
            
            batch_data.append(values)
            
            # 當批次滿了或到文件末尾時，執行插入
            if len(batch_data) >= batch_size:
                sql = f"""
                INSERT INTO tags_final (name, main_category, sub_category, 
                                      classification_source, classification_confidence, post_count)
                VALUES {','.join(batch_data)}
                ON CONFLICT (name) DO UPDATE SET
                    main_category = EXCLUDED.main_category,
                    sub_category = EXCLUDED.sub_category,
                    classification_source = EXCLUDED.classification_source,
                    classification_confidence = EXCLUDED.classification_confidence,
                    post_count = EXCLUDED.post_count,
                    updated_at = CURRENT_TIMESTAMP;
                """
                
                # 將 SQL 寫入文件供 MCP 使用
                with open(f'stage1/batch_{batch_num:04d}.sql', 'w', encoding='utf-8') as f:
                    f.write(sql)
                
                print(f"批次 {batch_num} 準備完成: {len(batch_data)} 筆記錄")
                total_processed += len(batch_data)
                batch_data = []
                batch_num += 1
        
        # 處理剩餘數據
        if batch_data:
            sql = f"""
            INSERT INTO tags_final (name, main_category, sub_category, 
                                  classification_source, classification_confidence, post_count)
            VALUES {','.join(batch_data)}
            ON CONFLICT (name) DO UPDATE SET
                main_category = EXCLUDED.main_category,
                sub_category = EXCLUDED.sub_category,
                classification_source = EXCLUDED.classification_source,
                classification_confidence = EXCLUDED.classification_confidence,
                post_count = EXCLUDED.post_count,
                updated_at = CURRENT_TIMESTAMP;
            """
            
            with open(f'stage1/batch_{batch_num:04d}.sql', 'w', encoding='utf-8') as f:
                f.write(sql)
            
            print(f"批次 {batch_num} 準備完成: {len(batch_data)} 筆記錄")
            total_processed += len(batch_data)
    
    print(f"SQL 文件準備完成！總計 {total_processed:,} 筆記錄，共 {batch_num} 個批次")
    print(f"請使用 MCP 工具逐個執行 batch_*.sql 文件")

if __name__ == '__main__':
    batch_insert_supabase()
