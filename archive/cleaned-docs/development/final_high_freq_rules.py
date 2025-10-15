#!/usr/bin/env python3
"""
最終高頻標籤分類規則
處理剩餘的 12 個高頻未分類標籤
"""

import sqlite3

# 最終高頻標籤手動分類規則
FINAL_HIGH_FREQ_RULES = {
    # 物品/效果
    'explosive': ('OBJECTS', 'WEAPONS', 0.90, '爆炸物/炸藥'),
    'dango': ('OBJECTS', 'FOOD', 0.98, '日式糰子（食物）'),
    'sake': ('OBJECTS', 'FOOD', 0.98, '日本清酒'),
    
    # 關係/互動
    'father_and_daughter': ('THEME_CONCEPT', 'CONCEPT', 0.95, '父女關係標籤'),
    'husband_and_wife': ('THEME_CONCEPT', 'CONCEPT', 0.95, '夫妻關係標籤'),
    
    # 表情/動作
    'turn_pale': ('ACTION_POSE', 'EXPRESSION', 0.90, '臉色蒼白的表情反應'),
    
    # 角色類型/職業
    'knight': ('CHARACTER_RELATED', None, 0.85, '騎士角色（涉及服裝、概念等多重屬性）'),
    
    # 場景/環境
    'train_interior': ('ENVIRONMENT', 'INDOOR', 0.95, '火車內部場景'),
    'castle': ('ENVIRONMENT', 'FANTASY', 0.95, '城堡建築場景'),
    
    # 服裝細節
    'notched_lapels': ('CHARACTER_RELATED', 'CLOTHING', 0.92, '西裝領口設計細節'),
    
    # 成人內容
    'exhibitionism': ('ADULT_CONTENT', 'SUGGESTIVE', 0.95, '露出癖/展示行為'),
    
    # 遊戲特定標籤
    'oripathy_lesion_(arknights)': ('CHARACTER_RELATED', 'BODY_PARTS', 0.90, 'Arknights 遊戲特定的礦石病特徵'),
}

def apply_final_high_freq_rules():
    """應用最終高頻標籤規則"""
    print("="*80)
    print("最終高頻標籤分類")
    print("="*80)
    
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    updated_count = 0
    total_usage = 0
    
    for tag_name, (main_cat, sub_cat, confidence, reasoning) in FINAL_HIGH_FREQ_RULES.items():
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
                    classification_source = 'final_high_freq_manual',
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
    
    # 檢查剩餘
    remaining = cursor.execute('''
        SELECT COUNT(*) FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 100000
    ''').fetchone()[0]
    
    print(f"\n{'='*80}")
    print(f"最終高頻標籤處理結果")
    print(f"{'='*80}")
    print(f"成功更新標籤: {updated_count} 個")
    print(f"影響使用次數: {total_usage:,} 次")
    print(f"剩餘高頻未分類 (>=100K): {remaining} 個")
    print(f"整體覆蓋率: {coverage:.2f}%")
    
    conn.close()
    
    return updated_count, total_usage, coverage

if __name__ == "__main__":
    apply_final_high_freq_rules()

