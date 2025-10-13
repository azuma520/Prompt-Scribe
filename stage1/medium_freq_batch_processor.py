#!/usr/bin/env python3
"""
中頻標籤批量處理器 (10K-100K)
目標：處理約 3,200 個中頻未分類標籤，預期提升覆蓋率 +2.5%
"""

import sqlite3
import time
from optimized_llm_classifier import OptimizedLLMClassifier

def analyze_medium_freq_tags():
    """分析中頻未分類標籤"""
    conn = sqlite3.connect('output/tags.db')
    
    # 獲取中頻未分類標籤統計
    stats = conn.execute('''
        SELECT 
            COUNT(*) as count,
            SUM(post_count) as total_usage,
            AVG(post_count) as avg_usage,
            MIN(post_count) as min_usage,
            MAX(post_count) as max_usage
        FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 10000 AND post_count < 100000
    ''').fetchone()
    
    count, total_usage, avg_usage, min_usage, max_usage = stats
    
    print("="*80)
    print("中頻標籤分析 (10K-100K)")
    print("="*80)
    print(f"標籤數量: {count:,} 個")
    print(f"總使用次數: {total_usage:,} 次")
    print(f"平均使用次數: {avg_usage:,.0f} 次")
    print(f"範圍: {min_usage:,} - {max_usage:,} 次")
    
    # 預估成本和覆蓋率提升
    estimated_batches = (count + 19) // 20
    estimated_cost = estimated_batches * 0.0001  # Gemini 2.5 Flash Lite 極低成本
    
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    estimated_coverage_gain = (count / total_tags) * 100
    
    print(f"\n預估:")
    print(f"  批次數: {estimated_batches} 個")
    print(f"  預估成本: ${estimated_cost:.3f}")
    print(f"  預估覆蓋率提升: +{estimated_coverage_gain:.2f}%")
    
    # 抽樣顯示
    print(f"\n前 20 個中頻未分類標籤:")
    samples = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 10000 AND post_count < 100000
        ORDER BY post_count DESC
        LIMIT 20
    ''').fetchall()
    
    for i, (name, usage) in enumerate(samples, 1):
        print(f"  {i:2}. {name:30} {usage:,} 次")
    
    conn.close()
    
    return count, total_usage

def process_medium_freq_batch(limit=None, batch_size=20):
    """處理中頻標籤批次"""
    print("\n" + "="*80)
    print("開始 LLM 批量處理中頻標籤")
    print("="*80)
    
    conn = sqlite3.connect('output/tags.db')
    
    # 獲取中頻未分類標籤
    query = '''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 10000 AND post_count < 100000
        ORDER BY post_count DESC
    '''
    
    if limit:
        query += f' LIMIT {limit}'
    
    unclassified = conn.execute(query).fetchall()
    conn.close()
    
    total_tags = len(unclassified)
    print(f"\n找到 {total_tags} 個中頻未分類標籤")
    
    if total_tags == 0:
        print("沒有需要處理的標籤")
        return
    
    # 初始化分類器
    classifier = OptimizedLLMClassifier()
    
    # 批次處理
    total_updated = 0
    total_batches = (total_tags + batch_size - 1) // batch_size
    
    for batch_idx in range(0, total_tags, batch_size):
        batch_tags = [tag for tag, _ in unclassified[batch_idx:batch_idx + batch_size]]
        batch_num = batch_idx // batch_size + 1
        
        print(f"\n處理批次 {batch_num}/{total_batches} ({len(batch_tags)} 個標籤)")
        print(f"  標籤: {', '.join(batch_tags[:5])}{'...' if len(batch_tags) > 5 else ''}")
        
        # 分類
        results = classifier.classify_batch(batch_tags)
        
        # 保存到資料庫
        updated = classifier.save_to_database(results, "medium_freq_llm_batch")
        total_updated += updated
        
        print(f"  批次 {batch_num} 完成: 更新 {updated}/{len(batch_tags)} 個標籤")
        
        # 避免 API 限流
        if batch_idx + batch_size < total_tags:
            time.sleep(1.5)
    
    # 最終統計
    conn = sqlite3.connect('output/tags.db')
    total_db_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_db_tags * 100
    conn.close()
    
    print(f"\n{'='*80}")
    print(f"中頻標籤批量處理完成")
    print(f"{'='*80}")
    print(f"處理標籤: {total_tags}")
    print(f"成功更新: {total_updated}")
    print(f"成功率: {total_updated/total_tags*100:.2f}%")
    print(f"新覆蓋率: {coverage:.2f}%")
    print(f"{'='*80}")

if __name__ == "__main__":
    import sys
    
    # 先分析
    analyze_medium_freq_tags()
    
    # 根據參數決定處理數量
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            print("\n[測試模式] 處理前 100 個標籤")
            process_medium_freq_batch(limit=100, batch_size=20)
        elif sys.argv[1] == '--sample':
            print("\n[樣本模式] 處理前 500 個標籤")
            process_medium_freq_batch(limit=500, batch_size=20)
        else:
            limit = int(sys.argv[1])
            print(f"\n[自定義模式] 處理 {limit} 個標籤")
            process_medium_freq_batch(limit=limit, batch_size=20)
    else:
        print("\n使用方式:")
        print("  python medium_freq_batch_processor.py --test    # 測試 100 個")
        print("  python medium_freq_batch_processor.py --sample  # 處理 500 個")
        print("  python medium_freq_batch_processor.py 1000      # 處理 1000 個")
        print("  python medium_freq_batch_processor.py           # 顯示此說明")

