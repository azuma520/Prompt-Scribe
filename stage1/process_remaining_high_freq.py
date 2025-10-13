#!/usr/bin/env python3
"""
處理剩餘的高頻未分類標籤 (>=100K)
手動審核並應用規則
"""

import sqlite3

# 剩餘高頻標籤的手動分類規則
HIGH_FREQ_MANUAL_RULES = {
    'playing_games': ('ACTION_POSE', 'INTERACTION', 0.95, '正在玩遊戲的互動行為'),
    'company_connection': ('THEME_CONCEPT', 'CONCEPT', 0.85, '公司/品牌關聯標籤'),
    'cake_slice': ('OBJECTS', 'FOOD', 0.98, '蛋糕切片'),
    'river': ('ENVIRONMENT', 'NATURE', 0.98, '河流自然場景'),
    'yukkuri_shiteitte_ne': ('THEME_CONCEPT', 'CONCEPT', 0.90, '日本網路迷因角色系列'),
    'twisted_torso': ('ACTION_POSE', 'BODY_POSE', 0.92, '扭曲的身體姿勢'),
}

def get_remaining_high_freq_tags():
    """獲取剩餘的高頻未分類標籤"""
    conn = sqlite3.connect('output/tags.db')
    
    tags = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 100000
        ORDER BY post_count DESC
    ''').fetchall()
    
    conn.close()
    return tags

def apply_manual_rules():
    """應用手動分類規則"""
    print("="*80)
    print("處理剩餘高頻未分類標籤")
    print("="*80)
    
    # 先顯示當前狀態
    remaining = get_remaining_high_freq_tags()
    print(f"\n當前剩餘高頻未分類標籤 (>=100K): {len(remaining)} 個")
    for name, usage in remaining[:15]:
        print(f"  {name:30} {usage:,} 次")
    
    print(f"\n準備應用手動規則...")
    
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    updated_count = 0
    total_usage = 0
    
    for tag_name, (main_cat, sub_cat, confidence, reasoning) in HIGH_FREQ_MANUAL_RULES.items():
        # 檢查標籤是否存在且未分類
        result = cursor.execute('''
            SELECT post_count FROM tags_final 
            WHERE name = ? AND danbooru_cat = 0 AND main_category IS NULL
        ''', (tag_name,)).fetchone()
        
        if result:
            post_count = result[0]
            
            # 更新資料庫
            cursor.execute('''
                UPDATE tags_final 
                SET main_category = ?,
                    sub_category = ?,
                    classification_source = 'high_freq_manual',
                    classification_confidence = ?,
                    classification_reasoning = ?,
                    classification_timestamp = datetime('now')
                WHERE name = ? AND danbooru_cat = 0 AND main_category IS NULL
            ''', (main_cat, sub_cat, confidence, reasoning, tag_name))
            
            if cursor.rowcount > 0:
                updated_count += 1
                total_usage += post_count
                print(f"\n[OK] {tag_name}")
                print(f"     分類: {main_cat}/{sub_cat or 'N/A'}")
                print(f"     使用: {post_count:,} 次")
                print(f"     信心度: {confidence:.2f}")
                print(f"     理由: {reasoning}")
    
    conn.commit()
    
    # 統計結果
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    # 再次檢查剩餘
    remaining_after = conn.execute('''
        SELECT COUNT(*) FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 100000
    ''').fetchone()[0]
    
    print(f"\n{'='*80}")
    print(f"處理結果")
    print(f"{'='*80}")
    print(f"成功更新標籤: {updated_count} 個")
    print(f"影響使用次數: {total_usage:,} 次")
    print(f"剩餘高頻未分類: {remaining_after} 個")
    print(f"整體覆蓋率: {coverage:.2f}%")
    
    conn.close()
    
    return updated_count, total_usage

if __name__ == "__main__":
    apply_manual_rules()

