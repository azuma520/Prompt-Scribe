"""
標籤分類器模組
"""

from .rule_classifier import RuleBasedClassifier
from .categories import MAIN_CATEGORIES, SUB_CATEGORIES

__all__ = [
    'RuleBasedClassifier',
    'MAIN_CATEGORIES',
    'SUB_CATEGORIES',
]

