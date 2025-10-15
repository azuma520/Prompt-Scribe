"""
Keyword Analyzer Service
關鍵字分析服務 - 分析關鍵字重要性和詞性
"""
from typing import List, Dict, Tuple, Set
import logging

logger = logging.getLogger(__name__)


# 詞性字典
WORD_CATEGORIES = {
    # 主詞（名詞）- 最高權重 1.0
    'nouns': {
        # 角色
        'girl', 'boy', 'woman', 'man', 'child', 'person', 'character',
        'cat', 'dog', 'dragon', 'animal', 'creature',
        
        # 地點
        'city', 'room', 'school', 'beach', 'forest', 'mountain', 
        'building', 'house', 'street', 'park', 'garden',
        
        # 物品
        'uniform', 'dress', 'sword', 'gun', 'book', 'flower',
        'weapon', 'clothing', 'outfit', 'bag', 'phone',
        
        # 概念
        'sky', 'ocean', 'night', 'day', 'sunset', 'sunrise',
        'rain', 'snow', 'wind', 'cloud', 'moon', 'sun',
    },
    
    # 修飾詞（形容詞）- 中高權重 0.85
    'adjectives': {
        # 外觀
        'cute', 'beautiful', 'handsome', 'pretty', 'gorgeous',
        'ugly', 'scary', 'creepy', 'amazing', 'wonderful',
        
        # 大小
        'big', 'small', 'large', 'tiny', 'huge', 'massive',
        'short', 'long', 'tall', 'wide', 'narrow',
        
        # 顏色
        'red', 'blue', 'green', 'yellow', 'black', 'white',
        'pink', 'purple', 'orange', 'brown', 'gray',
        
        # 情緒
        'happy', 'sad', 'angry', 'surprised', 'calm',
        'excited', 'bored', 'confused', 'lonely', 'peaceful',
        
        # 風格
        'realistic', 'fantasy', 'cyberpunk', 'anime', 'cartoon',
        'vintage', 'modern', 'futuristic', 'medieval',
        
        # 質量
        'detailed', 'simple', 'complex', 'beautiful', 'messy',
    },
    
    # 動詞/動作 - 中權重 0.8
    'verbs': {
        'sitting', 'standing', 'running', 'walking', 'jumping',
        'flying', 'swimming', 'dancing', 'fighting', 'sleeping',
        'looking', 'smiling', 'crying', 'laughing', 'eating',
        'holding', 'wearing', 'carrying', 'reading', 'writing',
    },
    
    # 副詞 - 中低權重 0.6
    'adverbs': {
        'very', 'extremely', 'highly', 'slightly', 'somewhat',
        'completely', 'partially', 'totally', 'barely',
        'quickly', 'slowly', 'carefully', 'gently',
    },
    
    # 介詞/連接詞 - 低權重 0.3
    'prepositions': {
        'in', 'on', 'at', 'by', 'with', 'from', 'to',
        'of', 'for', 'over', 'under', 'above', 'below',
        'between', 'among', 'through', 'during', 'before', 'after',
        'and', 'or', 'but', 'the', 'a', 'an',
    },
    
    # 特殊詞 - 特殊處理
    'numbers': {
        '1girl', '2girls', '3girls', 'multiple_girls',
        '1boy', '2boys', '3boys', 'multiple_boys',
        'solo', '2people', '3people',
    },
}


# 預定義權重
WORD_TYPE_WEIGHTS = {
    'nouns': 1.0,
    'adjectives': 0.85,
    'verbs': 0.8,
    'adverbs': 0.6,
    'prepositions': 0.3,
    'numbers': 1.0,  # 數量詞很重要
    'unknown': 0.7,  # 未知詞給予中等權重
}


def classify_word(word: str) -> str:
    """
    分類單詞的詞性
    
    Args:
        word: 單詞
        
    Returns:
        詞性類別
    """
    word_lower = word.lower()
    
    # 檢查各個類別
    for category, words in WORD_CATEGORIES.items():
        if word_lower in words:
            return category
    
    # 特殊模式檢查
    # 數字開頭的詞（如 1girl, 2boys）
    if word_lower[0].isdigit():
        return 'numbers'
    
    # 帶底線的複合詞（傾向於是名詞）
    if '_' in word_lower and len(word_lower) > 5:
        return 'nouns'
    
    return 'unknown'


def analyze_keyword_importance(keywords: List[str]) -> Dict[str, float]:
    """
    分析關鍵字的重要性權重
    
    Args:
        keywords: 關鍵字列表
        
    Returns:
        {keyword: weight} 字典
    """
    weights = {}
    
    for keyword in keywords:
        word_type = classify_word(keyword)
        weight = WORD_TYPE_WEIGHTS.get(word_type, 0.7)
        weights[keyword] = weight
        
        logger.debug(f"Keyword '{keyword}' classified as '{word_type}' with weight {weight}")
    
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
    weights = analyze_keyword_importance(keywords)
    
    # 排序
    sorted_keywords = sorted(
        weights.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return sorted_keywords[:top_n]


def explain_keyword_classification(keywords: List[str]) -> Dict[str, List[str]]:
    """
    解釋關鍵字分類（用於除錯和透明度）
    
    Returns:
        {category: [keywords]} 字典
    """
    classification = {}
    
    for keyword in keywords:
        word_type = classify_word(keyword)
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

