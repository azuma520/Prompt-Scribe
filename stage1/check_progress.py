#!/usr/bin/env python3
"""
檢查優化進度
"""

import sqlite3
from datetime import datetime

def check_progress():
    """檢查當前優化進度"""
    conn = sqlite3.connect('output/tags.db')
    
    print("="*80)
    print(f"Stage 1 優化進度報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 1. 基本統計
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    print(f"\n【整體進度】")
    print(f"  總標籤數: {total_tags:,}")
    print(f"  已分類標籤: {classified_tags:,}")
    print(f"  覆蓋率: {coverage:.2f}%")
    print(f"  未分類標籤: {total_tags - classified_tags:,}")
    
    # 2. 按來源統計
    print(f"\n【分類來源統計】")
    sources = conn.execute('''
        SELECT classification_source, COUNT(*) as count, SUM(post_count) as usage
        FROM tags_final 
        WHERE classification_source IS NOT NULL
        GROUP BY classification_source
        ORDER BY count DESC
        LIMIT 15
    ''').fetchall()
    
    for source, count, usage in sources:
        print(f"  {source:35} {count:5} 個標籤, {usage:12,} 次使用")
    
    # 3. 未分類標籤分布
    print(f"\n【未分類標籤分布】")
    
    freq_ranges = [
        ('超高頻 (>=1M)', 1000000, None),
        ('高頻 (100K-1M)', 100000, 1000000),
        ('中頻 (10K-100K)', 10000, 100000),
        ('低頻 (1K-10K)', 1000, 10000),
        ('極低頻 (<1K)', 0, 1000),
    ]
    
    for label, min_count, max_count in freq_ranges:
        if max_count:
            query = f'''
                SELECT COUNT(*), SUM(post_count)
                FROM tags_final
                WHERE danbooru_cat = 0 
                AND main_category IS NULL
                AND post_count >= {min_count} AND post_count < {max_count}
            '''
        else:
            query = f'''
                SELECT COUNT(*), SUM(post_count)
                FROM tags_final
                WHERE danbooru_cat = 0 
                AND main_category IS NULL
                AND post_count >= {min_count}
            '''
        
        result = conn.execute(query).fetchone()
        count, usage = result if result[0] else (0, 0)
        usage = usage or 0
        
        print(f"  {label:20} {count:5} 個標籤, {usage:12,} 次使用")
    
    # 4. 最近處理的標籤
    print(f"\n【最近處理的標籤 (Top 10)】")
    recent = conn.execute('''
        SELECT name, main_category, sub_category, classification_source, post_count
        FROM tags_final
        WHERE classification_timestamp IS NOT NULL
        ORDER BY classification_timestamp DESC
        LIMIT 10
    ''').fetchall()
    
    for i, (name, main, sub, source, usage) in enumerate(recent, 1):
        print(f"  {i:2}. {name:25} -> {main}/{sub or 'N/A':20} ({usage:,} 次)")
    
    # 5. 覆蓋率里程碑
    print(f"\n【覆蓋率里程碑】")
    milestones = [
        (88.57, "優化開始"),
        (89.00, "突破 89%"),
        (89.50, "接近 90%"),
        (90.00, "突破 90% [MILESTONE]"),
        (91.00, "突破 91%"),
        (92.00, "目標達成 [TARGET]"),
    ]
    
    for milestone, desc in milestones:
        if coverage >= milestone:
            status = "[OK]"
        elif coverage >= milestone - 0.5:
            status = "[->]"
        else:
            status = "[  ]"
        
        print(f"  {status} {milestone:.2f}% - {desc}")
    
    # 6. 預估完成度
    print(f"\n【距離目標】")
    target = 92.0
    remaining_percent = target - coverage
    remaining_tags = int((remaining_percent / 100) * total_tags)
    
    print(f"  目標覆蓋率: {target}%")
    print(f"  當前覆蓋率: {coverage:.2f}%")
    print(f"  剩餘距離: {remaining_percent:.2f}%")
    print(f"  約需處理: {remaining_tags:,} 個標籤")
    
    conn.close()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_progress()

