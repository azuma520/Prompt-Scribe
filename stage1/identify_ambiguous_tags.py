#!/usr/bin/env python3
"""
識別模糊分類標籤 (Classification Hierarchy Phase 2)
找出具有多重屬性、可能需要次要分類的標籤
"""

import sqlite3
from collections import defaultdict

def identify_ambiguous_by_confidence():
    """基於信心度識別模糊標籤"""
    conn = sqlite3.connect('output/tags.db')
    
    # 找出低信心度標籤（可能表示分類困難）
    low_confidence = conn.execute('''
        SELECT name, main_category, sub_category, 
               classification_confidence, post_count, classification_reasoning
        FROM tags_final
        WHERE classification_confidence IS NOT NULL
        AND classification_confidence < 0.85
        ORDER BY post_count DESC
        LIMIT 50
    ''').fetchall()
    
    print("="*80)
    print("低信心度標籤分析 (<0.85)")
    print("="*80)
    print(f"找到 {len(low_confidence)} 個低信心度標籤\n")
    
    for i, (name, main_cat, sub_cat, conf, usage, reasoning) in enumerate(low_confidence, 1):
        print(f"{i:2}. {name:30} -> {main_cat}/{sub_cat or 'N/A':20}")
        print(f"    信心度: {conf:.3f}, 使用: {usage:,} 次")
        print(f"    理由: {reasoning}")
        print()
    
    conn.close()
    return low_confidence

def identify_ambiguous_by_pattern():
    """基於模式識別可能的多屬性標籤"""
    conn = sqlite3.connect('output/tags.db')
    
    # 模式 1: 顏色 + 物品（最常見的多屬性）
    color_item_tags = conn.execute('''
        SELECT name, main_category, sub_category, post_count
        FROM tags_final
        WHERE main_category IS NOT NULL
        AND (
            name LIKE '%_dress' OR name LIKE '%_shirt' OR name LIKE '%_skirt' OR
            name LIKE '%_pants' OR name LIKE '%_eyes' OR name LIKE '%_hair' OR
            name LIKE 'red_%' OR name LIKE 'blue_%' OR name LIKE 'green_%' OR
            name LIKE 'black_%' OR name LIKE 'white_%' OR name LIKE 'pink_%'
        )
        AND post_count >= 10000
        ORDER BY post_count DESC
        LIMIT 30
    ''').fetchall()
    
    print("="*80)
    print("顏色 + 物品組合標籤 (候選多屬性)")
    print("="*80)
    print(f"找到 {len(color_item_tags)} 個標籤\n")
    
    for i, (name, main_cat, sub_cat, usage) in enumerate(color_item_tags, 1):
        print(f"{i:2}. {name:30} -> {main_cat}/{sub_cat or 'N/A':20} ({usage:,} 次)")
    
    # 模式 2: 動作 + 方向（可能涉及構圖）
    action_direction_tags = conn.execute('''
        SELECT name, main_category, sub_category, post_count
        FROM tags_final
        WHERE main_category IS NOT NULL
        AND (
            name LIKE '%_forward' OR name LIKE '%_back' OR name LIKE '%_up' OR
            name LIKE '%_down' OR name LIKE 'leaning_%' OR name LIKE 'looking_%'
        )
        AND post_count >= 10000
        ORDER BY post_count DESC
        LIMIT 20
    ''').fetchall()
    
    print(f"\n{'='*80}")
    print("動作 + 方向組合標籤 (候選構圖相關)")
    print("="*80)
    print(f"找到 {len(action_direction_tags)} 個標籤\n")
    
    for i, (name, main_cat, sub_cat, usage) in enumerate(action_direction_tags, 1):
        print(f"{i:2}. {name:30} -> {main_cat}/{sub_cat or 'N/A':20} ({usage:,} 次)")
    
    # 模式 3: 角色類型標籤（可能涉及服裝+概念）
    character_type_tags = conn.execute('''
        SELECT name, main_category, sub_category, post_count
        FROM tags_final
        WHERE main_category IS NOT NULL
        AND name IN (
            'knight', 'maid', 'nurse', 'witch', 'priest', 'monk',
            'warrior', 'soldier', 'pirate', 'ninja', 'samurai',
            'chef', 'butler', 'miko', 'idol', 'dancer'
        )
        ORDER BY post_count DESC
    ''').fetchall()
    
    print(f"\n{'='*80}")
    print("角色類型標籤 (候選多屬性)")
    print("="*80)
    print(f"找到 {len(character_type_tags)} 個標籤\n")
    
    for i, (name, main_cat, sub_cat, usage) in enumerate(character_type_tags, 1):
        print(f"{i:2}. {name:30} -> {main_cat}/{sub_cat or 'N/A':20} ({usage:,} 次)")
    
    conn.close()
    
    return {
        'color_item': color_item_tags,
        'action_direction': action_direction_tags,
        'character_type': character_type_tags
    }

def mark_ambiguous_tags(tag_list, note=""):
    """標記模糊分類標籤"""
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    marked_count = 0
    for tag_name in tag_list:
        cursor.execute('''
            UPDATE tags_final
            SET is_ambiguous = 1,
                classification_note = ?
            WHERE name = ?
            AND main_category IS NOT NULL
        ''', (note, tag_name))
        
        if cursor.rowcount > 0:
            marked_count += 1
    
    conn.commit()
    conn.close()
    
    return marked_count

def main():
    """主函數"""
    print("\n" + "="*80)
    print("識別模糊分類標籤 - Phase 2")
    print("="*80)
    
    # 識別所有候選
    low_confidence = identify_ambiguous_by_confidence()
    candidates = identify_ambiguous_by_pattern()
    
    # 顯示摘要
    print(f"\n{'='*80}")
    print("識別摘要")
    print("="*80)
    print(f"低信心度標籤: {len(low_confidence)} 個")
    print(f"顏色+物品組合: {len(candidates['color_item'])} 個")
    print(f"動作+方向組合: {len(candidates['action_direction'])} 個")
    print(f"角色類型標籤: {len(candidates['character_type'])} 個")
    
    total_candidates = (len(low_confidence) + 
                       len(candidates['color_item']) + 
                       len(candidates['action_direction']) + 
                       len(candidates['character_type']))
    
    print(f"\n總候選數: {total_candidates} 個")
    print(f"\n這些標籤是次要分類的優先候選對象")
    print(f"建議在 Phase 3 中為它們添加次要分類")

if __name__ == "__main__":
    main()

