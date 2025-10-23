#!/usr/bin/env python3
"""
進階規則擴展 - 基於模式匹配的智能規則生成
"""

import sqlite3
import re
from collections import defaultdict

def analyze_patterns():
    """分析未分類標籤的模式"""
    conn = sqlite3.connect('output/tags.db')
    
    # 獲取高頻未分類標籤 (10K+ 使用)
    unclassified = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 AND main_category IS NULL
        AND post_count >= 10000
        ORDER BY post_count DESC
    ''').fetchall()
    
    print(f"分析 {len(unclassified)} 個高頻未分類標籤...")
    
    # 模式分析
    patterns = defaultdict(list)
    
    for name, usage in unclassified:
        # 顏色模式
        colors = ['red', 'blue', 'green', 'black', 'white', 'yellow', 'pink', 'purple', 
                 'orange', 'brown', 'gray', 'grey', 'silver', 'gold', 'rainbow']
        if any(color in name.lower() for color in colors):
            patterns['colors'].append((name, usage))
        
        # 數字模式
        if re.search(r'\d+', name):
            patterns['numbers'].append((name, usage))
        
        # 服裝模式
        clothing_words = ['shirt', 'dress', 'skirt', 'pant', 'shoe', 'hat', 'glove', 'sock',
                         'jacket', 'coat', 'uniform', 'kimono', 'armor', 'swimsuit', 'bikini',
                         'boots', 'sleeves', 'underwear', 'panties', 'bra', 'lingerie']
        if any(word in name.lower() for word in clothing_words):
            patterns['clothing'].append((name, usage))
        
        # 身體部位模式
        body_parts = ['eye', 'hair', 'breast', 'leg', 'arm', 'hand', 'foot', 'head', 'face',
                     'mouth', 'nose', 'ear', 'chest', 'back', 'stomach', 'waist', 'hip',
                     'thigh', 'knee', 'ankle', 'shoulder', 'neck', 'finger', 'toe']
        if any(part in name.lower() for part in body_parts):
            patterns['body_parts'].append((name, usage))
        
        # 動作模式
        action_words = ['hold', 'wear', 'stand', 'sit', 'lie', 'walk', 'run', 'jump', 'dance',
                       'fight', 'fly', 'swim', 'kiss', 'hug', 'touch', 'point', 'wave']
        if any(word in name.lower() for word in action_words):
            patterns['actions'].append((name, usage))
        
        # 形容詞模式
        adjectives = ['cute', 'beautiful', 'sexy', 'hot', 'cool', 'nice', 'pretty', 'lovely',
                     'sweet', 'charming', 'elegant', 'cute', 'adorable']
        if any(adj in name.lower() for adj in adjectives):
            patterns['adjectives'].append((name, usage))
        
        # 大小模式
        size_words = ['large', 'small', 'big', 'tiny', 'huge', 'mini', 'giant', 'massive']
        if any(word in name.lower() for word in size_words):
            patterns['sizes'].append((name, usage))
    
    # 顯示分析結果
    for pattern_name, matches in patterns.items():
        if matches:
            print(f"\n{pattern_name.upper()} 模式 ({len(matches)} 個):")
            total_usage = sum(usage for _, usage in matches)
            print(f"  總使用次數: {total_usage:,}")
            
            # 顯示前10個
            for name, usage in matches[:10]:
                print(f"    {name:30} {usage:10,} 次")
    
    conn.close()
    return patterns

def generate_rules_from_patterns(patterns):
    """基於模式生成規則"""
    rules = {}
    
    # 顏色規則
    for name, usage in patterns.get('colors', []):
        if usage >= 50000:  # 只處理高頻
            rules[name] = 'CHARACTER_RELATED/COLORS'
    
    # 服裝規則
    for name, usage in patterns.get('clothing', []):
        if usage >= 50000:
            rules[name] = 'CHARACTER_RELATED/CLOTHING'
    
    # 身體部位規則
    for name, usage in patterns.get('body_parts', []):
        if usage >= 50000:
            rules[name] = 'CHARACTER_RELATED/BODY_PARTS'
    
    # 動作規則
    for name, usage in patterns.get('actions', []):
        if usage >= 50000:
            rules[name] = 'ACTION_POSE/GESTURE'
    
    return rules

def apply_advanced_rules():
    """應用進階規則"""
    print("="*80)
    print("進階規則擴展分析")
    print("="*80)
    
    # 分析模式
    patterns = analyze_patterns()
    
    # 生成規則
    rules = generate_rules_from_patterns(patterns)
    
    print(f"\n生成的規則數量: {len(rules)}")
    
    if not rules:
        print("沒有找到適合的高頻規則模式")
        return
    
    # 應用規則
    conn = sqlite3.connect('output/tags.db')
    
    updated_count = 0
    total_usage = 0
    
    for tag_name, classification in rules.items():
        # 檢查標籤是否存在且未分類
        result = conn.execute('''
            SELECT post_count FROM tags_final 
            WHERE name = ? AND danbooru_cat = 0 AND main_category IS NULL
        ''', (tag_name,)).fetchone()
        
        if result:
            post_count = result[0]
            
            # 解析主分類和副分類
            if '/' in classification:
                main_cat, sub_cat = classification.split('/')
            else:
                main_cat = classification
                sub_cat = None
            
            # 更新資料庫
            conn.execute('''
                UPDATE tags_final 
                SET main_category = ?, sub_category = ?, classification_source = 'advanced_rule_expansion'
                WHERE name = ? AND danbooru_cat = 0 AND main_category IS NULL
            ''', (main_cat, sub_cat, tag_name))
            
            updated_count += 1
            total_usage += post_count
            print(f"[ADV] {tag_name:30} -> {main_cat}/{sub_cat or 'N/A':20} ({post_count:,} 次)")
    
    conn.commit()
    
    # 統計結果
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    print(f"\n進階規則擴展結果:")
    print(f"更新標籤: {updated_count} 個")
    print(f"影響使用次數: {total_usage:,} 次")
    print(f"整體覆蓋率: {coverage:.2f}%")
    
    conn.close()

if __name__ == "__main__":
    apply_advanced_rules()
