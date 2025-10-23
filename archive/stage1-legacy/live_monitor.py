#!/usr/bin/env python3
"""
即時監控工具 - 查看批量處理進度
"""

import sqlite3
from datetime import datetime
import time

def live_monitor():
    """即時監控"""
    conn = sqlite3.connect('output/tags.db')
    
    # 獲取基本統計
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    # 各階段處理情況
    phases = {
        'phase_1_30k_50k': (30000, 50000),
        'phase_2_20k_30k': (20000, 30000),
        'phase_3_10k_20k': (10000, 20000),
    }
    
    print("="*80)
    print(f"即時監控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    print(f"\n【整體進度】")
    print(f"  當前覆蓋率: {coverage:.2f}%")
    print(f"  已分類: {classified_tags:,} / {total_tags:,}")
    print(f"  距離 92%: {92.0 - coverage:.2f}%")
    
    # 檢查各階段
    print(f"\n【各階段處理狀態】")
    
    for phase_name, (min_freq, max_freq) in phases.items():
        # 已處理
        processed = conn.execute(f'''
            SELECT COUNT(*), SUM(post_count)
            FROM tags_final
            WHERE classification_source LIKE '%{phase_name}%'
        ''').fetchone()
        
        processed_count, processed_usage = processed if processed[0] else (0, 0)
        processed_usage = processed_usage or 0
        
        # 剩餘
        remaining = conn.execute(f'''
            SELECT COUNT(*), SUM(post_count)
            FROM tags_final
            WHERE danbooru_cat = 0
            AND main_category IS NULL
            AND post_count >= {min_freq} AND post_count < {max_freq}
        ''').fetchone()
        
        remaining_count, remaining_usage = remaining if remaining[0] else (0, 0)
        remaining_usage = remaining_usage or 0
        
        total = processed_count + remaining_count
        progress = (processed_count / total * 100) if total > 0 else 0
        
        print(f"\n{phase_name.upper()}:")
        print(f"  已處理: {processed_count} 個 ({processed_usage:,} 次)")
        print(f"  剩餘: {remaining_count} 個 ({remaining_usage:,} 次)")
        print(f"  進度: {progress:.1f}%")
    
    # 最近處理的標籤
    print(f"\n【最近處理的 10 個標籤】")
    recent = conn.execute('''
        SELECT name, main_category, sub_category, 
               classification_confidence, post_count, classification_source
        FROM tags_final
        WHERE classification_timestamp IS NOT NULL
        ORDER BY classification_timestamp DESC
        LIMIT 10
    ''').fetchall()
    
    for i, (name, main, sub, conf, usage, source) in enumerate(recent, 1):
        conf_str = f"{conf:.3f}" if conf else "N/A"
        print(f"{i:2}. {name:25} -> {main}/{sub or 'N/A':15} (信心度: {conf_str}, {usage:,} 次)")
    
    conn.close()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    live_monitor()


