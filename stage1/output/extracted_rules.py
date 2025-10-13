#!/usr/bin/env python3
"""
自動提取的分類規則
生成時間: 2025-10-13 12:49:51
"""

# 後綴規則
SUFFIX_RULES = {
}

# 前綴規則
PREFIX_RULES = {
}

# 包含規則
CONTAINS_RULES = {
}

def apply_rules(tag_name: str) -> tuple:
    """應用提取的規則
    
    Returns:
        (main_category, sub_category) or (None, None)
    """
    # 後綴匹配
    for suffix, (main_cat, sub_cat) in SUFFIX_RULES.items():
        if tag_name.endswith(suffix):
            return (main_cat, sub_cat)
    
    # 前綴匹配
    for prefix, (main_cat, sub_cat) in PREFIX_RULES.items():
        if tag_name.startswith(prefix):
            return (main_cat, sub_cat)
    
    # 包含匹配
    for word, (main_cat, sub_cat) in CONTAINS_RULES.items():
        if word in tag_name:
            return (main_cat, sub_cat)
    
    return (None, None)
