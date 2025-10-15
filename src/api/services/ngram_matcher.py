"""
N-gram Matcher Service
N-gram 匹配服務 - 處理複合詞匹配
"""
from typing import List, Set, Tuple
import logging

logger = logging.getLogger(__name__)


def extract_ngrams(text: str, n: int = 2) -> List[str]:
    """
    提取 N-gram（連續 N 個詞）
    
    Args:
        text: 輸入文字
        n: N-gram 大小
        
    Returns:
        N-gram 列表
    """
    # 清理和分詞
    words = text.lower().replace(',', ' ').split()
    
    ngrams = []
    
    for i in range(len(words) - n + 1):
        # 使用底線連接（Danbooru 標籤格式）
        ngram = '_'.join(words[i:i+n])
        ngrams.append(ngram)
    
    return ngrams


def extract_all_ngrams(text: str, max_n: int = 3) -> Set[str]:
    """
    提取所有 N-gram（1-gram 到 max_n-gram）
    
    Args:
        text: 輸入文字
        max_n: 最大 N
        
    Returns:
        所有 N-gram 的集合
    """
    all_ngrams = set()
    
    # 提取單詞（1-gram）
    words = text.lower().replace(',', ' ').split()
    all_ngrams.update(words)
    
    # 提取 2-gram, 3-gram, ...
    for n in range(2, min(max_n + 1, len(words) + 1)):
        ngrams = extract_ngrams(text, n)
        all_ngrams.update(ngrams)
    
    logger.debug(f"Extracted {len(all_ngrams)} n-grams from '{text}'")
    
    return all_ngrams


def calculate_ngram_match_score(
    tag_name: str,
    ngrams: Set[str],
    original_words: List[str]
) -> Tuple[float, str]:
    """
    計算 N-gram 匹配分數
    
    Args:
        tag_name: 標籤名稱
        ngrams: N-gram 集合
        original_words: 原始單詞列表
        
    Returns:
        (匹配分數, 匹配類型)
    """
    tag_lower = tag_name.lower()
    
    # 1. 檢查完整 N-gram 匹配（最高優先級）
    # 例如: "school_uniform" 完全匹配 "school uniform" 的 bigram
    if tag_lower in ngrams:
        # 計算這是幾-gram
        gram_size = len(tag_lower.split('_'))
        # N 越大，分數越高
        score = min(0.95 + (gram_size * 0.05), 1.0)
        return (score, f'{gram_size}-gram_exact_match')
    
    # 2. 檢查標籤是否為某個 N-gram 的一部分
    for ngram in ngrams:
        if ngram in tag_lower:
            # N-gram 包含在標籤中
            ratio = len(ngram) / len(tag_lower)
            score = 0.8 + (ratio * 0.15)
            return (score, 'ngram_contained')
    
    # 3. 檢查單詞完全匹配
    for word in original_words:
        if tag_lower == word.lower():
            return (0.95, 'word_exact_match')
    
    # 4. 檢查前綴匹配
    for word in original_words:
        word_lower = word.lower()
        if tag_lower.startswith(word_lower):
            ratio = len(word_lower) / len(tag_lower)
            score = 0.7 + (ratio * 0.2)
            return (score, 'prefix_match')
        if word_lower.startswith(tag_lower):
            ratio = len(tag_lower) / len(word_lower)
            score = 0.65 + (ratio * 0.2)
            return (score, 'reverse_prefix_match')
    
    # 5. 檢查包含匹配
    for word in original_words:
        word_lower = word.lower()
        if word_lower in tag_lower:
            ratio = len(word_lower) / len(tag_lower)
            score = 0.5 + (ratio * 0.2)
            return (score, 'word_contained')
        if tag_lower in word_lower:
            ratio = len(tag_lower) / len(word_lower)
            score = 0.45 + (ratio * 0.2)
            return (score, 'reverse_contained')
    
    # 6. 無匹配
    return (0.0, 'no_match')


