#!/usr/bin/env python3
"""
分類品質審查和一致性檢查工具
"""

import sqlite3
from collections import defaultdict

def check_consistency():
    """檢查分類一致性"""
    conn = sqlite3.connect('output/tags.db')
    
    print("="*80)
    print("分類品質和一致性檢查")
    print("="*80)
    
    # 1. 檢查低信心度標籤
    print("\n【低信心度標籤檢查 (<0.8)】")
    print("-"*50)
    
    low_conf_tags = conn.execute('''
        SELECT name, main_category, sub_category, 
               classification_confidence, post_count, classification_source
        FROM tags_final
        WHERE classification_confidence IS NOT NULL
        AND classification_confidence < 0.80
        ORDER BY post_count DESC
    ''').fetchall()
    
    print(f"找到 {len(low_conf_tags)} 個低信心度標籤")
    
    if low_conf_tags:
        print("\n前 20 個高使用量低信心度標籤:")
        for i, (name, main, sub, conf, usage, source) in enumerate(low_conf_tags[:20], 1):
            print(f"{i:2}. {name:30} -> {main}/{sub or 'N/A':15} (信心度: {conf:.3f}, {usage:,} 次)")
    
    # 2. 檢查缺少副分類的高頻標籤
    print(f"\n【缺少副分類的高頻標籤 (>100K)】")
    print("-"*50)
    
    no_sub_category = conn.execute('''
        SELECT name, main_category, post_count
        FROM tags_final
        WHERE main_category IS NOT NULL
        AND sub_category IS NULL
        AND post_count > 100000
        ORDER BY post_count DESC
        LIMIT 20
    ''').fetchall()
    
    print(f"找到 {len(no_sub_category)} 個")
    
    for i, (name, main, usage) in enumerate(no_sub_category, 1):
        print(f"{i:2}. {name:30} -> {main:25} ({usage:,} 次)")
    
    # 3. 檢查可能的分類不一致
    print(f"\n【相似標籤分類一致性檢查】")
    print("-"*50)
    
    # 檢查顏色+眼睛標籤
    eye_tags = conn.execute('''
        SELECT name, main_category, sub_category, post_count
        FROM tags_final
        WHERE name LIKE '%_eyes'
        AND main_category IS NOT NULL
        ORDER BY post_count DESC
        LIMIT 10
    ''').fetchall()
    
    print("\n眼睛顏色標籤:")
    cat_distribution = defaultdict(int)
    for name, main, sub, usage in eye_tags:
        cat_key = f"{main}/{sub or 'N/A'}"
        cat_distribution[cat_key] += 1
        print(f"  {name:25} -> {main}/{sub or 'N/A':20} ({usage:,} 次)")
    
    print(f"\n  分類分布: {dict(cat_distribution)}")
    if len(cat_distribution) > 1:
        print(f"  [WARN] 發現不一致: {len(cat_distribution)} 種不同分類")
    else:
        print(f"  [OK] 分類一致")
    
    # 檢查顏色+頭髮標籤
    hair_tags = conn.execute('''
        SELECT name, main_category, sub_category, post_count
        FROM tags_final
        WHERE name LIKE '%_hair'
        AND main_category IS NOT NULL
        ORDER BY post_count DESC
        LIMIT 10
    ''').fetchall()
    
    print("\n頭髮顏色標籤:")
    cat_distribution = defaultdict(int)
    for name, main, sub, usage in hair_tags:
        cat_key = f"{main}/{sub or 'N/A'}"
        cat_distribution[cat_key] += 1
        print(f"  {name:25} -> {main}/{sub or 'N/A':20} ({usage:,} 次)")
    
    print(f"\n  分類分布: {dict(cat_distribution)}")
    if len(cat_distribution) > 1:
        print(f"  [WARN] 發現不一致: {len(cat_distribution)} 種不同分類")
    else:
        print(f"  [OK] 分類一致")
    
    # 4. 檢查異常分類
    print(f"\n【異常分類檢查】")
    print("-"*50)
    
    # null 主分類
    null_main = conn.execute('''
        SELECT COUNT(*) FROM tags_final
        WHERE main_category = 'null'
    ''').fetchone()[0]
    
    print(f"主分類為 'null' 的標籤: {null_main} 個")
    
    # null 副分類（不算異常，因為某些主分類可能沒有副分類）
    null_sub = conn.execute('''
        SELECT COUNT(*) FROM tags_final
        WHERE main_category IS NOT NULL
        AND sub_category = 'null'
    ''').fetchone()[0]
    
    print(f"副分類為 'null' 的標籤: {null_sub} 個")
    
    if null_main > 0 or null_sub > 0:
        print(f"[WARN] 發現 'null' 字符串，應該使用 NULL")
    
    # 5. 統計信心度分布
    print(f"\n【信心度分布統計】")
    print("-"*50)
    
    conf_dist = conn.execute('''
        SELECT 
            CASE 
                WHEN classification_confidence >= 0.95 THEN '極高 (>=0.95)'
                WHEN classification_confidence >= 0.90 THEN '高 (0.90-0.95)'
                WHEN classification_confidence >= 0.85 THEN '中高 (0.85-0.90)'
                WHEN classification_confidence >= 0.80 THEN '中等 (0.80-0.85)'
                WHEN classification_confidence >= 0.75 THEN '中低 (0.75-0.80)'
                ELSE '低 (<0.75)'
            END as range_name,
            COUNT(*) as count,
            SUM(post_count) as usage
        FROM tags_final
        WHERE classification_confidence IS NOT NULL
        GROUP BY range_name
        ORDER BY MIN(classification_confidence) DESC
    ''').fetchall()
    
    for range_name, count, usage in conf_dist:
        print(f"  {range_name:20} {count:5} 個標籤, {usage:12,} 次使用")
    
    # 6. 分類來源品質對比
    print(f"\n【分類來源品質對比】")
    print("-"*50)
    
    source_quality = conn.execute('''
        SELECT 
            classification_source,
            COUNT(*) as count,
            AVG(classification_confidence) as avg_conf,
            MIN(classification_confidence) as min_conf,
            MAX(classification_confidence) as max_conf
        FROM tags_final
        WHERE classification_source IS NOT NULL
        AND classification_confidence IS NOT NULL
        GROUP BY classification_source
        ORDER BY count DESC
    ''').fetchall()
    
    for source, count, avg_conf, min_conf, max_conf in source_quality:
        print(f"  {source:35}")
        print(f"    標籤數: {count:5}, 平均信心度: {avg_conf:.3f} (範圍: {min_conf:.3f}-{max_conf:.3f})")
    
    conn.close()
    
    print("\n" + "="*80)
    print("檢查完成")
    print("="*80)

if __name__ == "__main__":
    check_consistency()

