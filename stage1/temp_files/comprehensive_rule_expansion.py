#!/usr/bin/env python3
"""
全面規則擴展 - 處理所有可識別的模式
"""

import sqlite3
import re
from collections import defaultdict

def comprehensive_pattern_analysis():
    """全面分析未分類標籤的所有模式"""
    conn = sqlite3.connect('output/tags.db')
    
    # 獲取所有未分類標籤 (1K+ 使用)
    unclassified = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 AND main_category IS NULL
        AND post_count >= 1000
        ORDER BY post_count DESC
    ''').fetchall()
    
    print(f"分析 {len(unclassified)} 個未分類標籤...")
    
    # 擴展模式分析
    patterns = defaultdict(list)
    
    for name, usage in unclassified:
        name_lower = name.lower()
        
        # 1. 顏色模式 (擴展)
        colors = ['red', 'blue', 'green', 'black', 'white', 'yellow', 'pink', 'purple', 
                 'orange', 'brown', 'gray', 'grey', 'silver', 'gold', 'rainbow', 'cyan',
                 'magenta', 'beige', 'tan', 'navy', 'maroon', 'crimson', 'scarlet']
        if any(color in name_lower for color in colors):
            patterns['colors'].append((name, usage))
        
        # 2. 數字模式
        if re.search(r'\d+', name):
            patterns['numbers'].append((name, usage))
        
        # 3. 服裝模式 (擴展)
        clothing_words = ['shirt', 'dress', 'skirt', 'pant', 'shoe', 'hat', 'glove', 'sock',
                         'jacket', 'coat', 'uniform', 'kimono', 'armor', 'swimsuit', 'bikini',
                         'boots', 'sleeves', 'underwear', 'panties', 'bra', 'lingerie', 'robe',
                         'suit', 'vest', 'apron', 'leotard', 'corset', 'blouse', 'cardigan',
                         'sweater', 'hoodie', 'pajamas', 'nightgown', 'camisole', 'tank_top',
                         'crop_top', 'tube_top', 'halter_top', 'strapless', 'off_shoulder']
        if any(word in name_lower for word in clothing_words):
            patterns['clothing'].append((name, usage))
        
        # 4. 身體部位模式 (擴展)
        body_parts = ['eye', 'hair', 'breast', 'leg', 'arm', 'hand', 'foot', 'head', 'face',
                     'mouth', 'nose', 'ear', 'chest', 'back', 'stomach', 'waist', 'hip',
                     'thigh', 'knee', 'ankle', 'shoulder', 'neck', 'finger', 'toe', 'lip',
                     'tongue', 'teeth', 'nail', 'eyebrow', 'eyelash', 'cheek', 'chin',
                     'forehead', 'temple', 'jaw', 'collarbone', 'navel', 'belly']
        if any(part in name_lower for part in body_parts):
            patterns['body_parts'].append((name, usage))
        
        # 5. 動作模式 (擴展)
        action_words = ['hold', 'wear', 'stand', 'sit', 'lie', 'walk', 'run', 'jump', 'dance',
                       'fight', 'fly', 'swim', 'kiss', 'hug', 'touch', 'point', 'wave',
                       'grab', 'pull', 'push', 'lift', 'carry', 'throw', 'catch', 'strike',
                       'kick', 'punch', 'climb', 'crawl', 'bend', 'stretch', 'lean', 'rest']
        if any(word in name_lower for word in action_words):
            patterns['actions'].append((name, usage))
        
        # 6. 形容詞模式 (擴展)
        adjectives = ['cute', 'beautiful', 'sexy', 'hot', 'cool', 'nice', 'pretty', 'lovely',
                     'sweet', 'charming', 'elegant', 'adorable', 'gorgeous', 'stunning',
                     'attractive', 'handsome', 'cute', 'kawaii', 'moe', 'sexy', 'hot']
        if any(adj in name_lower for adj in adjectives):
            patterns['adjectives'].append((name, usage))
        
        # 7. 大小模式
        size_words = ['large', 'small', 'big', 'tiny', 'huge', 'mini', 'giant', 'massive',
                     'enormous', 'micro', 'macro', 'oversized', 'undersized', 'jumbo']
        if any(word in name_lower for word in size_words):
            patterns['sizes'].append((name, usage))
        
        # 8. 材質模式
        materials = ['leather', 'fabric', 'cotton', 'silk', 'wool', 'denim', 'metal', 'wood',
                    'plastic', 'rubber', 'glass', 'ceramic', 'stone', 'crystal', 'fur',
                    'feather', 'chain', 'rope', 'string', 'wire', 'thread']
        if any(mat in name_lower for mat in materials):
            patterns['materials'].append((name, usage))
        
        # 9. 形狀模式
        shapes = ['round', 'square', 'triangular', 'oval', 'circular', 'rectangular',
                 'curved', 'straight', 'zigzag', 'spiral', 'diamond', 'heart', 'star']
        if any(shape in name_lower for shape in shapes):
            patterns['shapes'].append((name, usage))
        
        # 10. 表情模式
        expressions = ['smile', 'grin', 'laugh', 'cry', 'angry', 'sad', 'happy', 'surprised',
                      'confused', 'worried', 'scared', 'excited', 'sleepy', 'tired', 'serious',
                      'playful', 'innocent', 'seductive', 'mysterious', 'determined']
        if any(expr in name_lower for expr in expressions):
            patterns['expressions'].append((name, usage))
    
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

def generate_comprehensive_rules(patterns):
    """基於全面模式生成規則"""
    rules = {}
    
    # 顏色規則 (降低閾值到 10K)
    for name, usage in patterns.get('colors', []):
        if usage >= 10000:
            rules[name] = 'CHARACTER_RELATED/COLORS'
    
    # 服裝規則 (降低閾值到 10K)
    for name, usage in patterns.get('clothing', []):
        if usage >= 10000:
            rules[name] = 'CHARACTER_RELATED/CLOTHING'
    
    # 身體部位規則 (降低閾值到 10K)
    for name, usage in patterns.get('body_parts', []):
        if usage >= 10000:
            rules[name] = 'CHARACTER_RELATED/BODY_PARTS'
    
    # 動作規則 (降低閾值到 10K)
    for name, usage in patterns.get('actions', []):
        if usage >= 10000:
            rules[name] = 'ACTION_POSE/GESTURE'
    
    # 形容詞規則 (降低閾值到 5K)
    for name, usage in patterns.get('adjectives', []):
        if usage >= 5000:
            rules[name] = 'THEME_CONCEPT/CONCEPT'
    
    # 大小規則 (降低閾值到 5K)
    for name, usage in patterns.get('sizes', []):
        if usage >= 5000:
            rules[name] = 'CHARACTER_RELATED/BODY_PARTS'
    
    # 材質規則 (降低閾值到 5K)
    for name, usage in patterns.get('materials', []):
        if usage >= 5000:
            rules[name] = 'OBJECTS/MATERIALS'
    
    # 形狀規則 (降低閾值到 5K)
    for name, usage in patterns.get('shapes', []):
        if usage >= 5000:
            rules[name] = 'VISUAL_EFFECTS/SHAPES'
    
    # 表情規則 (降低閾值到 5K)
    for name, usage in patterns.get('expressions', []):
        if usage >= 5000:
            rules[name] = 'ACTION_POSE/EXPRESSION'
    
    return rules

def apply_comprehensive_rules():
    """應用全面規則"""
    print("="*80)
    print("全面規則擴展分析")
    print("="*80)
    
    # 分析模式
    patterns = comprehensive_pattern_analysis()
    
    # 生成規則
    rules = generate_comprehensive_rules(patterns)
    
    print(f"\n生成的規則數量: {len(rules)}")
    
    if not rules:
        print("沒有找到適合的規則模式")
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
                SET main_category = ?, sub_category = ?, classification_source = 'comprehensive_rule_expansion'
                WHERE name = ? AND danbooru_cat = 0 AND main_category IS NULL
            ''', (main_cat, sub_cat, tag_name))
            
            updated_count += 1
            total_usage += post_count
            print(f"[COMP] {tag_name:30} -> {main_cat}/{sub_cat or 'N/A':20} ({post_count:,} 次)")
    
    conn.commit()
    
    # 統計結果
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    print(f"\n全面規則擴展結果:")
    print(f"更新標籤: {updated_count} 個")
    print(f"影響使用次數: {total_usage:,} 次")
    print(f"整體覆蓋率: {coverage:.2f}%")
    
    conn.close()

if __name__ == "__main__":
    apply_comprehensive_rules()
