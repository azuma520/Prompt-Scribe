#!/usr/bin/env python3
"""
擴展符號標籤規則
處理剩餘的特殊符號和表情標籤
"""

import sqlite3

# 擴展的符號標籤規則庫
EXTENDED_SYMBOL_RULES = {
    # 擴展表情符號
    '._.': ('ACTION_POSE', 'EXPRESSION', 0.85, '無奈/無語的表情'),
    ':x': ('ACTION_POSE', 'EXPRESSION', 0.90, '閉嘴/封口的表情'),
    '>:(': ('ACTION_POSE', 'EXPRESSION', 0.92, '生氣的表情'),
    '>_o': ('ACTION_POSE', 'EXPRESSION', 0.88, '困惑/疑惑的表情'),
    'u_u': ('ACTION_POSE', 'EXPRESSION', 0.90, '閉眼平靜的表情'),
    ';3': ('ACTION_POSE', 'EXPRESSION', 0.88, '眨眼貓嘴表情'),
    ';q': ('ACTION_POSE', 'EXPRESSION', 0.85, '眨眼吐舌表情'),
    ':i': ('ACTION_POSE', 'EXPRESSION', 0.85, '特殊表情符號'),
    '69': ('ADULT_CONTENT', 'SEXUAL', 0.95, '特定性行為姿勢'),
    
    # 手勢符號
    '\\||/': ('ACTION_POSE', 'GESTURE', 0.90, '舉雙手的手勢符號'),
    
    # 數字和其他
    '6+others': ('CHARACTER_RELATED', 'CHARACTER_COUNT', 0.95, '6人以上的角色數量'),
    '2015': ('TECHNICAL', 'METADATA', 0.90, '年份標記'),
    '2019': ('TECHNICAL', 'METADATA', 0.90, '年份標記'),
    '2016': ('TECHNICAL', 'METADATA', 0.90, '年份標記'),
    '2017': ('TECHNICAL', 'METADATA', 0.90, '年份標記'),
    '2018': ('TECHNICAL', 'METADATA', 0.90, '年份標記'),
    
    # 特殊標記
    ':>=': ('TECHNICAL', 'METADATA', 0.75, '特殊標記符號'),
    '??': ('ACTION_POSE', 'EXPRESSION', 0.85, '疑問/困惑標記'),
}

def apply_extended_symbol_rules():
    """應用擴展符號規則"""
    print("="*80)
    print("擴展符號標籤規則應用")
    print("="*80)
    
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    updated_count = 0
    total_usage = 0
    
    for tag_name, (main_cat, sub_cat, confidence, reasoning) in EXTENDED_SYMBOL_RULES.items():
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
                    classification_source = 'extended_symbol_rules',
                    classification_confidence = ?,
                    classification_reasoning = ?,
                    classification_timestamp = datetime('now')
                WHERE name = ? AND danbooru_cat = 0 AND main_category IS NULL
            ''', (main_cat, sub_cat, confidence, reasoning, tag_name))
            
            if cursor.rowcount > 0:
                updated_count += 1
                total_usage += post_count
                print(f"[OK] {tag_name:20} -> {main_cat}/{sub_cat or 'N/A':20} ({post_count:,} 次)")
    
    conn.commit()
    
    # 統計結果
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    print(f"\n{'='*80}")
    print(f"擴展符號規則應用結果")
    print(f"{'='*80}")
    print(f"成功更新標籤: {updated_count} 個")
    print(f"影響使用次數: {total_usage:,} 次")
    print(f"整體覆蓋率: {coverage:.2f}%")
    print(f"節省 LLM 成本: ${updated_count * 0.000005:.6f}")
    
    conn.close()
    
    return updated_count, total_usage

if __name__ == "__main__":
    apply_extended_symbol_rules()

