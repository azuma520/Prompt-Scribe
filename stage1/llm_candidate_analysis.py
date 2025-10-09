"""
LLM 候選標籤深度分析

目的：
1. 分析哪些標籤可以用規則擴展處理
2. 識別真正需要 LLM 的標籤
3. 生成精進方案
"""

import sqlite3
from pathlib import Path
from collections import defaultdict


def analyze_llm_candidates():
    """分析 LLM 候選標籤"""
    
    conn = sqlite3.connect('output/tags.db')
    
    print("="*80)
    print("LLM 候選標籤深度分析")
    print("="*80)
    
    # 獲取所有超高頻未分類標籤
    candidates = conn.execute("""
        SELECT name, post_count
        FROM tags_final
        WHERE danbooru_cat = 0 
          AND main_category IS NULL
          AND post_count >= 1000000
        ORDER BY post_count DESC
    """).fetchall()
    
    print(f"\n總計 {len(candidates)} 個超高頻未分類標籤 (>1M 使用次數)")
    print(f"合計使用次數: {sum(c[1] for c in candidates):,}")
    
    # 手動分類分析
    rule_expandable = {
        'CLOTHING': [],
        'BODY_PARTS': [],
        'ACCESSORIES': [],
        'EXPRESSION': [],
        'OBJECTS': [],
        'ART_STYLE': [],
        'TECHNICAL': [],
        'ADULT_CONTENT': [],
        'NEED_LLM': [],  # 真正需要 LLM 的
    }
    
    # 分析每個標籤
    for name, usage in candidates:
        # 服裝相關
        if any(word in name for word in [
            'clothes', 'clothing', 'dress', 'shirt', 'skirt', 'pants',
            'jacket', 'coat', 'vest', 'sweater', 'hoodie', 'apron',
            'collar', 'hood', 'choker', 'belt', 'serafuku', 'japanese_clothes',
            'footwear', 'shoes', 'boots', 'sandals', 'heels',
            'leotard', 'bodysuit', 'crop', 'strapless', 'fur_trim',
            'cutout', 'see-through'
        ]):
            rule_expandable['CLOTHING'].append((name, usage))
        
        # 身體部位
        elif any(word in name for word in [
            'tongue', 'fang', 'pointy_ears', 'ears', 'armpits', 'armpit',
            'mole', 'midriff', 'toes', 'fingernails', 'eyelashes',
            'eyebrows', 'abs', 'facial_mark', 'cameltoe'
        ]):
            rule_expandable['BODY_PARTS'].append((name, usage))
        
        # 配飾
        elif any(word in name for word in [
            'headband', 'nail_polish', 'ring', 'wrist_cuffs'
        ]):
            rule_expandable['ACCESSORIES'].append((name, usage))
        
        # 表情/姿勢
        elif any(word in name for word in [
            'happy', 'sweatdrop', 'arm_', 'on_side', 'eating'
        ]):
            rule_expandable['EXPRESSION'].append((name, usage))
        
        # 物件
        elif any(word in name for word in [
            'bubble', 'halo', 'stuffed', 'toy', 'star_', 'symbol'
        ]):
            rule_expandable['OBJECTS'].append((name, usage))
        
        # 藝術風格/技術
        elif any(word in name for word in [
            '4koma', 'border', 'username', 'text', 'dated'
        ]):
            if 'text' in name or 'username' in name or 'dated' in name:
                rule_expandable['TECHNICAL'].append((name, usage))
            else:
                rule_expandable['ART_STYLE'].append((name, usage))
        
        # 成人內容
        elif any(word in name for word in [
            'erection', 'testicles', 'groping'
        ]):
            rule_expandable['ADULT_CONTENT'].append((name, usage))
        
        # 真正需要 LLM 的
        else:
            rule_expandable['NEED_LLM'].append((name, usage))
    
    # 顯示分析結果
    print("\n" + "="*80)
    print("分類分析結果")
    print("="*80)
    
    total_rule_expandable = 0
    total_rule_usage = 0
    
    for category, tags in rule_expandable.items():
        if tags and category != 'NEED_LLM':
            count = len(tags)
            usage = sum(t[1] for t in tags)
            total_rule_expandable += count
            total_rule_usage += usage
            print(f"\n{category}: {count} 個標籤")
            print(f"  合計使用次數: {usage:,}")
            print(f"  前 5 個標籤:")
            for i, (tag, tag_usage) in enumerate(tags[:5], 1):
                print(f"    {i}. {tag:30} {tag_usage:>12,} 次")
    
    # 真正需要 LLM 的
    print(f"\n{'='*80}")
    print(f"NEED_LLM (真正需要 LLM 處理): {len(rule_expandable['NEED_LLM'])} 個標籤")
    llm_usage = sum(t[1] for t in rule_expandable['NEED_LLM'])
    print(f"  合計使用次數: {llm_usage:,}")
    if rule_expandable['NEED_LLM']:
        print(f"  標籤列表:")
        for i, (tag, tag_usage) in enumerate(rule_expandable['NEED_LLM'], 1):
            print(f"    {i}. {tag:30} {tag_usage:>12,} 次")
    
    # 總結
    print(f"\n{'='*80}")
    print("總結")
    print(f"{'='*80}")
    print(f"可用規則擴展處理: {total_rule_expandable} 個標籤 ({total_rule_expandable/len(candidates)*100:.1f}%)")
    print(f"  影響使用次數: {total_rule_usage:,}")
    print(f"  佔總使用量: {total_rule_usage / sum(c[1] for c in candidates) * 100:.1f}%")
    print(f"\n真正需要 LLM: {len(rule_expandable['NEED_LLM'])} 個標籤 ({len(rule_expandable['NEED_LLM'])/len(candidates)*100:.1f}%)")
    print(f"  影響使用次數: {llm_usage:,}")
    print(f"  佔總使用量: {llm_usage / sum(c[1] for c in candidates) * 100:.1f}%")
    
    # 成本估算
    print(f"\n{'='*80}")
    print("成本估算")
    print(f"{'='*80}")
    
    # 規則擴展成本
    print(f"\n方案 A: 規則擴展 (推薦)")
    print(f"  - 需處理: {total_rule_expandable} 個標籤")
    print(f"  - 預估時間: 2-3 小時")
    print(f"  - 成本: $0")
    print(f"  - 預期覆蓋率提升: 41.59% → 50-55%")
    
    # LLM 處理成本
    llm_count = len(rule_expandable['NEED_LLM'])
    llm_cost = llm_count * 0.00005  # 每個標籤約 $0.00005
    print(f"\n方案 B: 僅 LLM 處理無法用規則的標籤")
    print(f"  - 需處理: {llm_count} 個標籤")
    print(f"  - 預估成本: ${llm_cost:.2f}")
    print(f"  - 預期覆蓋率提升: +少量")
    
    # 混合方案
    print(f"\n方案 C: 混合方案 (推薦)")
    print(f"  - 階段 1: 規則擴展 ({total_rule_expandable} 個)")
    print(f"  - 階段 2: LLM 補充 ({llm_count} 個)")
    print(f"  - 總成本: ${llm_cost:.2f}")
    print(f"  - 預期覆蓋率: 41.59% → 55-60%")
    
    # 生成規則擴展建議
    print(f"\n{'='*80}")
    print("規則擴展建議")
    print(f"{'='*80}")
    
    for category in ['CLOTHING', 'BODY_PARTS', 'ACCESSORIES', 'EXPRESSION', 'TECHNICAL', 'ADULT_CONTENT']:
        tags = rule_expandable.get(category, [])
        if tags:
            print(f"\n{category} 需添加的關鍵字 ({len(tags)} 個標籤):")
            keywords = set()
            for tag, _ in tags[:20]:  # 只看前20個高頻的
                # 提取關鍵字
                parts = tag.replace('_', ' ').split()
                keywords.update(parts)
            print(f"  建議關鍵字: {', '.join(sorted(keywords)[:15])}")
    
    conn.close()
    
    return rule_expandable


if __name__ == '__main__':
    analyze_llm_candidates()

