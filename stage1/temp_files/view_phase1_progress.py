#!/usr/bin/env python3
"""查看 Plan C Phase 1 執行進度"""

import sqlite3

DB_PATH = 'output/tags.db'

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("Plan C Phase 1 執行進度報告")
    print("=" * 80)
    print()
    
    # 整體統計
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified
        FROM tags_final
    """)
    total_tags, classified_tags = cursor.fetchone()
    coverage = (classified_tags / total_tags * 100) if total_tags > 0 else 0
    
    print(f"【整體統計】")
    print(f"  總標籤數: {total_tags:,}")
    print(f"  已分類: {classified_tags:,}")
    print(f"  覆蓋率: {coverage:.2f}%")
    print(f"  待分類: {total_tags - classified_tags:,}")
    print()
    
    # 一般標籤統計
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified
        FROM tags_final 
        WHERE danbooru_cat = 0
    """)
    cat0_total, cat0_classified = cursor.fetchone()
    cat0_coverage = (cat0_classified / cat0_total * 100) if cat0_total > 0 else 0
    
    print(f"【一般標籤 (danbooru_cat=0)】")
    print(f"  總標籤數: {cat0_total:,}")
    print(f"  已分類: {cat0_classified:,}")
    print(f"  覆蓋率: {cat0_coverage:.2f}%")
    print(f"  待分類: {cat0_total - cat0_classified:,}")
    print()
    
    # Phase 1 統計
    print(f"【Phase 1 處理統計】")
    cursor.execute("SELECT COUNT(*) FROM tags_final WHERE source_tag LIKE 'phase1_%'")
    phase1_total = cursor.fetchone()[0]
    print(f"  Phase 1 總處理: {phase1_total:,} 個標籤")
    
    # Phase 1 對一般標籤的貢獻
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tags_final 
        WHERE danbooru_cat = 0 AND source_tag LIKE 'phase1_%'
    """)
    phase1_cat0 = cursor.fetchone()[0]
    print(f"  Phase 1 一般標籤: {phase1_cat0:,} 個")
    print()
    
    # 各子階段統計
    print(f"【各子階段詳情】")
    phases = [
        ('phase1_2_30k_50k_batch', 'Phase 1-2: 30K-50K'),
        ('phase1_3_20k_30k_batch', 'Phase 1-3: 20K-30K'),
        ('phase1_4_10k_20k_batch', 'Phase 1-4: 10K-20K')
    ]
    
    for source_tag, phase_name in phases:
        cursor.execute(f"SELECT COUNT(*) FROM tags_final WHERE source_tag = ?", (source_tag,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            # 統計信心度
            cursor.execute("""
                SELECT 
                    AVG(confidence_score),
                    MIN(confidence_score),
                    MAX(confidence_score),
                    SUM(CASE WHEN confidence_score < 0.80 THEN 1 ELSE 0 END)
                FROM tags_final 
                WHERE source_tag = ? AND confidence_score IS NOT NULL
            """, (source_tag,))
            avg_conf, min_conf, max_conf, low_conf_count = cursor.fetchone()
            
            print(f"\n  {phase_name}:")
            print(f"    處理標籤: {count:,} 個")
            if avg_conf:
                print(f"    平均信心度: {avg_conf:.3f}")
                print(f"    信心度範圍: {min_conf:.3f} - {max_conf:.3f}")
                print(f"    低信心度標籤: {low_conf_count} 個")
    
    print()
    print("=" * 80)
    
    # 待處理標籤統計（按頻率）
    print()
    print(f"【待處理標籤統計（按使用頻率）】")
    
    frequency_ranges = [
        (100000, None, "100K+"),
        (50000, 100000, "50K-100K"),
        (30000, 50000, "30K-50K"),
        (20000, 30000, "20K-30K"),
        (10000, 20000, "10K-20K"),
        (5000, 10000, "5K-10K"),
        (1000, 5000, "1K-5K"),
        (100, 1000, "100-1K"),
        (0, 100, "<100")
    ]
    
    total_unclassified = 0
    for min_freq, max_freq, label in frequency_ranges:
        if max_freq:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tags_final 
                WHERE danbooru_cat = 0 
                  AND main_category IS NULL 
                  AND post_count >= ? 
                  AND post_count < ?
            """, (min_freq, max_freq))
        else:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tags_final 
                WHERE danbooru_cat = 0 
                  AND main_category IS NULL 
                  AND post_count >= ?
            """, (min_freq,))
        
        count = cursor.fetchone()[0]
        if count > 0:
            total_unclassified += count
            print(f"  {label:12s}: {count:5,} 個標籤")
    
    print(f"\n  {'總計':12s}: {total_unclassified:5,} 個待分類標籤")
    
    conn.close()
    
    print()
    print("=" * 80)
    print("Phase 1 執行完成！")
    print()
    print("下一步: 執行 Phase 2 處理 5K-10K 和 1K-5K 頻率的標籤")
    print("執行命令: python run_plan_c_phase2.py")
    print("=" * 80)

if __name__ == '__main__':
    main()

