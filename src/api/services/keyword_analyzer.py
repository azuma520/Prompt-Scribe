from typing import List, Dict, Any, Set, Tuple
import logging

logger = logging.getLogger(__name__)

class KeywordAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self._word_categories: Dict[str, Set[str]] = {
            category: set(words) for category, words in config.get("word_categories", {}).items()
        }
        self._word_type_weights: Dict[str, float] = config.get("word_type_weights", {})
        self._unknown_weight: float = self._word_type_weights.get("unknown", 0.7)

    def classify_word(self, word: str) -> str:
        word_lower = word.lower()
        for category, words in self._word_categories.items():
            if word_lower in words:
                return category
        
        if word_lower and word_lower[0].isdigit():
            return 'numbers'
        
        if '_' in word_lower and len(word_lower) > 5:
            return 'nouns'

        return 'unknown'

    def analyze_keyword_importance(self, keywords: List[str]) -> Dict[str, float]:
        weights = {}
        for keyword in keywords:
            word_type = self.classify_word(keyword)
            weight = self._word_type_weights.get(word_type, self._unknown_weight)
            weights[keyword] = weight
        return weights

def calculate_weighted_relevance(
    tag_name: str,
    keywords: List[str],
    keyword_weights: Dict[str, float]
) -> float:
    """
    計算加權相關性分數
    
    Args:
        tag_name: 標籤名稱
        keywords: 關鍵字列表
        keyword_weights: 關鍵字權重字典
        
    Returns:
        加權相關性分數 (0.0-1.0)
    """
    tag_lower = tag_name.lower()
    total_weight = 0.0
    matched_weight = 0.0
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        weight = keyword_weights.get(keyword, 0.7)
        total_weight += weight
        
        # 計算匹配分數
        match_score = 0.0
        
        # 完全匹配
        if tag_lower == keyword_lower:
            match_score = 1.0
        # 前綴匹配
        elif tag_lower.startswith(keyword_lower):
            match_score = 0.9
        elif keyword_lower.startswith(tag_lower):
            match_score = 0.85
        # 包含匹配
        elif keyword_lower in tag_lower:
            match_score = 0.7
        elif tag_lower in keyword_lower:
            match_score = 0.6
        
        # 累加加權分數
        if match_score > 0:
            matched_weight += match_score * weight
    
    # 計算最終分數
    if total_weight == 0:
        return 0.0
    
    # 正規化到 0-1
    relevance = min(matched_weight / total_weight, 1.0)
    
    return relevance


def extract_important_keywords(
    keywords: List[str],
    analyzer: KeywordAnalyzer,
    top_n: int = 10
) -> List[Tuple[str, float]]:
    """
    提取最重要的關鍵字
    
    Args:
        keywords: 關鍵字列表
        top_n: 返回前 N 個
        
    Returns:
        [(keyword, weight), ...] 列表，按權重排序
    """
    weights = analyzer.analyze_keyword_importance(keywords)
    
    # 排序
    sorted_keywords = sorted(
        weights.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return sorted_keywords[:top_n]


def explain_keyword_classification(keywords: List[str], analyzer: KeywordAnalyzer) -> Dict[str, List[str]]:
    """
    解釋關鍵字分類（用於除錯和透明度）
    
    Returns:
        {category: [keywords]} 字典
    """
    classification = {}
    
    for keyword in keywords:
        word_type = analyzer.classify_word(keyword)
        if word_type not in classification:
            classification[word_type] = []
        classification[word_type].append(keyword)
    
    return classification


# 快速參考
def get_word_type_examples() -> Dict[str, List[str]]:
    """獲取各詞性的範例（用於文檔）"""
    return {
        'nouns (1.0)': ['girl', 'city', 'uniform', 'cat'],
        'adjectives (0.85)': ['cute', 'happy', 'big', 'blue'],
        'verbs (0.8)': ['sitting', 'running', 'smiling'],
        'adverbs (0.6)': ['very', 'extremely', 'quickly'],
        'prepositions (0.3)': ['in', 'on', 'at', 'with'],
        'numbers (1.0)': ['1girl', '2girls', 'solo'],
    }

from functools import lru_cache
try:
    from ..config import settings as _settings
except Exception:
    try:
        from src.api.config import settings as _settings
    except Exception:
        from config import settings as _settings

@lru_cache()
def get_keyword_analyzer() -> "KeywordAnalyzer":
    """獲取關鍵字分析器單例"""
    return KeywordAnalyzer(_settings.tag_weights)
