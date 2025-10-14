#!/usr/bin/env python3
"""
全面分類測試和驗證
"""

import sqlite3
from collections import defaultdict
import random

def comprehensive_classification_test():
    """執行全面的分類測試"""
    conn = sqlite3.connect('output/tags.db')
    
    print("="*80)
    print("全面分類測試報告")
    print("="*80)
    
    # 1. 基本統計
    print("\n【基本統計】")
    print("-"*50)
    
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    print(f"總標籤數: {total_tags:,}")
    print(f"已分類標籤: {classified_tags:,}")
    print(f"覆蓋率: {coverage:.2f}%")
    print(f"未分類標籤: {total_tags - classified_tags:,}")
    
    # 2. 分類來源分析
    print("\n【分類來源分析】")
    print("-"*50)
    
    sources = conn.execute('''
        SELECT classification_source, COUNT(*) as count, SUM(post_count) as usage
        FROM tags_final 
        WHERE classification_source IS NOT NULL
        GROUP BY classification_source
        ORDER BY count DESC
    ''').fetchall()
    
    for source, count, usage in sources:
        print(f"{source:30} {count:6} 個標籤，{usage:12,} 次使用")
    
    # 3. 主分類分布
    print("\n【主分類分布】")
    print("-"*50)
    
    main_cats = conn.execute('''
        SELECT main_category, COUNT(*) as count, SUM(post_count) as usage
        FROM tags_final 
        WHERE main_category IS NOT NULL
        GROUP BY main_category
        ORDER BY count DESC
    ''').fetchall()
    
    for cat, count, usage in main_cats:
        print(f"{cat:20} {count:6} 個標籤，{usage:12,} 次使用")
    
    # 4. 副分類分布 (Top 20)
    print("\n【副分類分布 (Top 20)】")
    print("-"*50)
    
    sub_cats = conn.execute('''
        SELECT sub_category, COUNT(*) as count, SUM(post_count) as usage
        FROM tags_final 
        WHERE sub_category IS NOT NULL
        GROUP BY sub_category
        ORDER BY count DESC
        LIMIT 20
    ''').fetchall()
    
    for sub_cat, count, usage in sub_cats:
        print(f"{sub_cat:20} {count:6} 個標籤，{usage:12,} 次使用")
    
    # 5. LLM 分類品質分析
    print("\n【LLM 分類品質分析】")
    print("-"*50)
    
    llm_stats = conn.execute('''
        SELECT 
            COUNT(*) as count,
            AVG(classification_confidence) as avg_confidence,
            MIN(classification_confidence) as min_confidence,
            MAX(classification_confidence) as max_confidence,
            SUM(post_count) as total_usage
        FROM tags_final 
        WHERE classification_source LIKE '%qwen%' OR classification_source LIKE '%llm%'
    ''').fetchone()
    
    if llm_stats[0] > 0:
        count, avg_conf, min_conf, max_conf, usage = llm_stats
        print(f"LLM 分類標籤數: {count:,}")
        print(f"總使用次數: {usage:,}")
        print(f"平均信心度: {avg_conf:.3f}")
        print(f"最低信心度: {min_conf:.3f}")
        print(f"最高信心度: {max_conf:.3f}")
    
    # 6. 信心度分布
    print("\n【信心度分布】")
    print("-"*50)
    
    confidence_dist = conn.execute('''
        SELECT 
            CASE 
                WHEN classification_confidence >= 0.9 THEN '高信心度 (>=0.9)'
                WHEN classification_confidence >= 0.8 THEN '中高信心度 (0.8-0.9)'
                WHEN classification_confidence >= 0.7 THEN '中等信心度 (0.7-0.8)'
                WHEN classification_confidence >= 0.6 THEN '中低信心度 (0.6-0.7)'
                ELSE '低信心度 (<0.6)'
            END as conf_range,
            COUNT(*) as count
        FROM tags_final 
        WHERE classification_confidence IS NOT NULL
        GROUP BY conf_range
        ORDER BY MIN(classification_confidence) DESC
    ''').fetchall()
    
    for conf_range, count in confidence_dist:
        print(f"{conf_range:20} {count:6} 個標籤")
    
    # 7. 高頻標籤抽樣驗證
    print("\n【高頻標籤抽樣驗證】")
    print("-"*50)
    
    high_freq_sample = conn.execute('''
        SELECT name, main_category, sub_category, 
               classification_confidence, post_count, classification_source
        FROM tags_final
        WHERE main_category IS NOT NULL
        AND post_count > 1000000
        ORDER BY RANDOM()
        LIMIT 10
    ''').fetchall()
    
    print("隨機抽取 10 個高頻已分類標籤 (>1M 使用):\n")
    for i, (name, main, sub, conf, usage, source) in enumerate(high_freq_sample, 1):
        conf_str = f"{conf:.3f}" if conf else "N/A"
        print(f"{i:2}. {name:30} -> {main}/{sub or 'N/A':20} (信心度: {conf_str}, {usage:,} 次, {source})")
    
    # 8. 未分類標籤分析
    print("\n【未分類標籤分析】")
    print("-"*50)
    
    unclassified_high_freq = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE main_category IS NULL
        AND post_count >= 100000
        ORDER BY post_count DESC
        LIMIT 10
    ''').fetchall()
    
    print("最高頻未分類標籤 (>=100K 使用):")
    for i, (name, usage) in enumerate(unclassified_high_freq, 1):
        print(f"{i:2}. {name:30} {usage:12,} 次")
    
    # 9. 一致性檢查
    print("\n【一致性檢查】")
    print("-"*50)
    
    # 檢查是否有重複分類
    duplicates = conn.execute('''
        SELECT name, COUNT(*) as count
        FROM tags_final 
        WHERE main_category IS NOT NULL
        GROUP BY name
        HAVING COUNT(*) > 1
        LIMIT 5
    ''').fetchall()
    
    if duplicates:
        print("發現重複分類的標籤:")
        for name, count in duplicates:
            print(f"  {name}: {count} 次")
    else:
        print("[OK] 沒有發現重複分類")
    
    # 10. 規則擴展效果分析
    print("\n【規則擴展效果分析】")
    print("-"*50)
    
    rule_expansion_stats = conn.execute('''
        SELECT 
            COUNT(*) as count,
            SUM(post_count) as usage
        FROM tags_final 
        WHERE classification_source LIKE '%rule_expansion%' 
        OR classification_source LIKE '%comprehensive_rule%'
        OR classification_source LIKE '%advanced_rule%'
    ''').fetchone()
    
    if rule_expansion_stats[0] > 0:
        count, usage = rule_expansion_stats
        print(f"規則擴展處理標籤: {count:,} 個")
        print(f"影響使用次數: {usage:,} 次")
        print(f"佔總使用量比例: {usage / conn.execute('SELECT SUM(post_count) FROM tags_final').fetchone()[0] * 100:.2f}%")
    
    conn.close()
    
    print("\n" + "="*80)
    print("測試完成")
    print("="*80)

if __name__ == "__main__":
    comprehensive_classification_test()
