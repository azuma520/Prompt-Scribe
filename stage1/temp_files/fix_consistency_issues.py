#!/usr/bin/env python3
"""
修復分類一致性問題
"""

import sqlite3

def fix_null_strings():
    """修復 'null' 字符串為 NULL"""
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    print("="*80)
    print("修復 'null' 字符串問題")
    print("="*80)
    
    # 修復主分類
    cursor.execute('''
        UPDATE tags_final
        SET main_category = NULL
        WHERE main_category = 'null'
    ''')
    main_fixed = cursor.rowcount
    print(f"[OK] 修復主分類 'null': {main_fixed} 個")
    
    # 修復副分類
    cursor.execute('''
        UPDATE tags_final
        SET sub_category = NULL
        WHERE sub_category = 'null' OR sub_category = 'N/A'
    ''')
    sub_fixed = cursor.rowcount
    print(f"[OK] 修復副分類 'null'/'N/A': {sub_fixed} 個")
    
    conn.commit()
    conn.close()
    
    return main_fixed, sub_fixed

def fix_eye_color_consistency():
    """修復眼睛顏色標籤的一致性"""
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    print(f"\n{'='*80}")
    print("修復眼睛顏色標籤一致性")
    print("="*80)
    
    # 所有 *_eyes 標籤應該歸類為 CHARACTER_RELATED/BODY_PARTS
    cursor.execute('''
        UPDATE tags_final
        SET main_category = 'CHARACTER_RELATED',
            sub_category = 'BODY_PARTS',
            classification_note = '眼睛顏色統一歸類為身體部位'
        WHERE name LIKE '%_eyes'
        AND main_category IS NOT NULL
        AND (sub_category IS NULL OR sub_category != 'BODY_PARTS')
    ''')
    
    eye_fixed = cursor.rowcount
    print(f"[OK] 修復眼睛標籤: {eye_fixed} 個")
    
    conn.commit()
    conn.close()
    
    return eye_fixed

def fix_hair_color_consistency():
    """修復頭髮顏色標籤的一致性"""
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    print(f"\n{'='*80}")
    print("修復頭髮顏色標籤一致性")
    print("="*80)
    
    # 所有 *_hair 標籤應該歸類為 CHARACTER_RELATED/HAIR
    cursor.execute('''
        UPDATE tags_final
        SET main_category = 'CHARACTER_RELATED',
            sub_category = 'HAIR',
            classification_note = '頭髮標籤統一歸類為HAIR'
        WHERE name LIKE '%_hair'
        AND main_category IS NOT NULL
        AND sub_category != 'HAIR'
    ''')
    
    hair_fixed = cursor.rowcount
    print(f"[OK] 修復頭髮標籤: {hair_fixed} 個")
    
    # 特別修復 pink_hair
    cursor.execute('''
        SELECT name, main_category, sub_category FROM tags_final
        WHERE name = 'pink_hair'
    ''')
    result = cursor.fetchone()
    if result:
        print(f"  pink_hair 當前分類: {result[1]}/{result[2]}")
    
    conn.commit()
    conn.close()
    
    return hair_fixed

def fix_low_confidence_tags():
    """審查並修復低信心度標籤"""
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    print(f"\n{'='*80}")
    print("低信心度標籤人工修正")
    print("="*80)
    
    # 'w' 標籤 - 日文笑聲
    cursor.execute('''
        UPDATE tags_final
        SET main_category = 'ACTION_POSE',
            sub_category = 'EXPRESSION',
            classification_confidence = 0.85,
            classification_reasoning = '日文笑聲縮寫 (warau)',
            classification_source = 'manual_fix'
        WHERE name = 'w'
        AND main_category IS NULL OR main_category = 'null'
    ''')
    w_fixed = cursor.rowcount
    
    if w_fixed > 0:
        print(f"[OK] 修復 'w' 標籤")
    
    # 其他低信心度標籤標記為需要審查
    cursor.execute('''
        UPDATE tags_final
        SET is_ambiguous = 1,
            classification_note = '低信心度標籤，需要人工審查'
        WHERE classification_confidence < 0.75
        AND is_ambiguous = 0
    ''')
    
    marked = cursor.rowcount
    print(f"[OK] 標記低信心度標籤: {marked} 個")
    
    conn.commit()
    conn.close()
    
    return w_fixed + marked

def main():
    """執行所有修復"""
    print("開始修復分類一致性問題...\n")
    
    # 1. 修復 null 字符串
    main_fixed, sub_fixed = fix_null_strings()
    
    # 2. 修復眼睛標籤
    eye_fixed = fix_eye_color_consistency()
    
    # 3. 修復頭髮標籤
    hair_fixed = fix_hair_color_consistency()
    
    # 4. 修復低信心度標籤
    low_conf_fixed = fix_low_confidence_tags()
    
    # 最終統計
    conn = sqlite3.connect('output/tags.db')
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    ambiguous_count = conn.execute('SELECT COUNT(*) FROM tags_final WHERE is_ambiguous = 1').fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*80}")
    print("修復總結")
    print("="*80)
    print(f"修復 'null' 主分類: {main_fixed} 個")
    print(f"修復 'null' 副分類: {sub_fixed} 個")
    print(f"修復眼睛標籤: {eye_fixed} 個")
    print(f"修復頭髮標籤: {hair_fixed} 個")
    print(f"處理低信心度標籤: {low_conf_fixed} 個")
    print(f"\n當前覆蓋率: {coverage:.2f}%")
    print(f"模糊標籤數: {ambiguous_count} 個")
    print("="*80)

if __name__ == "__main__":
    main()

