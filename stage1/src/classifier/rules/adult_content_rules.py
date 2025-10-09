"""
ADULT_CONTENT 主分類規則（Phase 2.5 新增）

目的：明確標記成人相關內容，便於過濾和管理

副分類：
- SEXUAL: 性行為相關
- EXPLICIT_BODY: 裸露身體部位  
- SUGGESTIVE: 暗示性內容
- CENSORSHIP: 審查相關
"""

from typing import Optional, Set


class AdultContentRules:
    """ADULT_CONTENT 分類規則引擎"""
    
    def __init__(self):
        """初始化規則"""
        self._sexual_keywords = self._build_sexual_keywords()
        self._explicit_body_keywords = self._build_explicit_body_keywords()
        self._suggestive_keywords = self._build_suggestive_keywords()
        self._censorship_keywords = self._build_censorship_keywords()
    
    def is_adult_content(self, tag: str) -> bool:
        """
        判斷是否為成人內容
        
        Args:
            tag: 標籤名稱（已小寫化）
        
        Returns:
            是否為成人內容
        """
        # 檢查是否匹配任何成人內容關鍵字
        if self._is_sexual(tag):
            return True
        if self._is_explicit_body(tag):
            return True
        if self._is_suggestive(tag):
            return True
        if self._is_censorship(tag):
            return True
        
        return False
    
    def classify_sub(self, tag: str) -> Optional[str]:
        """
        對 ADULT_CONTENT 標籤進行副分類
        
        Args:
            tag: 標籤名稱（已小寫化）
        
        Returns:
            副分類代碼，或 None
        """
        # 優先級 1: 性行為（最明確）
        if self._is_sexual(tag):
            return 'SEXUAL'
        
        # 優先級 2: 裸露身體（明確）
        if self._is_explicit_body(tag):
            return 'EXPLICIT_BODY'
        
        # 優先級 3: 審查標記
        if self._is_censorship(tag):
            return 'CENSORSHIP'
        
        # 優先級 4: 暗示性（較模糊）
        if self._is_suggestive(tag):
            return 'SUGGESTIVE'
        
        return None
    
    def _is_sexual(self, tag: str) -> bool:
        """判斷是否為性行為相關"""
        return any(word in tag for word in self._sexual_keywords)
    
    def _is_explicit_body(self, tag: str) -> bool:
        """判斷是否為裸露身體部位"""
        return any(word in tag for word in self._explicit_body_keywords)
    
    def _is_suggestive(self, tag: str) -> bool:
        """判斷是否為暗示性內容"""
        return any(word in tag for word in self._suggestive_keywords)
    
    def _is_censorship(self, tag: str) -> bool:
        """判斷是否為審查相關"""
        return any(word in tag for word in self._censorship_keywords)
    
    # ========================================================================
    # 關鍵字集合構建
    # ========================================================================
    
    def _build_sexual_keywords(self) -> Set[str]:
        """構建性行為關鍵字"""
        return {
            # 性行為（高頻）
            'sex', 'hetero', 'yuri', 'yaoi',
            'masturbation', 'masturbating',
            # 具體行為
            'oral', 'fellatio', 'cunnilingus',
            'paizuri', 'handjob', 'footjob',
            'penetration', 'penetrating',
            'ejaculation', 'cum', 'cumming',
            # 性相關描述
            'sexual', 'erotic', 'explicit',
            'intercourse', 'orgasm',
        }
    
    def _build_explicit_body_keywords(self) -> Set[str]:
        """構建裸露身體部位關鍵字"""
        return {
            # 明確裸露（高頻）
            'nipples', 'areola', 'areolae',
            'penis', 'pussy', 'vagina', 'anus',
            'ass', 'buttocks', 'butt',
            'genitals', 'genital',
            # 裸露狀態
            'nude', 'naked', 'nudity',
            'topless', 'bottomless',
            'completely_nude', 'fully_nude',
            'breasts_out', 'nipples_visible',
            # 特定部位
            'pubic', 'pubic_hair',
            'crotch', 'groin',
        }
    
    def _build_suggestive_keywords(self) -> Set[str]:
        """構建暗示性內容關鍵字"""
        return {
            # 暗示性姿勢
            'sexually_suggestive', 'suggestive',
            'seductive', 'provocative', 'sensual',
            'inviting', 'tempting',
            # 暗示性表情
            'bedroom_eyes', 'come_hither',
            'ahegao', 'orgasm_face',
            # 情境
            'erotic_pose', 'sexual_pose',
        }
    
    def _build_censorship_keywords(self) -> Set[str]:
        """構建審查相關關鍵字"""
        return {
            # 審查標記（高頻）
            'censored', 'uncensored',
            'mosaic_censoring', 'mosaic_censor',
            'bar_censor', 'bars_censor',
            'convenient_censoring',
            'censorship', 'censor',
            # 審查類型
            'blurred', 'pixelated',
            'covered', 'obscured',
        }

