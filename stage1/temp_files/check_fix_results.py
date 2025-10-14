#!/usr/bin/env python3
"""
檢查修復結果
"""

import sqlite3

def check_hair_tags():
    """檢查頭髮標籤狀況"""
    print("="*80)
    print("檢查頭髮標籤修復結果")
    print("="*80)
    
    conn = sqlite3.connect("output/tags.db")
    cursor = conn.cursor()
    
    # 檢查頭髮標籤
    cursor.execute("""
        SELECT name, main_category, sub_category, post_count
        FROM tags_final
        WHERE name LIKE '%_hair'
        ORDER BY post_count DESC
        LIMIT 10
    """)
    
    hair_tags = cursor.fetchall()
    print(f"找到 {len(hair_tags)} 個頭髮相關標籤:")
    print("-" * 80)
    
    for name, main, sub, count in hair_tags:
        status = "OK" if (main == 'CHARACTER_RELATED' and sub == 'HAIR') else "ERR"
        print(f"{status:3} {name:40} -> {main:25}/{sub or 'None':20} ({count:,} 次)")
    
    # 檢查 NULL 字符串
    cursor.execute("""
        SELECT COUNT(*) FROM tags_final WHERE sub_category = 'null'
    """)
    
    null_count = cursor.fetchone()[0]
    print(f"\n剩餘 NULL 字符串: {null_count} 個")
    
    # 檢查低信心度來源
    cursor.execute("""
        SELECT 
            classification_source,
            COUNT(*) as tag_count,
            ROUND(AVG(classification_confidence), 3) as avg_confidence
        FROM tags_final
        WHERE classification_source IS NOT NULL
          AND classification_confidence IS NOT NULL
        GROUP BY classification_source
        HAVING AVG(classification_confidence) < 0.70
        ORDER BY avg_confidence ASC
    """)
    
    low_conf_sources = cursor.fetchall()
    print(f"\n低信心度來源: {len(low_conf_sources)} 個")
    
    for source, count, avg_conf in low_conf_sources:
        print(f"  - {source:40} 標籤數: {count:5}, 平均信心度: {avg_conf:.3f}")
    
    conn.close()

if __name__ == "__main__":
    check_hair_tags()