def analyze_query_structure(query: str) -> Dict:
    """
    分析查詢結構
    
    Returns:
        查詢分析結果
    """
    words = query.lower().replace(',', ' ').split()
    
    # 提取所有 N-gram
    bigrams = extract_ngrams(query, 2)
    trigrams = extract_ngrams(query, 3)
    all_ngrams = extract_all_ngrams(query, max_n=3)
    
    # 分析詞性分佈
    from services.keyword_analyzer import classify_word
    
    word_types = {}
    for word in words:
        word_type = classify_word(word)
        if word_type not in word_types:
            word_types[word_type] = []
        word_types[word_type].append(word)
    
    return {
        'original_words': words,
        'word_count': len(words),
        'bigrams': bigrams,
        'trigrams': trigrams,
        'all_ngrams': list(all_ngrams),
        'ngram_count': len(all_ngrams),
        'word_type_distribution': word_types,
        'has_compound_words': len(bigrams) > 0
    }


def get_search_keywords_with_priority(query: str) -> List[Tuple[str, float, str]]:
    """
    獲取搜尋關鍵字及其優先級
    
    Args:
        query: 查詢文字
        
    Returns:
        [(keyword, priority, type), ...] 列表
        priority: 優先級分數 (0-1)
        type: 關鍵字類型
    """
    analysis = analyze_query_structure(query)
    results = []
    
    # 1. N-gram（複合詞）優先級最高
    for ngram in analysis['bigrams']:
        results.append((ngram, 1.0, 'bigram'))
    
    for ngram in analysis['trigrams']:
        results.append((ngram, 1.0, 'trigram'))
    
    # 2. 單詞按詞性優先級
    from services.keyword_analyzer import analyze_keyword_importance
    
    word_weights = analyze_keyword_importance(analysis['original_words'])
    for word, weight in word_weights.items():
        results.append((word, weight, 'word'))
    
    # 排序（優先級高的在前）
    results.sort(key=lambda x: x[1], reverse=True)
    
    logger.info(
        f"Extracted {len(results)} keywords with priority "
        f"(bigrams: {len(analysis['bigrams'])}, "
        f"trigrams: {len(analysis['trigrams'])}, "
        f"words: {len(analysis['original_words'])})"
    )
    
    return results


def explain_ngram_matching(tag_name: str, query: str) -> str:
    """
    解釋 N-gram 匹配結果（用於透明度）
    
    Returns:
        人類可讀的解釋
    """
    ngrams = extract_all_ngrams(query, max_n=3)
    words = query.lower().split()
    
    score, match_type = calculate_ngram_match_score(tag_name, ngrams, words)
    
    explanations = {
        '2-gram_exact_match': f"完全匹配查詢中的複合詞",
        '3-gram_exact_match': f"完全匹配查詢中的三詞組合",
        'ngram_contained': f"包含查詢中的複合詞",
        'word_exact_match': f"完全匹配查詢中的單詞",
        'prefix_match': f"以查詢詞開頭",
        'word_contained': f"包含查詢詞",
        'no_match': f"無直接匹配（可能通過同義詞）"
    }
    
    explanation = explanations.get(match_type, "未知匹配類型")
    
    return f"{explanation}（相關性: {score:.2f}）"


# 測試和範例
if __name__ == "__main__":
    # 測試範例
    test_queries = [
        "cute girl in school uniform",
        "lonely girl in cyberpunk city",
        "happy cat sitting on chair"
    ]
    
    for query in test_queries:
        print(f"\n查詢: {query}")
        print(f"分析結果:")
        analysis = analyze_query_structure(query)
        print(f"  單詞數: {analysis['word_count']}")
        print(f"  Bigrams: {analysis['bigrams']}")
        print(f"  總 N-grams: {analysis['ngram_count']}")
        print(f"  詞性分佈: {analysis['word_type_distribution']}")
        
        keywords = get_search_keywords_with_priority(query)
        print(f"  優先級排序:")
        for kw, priority, kw_type in keywords[:10]:
            print(f"    - {kw} ({kw_type}): {priority:.2f}")

