import sqlite3
import csv
import os

def export_to_csv():
    """將 SQLite 數據導出為 CSV 文件"""
    
    # 連接 SQLite
    conn = sqlite3.connect('stage1/output/tags.db')
    cursor = conn.cursor()
    
    # 導出所有數據
    cursor.execute('''
        SELECT name, main_category, sub_category, classification_source, 
               classification_confidence, post_count
        FROM tags_final
        ORDER BY post_count DESC
    ''')
    
    # 寫入 CSV
    with open('stage1/tags_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # 寫入標題
        writer.writerow(['name', 'main_category', 'sub_category', 
                        'classification_source', 'classification_confidence', 'post_count'])
        
        # 寫入數據
        batch_size = 1000
        total_written = 0
        
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
                
            writer.writerows(rows)
            total_written += len(rows)
            print(f'已寫入 {total_written:,} 筆記錄')
    
    conn.close()
    print(f'CSV 導出完成！總計 {total_written:,} 筆記錄')

if __name__ == '__main__':
    export_to_csv()



