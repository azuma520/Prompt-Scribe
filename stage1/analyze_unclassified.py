#!/usr/bin/env python3
"""
分析未分類標籤的特徵和優化機會
"""

import sqlite3

def analyze_unclassified_tags():
    """分析未分類標籤的分布和特徵"""
    conn = sqlite3.connect('output/tags.db')
    
    print("="*80)
    print("未分類標籤分析報告")
    print("="*80)
    
    # 1. 頻率分布分析
    print("\n【頻率分布分析】")
    print("-"*50)
    
    result = conn.execute('''
        SELECT 
            CASE 
                WHEN post_count >= 1000000 THEN '超高頻 (>=1M)'
                WHEN post_count >= 500000 THEN '高頻 (500K-1M)'
                WHEN post_count >= 100000 THEN '中高頻 (100K-500K)'
                WHEN post_count >= 50000 THEN '中頻 (50K-100K)'
                WHEN post_count >= 10000 THEN '中低頻 (10K-50K)'
                ELSE '低頻 (<10K)'
            END as freq_range,
            COUNT(*) as count,
            SUM(post_count) as total_usage
        FROM tags_final 
        WHERE danbooru_cat = 0 AND main_category IS NULL
        GROUP BY freq_range
        ORDER BY MIN(post_count) DESC
    ''').fetchall()
    
    total_unclassified = 0
    total_usage = 0
    
    for range_name, count, usage in result:
        print(f"{range_name:20} {count:6} 個標籤，總使用 {usage:12,} 次")
        total_unclassified += count
        total_usage += usage
    
    print(f"\n總計: {total_unclassified:,} 個未分類標籤，總使用 {total_usage:,} 次")
    
    # 2. 最高頻未分類標籤
    print("\n【最高頻未分類標籤 TOP 20】")
    print("-"*50)
    
    top_unclassified = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 AND main_category IS NULL
        ORDER BY post_count DESC
        LIMIT 20
    ''').fetchall()
    
    for i, (name, usage) in enumerate(top_unclassified, 1):
        print(f"{i:2}. {name:30} {usage:12,} 次")
    
    # 3. 潛在規則擴展機會
    print("\n【潛在規則擴展機會】")
    print("-"*50)
    
    # 分析常見模式
    patterns = {
        'body_parts': ['eye', 'hair', 'breast', 'leg', 'arm', 'hand', 'foot', 'head', 'face'],
        'clothing': ['shirt', 'dress', 'skirt', 'pant', 'shoe', 'hat', 'glove', 'sock'],
        'colors': ['red', 'blue', 'green', 'black', 'white', 'yellow', 'pink', 'purple'],
        'sizes': ['large', 'small', 'big', 'tiny', 'huge', 'mini'],
        'positions': ['top', 'bottom', 'front', 'back', 'side', 'center'],
        'numbers': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        'actions': ['hold', 'wear', 'stand', 'sit', 'lie', 'walk', 'run'],
        'adjectives': ['cute', 'beautiful', 'sexy', 'hot', 'cool', 'nice', 'pretty']
    }
    
    for pattern_name, keywords in patterns.items():
        matches = []
        for name, usage in top_unclassified:
            if any(keyword in name.lower() for keyword in keywords):
                matches.append((name, usage))
        
        if matches:
            print(f"\n{pattern_name.upper()} 模式 ({len(matches)} 個匹配):")
            for name, usage in matches[:5]:  # 只顯示前5個
                print(f"  - {name:30} {usage:10,} 次")
    
    # 4. LLM 處理建議
    print("\n【LLM 處理建議】")
    print("-"*50)
    
    # 中高頻標籤 (100K-1M)
    medium_freq = conn.execute('''
        SELECT COUNT(*) as count, SUM(post_count) as usage
        FROM tags_final 
        WHERE danbooru_cat = 0 AND main_category IS NULL
        AND post_count >= 100000 AND post_count < 1000000
    ''').fetchone()
    
    print(f"中高頻標籤 (100K-1M): {medium_freq[0]:,} 個")
    print(f"總使用次數: {medium_freq[1]:,} 次")
    print(f"建議: 使用 LLM 批量處理，預估成本 <$0.05")
    
    # 中頻標籤 (10K-100K)
    mid_freq = conn.execute('''
        SELECT COUNT(*) as count, SUM(post_count) as usage
        FROM tags_final 
        WHERE danbooru_cat = 0 AND main_category IS NULL
        AND post_count >= 10000 AND post_count < 100000
    ''').fetchone()
    
    print(f"\n中頻標籤 (10K-100K): {mid_freq[0]:,} 個")
    print(f"總使用次數: {mid_freq[1]:,} 次")
    print(f"建議: 規則擴展優先，LLM 補充")
    
    conn.close()

if __name__ == "__main__":
    analyze_unclassified_tags()
