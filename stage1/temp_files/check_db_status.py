#!/usr/bin/env python3
"""
資料庫狀況檢查工具
檢查當前 tags.db 的詳細狀況
"""

import sqlite3
from collections import defaultdict

def check_db_status():
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    print("="*80)
    print("資料庫完整狀況報告")
    print("="*80)
    
    # 1. 總體統計
    print("\n【1. 總體統計】")
    print("-"*80)
    
    cursor.execute("SELECT COUNT(*) FROM tags_final")
    total_tags = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL")
    classified_tags = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tags_final WHERE main_category IS NULL")
    unclassified_tags = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(post_count) FROM tags_final")
    total_usage = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(post_count) FROM tags_final WHERE main_category IS NOT NULL")
    classified_usage = cursor.fetchone()[0]
    
    print(f"總標籤數: {total_tags:,}")
    print(f"已分類標籤: {classified_tags:,} ({classified_tags/total_tags*100:.2f}%)")
    print(f"待分類標籤: {unclassified_tags:,} ({unclassified_tags/total_tags*100:.2f}%)")
    print(f"總使用次數: {total_usage:,}")
    print(f"已分類使用次數: {classified_usage:,} ({classified_usage/total_usage*100:.2f}%)")
    
    # 2. 主分類分布
    print("\n【2. 主分類分布】")
    print("-"*80)
    
    cursor.execute("""
        SELECT main_category, COUNT(*) as count, SUM(post_count) as usage
        FROM tags_final
        WHERE main_category IS NOT NULL
        GROUP BY main_category
        ORDER BY count DESC
    """)
    
    print(f"{'主分類':25} {'標籤數':>12} {'使用次數':>15} {'標籤占比':>10} {'使用占比':>10}")
    print("-"*80)
    
    for row in cursor.fetchall():
        main_cat, count, usage = row
        tag_pct = count / classified_tags * 100
        usage_pct = usage / classified_usage * 100
        print(f"{main_cat:25} {count:>12,} {usage:>15,} {tag_pct:>9.2f}% {usage_pct:>9.2f}%")
    
    # 3. 副分類統計
    print("\n【3. 副分類統計】")
    print("-"*80)
    
    cursor.execute("""
        SELECT COUNT(*) FROM tags_final
        WHERE main_category IS NOT NULL AND (sub_category IS NULL OR sub_category = '')
    """)
    no_sub = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM tags_final
        WHERE main_category IS NOT NULL AND sub_category IS NOT NULL AND sub_category != ''
    """)
    has_sub = cursor.fetchone()[0]
    
    print(f"有副分類: {has_sub:,} ({has_sub/classified_tags*100:.2f}%)")
    print(f"無副分類: {no_sub:,} ({no_sub/classified_tags*100:.2f}%)")
    
    # 4. 信心度分布
    print("\n【4. 信心度分布】")
    print("-"*80)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN classification_confidence >= 0.95 THEN '極高 (>=0.95)'
                WHEN classification_confidence >= 0.90 THEN '高 (0.90-0.95)'
                WHEN classification_confidence >= 0.85 THEN '中高 (0.85-0.90)'
                WHEN classification_confidence >= 0.80 THEN '中等 (0.80-0.85)'
                WHEN classification_confidence >= 0.75 THEN '中低 (0.75-0.80)'
                WHEN classification_confidence >= 0.60 THEN '低 (0.60-0.75)'
                ELSE '極低 (<0.60)'
            END as level,
            COUNT(*) as count,
            SUM(post_count) as usage
        FROM tags_final
        WHERE classification_confidence IS NOT NULL
        GROUP BY level
        ORDER BY MIN(classification_confidence) DESC
    """)
    
    print(f"{'信心度等級':20} {'標籤數':>12} {'使用次數':>15} {'占比':>10}")
    print("-"*80)
    
    for row in cursor.fetchall():
        level, count, usage = row
        pct = count / classified_tags * 100
        print(f"{level:20} {count:>12,} {usage:>15,} {pct:>9.2f}%")
    
    # 5. 分類來源統計
    print("\n【5. 分類來源統計】")
    print("-"*80)
    
    cursor.execute("""
        SELECT classification_source, COUNT(*) as count, AVG(classification_confidence) as avg_conf
        FROM tags_final
        WHERE classification_source IS NOT NULL
        GROUP BY classification_source
        ORDER BY count DESC
        LIMIT 15
    """)
    
    print(f"{'分類來源':40} {'標籤數':>12} {'平均信心度':>12}")
    print("-"*80)
    
    for row in cursor.fetchall():
        source, count, avg_conf = row
        conf_str = f"{avg_conf:.3f}" if avg_conf else "N/A"
        print(f"{source:40} {count:>12,} {conf_str:>12}")
    
    # 6. 頻率範圍分析
    print("\n【6. 標籤頻率分布】")
    print("-"*80)
    
    frequency_ranges = [
        (1000000, float('inf'), '超高頻 (>=1M)'),
        (100000, 1000000, '極高頻 (100K-1M)'),
        (50000, 100000, '高頻 (50K-100K)'),
        (10000, 50000, '中高頻 (10K-50K)'),
        (5000, 10000, '中頻 (5K-10K)'),
        (1000, 5000, '中低頻 (1K-5K)'),
        (100, 1000, '低頻 (100-1K)'),
        (0, 100, '極低頻 (<100)')
    ]
    
    print(f"{'頻率範圍':20} {'總標籤':>12} {'已分類':>12} {'待分類':>12} {'覆蓋率':>10}")
    print("-"*80)
    
    for min_freq, max_freq, label in frequency_ranges:
        if max_freq == float('inf'):
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified
                FROM tags_final
                WHERE post_count >= ?
            """, (min_freq,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified
                FROM tags_final
                WHERE post_count >= ? AND post_count < ?
            """, (min_freq, max_freq))
        
        total, classified = cursor.fetchone()
        if total > 0:
            unclassified = total - classified
            coverage = classified / total * 100
            print(f"{label:20} {total:>12,} {classified:>12,} {unclassified:>12,} {coverage:>9.2f}%")
    
    # 7. 品質問題檢查
    print("\n【7. 品質問題檢查】")
    print("-"*80)
    
    # NULL 字符串
    cursor.execute("""
        SELECT COUNT(*) FROM tags_final
        WHERE main_category = 'null' OR sub_category = 'null'
    """)
    null_strings = cursor.fetchone()[0]
    
    # 低信心度
    cursor.execute("""
        SELECT COUNT(*) FROM tags_final
        WHERE main_category IS NOT NULL 
        AND classification_confidence IS NOT NULL 
        AND classification_confidence < 0.75
    """)
    low_confidence = cursor.fetchone()[0]
    
    # 缺少副分類的高頻標籤
    cursor.execute("""
        SELECT COUNT(*) FROM tags_final
        WHERE main_category IS NOT NULL
        AND (sub_category IS NULL OR sub_category = '')
        AND post_count > 100000
    """)
    high_freq_no_sub = cursor.fetchone()[0]
    
    print(f"NULL 字符串標籤: {null_strings:,}")
    print(f"低信心度標籤 (<0.75): {low_confidence:,} ({low_confidence/classified_tags*100:.2f}%)")
    print(f"高頻標籤缺副分類 (>100K): {high_freq_no_sub:,}")
    
    if null_strings == 0 and low_confidence < 1000 and high_freq_no_sub == 0:
        print("\n[OK] 品質狀況良好！")
    else:
        print("\n[WARN] 仍有品質問題需要關注")
    
    # 8. Danbooru 分類統計
    print("\n【8. Danbooru 原生分類統計】")
    print("-"*80)
    
    cursor.execute("""
        SELECT danbooru_cat, COUNT(*) as count
        FROM tags_final
        GROUP BY danbooru_cat
        ORDER BY danbooru_cat
    """)
    
    danbooru_map = {
        0: '一般標籤 (General)',
        1: '藝術家 (Artist)', 
        3: '版權 (Copyright)',
        4: '角色 (Character)',
        5: '元標籤 (Meta)'
    }
    
    print(f"{'Danbooru 分類':30} {'標籤數':>12} {'已分類':>12} {'覆蓋率':>10}")
    print("-"*80)
    
    for row in cursor.fetchall():
        cat, total = row
        cat_name = danbooru_map.get(cat, f'未知 ({cat})')
        
        cursor.execute("""
            SELECT COUNT(*) FROM tags_final
            WHERE danbooru_cat = ? AND main_category IS NOT NULL
        """, (cat,))
        classified = cursor.fetchone()[0]
        
        coverage = classified / total * 100 if total > 0 else 0
        print(f"{cat_name:30} {total:>12,} {classified:>12,} {coverage:>9.2f}%")
    
    conn.close()
    
    print("\n" + "="*80)
    print("報告完成")
    print("="*80)

if __name__ == "__main__":
    check_db_status()

