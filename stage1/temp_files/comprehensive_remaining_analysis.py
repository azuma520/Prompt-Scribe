#!/usr/bin/env python3
"""
全面分析所有剩餘未分類標籤的特徵類型
包括中頻 (10K-100K) 和低頻 (1K-10K)
"""

import sqlite3
from collections import defaultdict
import re

def analyze_all_remaining_tags():
    """分析所有剩餘未分類標籤"""
    conn = sqlite3.connect('output/tags.db')
    
    # 獲取所有剩餘未分類標籤
    all_remaining = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        ORDER BY post_count DESC
    ''').fetchall()
    
    print("="*80)
    print("全面剩餘標籤特徵分析")
    print("="*80)
    print(f"總剩餘未分類標籤: {len(all_remaining):,} 個")
    print(f"總使用次數: {sum(usage for _, usage in all_remaining):,} 次")
    
    # 按頻率分段
    freq_segments = {
        '中頻 (10K-100K)': (10000, 100000),
        '低頻 (1K-10K)': (1000, 10000),
        '極低頻 (<1K)': (0, 1000),
    }
    
    print(f"\n【頻率分段】")
    print("-"*50)
    
    segment_data = {}
    for seg_name, (min_freq, max_freq) in freq_segments.items():
        tags_in_segment = [
            (name, usage) for name, usage in all_remaining 
            if min_freq <= usage < max_freq
        ]
        count = len(tags_in_segment)
        total_usage = sum(usage for _, usage in tags_in_segment)
        
        segment_data[seg_name] = tags_in_segment
        
        print(f"{seg_name:20} {count:5} 個, {total_usage:12,} 次使用")
    
    # 深度特徵分析
    print(f"\n{'='*80}")
    print("標籤特徵類型分析 (分析前 1000 個高頻)")
    print("="*80)
    
    # 分析前 1000 個（涵蓋大部分價值）
    analysis_sample = all_remaining[:1000]
    
    feature_categories = {
        # 語言和符號類
        '特殊符號/表情': [],
        '日文專有詞彙': [],
        '遊戲特定標籤': [],
        '年份日期': [],
        
        # 內容類
        '服裝配飾': [],
        '身體部位': [],
        '動作行為': [],
        '表情情緒': [],
        
        # 物品類
        '武器道具': [],
        '食物飲料': [],
        '動物生物': [],
        '日常物品': [],
        
        # 場景類
        '室內場景': [],
        '室外環境': [],
        '自然景觀': [],
        
        # 視覺效果類
        '顏色組合': [],
        '圖案花紋': [],
        '視覺特效': [],
        
        # 概念類
        '人物關係': [],
        '主題概念': [],
        '成人內容': [],
        
        # 技術類
        '元數據': [],
        '品質標記': [],
        
        # 其他
        '未分類/複雜': []
    }
    
    for name, usage in analysis_sample:
        name_lower = name.lower()
        categorized = False
        
        # 特殊符號/表情
        if re.search(r'^[^a-z]|[:\(\)><;\|\[\]{}]', name_lower):
            feature_categories['特殊符號/表情'].append((name, usage))
            categorized = True
        
        # 年份
        elif re.match(r'^\d{4}$', name) or re.search(r'20\d{2}', name):
            feature_categories['年份日期'].append((name, usage))
            categorized = True
        
        # 遊戲特定 (帶括號)
        elif '(' in name and ')' in name:
            feature_categories['遊戲特定標籤'].append((name, usage))
            categorized = True
        
        # 日文詞彙
        elif any(jp_word in name_lower for jp_word in [
            'japanese', 'yukata', 'hakama', 'kimono', 'miko', 'geta', 'obi',
            'wa_', 'dougi', 'haori', 'fundoshi', 'sarashi', 'tabi', 'zouri'
        ]):
            feature_categories['日文專有詞彙'].append((name, usage))
            categorized = True
        
        # 服裝配飾
        elif any(word in name_lower for word in [
            'dress', 'shirt', 'skirt', 'pant', 'jacket', 'coat', 'uniform',
            'hat', 'cap', 'helmet', 'mask', 'glove', 'boot', 'shoe',
            'outfit', 'clothes', 'wear', 'fashion'
        ]):
            feature_categories['服裝配飾'].append((name, usage))
            categorized = True
        
        # 身體部位
        elif any(word in name_lower for word in [
            'eye', 'hair', 'ear', 'nose', 'mouth', 'lip', 'teeth', 'tongue',
            'hand', 'finger', 'arm', 'leg', 'foot', 'toe',
            'chest', 'breast', 'belly', 'waist', 'hip', 'thigh',
            'head', 'face', 'neck', 'shoulder', 'back'
        ]):
            feature_categories['身體部位'].append((name, usage))
            categorized = True
        
        # 動作行為
        elif name_lower.endswith('ing') or any(word in name_lower for word in [
            'hold', 'grab', 'pull', 'push', 'carry', 'lift',
            'stand', 'sit', 'lie', 'kneel', 'lean',
            'walk', 'run', 'jump', 'dance', 'fight'
        ]):
            feature_categories['動作行為'].append((name, usage))
            categorized = True
        
        # 表情情緒
        elif any(word in name_lower for word in [
            'smile', 'laugh', 'cry', 'angry', 'sad', 'happy',
            'surprised', 'scared', 'worried', 'confused',
            'expression', 'emotion', 'mood'
        ]):
            feature_categories['表情情緒'].append((name, usage))
            categorized = True
        
        # 武器道具
        elif any(word in name_lower for word in [
            'sword', 'gun', 'rifle', 'pistol', 'blade', 'knife',
            'spear', 'lance', 'bow', 'arrow', 'axe', 'hammer',
            'weapon', 'shield'
        ]):
            feature_categories['武器道具'].append((name, usage))
            categorized = True
        
        # 食物飲料
        elif any(word in name_lower for word in [
            'food', 'cake', 'bread', 'rice', 'noodle', 'meat',
            'fruit', 'apple', 'orange', 'strawberry',
            'drink', 'tea', 'coffee', 'juice', 'water', 'beer', 'wine'
        ]):
            feature_categories['食物飲料'].append((name, usage))
            categorized = True
        
        # 動物生物
        elif any(word in name_lower for word in [
            'cat', 'dog', 'bird', 'fish', 'dragon', 'wolf',
            'bear', 'fox', 'rabbit', 'tiger', 'lion',
            'animal', 'creature', 'monster'
        ]):
            feature_categories['動物生物'].append((name, usage))
            categorized = True
        
        # 日常物品
        elif any(word in name_lower for word in [
            'book', 'pen', 'paper', 'phone', 'computer',
            'chair', 'table', 'bed', 'door', 'window',
            'cup', 'plate', 'bowl', 'bottle'
        ]):
            feature_categories['日常物品'].append((name, usage))
            categorized = True
        
        # 場景環境
        elif any(word in name_lower for word in [
            'room', 'house', 'building', 'street', 'road',
            'forest', 'mountain', 'ocean', 'sky', 'cloud',
            'indoor', 'outdoor', 'background', 'scenery'
        ]):
            if 'indoor' in name_lower or 'room' in name_lower:
                feature_categories['室內場景'].append((name, usage))
            elif 'outdoor' in name_lower or 'sky' in name_lower:
                feature_categories['室外環境'].append((name, usage))
            else:
                feature_categories['自然景觀'].append((name, usage))
            categorized = True
        
        # 顏色組合
        elif any(color in name_lower for color in [
            'red_', 'blue_', 'green_', 'black_', 'white_',
            'pink_', 'yellow_', 'purple_', 'orange_', 'brown_', 'grey_', 'gray_'
        ]):
            feature_categories['顏色組合'].append((name, usage))
            categorized = True
        
        # 圖案花紋
        elif any(word in name_lower for word in [
            'print', 'pattern', 'stripe', 'dot', 'checkered',
            'plaid', 'floral', 'argyle'
        ]):
            feature_categories['圖案花紋'].append((name, usage))
            categorized = True
        
        # 人物關係
        elif any(word in name_lower for word in [
            'and_', 'with_', 'couple', 'family', 'brother', 'sister',
            'mother', 'father', 'son', 'daughter', 'friend'
        ]):
            feature_categories['人物關係'].append((name, usage))
            categorized = True
        
        # 成人內容
        elif any(word in name_lower for word in [
            'sex', 'nude', 'naked', 'penis', 'vagina', 'breast',
            'nipple', 'ass', 'pussy', 'dick', 'fuck', 'cum'
        ]):
            feature_categories['成人內容'].append((name, usage))
            categorized = True
        
        # 視覺效果
        elif any(word in name_lower for word in [
            'light', 'shadow', 'glow', 'shine', 'sparkle',
            'blur', 'effect', 'lens', 'depth'
        ]):
            feature_categories['視覺特效'].append((name, usage))
            categorized = True
        
        # 概念主題
        elif any(word in name_lower for word in [
            'dream', 'magic', 'fantasy', 'sci-fi', 'horror',
            'cute', 'cool', 'epic', 'concept'
        ]):
            feature_categories['主題概念'].append((name, usage))
            categorized = True
        
        # 元數據
        elif any(word in name_lower for word in [
            'copyright', 'artist', 'source', 'official',
            'fanart', 'comic', 'manga', 'anime'
        ]):
            feature_categories['元數據'].append((name, usage))
            categorized = True
        
        # 未分類
        if not categorized:
            feature_categories['未分類/複雜'].append((name, usage))
    
    # 顯示分析結果
    print(f"\n【特徵類型分布】")
    print("-"*50)
    
    # 按數量排序
    sorted_categories = sorted(
        feature_categories.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    for cat_name, tags in sorted_categories:
        if tags:
            total_usage = sum(usage for _, usage in tags)
            avg_usage = total_usage // len(tags) if tags else 0
            
            print(f"\n{cat_name} ({len(tags)} 個):")
            print(f"  總使用: {total_usage:,} 次, 平均: {avg_usage:,} 次/標籤")
            
            # 顯示前 10 個
            print(f"  前 10 個標籤:")
            for i, (name, usage) in enumerate(tags[:10], 1):
                print(f"    {i:2}. {name:35} {usage:,} 次")
    
    # 處理難度評估
    print(f"\n{'='*80}")
    print("處理難度評估")
    print("="*80)
    
    difficulty_assessment = {
        '容易 (可規則化)': [
            '服裝配飾', '食物飲料', '日常物品', '武器道具',
            '動物生物', '年份日期'
        ],
        '中等 (LLM 效果好)': [
            '動作行為', '表情情緒', '室內場景', '室外環境',
            '自然景觀', '顏色組合', '圖案花紋'
        ],
        '困難 (需要特殊處理)': [
            '特殊符號/表情', '日文專有詞彙', '遊戲特定標籤',
            '人物關係', '主題概念', '成人內容'
        ],
        '複雜 (可能需要人工)': [
            '元數據', '品質標記', '視覺特效', '未分類/複雜'
        ]
    }
    
    for difficulty, categories in difficulty_assessment.items():
        total_tags = sum(len(feature_categories[cat]) for cat in categories if cat in feature_categories)
        total_usage = sum(
            sum(usage for _, usage in feature_categories[cat])
            for cat in categories if cat in feature_categories
        )
        
        print(f"\n{difficulty}:")
        print(f"  標籤數: {total_tags} 個")
        print(f"  使用次數: {total_usage:,} 次")
        print(f"  包含類別: {', '.join(categories)}")
    
    # 成本效益分析
    print(f"\n{'='*80}")
    print("成本效益分析")
    print("="*80)
    
    for seg_name, tags in segment_data.items():
        if tags:
            count = len(tags)
            total_usage = sum(usage for _, usage in tags)
            avg_usage = total_usage // count
            
            # 估算成本和覆蓋率提升
            estimated_cost = (count // 20 + 1) * 0.0001
            conn_temp = sqlite3.connect('output/tags.db')
            total_db_tags = conn_temp.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
            conn_temp.close()
            
            coverage_gain = (count / total_db_tags) * 100
            cost_per_percent = estimated_cost / coverage_gain if coverage_gain > 0 else 0
            
            print(f"\n{seg_name}:")
            print(f"  標籤數: {count:,} 個")
            print(f"  平均使用: {avg_usage:,} 次")
            print(f"  預估成本: ${estimated_cost:.3f}")
            print(f"  覆蓋率提升: +{coverage_gain:.2f}%")
            print(f"  單位成本: ${cost_per_percent:.3f} / 1%覆蓋率")
    
    conn.close()
    
    return feature_categories, segment_data

def recommend_processing_order(feature_categories):
    """推薦處理順序"""
    print(f"\n{'='*80}")
    print("推薦處理順序")
    print("="*80)
    
    processing_order = [
        {
            'name': '第一優先 - 容易分類',
            'categories': ['服裝配飾', '食物飲料', '日常物品', '武器道具', '動物生物'],
            'method': 'LLM 批量處理 (批次 20)',
            'expected_success': '98%+',
        },
        {
            'name': '第二優先 - 標準分類', 
            'categories': ['動作行為', '表情情緒', '室內場景', '室外環境', '自然景觀'],
            'method': 'LLM 批量處理 (批次 15)',
            'expected_success': '95%+',
        },
        {
            'name': '第三優先 - 需要微調',
            'categories': ['顏色組合', '圖案花紋', '視覺特效', '人物關係'],
            'method': 'LLM 批量處理 (批次 15) + 提示詞優化',
            'expected_success': '90%+',
        },
        {
            'name': '第四優先 - 特殊處理',
            'categories': ['遊戲特定標籤', '日文專有詞彙', '成人內容', '主題概念'],
            'method': 'LLM 批量處理 (批次 10-15) + 特殊提示',
            'expected_success': '85%+',
        },
        {
            'name': '第五優先 - 符號規則',
            'categories': ['特殊符號/表情', '年份日期'],
            'method': '規則庫處理 → LLM 補充',
            'expected_success': '80%+',
        },
        {
            'name': '最後處理 - 可能需要人工',
            'categories': ['元數據', '品質標記', '未分類/複雜'],
            'method': 'LLM + 人工審核',
            'expected_success': '70%+',
        },
    ]
    
    for i, group in enumerate(processing_order, 1):
        print(f"\n{i}. {group['name']}")
        print(f"   類別: {', '.join(group['categories'])}")
        
        # 計算這組的標籤數
        total_in_group = sum(
            len(feature_categories.get(cat, []))
            for cat in group['categories']
        )
        
        print(f"   標籤數: {total_in_group} 個")
        print(f"   方法: {group['method']}")
        print(f"   預期成功率: {group['expected_success']}")

if __name__ == "__main__":
    feature_categories, segment_data = analyze_all_remaining_tags()
    recommend_processing_order(feature_categories)

