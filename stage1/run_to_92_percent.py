#!/usr/bin/env python3
"""
衝刺 92% 覆蓋率 - 簡化執行腳本
處理所有剩餘中頻標籤 (10K-100K)
"""

import sys
import os

# 確保在正確的目錄
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 導入處理器
from optimized_llm_classifier import OptimizedLLMClassifier
import sqlite3
import time

def process_all_medium_freq():
    """處理所有中頻標籤"""
    print("="*80)
    print("衝刺 92% 覆蓋率 - 處理所有中頻標籤")
    print("="*80)
    
    conn = sqlite3.connect('output/tags.db')
    
    # 獲取所有中頻未分類標籤
    remaining = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 10000 AND post_count < 100000
        ORDER BY post_count DESC
    ''').fetchall()
    
    conn.close()
    
    total_tags = len(remaining)
    total_usage = sum(usage for _, usage in remaining)
    
    print(f"\n目標:")
    print(f"  剩餘中頻標籤: {total_tags:,} 個")
    print(f"  總使用次數: {total_usage:,} 次")
    print(f"  預估批次: {(total_tags + 19) // 20}")
    print(f"  預估成本: ${(total_tags // 20 + 1) * 0.0001:.3f}")
    print(f"  預估時間: {(total_tags // 20 + 1) * 2 / 60:.1f} 分鐘")
    
    # 確認執行
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        print("\n[自動模式] 開始處理...")
    else:
        confirm = input(f"\n確定要處理 {total_tags} 個標籤嗎？(y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return
    
    # 初始化分類器
    classifier = OptimizedLLMClassifier()
    
    # 批量處理
    batch_size = 20
    total_updated = 0
    checkpoint_interval = 300
    
    for batch_idx in range(0, total_tags, batch_size):
        batch_tags = [tag for tag, _ in remaining[batch_idx:batch_idx + batch_size]]
        batch_num = batch_idx // batch_size + 1
        total_batches = (total_tags + batch_size - 1) // batch_size
        
        print(f"\n批次 {batch_num}/{total_batches} ({len(batch_tags)} 個標籤)")
        print(f"  進度: {batch_idx + len(batch_tags)}/{total_tags} ({(batch_idx + len(batch_tags))/total_tags*100:.1f}%)")
        
        # 分類
        results = classifier.classify_batch(batch_tags)
        
        # 保存
        updated = classifier.save_to_database(results, "final_medium_freq_batch")
        total_updated += updated
        
        print(f"  完成: {updated}/{len(batch_tags)} 個")
        
        # 檢查點
        if (batch_idx + len(batch_tags)) % checkpoint_interval == 0 or (batch_idx + len(batch_tags)) == total_tags:
            conn_check = sqlite3.connect('output/tags.db')
            total_db = conn_check.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
            classified = conn_check.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
            coverage = classified / total_db * 100
            conn_check.close()
            
            print(f"\n  --- 檢查點 ({batch_idx + len(batch_tags)} 個已處理) ---")
            print(f"  當前覆蓋率: {coverage:.2f}%")
            print(f"  本輪成功率: {total_updated/(batch_idx + len(batch_tags))*100:.2f}%")
        
        # 延遲
        if batch_idx + batch_size < total_tags:
            time.sleep(1.5)
    
    # 最終統計
    conn_final = sqlite3.connect('output/tags.db')
    total_db = conn_final.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified = conn_final.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    final_coverage = classified / total_db * 100
    conn_final.close()
    
    print(f"\n{'='*80}")
    print("處理完成！")
    print("="*80)
    print(f"處理標籤: {total_tags}")
    print(f"成功更新: {total_updated}")
    print(f"成功率: {total_updated/total_tags*100:.2f}%")
    print(f"最終覆蓋率: {final_coverage:.2f}%")
    
    if final_coverage >= 92.0:
        print("\n🎉🎉🎉 恭喜！已達成 92% 目標！ 🎉🎉🎉")
    else:
        print(f"\n距離 92%: {92.0 - final_coverage:.2f}%")
        print(f"約需再處理: {int((92.0 - final_coverage) / 100 * total_db)} 個標籤")
    
    print("="*80)

if __name__ == "__main__":
    process_all_medium_freq()

