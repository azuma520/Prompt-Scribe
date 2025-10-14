#!/usr/bin/env python3
"""檢查 Plan C Phase 1 執行進度"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'data' / 'raw' / 'danbooru_tags.db'

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("Plan C Phase 1 執行進度詳情")
    print("=" * 80)
    print()
    
    # 整體統計
    cursor.execute("SELECT COUNT(*) FROM tags")
    total_tags = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tags WHERE classification IS NOT NULL")
    classified_tags = cursor.fetchone()[0]
    
    coverage = (classified_tags / total_tags * 100) if total_tags > 0 else 0
    
    print(f"整體統計:")
    print(f"  總標籤數: {total_tags:,}")
    print(f"  已分類: {classified_tags:,}")
    print(f"  覆蓋率: {coverage:.2f}%")
    print()
    
    # Phase 1 統計
    print("Phase 1 處理統計:")
    cursor.execute("SELECT COUNT(*) FROM tags WHERE source_tag LIKE 'phase1_%'")
    phase1_total = cursor.fetchone()[0]
    print(f"  Phase 1 總處理: {phase1_total:,} 個標籤")
    print()
    
    # 各子階段統計
    print("各子階段詳情:")
    phases = [
        ('phase1_2_30k_50k_batch', 'Phase 1-2: 30K-50K'),
        ('phase1_3_20k_30k_batch', 'Phase 1-3: 20K-30K'),
        ('phase1_4_10k_20k_batch', 'Phase 1-4: 10K-20K')
    ]
    
    for source_tag, phase_name in phases:
        cursor.execute(f"SELECT COUNT(*) FROM tags WHERE source_tag = ?", (source_tag,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            # 統計信心度
            cursor.execute("""
                SELECT 
                    AVG(confidence_score),
                    MIN(confidence_score),
                    MAX(confidence_score)
                FROM tags 
                WHERE source_tag = ? AND confidence_score IS NOT NULL
            """, (source_tag,))
            avg_conf, min_conf, max_conf = cursor.fetchone()
            
            print(f"\n  {phase_name}:")
            print(f"    處理標籤: {count:,} 個")
            if avg_conf:
                print(f"    平均信心度: {avg_conf:.3f}")
                print(f"    信心度範圍: {min_conf:.3f} - {max_conf:.3f}")
            
            # 低信心度標籤
            cursor.execute("""
                SELECT name, confidence_score, classification
                FROM tags 
                WHERE source_tag = ? AND confidence_score < 0.80
                ORDER BY confidence_score
            """, (source_tag,))
            low_conf_tags = cursor.fetchall()
            
            if low_conf_tags:
                print(f"    低信心度標籤 ({len(low_conf_tags)} 個):")
                for name, conf, cls in low_conf_tags[:5]:  # 只顯示前5個
                    print(f"      - {name}: {conf:.2f} → {cls}")
                if len(low_conf_tags) > 5:
                    print(f"      ... 還有 {len(low_conf_tags) - 5} 個")
    
    print()
    print("=" * 80)
    
    # 一般標籤統計
    print()
    print("一般標籤 (danbooru_cat=0) 統計:")
    cursor.execute("SELECT COUNT(*) FROM tags WHERE danbooru_cat = 0")
    cat0_total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tags WHERE danbooru_cat = 0 AND classification IS NOT NULL")
    cat0_classified = cursor.fetchone()[0]
    
    cat0_coverage = (cat0_classified / cat0_total * 100) if cat0_total > 0 else 0
    
    print(f"  總標籤數: {cat0_total:,}")
    print(f"  已分類: {cat0_classified:,}")
    print(f"  覆蓋率: {cat0_coverage:.2f}%")
    print(f"  待分類: {cat0_total - cat0_classified:,}")
    
    # Phase 1 對一般標籤的貢獻
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tags 
        WHERE danbooru_cat = 0 AND source_tag LIKE 'phase1_%'
    """)
    phase1_cat0 = cursor.fetchone()[0]
    print(f"  Phase 1 新增: {phase1_cat0:,} 個")
    
    print()
    print("=" * 80)
    
    # 待處理標籤統計（按頻率）
    print()
    print("待處理標籤統計（按使用頻率）:")
    
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
    
    for min_freq, max_freq, label in frequency_ranges:
        if max_freq:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tags 
                WHERE danbooru_cat = 0 
                  AND classification IS NULL 
                  AND post_count >= ? 
                  AND post_count < ?
            """, (min_freq, max_freq))
        else:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tags 
                WHERE danbooru_cat = 0 
                  AND classification IS NULL 
                  AND post_count >= ?
            """, (min_freq,))
        
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"  {label:12s}: {count:5,} 個標籤")
    
    conn.close()
    
    print()
    print("=" * 80)
    print("Phase 1 執行完成！")
    print()

if __name__ == '__main__':
    main()

