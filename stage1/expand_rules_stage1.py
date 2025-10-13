#!/usr/bin/env python3
"""
Stage 1 規則擴展實施腳本

目標：通過擴展現有規則分類器，提升覆蓋率 2.5%
"""

import sqlite3
from pathlib import Path
import sys

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / 'src'))

from classifier.rule_classifier import RuleBasedClassifier

def expand_character_related_rules():
    """擴展 CHARACTER_RELATED 規則"""
    
    # 需要添加的高頻標籤
    new_clothing_tags = {
        'polka_dot': 'CHARACTER_RELATED/CLOTHING',
        'fishnets': 'CHARACTER_RELATED/CLOTHING', 
        'loafers': 'CHARACTER_RELATED/CLOTHING',
        'veil': 'CHARACTER_RELATED/CLOTHING',
        'bandaid': 'CHARACTER_RELATED/CLOTHING',
        'single_thighhigh': 'CHARACTER_RELATED/CLOTHING',
        'lipstick': 'CHARACTER_RELATED/COSMETICS',
    }
    
    new_accessories_tags = {
        'brooch': 'CHARACTER_RELATED/ACCESSORIES',
        'goggles': 'CHARACTER_RELATED/ACCESSORIES',
    }
    
    new_body_parts_tags = {
        'eyewear_on_head': 'CHARACTER_RELATED/BODY_PARTS',
        'shaded_face': 'CHARACTER_RELATED/BODY_PARTS',
        'tan': 'CHARACTER_RELATED/BODY_PARTS',
        'extra_ears': 'CHARACTER_RELATED/BODY_PARTS',
    }
    
    return {
        **new_clothing_tags,
        **new_accessories_tags, 
        **new_body_parts_tags
    }

def expand_action_pose_rules():
    """擴展 ACTION_POSE 規則"""
    
    return {
        'bent_over': 'ACTION_POSE/BODY_POSE',
        'all_fours': 'ACTION_POSE/BODY_POSE',
        'kiss': 'ACTION_POSE/GESTURE',
        'staff': 'ACTION_POSE/PROPS',
    }

def expand_technical_rules():
    """擴展 TECHNICAL 規則"""
    
    return {
        'letterboxed': 'TECHNICAL/FRAMING',
    }

def expand_adult_content_rules():
    """擴展 ADULT_CONTENT 規則"""
    
    return {
        'bondage': 'ADULT_CONTENT/EXPLICIT_BODY',
    }

def expand_theme_concept_rules():
    """擴展 THEME_CONCEPT 規則"""
    
    return {
        'otoko_no_ko': 'THEME_CONCEPT/CONCEPT',
    }

def apply_rule_expansions():
    """應用所有規則擴展"""
    
    print("="*80)
    print("Stage 1 規則擴展實施")
    print("="*80)
    
    # 獲取所有擴展規則
    all_expansions = {}
    all_expansions.update(expand_character_related_rules())
    all_expansions.update(expand_action_pose_rules())
    all_expansions.update(expand_technical_rules())
    all_expansions.update(expand_adult_content_rules())
    all_expansions.update(expand_theme_concept_rules())
    
    print(f"總計擴展規則: {len(all_expansions)} 個")
    
    # 連接資料庫
    conn = sqlite3.connect('output/tags.db')
    
    # 統計擴展前狀態
    unclassified_before = conn.execute('''
        SELECT COUNT(*) FROM tags_final 
        WHERE danbooru_cat = 0 AND main_category IS NULL
    ''').fetchone()[0]
    
    print(f"\n擴展前未分類標籤: {unclassified_before:,}")
    
    # 應用規則擴展
    updated_count = 0
    total_usage = 0
    
    for tag_name, classification in all_expansions.items():
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
                SET main_category = ?, sub_category = ?, classification_source = 'rule_expansion_stage1'
                WHERE name = ? AND danbooru_cat = 0 AND main_category IS NULL
            ''', (main_cat, sub_cat, tag_name))
            
            updated_count += 1
            total_usage += post_count
            print(f"[OK] {tag_name:30} -> {main_cat}/{sub_cat or 'N/A':20} ({post_count:,} 次)")
        else:
            print(f"[SKIP] {tag_name:30} -> 未找到或已分類")
    
    # 提交變更
    conn.commit()
    
    # 統計擴展後狀態
    unclassified_after = conn.execute('''
        SELECT COUNT(*) FROM tags_final 
        WHERE danbooru_cat = 0 AND main_category IS NULL
    ''').fetchone()[0]
    
    # 計算整體覆蓋率
    total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    coverage = classified_tags / total_tags * 100
    
    print(f"\n" + "="*80)
    print("規則擴展結果")
    print("="*80)
    print(f"成功更新標籤: {updated_count} 個")
    print(f"影響使用次數: {total_usage:,} 次")
    print(f"未分類標籤: {unclassified_before:,} → {unclassified_after:,} (-{unclassified_before - unclassified_after:,})")
    print(f"整體覆蓋率: {coverage:.2f}%")
    print(f"覆蓋率提升: +{(updated_count / total_tags * 100):.2f}%")
    
    conn.close()
    
    return updated_count, total_usage, coverage

if __name__ == "__main__":
    apply_rule_expansions()
