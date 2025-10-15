"""
Keyword Expander Service
關鍵字擴展服務 - 使用同義詞字典擴展搜尋關鍵字
"""
import yaml
from pathlib import Path
from typing import List, Set, Dict
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class KeywordExpander:
    """關鍵字擴展器"""
    
    def __init__(self, synonyms_file: str = "data/keyword_synonyms.yaml"):
        """初始化關鍵字擴展器"""
        self.synonyms: Dict[str, Dict[str, List[str]]] = {}
        self.synonyms_file = synonyms_file
        self._load_synonyms()
        # 載入擴展同義詞
        self._load_extended_synonyms()
    
    def _load_synonyms(self):
        """載入同義詞字典"""
        try:
            # 構建絕對路徑
            base_path = Path(__file__).parent.parent
            synonyms_path = base_path / self.synonyms_file
            
            if not synonyms_path.exists():
                logger.warning(f"Synonyms file not found: {synonyms_path}")
                return
            
            with open(synonyms_path, 'r', encoding='utf-8') as f:
                self.synonyms = yaml.safe_load(f) or {}
            
            # 統計同義詞數量
            total_entries = sum(
                len(category_syns) 
                for category_syns in self.synonyms.values()
            )
            logger.info(f"✅ Loaded {total_entries} synonym entries from {len(self.synonyms)} categories")
            
        except Exception as e:
            logger.error(f"❌ Failed to load synonyms: {e}")
            self.synonyms = {}
    
    def _load_extended_synonyms(self):
        """載入擴展同義詞字典"""
        try:
            base_path = Path(__file__).parent.parent
            extended_path = base_path / "data/keyword_synonyms_extended.yaml"
            
            if not extended_path.exists():
                logger.info("Extended synonyms file not found, skipping")
                return
            
            with open(extended_path, 'r', encoding='utf-8') as f:
                extended_syns = yaml.safe_load(f) or {}
            
            # 合併到現有同義詞
            for category, words in extended_syns.items():
                if category not in self.synonyms:
                    self.synonyms[category] = {}
                self.synonyms[category].update(words)
            
            logger.info(f"✅ Loaded extended synonyms, total categories: {len(self.synonyms)}")
            
        except Exception as e:
            logger.warning(f"Failed to load extended synonyms: {e}")
    
    def expand_keyword(self, keyword: str) -> Set[str]:
        """
        擴展單個關鍵字
        
        Args:
            keyword: 原始關鍵字
            
        Returns:
            擴展後的關鍵字集合(包含原始關鍵字)
        """
        keyword = keyword.lower().strip()
        expanded = {keyword}  # 始終包含原始關鍵字
        
        # 在所有分類中搜尋匹配
        for category, synonyms_dict in self.synonyms.items():
            if keyword in synonyms_dict:
                # 找到匹配,添加所有同義詞
                expanded.update(synonyms_dict[keyword])
                logger.debug(f"Expanded '{keyword}' -> {synonyms_dict[keyword]}")
        
        return expanded
    
    def expand_keywords(self, keywords: List[str]) -> List[str]:
        """
        擴展關鍵字列表
        
        Args:
            keywords: 原始關鍵字列表
            
        Returns:
            擴展後的關鍵字列表(去重)
        """
        all_expanded = set()
        
        for keyword in keywords:
            expanded = self.expand_keyword(keyword)
            all_expanded.update(expanded)
        
        result = list(all_expanded)
        logger.info(f"Expanded {len(keywords)} keywords -> {len(result)} keywords")
        
        return result
    
    def expand_query(self, query: str) -> tuple[List[str], List[str]]:
        """
        擴展查詢字串
        
        Args:
            query: 原始查詢字串
            
        Returns:
            (原始關鍵字列表, 擴展後的關鍵字列表)
        """
        # 提取關鍵字(簡化版:空格分割)
        original_keywords = [
            kw.strip().lower() 
            for kw in query.split() 
            if kw.strip()
        ]
        
        # 擴展關鍵字
        expanded_keywords = self.expand_keywords(original_keywords)
        
        return original_keywords, expanded_keywords
    
    def get_category_keywords(self, category: str) -> Dict[str, List[str]]:
        """
        獲取特定分類的所有關鍵字
        
        Args:
            category: 分類名稱
            
        Returns:
            該分類的同義詞字典
        """
        return self.synonyms.get(category, {})
    
    def get_all_categories(self) -> List[str]:
        """獲取所有分類名稱"""
        return list(self.synonyms.keys())
    
    def reload_synonyms(self):
        """重新載入同義詞字典"""
        self._load_synonyms()


# 全域擴展器實例
@lru_cache()
def get_keyword_expander() -> KeywordExpander:
    """獲取關鍵字擴展器單例"""
    return KeywordExpander()


# 便捷函數
def expand_query(query: str) -> tuple[List[str], List[str]]:
    """擴展查詢(便捷函數)"""
    expander = get_keyword_expander()
    return expander.expand_query(query)


def expand_keywords(keywords: List[str]) -> List[str]:
    """擴展關鍵字列表(便捷函數)"""
    expander = get_keyword_expander()
    return expander.expand_keywords(keywords)

