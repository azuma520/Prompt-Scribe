"""
CHARACTER_RELATED 副分類規則

階段 1 實作：
- CLOTHING（服裝）- 優先級：高
- HAIR（頭髮）- 優先級：高
- CHARACTER_COUNT（角色數量）- 優先級：中
"""

from typing import Optional, Set


class CharacterRelatedSubRules:
    """CHARACTER_RELATED 副分類規則引擎"""
    
    def __init__(self):
        """初始化規則"""
        self._clothing_keywords = self._build_clothing_keywords()
        self._hair_keywords = self._build_hair_keywords()
        self._character_count_patterns = self._build_character_count_patterns()
    
    def classify(self, tag_name: str) -> Optional[str]:
        """
        對 CHARACTER_RELATED 標籤進行副分類
        
        Args:
            tag_name: 標籤名稱（已小寫化）
        
        Returns:
            副分類代碼，或 None
        """
        # 優先級 1：角色數量（最明確）
        if self._is_character_count(tag_name):
            return 'CHARACTER_COUNT'
        
        # 優先級 2：頭髮（明顯特徵）
        if self._is_hair(tag_name):
            return 'HAIR'
        
        # 優先級 3：服裝（數量最多）
        if self._is_clothing(tag_name):
            return 'CLOTHING'
        
        # 優先級 4：身體特徵（可選，暫不實作）
        # if self._is_body_features(tag_name):
        #     return 'BODY_FEATURES'
        
        return None
    
    def _is_character_count(self, tag: str) -> bool:
        """判斷是否為角色數量"""
        # 精確匹配
        return tag in self._character_count_patterns
    
    def _is_hair(self, tag: str) -> bool:
        """判斷是否為頭髮相關"""
        # 1. 後綴匹配
        if tag.endswith('_hair') or tag.endswith('hair'):
            return True
        
        # 2. 髮型關鍵字
        if any(word in tag for word in self._hair_keywords):
            return True
        
        return False
    
    def _is_clothing(self, tag: str) -> bool:
        """判斷是否為服裝相關"""
        # 關鍵字匹配
        return any(word in tag for word in self._clothing_keywords)
    
    # ========================================================================
    # 關鍵字集合構建
    # ========================================================================
    
    def _build_character_count_patterns(self) -> Set[str]:
        """構建角色數量模式"""
        return {
            # 女性
            '1girl', '2girls', '3girls', '4girls', '5girls', '6+girls',
            'multiple_girls', 'many_girls',
            # 男性
            '1boy', '2boys', '3boys', '4boys', '5boys', '6+boys',
            'multiple_boys', 'many_boys',
            # 通用
            'solo', 'duo', 'trio', 'group',
            'solo_focus', 'multiple_persona',
            # 性別
            'male', 'female', 'male_focus', 'female_focus',
            '1male', '1female', '2males', '2females',
        }
    
    def _build_hair_keywords(self) -> Set[str]:
        """構建頭髮關鍵字"""
        return {
            # 髮型
            'ponytail', 'twintails', 'twin_tails', 'braid', 'braided',
            'bun', 'hair_bun', 'double_bun',
            'bob_cut', 'bob', 'pixie_cut',
            'side_ponytail', 'high_ponytail', 'low_ponytail',
            'drill_hair', 'ringlets',
            # 髮長（已由 *_hair 後綴覆蓋）
            'long', 'short', 'medium', 'very_long',
            # 髮色（已由 *_hair 後綴覆蓋）
            'blonde', 'black', 'brown', 'red', 'blue', 'green',
            'white', 'silver', 'gray', 'pink', 'purple',
            # 其他髮部特徵
            'ahoge', 'hair_ribbon', 'hair_ornament', 'hair_bow',
            'hairband', 'hairclip', 'hair_flower',
            'bangs', 'sideburns', 'side_hair',
        }
    
    def _build_clothing_keywords(self) -> Set[str]:
        """構建服裝關鍵字"""
        return {
            # 上衣
            'shirt', 'blouse', 'top', 't-shirt', 'tshirt',
            'sweater', 'cardigan', 'hoodie',
            'jacket', 'coat', 'blazer',
            'vest', 'tank_top', 'tube_top',
            # 下裝
            'skirt', 'pants', 'trousers', 'jeans',
            'shorts', 'leggings',
            'miniskirt', 'long_skirt', 'pleated_skirt',
            # 連身衣服
            'dress', 'gown', 'robe', 'kimono', 'yukata',
            'one-piece', 'jumpsuit', 'overalls',
            # 制服類
            'uniform', 'school_uniform', 'military_uniform',
            'maid', 'maid_dress', 'maid_outfit',
            'nurse', 'waitress', 'police',
            # 特殊服裝
            'armor', 'armored', 'plate_armor',
            'swimsuit', 'bikini', 'one-piece_swimsuit',
            'bodysuit', 'leotard', 'unitard',
            # 配件類
            'hat', 'cap', 'beret', 'helmet', 'crown',
            'glasses', 'sunglasses', 'goggles',
            'gloves', 'mittens', 'fingerless_gloves',
            'boots', 'shoes', 'sandals', 'heels', 'sneakers',
            'socks', 'stockings', 'thighhighs', 'pantyhose',
            'scarf', 'necktie', 'bowtie', 'ribbon',
            'belt', 'collar', 'choker', 'necklace',
            'earrings', 'bracelet', 'ring',
            # 服裝狀態
            'wearing', 'dressed', 'clothed',
            'bare', 'topless', 'bottomless',
            'partially_clothed', 'undressing',
        }

