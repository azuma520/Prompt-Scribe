import sqlite3

def check_sqlite_data():
    conn = sqlite3.connect('stage1/output/tags.db')
    cursor = conn.cursor()
    
    # 檢查總記錄數
    cursor.execute('SELECT COUNT(*) FROM tags_final')
    total_count = cursor.fetchone()[0]
    print(f'總記錄數: {total_count:,}')
    
    # 檢查前5個主分類
    cursor.execute('''
        SELECT main_category, COUNT(*) 
        FROM tags_final 
        WHERE main_category IS NOT NULL 
        GROUP BY main_category 
        ORDER BY COUNT(*) DESC 
        LIMIT 5
    ''')
    print('前5個主分類:')
    for cat, count in cursor.fetchall():
        print(f'  {cat}: {count:,} 筆')
    
    # 檢查覆蓋率
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified,
            ROUND(SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as coverage
        FROM tags_final
    ''')
    total, classified, coverage = cursor.fetchone()
    print(f'覆蓋率: {coverage}% ({classified:,}/{total:,})')
    
    conn.close()

if __name__ == '__main__':
    check_sqlite_data()
