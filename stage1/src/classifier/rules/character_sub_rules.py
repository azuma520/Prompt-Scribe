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
        self._character_count_patterns = self._build_character_count_patterns()
        self._accessories_keywords = self._build_accessories_keywords()
        self._body_parts_keywords = self._build_body_parts_keywords()
        # _hair_keywords 已移除，邏輯已內嵌至 _is_hair() 方法
    
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
        
        # 優先級 2：配飾（需在服裝前檢查，避免誤判）
        if self._is_accessories(tag_name):
            return 'ACCESSORIES'
        
        # 優先級 3：服裝（關鍵字更具體，避免誤判）
        if self._is_clothing(tag_name):
            return 'CLOTHING'
        
        # 優先級 4：頭髮（已修復誤判問題）
        if self._is_hair(tag_name):
            return 'HAIR'
        
        # 優先級 5：身體部位（Phase 2 新增）
        if self._is_body_parts(tag_name):
            return 'BODY_PARTS'
        
        return None
    
    def _is_character_count(self, tag: str) -> bool:
        """判斷是否為角色數量"""
        # 精確匹配
        return tag in self._character_count_patterns
    
    def _is_hair(self, tag: str) -> bool:
        """判斷是否為頭髮相關"""
        # 1. 後綴匹配 - 最明確的髮相關標籤
        if tag.endswith('_hair') or tag.endswith('hair'):
            return True
        
        # 2. 必須包含 'hair' 才檢查髮色/髮長
        # 避免 'white_shirt', 'long_sleeves' 被誤判
        if 'hair' in tag:
            # 髮色、髮長詞只在包含 'hair' 時才生效
            color_length_words = {
                'long', 'short', 'medium', 'very_long',
                'blonde', 'black', 'brown', 'red', 'blue', 'green',
                'white', 'silver', 'gray', 'grey', 'pink', 'purple',
            }
            if any(word in tag for word in color_length_words):
                return True
        
        # 3. 髮型相關關鍵字（不需要包含 'hair'） - Phase 2 擴展
        hairstyle_keywords = {
            'ponytail', 'twintails', 'twin_tails', 'braid', 'braided',
            'bun', 'hair_bun', 'double_bun',
            'bob_cut', 'pixie_cut',
            'side_ponytail', 'high_ponytail', 'low_ponytail',
            'drill_hair', 'ringlets',
            # Phase 2 高頻擴展
            'ahoge', 'sidelocks', 'bangs', 'sideburns', 'side_hair',
            'hair_between_eyes', 'parted_bangs', 'swept_bangs',
            # 髮飾（Phase 2 擴展）
            'hair_ribbon', 'hair_ornament', 'hair_bow',
            'hairband', 'hairclip', 'hair_flower',
        }
        if any(word in tag for word in hairstyle_keywords):
            return True
        
        return False
    
    def _is_clothing(self, tag: str) -> bool:
        """判斷是否為服裝相關"""
        # 關鍵字匹配
        return any(word in tag for word in self._clothing_keywords)
    
    def _is_accessories(self, tag: str) -> bool:
        """判斷是否為配飾相關"""
        # 精確匹配高頻配飾
        if tag in {'jewelry', 'earrings', 'necklace', 'bracelet', 'ring', 'rings'}:
            return True
        # 關鍵字匹配
        return any(word in tag for word in self._accessories_keywords)
    
    def _is_body_parts(self, tag: str) -> bool:
        """判斷是否為身體部位"""
        # 精確匹配高頻身體部位
        if tag in {'navel', 'collarbone', 'thighs', 'teeth', 'cleavage'}:
            return True
        # 關鍵字匹配
        return any(word in tag for word in self._body_parts_keywords)
    
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
    
    # _build_hair_keywords() 已移除
    # 髮相關關鍵字現已直接定義在 _is_hair() 方法中，
    # 以實現更精確的上下文感知匹配邏輯
    
    def _build_clothing_keywords(self) -> Set[str]:
        """構建服裝關鍵字（Phase 2 擴展）"""
        return {
            # 上衣
            'shirt', 'blouse', 'top', 't-shirt', 'tshirt',
            'sweater', 'cardigan', 'hoodie',
            'jacket', 'coat', 'blazer',
            'vest', 'tank_top', 'tube_top',
            # 袖子（高頻）
            'sleeves', 'long_sleeves', 'short_sleeves', 'sleeveless',
            'detached_sleeves', 'wide_sleeves', 'puffy_sleeves',
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
            # 頭部配件（非配飾）
            'hat', 'cap', 'beret', 'helmet', 'crown', 'tiara',
            # 腿部服裝（Phase 2 高優先級擴展）
            'thighhighs', 'pantyhose', 'stockings', 'garter',
            'leg_warmers', 'knee_highs', 'over-kneehighs',
            # 內衣類（Phase 2 高優先級擴展）
            'underwear', 'panties', 'bra', 'lingerie', 'camisole',
            # 鞋類
            'boots', 'shoes', 'sandals', 'heels', 'sneakers',
            # 領飾（Phase 2 高優先級擴展）
            'necktie', 'bowtie', 'scarf', 'neckwear',
            # 服裝細節（Phase 2 擴展）
            'frills', 'ruffles', 'lace', 'buttons',
            'zipper', 'belt', 'buckle',
            # 服裝狀態（Phase 2 擴展）
            'open_clothes', 'open_shirt', 'open_jacket', 'unbuttoned',
            'torn_clothes', 'damaged_clothes',
            'wearing', 'dressed', 'clothed',
            'bare_shoulders', 'off_shoulder',
        }
    
    def _build_accessories_keywords(self) -> Set[str]:
        """構建配飾關鍵字（Phase 2 新增）"""
        return {
            # 珠寶（高頻）
            'jewelry', 'jewel',
            'earring', 'necklace', 'bracelet', 'ring', 'pendant',
            'brooch', 'piercing',
            # 眼鏡類
            'glasses', 'eyewear', 'sunglasses', 'goggles', 'monocle',
            # 手腕配飾
            'watch', 'wristwatch', 'wristband',
            # 其他配飾
            'badge', 'pin', 'medal',
        }
    
    def _build_body_parts_keywords(self) -> Set[str]:
        """構建身體部位關鍵字（Phase 2 新增）"""
        return {
            # 軀幹（高頻）
            'navel', 'collarbone', 'neck', 'shoulder', 'waist',
            'midriff', 'stomach', 'belly', 'back', 'spine',
            # 胸部相關（非成人）
            'cleavage', 'breasts', 'chest', 'bust',
            'small_breasts', 'medium_breasts', 'large_breasts',
            'flat_chest',
            # 四肢（高頻）
            'thighs', 'legs', 'leg', 'calves', 'calf', 'ankle', 'ankles',
            'feet', 'foot', 'toes',
            'arms', 'arm', 'elbow', 'wrist',
            'hands', 'hand', 'fingers', 'finger', 'palm',
            # 臀部（非成人）
            'hips', 'hip',
            # 臉部細節（高頻）
            'teeth', 'tooth', 'tongue', 'lips', 'lip',
            'chin', 'cheek', 'cheeks', 'forehead',
            'eyebrow', 'eyebrows', 'eyelash', 'eyelashes',
            # 其他
            'skin', 'muscle', 'abs',
        }

