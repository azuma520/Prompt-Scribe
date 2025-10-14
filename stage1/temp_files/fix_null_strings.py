#!/usr/bin/env python3
"""
修復 NULL 字符串問題
"""

import sqlite3

def fix_null_strings():
    """修復 NULL 字符串"""
    print("開始修復 NULL 字符串...")
    
    conn = sqlite3.connect("output/tags.db")
    cursor = conn.cursor()
    
    # 獲取所有 NULL 字符串標籤
    cursor.execute("""
        SELECT name, main_category, post_count
        FROM tags_final
        WHERE sub_category = 'null'
        ORDER BY post_count DESC
    """)
    
    null_tags = cursor.fetchall()
    print(f"找到 {len(null_tags)} 個 NULL 字符串標籤")
    
    # 推斷邏輯
    inference_rules = {
        'ART_STYLE': {
            'tokusatsu': 'TOKUSATSU',
            'inktober': 'INKTOBER', 
            'itasha': 'ITASHA',
            'hip_hop': 'HIP_HOP'
        },
        'CHARACTER_COUNT': {
            'absolutely_everyone': 'CROWD',
            'four_of_a_kind_(touhou)': 'FOUR',
            'quintuplets': 'FIVE',
            'mixed_maids': 'MULTIPLE',
            'multiple_fusions': 'MULTIPLE'
        },
        'BODY_PARTS': {
            'hollow_mouth': 'MOUTH'
        }
    }
    
    fixed_count = 0
    
    try:
        for name, main_category, count in null_tags:
            # 根據名稱推斷子分類
            new_sub_category = None
            
            if main_category in inference_rules:
                for keyword, sub_cat in inference_rules[main_category].items():
                    if keyword in name.lower():
                        new_sub_category = sub_cat
                        break
            
            # 如果沒有匹配，使用預設值
            if not new_sub_category:
                if main_category == 'ART_STYLE':
                    new_sub_category = 'STYLE'
                elif main_category == 'CHARACTER_COUNT':
                    new_sub_category = 'COUNT'
                elif main_category == 'BODY_PARTS':
                    new_sub_category = 'GENERAL'
                else:
                    new_sub_category = 'GENERAL'
            
            # 更新資料庫
            cursor.execute("""
                UPDATE tags_final
                SET sub_category = ?,
                    classification_source = 'quality_issue_fix',
                    classification_confidence = COALESCE(classification_confidence, 0.80)
                WHERE name = ?
            """, (new_sub_category, name))
            
            print(f"修復: {name:40} -> {main_category}/{new_sub_category}")
            fixed_count += 1
        
        conn.commit()
        print(f"\n成功修復 {fixed_count} 個 NULL 字符串")
        
    except Exception as e:
        print(f"修復失敗: {e}")
        conn.rollback()
        fixed_count = 0
    finally:
        conn.close()
    
    return fixed_count

if __name__ == "__main__":
    fix_null_strings()
