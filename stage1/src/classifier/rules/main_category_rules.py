"""
主分類規則（9 個）

規則設計原則：
1. 優先使用精確匹配（完整單字）
2. 再使用模式匹配（前綴、後綴、包含）
3. 最後使用關鍵字匹配
4. 規則按優先級順序執行，先匹配的規則生效
"""

from typing import Optional, Set
import re


class MainCategoryRules:
    """主分類規則引擎"""
    
    def __init__(self):
        """初始化規則"""
        # 預編譯關鍵字集合（提升效能）
        self._character_keywords = self._build_character_keywords()
        self._objects_keywords = self._build_objects_keywords()
        self._environment_keywords = self._build_environment_keywords()
        self._composition_keywords = self._build_composition_keywords()
        self._visual_effects_keywords = self._build_visual_effects_keywords()
        self._art_style_keywords = self._build_art_style_keywords()
        self._action_pose_keywords = self._build_action_pose_keywords()
        self._quality_keywords = self._build_quality_keywords()
        self._technical_keywords = self._build_technical_keywords()
    
    def classify(self, tag_name: str) -> Optional[str]:
        """
        對標籤進行主分類
        
        Args:
            tag_name: 標籤名稱（已小寫化）
        
        Returns:
            主分類代碼，或 None
        """
        # 規則按優先級執行
        
        # 優先級 1：元資訊維度（最容易識別）
        if self._is_quality(tag_name):
            return 'QUALITY'
        if self._is_technical(tag_name):
            return 'TECHNICAL'
        
        # 優先級 2：表現維度 - 構圖（明顯特徵）
        if self._is_composition(tag_name):
            return 'COMPOSITION'
        
        # 優先級 3：內容維度 - 人物相關（最常見）
        if self._is_character_related(tag_name):
            return 'CHARACTER_RELATED'
        
        # 優先級 4：表現維度 - 其他
        if self._is_visual_effects(tag_name):
            return 'VISUAL_EFFECTS'
        if self._is_art_style(tag_name):
            return 'ART_STYLE'
        if self._is_action_pose(tag_name):
            return 'ACTION_POSE'
        
        # 優先級 5：內容維度 - 其他
        if self._is_environment(tag_name):
            return 'ENVIRONMENT'
        if self._is_objects(tag_name):
            return 'OBJECTS'
        
        return None
    
    # ========================================================================
    # 內容維度判定
    # ========================================================================
    
    def _is_character_related(self, tag: str) -> bool:
        """判斷是否為人物相關"""
        # 1. 精確匹配
        if tag in {'1girl', '2girls', '3girls', '4girls', '5girls', '6+girls',
                   '1boy', '2boys', '3boys', '4boys', '5boys', '6+boys',
                   'solo', 'solo_focus', 'multiple_girls', 'multiple_boys',
                   'male', 'female', 'male_focus', 'female_focus'}:
            return True
        
        # 2. 模式匹配
        # 頭髮相關
        if tag.endswith('_hair') or tag.endswith('hair'):
            return True
        if any(word in tag for word in ['ponytail', 'twintails', 'braid', 'bun']):
            return True
        
        # 眼睛相關
        if '_eyes' in tag or tag.endswith('eyes'):
            return True
        
        # 服裝相關（大類）
        if any(word in tag for word in self._character_keywords):
            return True
        
        # 身體特徵
        if any(word in tag for word in ['breasts', 'chest', 'muscular', 'tall', 'short', 'petite']):
            return True
        
        return False
    
    def _is_objects(self, tag: str) -> bool:
        """判斷是否為物件道具"""
        # 1. 精確匹配
        if tag in {'sword', 'gun', 'weapon', 'book', 'phone', 'cup', 
                   'chair', 'table', 'flower', 'cat', 'dog', 'bird'}:
            return True
        
        # 2. 關鍵字匹配
        if any(word in tag for word in self._objects_keywords):
            return True
        
        return False
    
    def _is_environment(self, tag: str) -> bool:
        """判斷是否為場景環境"""
        # 1. 精確匹配
        if tag in {'indoors', 'outdoors', 'inside', 'outside',
                   'forest', 'mountain', 'beach', 'ocean', 'sky',
                   'city', 'street', 'building', 'room',
                   'night', 'day', 'sunset', 'sunrise', 'morning',
                   'rain', 'snow', 'cloudy', 'sunny'}:
            return True
        
        # 2. 關鍵字匹配
        if any(word in tag for word in self._environment_keywords):
            return True
        
        return False
    
    # ========================================================================
    # 表現維度判定
    # ========================================================================
    
    def _is_composition(self, tag: str) -> bool:
        """判斷是否為構圖技法"""
        # 1. 鏡頭角度（明顯特徵）
        if tag.startswith('from_'):
            return True
        
        # 2. 精確匹配
        if tag in {'close-up', 'portrait', 'upper_body', 'lower_body',
                   'full_body', 'cowboy_shot', 'wide_shot',
                   'looking_at_viewer', 'looking_away', 'looking_back',
                   'eye_contact', 'pov'}:
            return True
        
        # 3. 關鍵字匹配
        if any(word in tag for word in self._composition_keywords):
            return True
        
        return False
    
    def _is_visual_effects(self, tag: str) -> bool:
        """判斷是否為視覺效果"""
        # 1. 光影效果（明顯特徵）
        if 'lighting' in tag or 'light' in tag or 'shadow' in tag:
            return True
        
        # 2. 精確匹配
        if tag in {'glowing', 'sparkle', 'shining', 'bright', 'dark',
                   'monochrome', 'sepia', 'colorful', 'vivid',
                   'bokeh', 'blur', 'motion_blur'}:
            return True
        
        # 3. 關鍵字匹配
        if any(word in tag for word in self._visual_effects_keywords):
            return True
        
        return False
    
    def _is_art_style(self, tag: str) -> bool:
        """判斷是否為藝術風格"""
        # 1. 精確匹配
        if tag in {'anime', 'realistic', 'semi-realistic', 'cartoon',
                   'chibi', 'sketch', 'lineart', 'watercolor',
                   'oil_painting', 'digital', 'traditional'}:
            return True
        
        # 2. 關鍵字匹配
        if any(word in tag for word in self._art_style_keywords):
            return True
        
        return False
    
    def _is_action_pose(self, tag: str) -> bool:
        """判斷是否為動作姿態"""
        # 1. 姿勢
        if tag in {'sitting', 'standing', 'lying', 'kneeling', 'crouching',
                   'leaning', 'squatting'}:
            return True
        
        # 2. 表情
        if tag in {'smile', 'smiling', 'grin', 'laughing', 'blush', 'blushing',
                   'crying', 'tears', 'angry', 'sad', 'surprised',
                   'open_mouth', 'closed_mouth'}:
            return True
        
        # 3. 動作
        if tag in {'walking', 'running', 'jumping', 'dancing', 'fighting',
                   'flying', 'swimming'}:
            return True
        
        # 4. 手勢
        if 'arms_' in tag or 'hand' in tag or 'hands_' in tag:
            return True
        
        # 5. 關鍵字
        if any(word in tag for word in self._action_pose_keywords):
            return True
        
        return False
    
    # ========================================================================
    # 元資訊維度判定
    # ========================================================================
    
    def _is_quality(self, tag: str) -> bool:
        """判斷是否為品質等級"""
        if 'quality' in tag:
            return True
        if tag in {'masterpiece', 'best', 'high', 'low', 'worst', 'normal',
                   'amazing', 'great', 'good', 'bad', 'terrible'}:
            return True
        return False
    
    def _is_technical(self, tag: str) -> bool:
        """判斷是否為技術規格"""
        # 1. 解析度相關（精確匹配，避免誤判 'forest' 等）
        if tag.endswith('res') or tag.startswith('res'):  # highres, absurdres, lowres
            return True
        if tag in {'4k', '8k', '1080p', 'hd', 'uhd', 'resolution'}:
            return True
        
        # 2. 細節相關
        if 'detailed' in tag:  # extremely_detailed, highly_detailed
            return True
        
        return False
    
    # ========================================================================
    # 關鍵字集合構建
    # ========================================================================
    
    def _build_character_keywords(self) -> Set[str]:
        """構建人物相關關鍵字"""
        return {
            # 性別數量
            'girl', 'boy', 'solo', 'male', 'female',
            # 服裝（高頻）
            'dress', 'shirt', 'skirt', 'pants', 'shorts', 'jacket', 'coat',
            'uniform', 'kimono', 'armor', 'swimsuit', 'bikini',
            'hat', 'cap', 'glasses', 'gloves', 'boots', 'shoes',
            'sleeves', 'sleeve',  # 添加袖子
            # 頭髮配飾（高頻）
            'ornament', 'ribbon',  # 添加髮飾
            # 身體
            'bare', 'nude', 'naked',
        }
    
    def _build_objects_keywords(self) -> Set[str]:
        """構建物件道具關鍵字"""
        return {
            'sword', 'weapon', 'gun', 'knife', 'bow',
            'book', 'phone', 'cup', 'bag',
            'flower', 'plant', 'rose',
            'chair', 'table', 'furniture',
            'animal', 'cat', 'dog', 'bird',
        }
    
    def _build_environment_keywords(self) -> Set[str]:
        """構建場景環境關鍵字"""
        return {
            'indoor', 'outdoor', 'inside', 'outside',
            'forest', 'mountain', 'beach', 'ocean', 'sea', 'water',
            'city', 'street', 'building', 'house', 'room',
            'sky', 'cloud', 'weather',
            'nature', 'tree', 'grass',
            # 背景相關（高頻）
            'background', 'simple_background', 'white_background',
            'black_background', 'grey_background', 'gradient_background',
        }
    
    def _build_composition_keywords(self) -> Set[str]:
        """構建構圖技法關鍵字"""
        return {
            'from', 'looking', 'view', 'angle', 'shot',
            'close', 'portrait', 'body', 'focus',
            'pov', 'perspective',
        }
    
    def _build_visual_effects_keywords(self) -> Set[str]:
        """構建視覺效果關鍵字"""
        return {
            'light', 'shadow', 'glow', 'shine', 'sparkle',
            'bright', 'dark', 'color', 'tone',
            'blur', 'bokeh', 'depth',
        }
    
    def _build_art_style_keywords(self) -> Set[str]:
        """構建藝術風格關鍵字"""
        return {
            'anime', 'realistic', 'cartoon', 'chibi',
            'sketch', 'painting', 'watercolor', 'oil',
            'style', 'art', 'vintage', 'retro',
        }
    
    def _build_action_pose_keywords(self) -> Set[str]:
        """構建動作姿態關鍵字"""
        return {
            'sitting', 'standing', 'lying', 'walking', 'running',
            'smile', 'blush', 'crying', 'angry',
            'arms', 'hands', 'legs',
            'pose', 'action', 'motion',
            'holding', 'held',  # 添加手持動作（高頻）
        }
    
    def _build_quality_keywords(self) -> Set[str]:
        """構建品質關鍵字"""
        return {
            'quality', 'masterpiece', 'best', 'worst',
            'high', 'low', 'normal', 'amazing',
        }
    
    def _build_technical_keywords(self) -> Set[str]:
        """構建技術規格關鍵字"""
        return {
            'res', 'resolution', 'detailed', 'detail',
            '4k', '8k', 'hd', 'uhd',
        }

