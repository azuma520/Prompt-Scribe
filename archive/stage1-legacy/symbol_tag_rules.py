#!/usr/bin/env python3
"""
符號標籤專用分類規則
處理表情符號、特殊符號等難以通過 LLM 理解的標籤
"""

import sqlite3

# 符號標籤規則庫
SYMBOL_TAG_RULES = {
    # 表情符號 - 面部表情
    ':>': ('ACTION_POSE', 'EXPRESSION', 0.95, '害羞/調皮的表情符號'),
    ':d': ('ACTION_POSE', 'EXPRESSION', 0.95, '開心大笑的表情'),
    ':D': ('ACTION_POSE', 'EXPRESSION', 0.95, '開心大笑的表情'),
    ':o': ('ACTION_POSE', 'EXPRESSION', 0.95, '驚訝的表情'),
    ':O': ('ACTION_POSE', 'EXPRESSION', 0.95, '驚訝的表情'),
    ':p': ('ACTION_POSE', 'EXPRESSION', 0.95, '吐舌頭的表情'),
    ':P': ('ACTION_POSE', 'EXPRESSION', 0.95, '吐舌頭的表情'),
    ':q': ('ACTION_POSE', 'EXPRESSION', 0.95, '吐舌頭的表情'),
    ':t': ('ACTION_POSE', 'EXPRESSION', 0.90, '不滿的表情'),
    ':|': ('ACTION_POSE', 'EXPRESSION', 0.95, '面無表情/冷淡'),
    ':3': ('ACTION_POSE', 'EXPRESSION', 0.95, '貓嘴表情'),
    ':<': ('ACTION_POSE', 'EXPRESSION', 0.90, '難過的表情'),
    ';)': ('ACTION_POSE', 'EXPRESSION', 0.95, '眨眼表情'),
    ';o': ('ACTION_POSE', 'EXPRESSION', 0.90, '眨眼驚訝'),
    ';p': ('ACTION_POSE', 'EXPRESSION', 0.90, '眨眼吐舌'),
    ';|': ('ACTION_POSE', 'EXPRESSION', 0.85, '眨眼面無表情'),
    '>_<': ('ACTION_POSE', 'EXPRESSION', 0.95, '痛苦/尷尬的表情'),
    '^_^': ('ACTION_POSE', 'EXPRESSION', 0.95, '開心閉眼笑'),
    'x_x': ('ACTION_POSE', 'EXPRESSION', 0.95, '暈倒/死亡的表情'),
    '0_0': ('ACTION_POSE', 'EXPRESSION', 0.95, '驚訝/呆滯的表情'),
    '@_@': ('ACTION_POSE', 'EXPRESSION', 0.95, '眼冒金星/暈眩'),
    '=_=': ('ACTION_POSE', 'EXPRESSION', 0.95, '無奈/疲倦的表情'),
    'o_o': ('ACTION_POSE', 'EXPRESSION', 0.95, '驚訝的表情'),
    'o3o': ('ACTION_POSE', 'EXPRESSION', 0.90, '親親的表情'),
    'd:': ('ACTION_POSE', 'EXPRESSION', 0.90, '開心的表情'),
    
    # 手勢符號
    '\\m/': ('ACTION_POSE', 'GESTURE', 0.95, '搖滾手勢'),
    
    # 驚嘆與強調
    '!': ('ACTION_POSE', 'EXPRESSION', 0.90, '驚訝/發現'),
    '!!': ('ACTION_POSE', 'EXPRESSION', 0.90, '非常驚訝'),
    '!?': ('ACTION_POSE', 'EXPRESSION', 0.90, '困惑驚訝'),
    '?': ('ACTION_POSE', 'EXPRESSION', 0.85, '疑問'),
    '...': ('TECHNICAL', 'METADATA', 0.85, '省略符號/沉默'),
    '+++': ('TECHNICAL', 'METADATA', 0.80, '強調符號'),
    
    # 特殊標記符號
    '|_|': ('TECHNICAL', 'METADATA', 0.90, '特殊標記符號'),
    
    # 數字比例標記（技術標籤）
    '3:': ('TECHNICAL', 'METADATA', 0.85, '寬高比標記'),
    '16:9': ('TECHNICAL', 'METADATA', 0.90, '寬高比 16:9'),
    '4:3': ('TECHNICAL', 'METADATA', 0.90, '寬高比 4:3'),
    
    # 字母符號（通常是縮寫或音效）
    'w': ('ACTION_POSE', 'EXPRESSION', 0.70, '日文笑聲 (warau)'),
    'm': ('ACTION_POSE', 'GESTURE', 0.60, '可能是手勢或縮寫'),
}

def apply_symbol_rules():
    """應用符號標籤規則"""
    print("="*80)
    print("符號標籤專用規則應用")
    print("="*80)
    
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    updated_count = 0
    total_usage = 0
    
    for tag_name, (main_cat, sub_cat, confidence, reasoning) in SYMBOL_TAG_RULES.items():
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
                    classification_source = 'symbol_tag_rules',
                    classification_confidence = ?,
                    classification_reasoning = ?,
                    classification_timestamp = datetime('now')
                WHERE name = ? AND danbooru_cat = 0 AND main_category IS NULL
            ''', (main_cat, sub_cat, confidence, reasoning, tag_name))
            
            if cursor.rowcount > 0:
                updated_count += 1
                total_usage += post_count
                print(f"[OK] {tag_name:20} -> {main_cat}/{sub_cat or 'N/A':20} ({post_count:,} 次, 信心度: {confidence:.2f})")
        else:
            # 標籤不存在或已分類
            pass
    
    conn.commit()
    
    # 統計結果
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    print(f"\n{'='*80}")
    print(f"符號標籤規則應用結果")
    print(f"{'='*80}")
    print(f"成功更新標籤: {updated_count} 個")
    print(f"影響使用次數: {total_usage:,} 次")
    print(f"整體覆蓋率: {coverage:.2f}%")
    
    conn.close()
    
    return updated_count, total_usage

if __name__ == "__main__":
    apply_symbol_rules()

