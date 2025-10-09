"""
分類規則字典：定義主分類和副分類的關鍵字

這個模組是 src/classifier/ 模組的簡化封裝，供 run_pipeline.py 使用。
完整的分類器實作請參考 src/classifier/ 目錄。
"""

import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, List

# 添加 src 目錄到路徑
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from classifier import RuleBasedClassifier, MAIN_CATEGORIES, SUB_CATEGORIES
from classifier.categories import CATEGORY_DESCRIPTIONS


# 創建全局分類器實例
_classifier = RuleBasedClassifier()


# 導出分類類別定義（供其他模組使用）
MAIN_CATEGORY_RULES = MAIN_CATEGORIES
SUB_CATEGORY_RULES = SUB_CATEGORIES


def classify_tag(
    tag_name: str, 
    danbooru_cat: Optional[int] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    根據規則對標籤進行分類（整合 Danbooru 原始分類）
    
    Args:
        tag_name: 標籤名稱
        danbooru_cat: Danbooru 原始分類號碼 (0-5)，如果有的話
    
    Returns:
        (main_category, sub_category) 的元組
        未分類時返回 (None, None)
    
    Example:
        >>> classify_tag('school_uniform')
        ('CHARACTER_RELATED', 'CLOTHING')
        
        >>> classify_tag('hatsune_miku', danbooru_cat=4)
        ('CHARACTER', None)
        
        >>> classify_tag('unknown_tag_xyz')
        (None, None)
    """
    return _classifier.classify(tag_name, danbooru_cat)


def get_classifier_stats() -> Dict:
    """
    取得分類器統計資訊
    
    Returns:
        包含分類統計的字典
    """
    return _classifier.get_stats()


def reset_classifier_stats():
    """重置分類器統計資訊"""
    _classifier.reset_stats()

