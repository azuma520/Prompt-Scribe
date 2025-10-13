#!/usr/bin/env python3
"""
資料庫分類品質測試
檢查 LLM 分類的準確性與一致性
"""

import sqlite3
from collections import defaultdict
import random

def test_classification_quality():
    """執行完整的分類品質測試"""
    
    print("="*80)
    print("資料庫分類品質測試")
    print("="*80)
    print()
    
    conn = sqlite3.connect('output/tags.db')
    
    # ===== 測試 1: 基本統計 =====
    print("【測試 1】基本統計")
    print("-"*80)
    
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    llm_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE classification_source = "qwen3_80b"').fetchone()[0]
    rule_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL AND classification_source IS NULL').fetchone()[0]
    
    print(f"總標籤數: {total_tags:,}")
    print(f"已分類: {classified_tags:,} ({classified_tags/total_tags*100:.2f}%)")
    print(f"  - 規則分類: {rule_tags:,}")
    print(f"  - LLM 分類: {llm_tags:,}")
    print()
    
    # ===== 測試 2: LLM 分類置信度分布 =====
    print("【測試 2】LLM 分類置信度分布")
    print("-"*80)
    
    confidence_ranges = [
        (0.0, 0.5, '極低 (<0.5)'),
        (0.5, 0.7, '低 (0.5-0.7)'),
        (0.7, 0.85, '中等 (0.7-0.85)'),
        (0.85, 0.95, '高 (0.85-0.95)'),
        (0.95, 1.01, '極高 (>=0.95)')
    ]
    
    for min_conf, max_conf, label in confidence_ranges:
        count = conn.execute(f'''
            SELECT COUNT(*) FROM tags_final 
            WHERE classification_source = "qwen3_80b"
            AND classification_confidence >= {min_conf}
            AND classification_confidence < {max_conf}
        ''').fetchone()[0]
        
        if count > 0:
            pct = count / llm_tags * 100
            bar = '█' * int(pct / 2)
            print(f"{label:20} {count:3} ({pct:5.1f}%) {bar}")
    
    avg_conf = conn.execute('''
        SELECT AVG(classification_confidence) 
        FROM tags_final 
        WHERE classification_source = "qwen3_80b"
    ''').fetchone()[0]
    print(f"\n平均置信度: {avg_conf:.3f}")
    print()
    
    # ===== 測試 3: 低置信度標籤審查 =====
    print("【測試 3】低置信度標籤（<0.8）")
    print("-"*80)
    
    low_conf_tags = conn.execute('''
        SELECT name, main_category, sub_category, 
               classification_confidence, post_count, classification_reasoning
        FROM tags_final
        WHERE classification_source = "qwen3_80b"
        AND classification_confidence < 0.8
        ORDER BY post_count DESC
        LIMIT 10
    ''').fetchall()
    
    if low_conf_tags:
        print(f"發現 {len(low_conf_tags)} 個低置信度標籤（顯示前 10 個）:\n")
        for i, (name, main, sub, conf, usage, reason) in enumerate(low_conf_tags, 1):
            print(f"{i}. {name} (使用: {usage:,} 次)")
            print(f"   分類: {main} / {sub or 'None'}")
            print(f"   置信度: {conf:.3f}")
            print(f"   理由: {reason[:80]}...")
            print()
    else:
        print("[OK] 沒有低置信度標籤")
    print()
    
    # ===== 測試 4: 分類一致性檢查 =====
    print("【測試 4】相似標籤分類一致性")
    print("-"*80)
    
    # 檢查帶有相同前綴的標籤
    similar_groups = defaultdict(list)
    
    llm_classified = conn.execute('''
        SELECT name, main_category, sub_category, classification_confidence
        FROM tags_final
        WHERE classification_source = "qwen3_80b"
        ORDER BY name
    ''').fetchall()
    
    for name, main, sub, conf in llm_classified:
        if '_' in name:
            prefix = name.split('_')[0]
            if len(prefix) >= 3:  # 忽略太短的前綴
                similar_groups[prefix].append((name, main, sub, conf))
    
    # 找出不一致的組
    inconsistent = []
    for prefix, tags in similar_groups.items():
        if len(tags) >= 2:
            main_cats = set(tag[1] for tag in tags)
            if len(main_cats) > 1:
                inconsistent.append((prefix, tags))
    
    if inconsistent:
        print(f"發現 {len(inconsistent)} 組相似標籤分類不一致（顯示前 5 組）:\n")
        for i, (prefix, tags) in enumerate(inconsistent[:5], 1):
            print(f"{i}. 前綴: {prefix}_*")
            for name, main, sub, conf in tags[:3]:
                print(f"   - {name:30} -> {main:20} / {sub or 'None':15} (conf: {conf:.2f})")
            print()
    else:
        print("[OK] 沒有發現明顯的不一致")
    print()
    
    # ===== 測試 5: 主分類分布合理性 =====
    print("【測試 5】LLM 主分類分布")
    print("-"*80)
    
    main_dist = conn.execute('''
        SELECT main_category, COUNT(*) as count
        FROM tags_final
        WHERE classification_source = "qwen3_80b"
        GROUP BY main_category
        ORDER BY count DESC
    ''').fetchall()
    
    for main, count in main_dist:
        pct = count / llm_tags * 100
        bar = '█' * int(pct / 2)
        print(f"{main:25} {count:3} ({pct:5.1f}%) {bar}")
    print()
    
    # ===== 測試 6: 副分類覆蓋率 =====
    print("【測試 6】副分類覆蓋情況")
    print("-"*80)
    
    with_sub = conn.execute('''
        SELECT COUNT(*) FROM tags_final
        WHERE classification_source = "qwen3_80b"
        AND sub_category IS NOT NULL
    ''').fetchone()[0]
    
    without_sub = llm_tags - with_sub
    
    print(f"有副分類: {with_sub} ({with_sub/llm_tags*100:.1f}%)")
    print(f"無副分類: {without_sub} ({without_sub/llm_tags*100:.1f}%)")
    
    # 顯示沒有副分類的標籤
    if without_sub > 0:
        no_sub_tags = conn.execute('''
            SELECT name, main_category, post_count
            FROM tags_final
            WHERE classification_source = "qwen3_80b"
            AND sub_category IS NULL
            ORDER BY post_count DESC
            LIMIT 5
        ''').fetchall()
        
        print(f"\n沒有副分類的標籤（前 5 個）:")
        for name, main, usage in no_sub_tags:
            print(f"  - {name:30} ({main}) - {usage:,} 次")
    print()
    
    # ===== 測試 7: 高頻標籤抽樣驗證 =====
    print("【測試 7】高頻標籤抽樣驗證")
    print("-"*80)
    
    high_freq_sample = conn.execute('''
        SELECT name, main_category, sub_category, 
               classification_confidence, post_count, classification_reasoning
        FROM tags_final
        WHERE classification_source = "qwen3_80b"
        AND post_count > 2000000
        ORDER BY RANDOM()
        LIMIT 5
    ''').fetchall()
    
    print("隨機抽取 5 個高頻標籤 (>2M 使用):\n")
    for i, (name, main, sub, conf, usage, reason) in enumerate(high_freq_sample, 1):
        print(f"{i}. {name} (使用: {usage:,} 次)")
        print(f"   分類: {main} / {sub or 'None'}")
        print(f"   置信度: {conf:.3f}")
        print(f"   理由: {reason}")
        
        # 簡單的合理性判斷
        issues = []
        if conf < 0.7:
            issues.append("置信度較低")
        if not sub and main in ['CHARACTER_RELATED', 'ACTION_POSE', 'OBJECTS', 'ENVIRONMENT']:
            issues.append("建議添加副分類")
        
        if issues:
            print(f"   [WARN] 注意: {', '.join(issues)}")
        else:
            print(f"   [OK] 看起來合理")
        print()
    
    # ===== 測試 8: 成人內容分類檢查 =====
    print("【測試 8】成人內容分類檢查")
    print("-"*80)
    
    adult_tags = conn.execute('''
        SELECT name, sub_category, classification_confidence, post_count
        FROM tags_final
        WHERE classification_source = "qwen3_80b"
        AND main_category = "ADULT_CONTENT"
        ORDER BY post_count DESC
    ''').fetchall()
    
    if adult_tags:
        print(f"發現 {len(adult_tags)} 個成人內容標籤:\n")
        for name, sub, conf, usage in adult_tags[:10]:
            print(f"  {name:25} [{sub or 'None':15}] conf: {conf:.2f}, 使用: {usage:,} 次")
    else:
        print("沒有分類為成人內容的標籤")
    print()
    
    # ===== 測試 9: 與規則分類器對比 =====
    print("【測試 9】LLM vs 規則分類器對比")
    print("-"*80)
    
    # 找出被 LLM 重新分類的標籤（如果有的話）
    reclassified = conn.execute('''
        SELECT name, main_category, post_count, classification_reasoning
        FROM tags_final
        WHERE classification_source = "qwen3_80b"
        AND name IN (
            SELECT name FROM tags_final 
            WHERE main_category IS NOT NULL 
            AND classification_source IS NULL
        )
        LIMIT 5
    ''').fetchall()
    
    if reclassified:
        print(f"發現 {len(reclassified)} 個被 LLM 重新分類的標籤:\n")
        for name, main, usage, reason in reclassified:
            print(f"  {name}: {main}")
            print(f"    使用: {usage:,} 次")
            print(f"    理由: {reason[:80]}...")
            print()
    else:
        print("[OK] LLM 分類的都是之前未分類的標籤")
    print()
    
    # ===== 總結 =====
    print("="*80)
    print("測試總結")
    print("="*80)
    
    issues_count = 0
    warnings_count = 0
    
    # 統計問題
    if len([c for _, _, _, c, _, _ in low_conf_tags]) > 0:
        warnings_count += len(low_conf_tags)
        print(f"[WARN] 發現 {len(low_conf_tags)} 個低置信度標籤")
    
    if inconsistent:
        warnings_count += len(inconsistent)
        print(f"[WARN] 發現 {len(inconsistent)} 組不一致的相似標籤")
    
    if avg_conf < 0.85:
        warnings_count += 1
        print(f"[WARN] 平均置信度偏低: {avg_conf:.3f}")
    
    if warnings_count == 0:
        print("[OK] 所有測試通過，分類品質優秀！")
    else:
        print(f"\n總計發現 {warnings_count} 個需要注意的項目")
    
    print("\n品質評級:")
    if avg_conf >= 0.95 and warnings_count == 0:
        print("  ***** 優秀 (Excellent)")
    elif avg_conf >= 0.90 and warnings_count <= 5:
        print("  **** 良好 (Good)")
    elif avg_conf >= 0.80 and warnings_count <= 10:
        print("  *** 合格 (Acceptable)")
    else:
        print("  ** 需要改進 (Needs Improvement)")
    
    conn.close()
    
    print("\n" + "="*80)
    print("測試完成")
    print("="*80)


if __name__ == "__main__":
    test_classification_quality()

