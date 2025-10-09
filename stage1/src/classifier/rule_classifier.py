"""
基於規則的標籤分類器

階段性實作策略：
1. 先實作主分類規則（9 個）
2. 再實作高優先級副分類規則
3. 按需擴展其他副分類
"""

from typing import Optional, Tuple, Dict, List
import re

from .categories import MAIN_CATEGORIES, SUB_CATEGORIES
from .rules import (
    MainCategoryRules,
    CharacterRelatedSubRules,
    ActionPoseSubRules,
)


class RuleBasedClassifier:
    """基於規則的標籤分類器"""
    
    def __init__(self):
        """初始化分類器"""
        self.main_rules = MainCategoryRules()
        self.character_sub_rules = CharacterRelatedSubRules()
        self.action_pose_sub_rules = ActionPoseSubRules()
        
        # 統計資訊
        self.stats = {
            'total_classified': 0,
            'main_category_coverage': {},
            'sub_category_coverage': {},
            'unclassified': 0,
        }
    
    def classify(
        self, 
        tag_name: str, 
        danbooru_cat: Optional[int] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        對標籤進行分類
        
        Args:
            tag_name: 標籤名稱
            danbooru_cat: Danbooru 原始分類 (0-5)，如果有的話
        
        Returns:
            (main_category, sub_category) 元組
            main_category: 主分類（可能為 None）
            sub_category: 副分類（可能為 None）
        """
        # 標準化標籤名稱
        tag_name_lower = tag_name.lower().strip()
        
        # 步驟 0：優先使用 Danbooru 分類（如果提供）
        main_category = self.classify_by_danbooru_cat(danbooru_cat)
        
        # 步驟 1：如果 Danbooru 分類無法判定，使用規則分類
        if main_category is None:
            main_category = self.classify_main_category(tag_name_lower)
        
        if main_category is None:
            self.stats['unclassified'] += 1
            return (None, None)
        
        # 更新統計
        self.stats['total_classified'] += 1
        self.stats['main_category_coverage'][main_category] = \
            self.stats['main_category_coverage'].get(main_category, 0) + 1
        
        # 步驟 2：判斷副分類（如果該主分類有副分類）
        sub_category = self.classify_sub_category(tag_name_lower, main_category)
        
        if sub_category:
            key = f"{main_category}.{sub_category}"
            self.stats['sub_category_coverage'][key] = \
                self.stats['sub_category_coverage'].get(key, 0) + 1
        
        return (main_category, sub_category)
    
    def classify_by_danbooru_cat(self, danbooru_cat: Optional[int]) -> Optional[str]:
        """
        根據 Danbooru 原始分類直接判定主分類
        
        Danbooru Category 對應：
        - 0: General (一般標籤) -> 使用規則分類
        - 1: Artist (藝術家) -> ARTIST
        - 3: Copyright (版權作品) -> COPYRIGHT
        - 4: Character (角色) -> CHARACTER
        - 5: Meta (元數據) -> TECHNICAL
        
        Args:
            danbooru_cat: Danbooru 分類號碼
        
        Returns:
            主分類代碼，或 None（需要進一步規則判定）
        """
        if danbooru_cat is None:
            return None
        
        # Danbooru 分類映射
        danbooru_mapping = {
            1: 'ARTIST',
            3: 'COPYRIGHT',
            4: 'CHARACTER',
            5: 'TECHNICAL',
        }
        
        return danbooru_mapping.get(danbooru_cat)
    
    def classify_main_category(self, tag_name: str) -> Optional[str]:
        """
        判斷主分類
        
        Args:
            tag_name: 標籤名稱（已小寫化）
        
        Returns:
            主分類代碼，或 None
        """
        return self.main_rules.classify(tag_name)
    
    def classify_sub_category(
        self, 
        tag_name: str, 
        main_category: str
    ) -> Optional[str]:
        """
        判斷副分類（在已知主分類的情況下）
        
        Args:
            tag_name: 標籤名稱（已小寫化）
            main_category: 主分類代碼
        
        Returns:
            副分類代碼，或 None
        """
        if main_category == 'CHARACTER_RELATED':
            return self.character_sub_rules.classify(tag_name)
        elif main_category == 'ACTION_POSE':
            return self.action_pose_sub_rules.classify(tag_name)
        # 其他主分類暫時沒有副分類
        return None
    
    def classify_batch(
        self, 
        tag_data: List[Tuple[str, Optional[int]]]
    ) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """
        批次分類
        
        Args:
            tag_data: (tag_name, danbooru_cat) 元組列表
        
        Returns:
            (tag_name, main_category, sub_category) 列表
        """
        results = []
        for tag_name, danbooru_cat in tag_data:
            main_cat, sub_cat = self.classify(tag_name, danbooru_cat)
            results.append((tag_name, main_cat, sub_cat))
        return results
    
    def get_stats(self) -> Dict:
        """取得分類統計資訊"""
        total = self.stats['total_classified'] + self.stats['unclassified']
        coverage_rate = (self.stats['total_classified'] / total * 100) if total > 0 else 0
        
        return {
            'total_processed': total,
            'classified': self.stats['total_classified'],
            'unclassified': self.stats['unclassified'],
            'coverage_rate': f"{coverage_rate:.1f}%",
            'main_category_distribution': self.stats['main_category_coverage'],
            'sub_category_distribution': self.stats['sub_category_coverage'],
        }
    
    def reset_stats(self):
        """重置統計資訊"""
        self.stats = {
            'total_classified': 0,
            'main_category_coverage': {},
            'sub_category_coverage': {},
            'unclassified': 0,
        }

