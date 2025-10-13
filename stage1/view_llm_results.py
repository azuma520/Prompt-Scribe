#!/usr/bin/env python3
"""
查看 LLM 分類結果
"""

import sqlite3

def view_results():
    conn = sqlite3.connect('output/tags.db')
    
    query = """
        SELECT name, main_category, sub_category, 
               classification_confidence, classification_reasoning, post_count
        FROM tags_final
        WHERE classification_source = 'qwen3_80b'
        ORDER BY post_count DESC
        LIMIT 30
    """
    
    cursor = conn.execute(query)
    results = cursor.fetchall()
    
    print("="*80)
    print(f"LLM 分類結果（共 {len(results)} 個標籤）")
    print("="*80)
    print()
    
    for i, row in enumerate(results, 1):
        name, main_cat, sub_cat, confidence, reasoning, post_count = row
        
        print(f"{i:2}. {name}")
        print(f"    分類: {main_cat} / {sub_cat or 'None'}")
        print(f"    置信度: {confidence:.2f}")
        print(f"    使用次數: {post_count:,}")
        print(f"    理由: {reasoning[:80]}{'...' if len(reasoning) > 80 else ''}")
        print()
    
    # 統計
    cursor = conn.execute("""
        SELECT 
            COUNT(*) as total,
            AVG(classification_confidence) as avg_conf,
            MIN(classification_confidence) as min_conf,
            MAX(classification_confidence) as max_conf
        FROM tags_final
        WHERE classification_source = 'qwen3_80b'
    """)
    
    total, avg_conf, min_conf, max_conf = cursor.fetchone()
    
    print("="*80)
    print("統計摘要")
    print("="*80)
    print(f"總標籤數: {total}")
    print(f"平均置信度: {avg_conf:.3f}")
    print(f"最低置信度: {min_conf:.3f}")
    print(f"最高置信度: {max_conf:.3f}")
    
    # 分類分布
    cursor = conn.execute("""
        SELECT main_category, COUNT(*) as count
        FROM tags_final
        WHERE classification_source = 'qwen3_80b'
        GROUP BY main_category
        ORDER BY count DESC
    """)
    
    print("\n主分類分布:")
    for main_cat, count in cursor.fetchall():
        print(f"  {main_cat}: {count}")
    
    conn.close()

if __name__ == "__main__":
    view_results()

