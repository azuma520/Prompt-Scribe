#!/usr/bin/env python3
"""
分析剩餘中頻標籤的特徵
為下一階段處理提供策略建議
"""

import sqlite3
from collections import defaultdict
import re

def analyze_remaining_medium_freq():
    """分析剩餘中頻標籤"""
    conn = sqlite3.connect('output/tags.db')
    
    # 獲取剩餘中頻標籤
    remaining = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 10000 AND post_count < 100000
        ORDER BY post_count DESC
    ''').fetchall()
    
    print("="*80)
    print(f"剩餘中頻標籤分析 (10K-100K)")
    print("="*80)
    print(f"總數: {len(remaining):,} 個標籤")
    print(f"使用次數: {sum(usage for _, usage in remaining):,} 次")
    print(f"平均使用: {sum(usage for _, usage in remaining) // len(remaining):,} 次/標籤")
    
    # 按使用頻率分段
    freq_segments = {
        '50K-100K': (50000, 100000),
        '30K-50K': (30000, 50000),
        '20K-30K': (20000, 30000),
        '10K-20K': (10000, 20000),
    }
    
    print(f"\n【頻率分段統計】")
    print("-"*50)
    
    segment_stats = {}
    for seg_name, (min_freq, max_freq) in freq_segments.items():
        tags_in_segment = [
            (name, usage) for name, usage in remaining 
            if min_freq <= usage < max_freq
        ]
        count = len(tags_in_segment)
        total_usage = sum(usage for _, usage in tags_in_segment)
        
        segment_stats[seg_name] = tags_in_segment
        
        print(f"{seg_name:15} {count:5} 個標籤, {total_usage:12,} 次使用")
    
    # 模式分析
    print(f"\n【標籤模式分析】")
    print("-"*50)
    
    patterns = {
        '特殊符號': [],
        '日文詞彙': [],
        '遊戲特定': [],
        '動作詞': [],
        '物品名詞': [],
        '形容詞': [],
        '顏色組合': [],
        '人物關係': [],
        '場景位置': [],
        '其他': []
    }
    
    for name, usage in remaining[:200]:  # 分析前 200 個
        # 特殊符號
        if re.search(r'^[^a-z]', name) or re.search(r'[^a-z0-9_\-()]', name):
            patterns['特殊符號'].append((name, usage))
        # 日文詞彙（假名、漢字相關）
        elif any(word in name for word in ['japanese', 'wa_', 'yukata', 'hakama', 'kimono', 'miko']):
            patterns['日文詞彙'].append((name, usage))
        # 遊戲特定
        elif '(' in name and ')' in name:
            patterns['遊戲特定'].append((name, usage))
        # 動作詞
        elif any(name.endswith(suffix) for suffix in ['ing', 'ed']):
            patterns['動作詞'].append((name, usage))
        # 物品名詞
        elif any(word in name for word in ['print', 'clothes', 'outfit', 'hat', 'mask']):
            patterns['物品名詞'].append((name, usage))
        # 形容詞
        elif any(name.startswith(prefix) for prefix in ['very_', 'super_', 'mega_', 'ultra_']):
            patterns['形容詞'].append((name, usage))
        # 顏色組合
        elif any(color in name for color in ['red_', 'blue_', 'green_', 'black_', 'white_', 'pink_', 'yellow_', 'purple_']):
            patterns['顏色組合'].append((name, usage))
        # 人物關係
        elif any(word in name for word in ['and_', 'with_', 'couple', 'family', 'brother', 'sister']):
            patterns['人物關係'].append((name, usage))
        # 場景位置
        elif any(word in name for word in ['on_', 'in_', 'at_', 'under_', 'over_', 'behind_']):
            patterns['場景位置'].append((name, usage))
        else:
            patterns['其他'].append((name, usage))
    
    for pattern_name, tags in patterns.items():
        if tags:
            total_usage = sum(usage for _, usage in tags)
            print(f"\n{pattern_name} ({len(tags)} 個):")
            print(f"  總使用: {total_usage:,} 次")
            # 顯示前 5 個
            for name, usage in tags[:5]:
                print(f"    {name:30} {usage:,} 次")
    
    conn.close()
    
    return remaining, segment_stats, patterns

def suggest_processing_strategy(segment_stats, patterns):
    """建議處理策略"""
    print(f"\n{'='*80}")
    print("處理策略建議")
    print("="*80)
    
    print("\n【策略選項】\n")
    
    print("方案 A: 按頻率優先 (推薦)")
    print("-"*50)
    print("優勢:")
    print("  + 最大化覆蓋率提升效率")
    print("  + 高頻標籤影響大")
    print("  + 成本效益比最高")
    print("\n處理順序:")
    print("  1. 50K-100K 標籤 (約 50-100 個)")
    print("  2. 30K-50K 標籤 (約 200-300 個)")
    print("  3. 20K-30K 標籤 (約 300-400 個)")
    print("  4. 10K-20K 標籤 (約 900-1000 個)")
    
    print("\n\n方案 B: 按模式分批")
    print("-"*50)
    print("優勢:")
    print("  + 同類標籤一起處理，一致性更好")
    print("  + 可以針對性優化提示詞")
    print("  + 容易發現規則模式")
    print("\n處理順序:")
    print("  1. 物品名詞 (最容易分類)")
    print("  2. 動作詞 (動作姿態)")
    print("  3. 場景位置 (環境相關)")
    print("  4. 顏色組合 (需要次要分類)")
    print("  5. 特殊符號和日文詞彙 (最困難)")
    
    print("\n\n方案 C: 混合策略 (最優)")
    print("-"*50)
    print("優勢:")
    print("  + 結合 A 和 B 的優勢")
    print("  + 靈活應對不同類型標籤")
    print("  + 最佳的成本效益和品質平衡")
    print("\n處理順序:")
    print("  1. 高頻物品名詞 (50K+，容易分類)")
    print("  2. 高頻動作詞 (50K+，提示詞優化)")
    print("  3. 中頻批量 (30K-50K，混合處理)")
    print("  4. 低中頻批量 (20K-30K，選擇性處理)")
    print("  5. 最低檔 (10K-20K，按需處理)")
    
    print("\n\n【建議】")
    print("-"*50)
    print("推薦使用 方案 C: 混合策略")
    print("\n理由:")
    print("  1. 已經有成功的 LLM 批量處理經驗")
    print("  2. 可以先處理容易的，建立信心")
    print("  3. 困難的標籤可以最後集中處理")
    print("  4. 靈活調整策略，避免僵化")

if __name__ == "__main__":
    remaining, segment_stats, patterns = analyze_remaining_medium_freq()
    suggest_processing_strategy(segment_stats, patterns)

