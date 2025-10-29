"""
Relevance Scoring Service
相關性評分服務 - 計算標籤與關鍵字的相關性（升級版）
支援：
- 多級關鍵字權重（詞性分析）
- N-gram 複合詞匹配
- 加權相關性評分
"""
from typing import List, Dict
import logging

from services.keyword_analyzer import (
    calculate_weighted_relevance
)
from services.ngram_matcher import (
    extract_all_ngrams,
    calculate_ngram_match_score
)

logger = logging.getLogger(__name__)


from services.keyword_analyzer import KeywordAnalyzer

def calculate_relevance_score(
    tag_name: str,
    keywords: List[str],
    analyzer: KeywordAnalyzer,
    use_ngram: bool = True,
    use_weighted: bool = True,
) -> float:
    """
    計算標籤與關鍵字的相關性分數（升級版）
    
    Args:
        tag_name: 標籤名稱
        keywords: 關鍵字列表
        use_ngram: 使用 N-gram 匹配
        use_weighted: 使用加權評分
        
    Returns:
        相關性分數 (0.0-1.0)
    """
    if not keywords:
        return 0.0
    
    # 方法 1: N-gram 增強匹配（優先）
    if use_ngram:
        # 從原始關鍵字構建查詢
        query = ' '.join(keywords)
        ngrams = extract_all_ngrams(query, max_n=3)
        
        ngram_score, match_type = calculate_ngram_match_score(
            tag_name,
            ngrams,
            keywords
        )
        
        # 如果有好的 N-gram 匹配，直接返回
        if ngram_score >= 0.8:
            logger.debug(f"N-gram match: {tag_name} - {match_type} ({ngram_score:.2f})")
            return ngram_score
    
    # 方法 2: 加權關鍵字匹配
    if use_weighted:
        # 分析關鍵字重要性
        keyword_weights = analyzer.analyze_keyword_importance(keywords)
        
        # 計算加權相關性
        weighted_score = calculate_weighted_relevance(
            tag_name,
            keywords,
            keyword_weights
        )
        
        if weighted_score > 0:
            logger.debug(f"Weighted match: {tag_name} ({weighted_score:.2f})")
            return weighted_score
    
    # 方法 3: 基礎匹配（後備）
    tag_lower = tag_name.lower()
    keywords_lower = [k.lower() for k in keywords]
    
    # 完全匹配
    if tag_lower in keywords_lower:
        return 1.0
    
    max_score = 0.0
    
    for keyword in keywords_lower:
        # 前綴匹配
        if tag_lower.startswith(keyword):
            ratio = len(keyword) / len(tag_lower)
            score = 0.8 + (ratio * 0.1)
            max_score = max(max_score, score)
        # 包含匹配
        elif keyword in tag_lower:
            ratio = len(keyword) / len(tag_lower)
            score = 0.5 + (ratio * 0.2)
            max_score = max(max_score, score)
    
    return max(max_score, 0.1)


def calculate_final_score(
    tag_name: str,
    keywords: List[str],
    post_count: int,
    analyzer: KeywordAnalyzer,
    relevance_weight: float = 0.7,
    popularity_weight: float = 0.3,
    use_advanced: bool = True,
) -> Dict[str, float]:
    """
    計算最終綜合分數（升級版）
    
    Args:
        tag_name: 標籤名稱
        keywords: 關鍵字列表
        post_count: 使用次數
        relevance_weight: 相關性權重 (預設 0.7)
        popularity_weight: 流行度權重 (預設 0.3)
        use_advanced: 使用進階功能（N-gram + 加權）
        
    Returns:
        分數字典 {relevance, popularity, final, match_type}
    """
    # 計算相關性分數（使用升級版功能）
    relevance_score = calculate_relevance_score(
        tag_name,
        keywords,
        analyzer,
        use_ngram=use_advanced,
        use_weighted=use_advanced,
    )
    
    # 計算流行度分數（正規化到 0-1）
    # 使用對數尺度，避免極端值主導
    import math
    if post_count > 0:
        # log10(1M) = 6, log10(100K) = 5, log10(10K) = 4
        # 調整: 使用 log10(100M) = 8 作為上限，適應 Danbooru 數據規模
        popularity_score = min(math.log10(max(post_count, 1)) / 8, 1.0)
    else:
        popularity_score = 0.0
    
    # 計算最終分數
    final_score = (
        relevance_score * relevance_weight +
        popularity_score * popularity_weight
    )
    
    return {
        'relevance': relevance_score,
        'popularity': popularity_score,
        'final': final_score,
        'use_advanced': use_advanced
    }


def rank_tags_by_relevance(
    tags: List[Dict],
    keywords: List[str],
    analyzer: KeywordAnalyzer,
    relevance_weight: float = 0.7,
) -> List[Dict]:
    """
    根據相關性對標籤進行排序
    
    Args:
        tags: 標籤列表（包含 name 和 post_count）
        keywords: 關鍵字列表
        relevance_weight: 相關性權重
        
    Returns:
        排序後的標籤列表（添加了 relevance_score 欄位）
    """
    scored_tags = []
    
    for tag in tags:
        scores = calculate_final_score(
            tag['name'],
            keywords,
            tag['post_count'],
            analyzer,
            relevance_weight=relevance_weight,
            popularity_weight=1.0 - relevance_weight,
        )
        
        tag_with_score = {
            **tag,
            'relevance_score': scores['relevance'],
            'popularity_score': scores['popularity'],
            'final_score': scores['final']
        }
        
        scored_tags.append(tag_with_score)
    
    # 按最終分數排序
    scored_tags.sort(key=lambda x: x['final_score'], reverse=True)
    
    logger.info(
        f"Ranked {len(scored_tags)} tags by relevance "
        f"(weight: {relevance_weight:.1f})"
    )
    
    return scored_tags


def explain_score(
    tag_name: str, 
    keywords: List[str], 
    score: float,
    use_ngram: bool = True
) -> str:
    """
    解釋相關性分數（升級版）
    
    Returns:
        人類可讀的解釋
    """
    # 使用 N-gram 匹配解釋
    if use_ngram:
        from services.ngram_matcher import explain_ngram_matching
        query = ' '.join(keywords)
        return explain_ngram_matching(tag_name, query)
    
    # 基礎解釋
    tag_lower = tag_name.lower()
    
    # 檢查匹配類型
    for keyword in keywords:
        kw_lower = keyword.lower()
        
        if tag_lower == kw_lower:
            return f"完全匹配關鍵字 '{keyword}'"
        
        if tag_lower.startswith(kw_lower):
            return f"以關鍵字 '{keyword}' 開頭"
        
        if kw_lower in tag_lower:
            return f"包含關鍵字 '{keyword}'"
    
    if score > 0.5:
        return "高度相關（通過同義詞擴展）"
    elif score > 0.3:
        return "部分相關"
    else:
        return "低相關性（流行度高）"

