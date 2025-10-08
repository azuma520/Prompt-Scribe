"""
ACTION_POSE 副分類規則

階段 1 實作：
- POSE（姿勢）- 靜態姿勢
- EXPRESSION（表情）- 面部表情和情緒
"""

from typing import Optional, Set


class ActionPoseSubRules:
    """ACTION_POSE 副分類規則引擎"""
    
    def __init__(self):
        """初始化規則"""
        self._pose_keywords = self._build_pose_keywords()
        self._expression_keywords = self._build_expression_keywords()
    
    def classify(self, tag_name: str) -> Optional[str]:
        """
        對 ACTION_POSE 標籤進行副分類
        
        Args:
            tag_name: 標籤名稱（已小寫化）
        
        Returns:
            副分類代碼，或 None
        """
        # 優先級 1：表情（更明確）
        if self._is_expression(tag_name):
            return 'EXPRESSION'
        
        # 優先級 2：姿勢
        if self._is_pose(tag_name):
            return 'POSE'
        
        # 優先級 3：動作（暫不細分，歸入 POSE）
        # 優先級 4：手勢（暫不細分，歸入 POSE）
        
        return None
    
    def _is_expression(self, tag: str) -> bool:
        """判斷是否為表情"""
        return any(word in tag for word in self._expression_keywords)
    
    def _is_pose(self, tag: str) -> bool:
        """判斷是否為姿勢"""
        return any(word in tag for word in self._pose_keywords)
    
    # ========================================================================
    # 關鍵字集合構建
    # ========================================================================
    
    def _build_expression_keywords(self) -> Set[str]:
        """構建表情關鍵字"""
        return {
            # 正面表情
            'smile', 'smiling', 'grin', 'grinning',
            'laugh', 'laughing', 'giggle',
            'happy', 'cheerful', 'joyful',
            'blush', 'blushing', 'embarrassed',
            # 負面表情
            'crying', 'tears', 'teary', 'sobbing',
            'sad', 'sadness', 'depressed',
            'angry', 'anger', 'annoyed', 'frown', 'frowning',
            'scared', 'fear', 'afraid', 'terrified',
            'worried', 'anxious', 'nervous',
            'disgust', 'disgusted',
            # 中性/其他表情
            'surprised', 'shock', 'shocked', 'stunned',
            'confused', 'puzzled',
            'serious', 'stern',
            'neutral', 'expressionless', 'blank',
            'sleepy', 'tired',
            # 嘴部
            'open_mouth', 'closed_mouth', 'mouth_open', 'mouth_closed',
            'tongue', 'tongue_out', 'lips', 'pout', 'pouting',
            # 眼睛（表情相關）
            'closed_eyes', 'one_eye_closed', 'wink', 'winking',
            'wide_eyes', 'narrowed_eyes',
            '>_<', '^_^', 'x_x',
            # 眉毛
            'raised_eyebrow', 'furrowed_brow',
        }
    
    def _build_pose_keywords(self) -> Set[str]:
        """構建姿勢關鍵字"""
        return {
            # 基本姿勢
            'sitting', 'sit', 'seated',
            'standing', 'stand', 'upright',
            'lying', 'laying', 'on_back', 'on_side', 'on_stomach',
            'kneeling', 'kneel',
            'crouching', 'crouch', 'squatting', 'squat',
            'leaning', 'lean',
            # 動態動作
            'walking', 'walk',
            'running', 'run', 'sprint', 'sprinting',
            'jumping', 'jump', 'leap', 'leaping',
            'dancing', 'dance',
            'fighting', 'fight', 'combat',
            'flying', 'fly', 'floating', 'float',
            'swimming', 'swim',
            'climbing', 'climb',
            'falling', 'fall',
            # 手部姿勢
            'arms_up', 'arms_raised',
            'arms_behind_back', 'arms_behind_head',
            'arms_crossed', 'crossed_arms',
            'hands_on_hips', 'hand_on_hip',
            'hands_together', 'hands_clasped',
            'hand_up', 'hand_on_own_face', 'hand_on_own_head',
            'reaching', 'reaching_out',
            'waving', 'wave', 'pointing', 'point',
            'peace_sign', 'v_sign', 'thumbs_up',
            'fist', 'clenched_fist',
            # 腿部姿勢
            'legs_crossed', 'crossed_legs',
            'legs_apart', 'legs_spread',
            'one_leg_raised',
            'on_tiptoes', 'tiptoes',
            # 身體彎曲
            'bent_over', 'bending',
            'arched_back', 'back_arch',
            'stretching', 'stretch',
            # 互動姿勢
            'hugging', 'hug', 'embrace', 'embracing',
            'kissing', 'kiss',
            'holding_hands', 'hand_holding',
            'carrying', 'carry', 'princess_carry',
            'piggyback', 'on_shoulders',
            # 放鬆姿勢
            'relaxed', 'casual',
            'sleeping', 'sleep', 'asleep',
            'resting', 'rest',
        }

