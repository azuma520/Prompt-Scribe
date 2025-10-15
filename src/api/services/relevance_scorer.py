"""
Relevance Scoring Service
相關性評分服務 - 計算標籤與關鍵字的相關性
"""
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def calculate_relevance_score(tag_name: str, keywords: List[str]) -> float:
    """
    計算標籤與關鍵字的相關性分數
    
    Args:
        tag_name: 標籤名稱
        keywords: 關鍵字列表
        
    Returns:
        相關性分數 (0.0-1.0)
    """
    tag_lower = tag_name.lower()
    keywords_lower = [k.lower() for k in keywords]
    
    # 1. 完全匹配：1.0
    if tag_lower in keywords_lower:
        return 1.0
    
    max_score = 0.0
    
    for keyword in keywords_lower:
        # 2. 完全相等（反向）：0.95
        if keyword == tag_lower:
            max_score = max(max_score, 0.95)
            continue
        
        # 3. 前綴匹配：0.8-0.9
        if tag_lower.startswith(keyword):
            # 前綴越長，分數越高
            ratio = len(keyword) / len(tag_lower)
            score = 0.8 + (ratio * 0.1)
            max_score = max(max_score, score)
            continue
        
        if keyword.startswith(tag_lower):
            ratio = len(tag_lower) / len(keyword)
            score = 0.75 + (ratio * 0.1)
            max_score = max(max_score, score)
            continue
        
        # 4. 包含匹配：0.5-0.7
        if keyword in tag_lower:
            # 關鍵字在標籤中的位置和長度
            ratio = len(keyword) / len(tag_lower)
            score = 0.5 + (ratio * 0.2)
            max_score = max(max_score, score)
            continue
        
        if tag_lower in keyword:
            ratio = len(tag_lower) / len(keyword)
            score = 0.45 + (ratio * 0.2)
            max_score = max(max_score, score)
            continue
    
    # 5. 無匹配：0.1（保留一些基礎分）
    return max(max_score, 0.1)


def calculate_final_score(
    tag_name: str,
    keywords: List[str],
    post_count: int,
    relevance_weight: float = 0.7,
    popularity_weight: float = 0.3
) -> Dict[str, float]:
    """
    計算最終綜合分數
    
    Args:
        tag_name: 標籤名稱
        keywords: 關鍵字列表
        post_count: 使用次數
        relevance_weight: 相關性權重 (預設 0.7)
        popularity_weight: 流行度權重 (預設 0.3)
        
    Returns:
        分數字典 {relevance, popularity, final}
    """
    # 計算相關性分數
    relevance_score = calculate_relevance_score(tag_name, keywords)
    
    # 計算流行度分數（正規化到 0-1）
    # 使用對數尺度，避免極端值主導
    import math
    if post_count > 0:
        # log10(1M) = 6, log10(100K) = 5, log10(10K) = 4
        popularity_score = min(math.log10(max(post_count, 1)) / 7, 1.0)
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
        'final': final_score
    }


def rank_tags_by_relevance(
    tags: List[Dict],
    keywords: List[str],
    relevance_weight: float = 0.7
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
            relevance_weight=relevance_weight,
            popularity_weight=1.0 - relevance_weight
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


def explain_score(tag_name: str, keywords: List[str], score: float) -> str:
    """
    解釋相關性分數
    
    Returns:
        人類可讀的解釋
    """
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
        return "高度相關"
    elif score > 0.3:
        return "部分相關"
    else:
        return "低相關性（流行度高）"

