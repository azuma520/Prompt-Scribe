"""
THEME_CONCEPT 主分類規則（Phase 2.5 新增）

目的：處理概念性、主題性標籤

副分類：
- SEASON: 季節
- HOLIDAY: 節日
- TIME: 時間
- WEATHER: 天氣
- CONCEPT: 抽象概念
"""

from typing import Optional, Set


class ThemeConceptRules:
    """THEME_CONCEPT 分類規則引擎"""
    
    def __init__(self):
        """初始化規則"""
        self._season_keywords = self._build_season_keywords()
        self._holiday_keywords = self._build_holiday_keywords()
        self._time_keywords = self._build_time_keywords()
        self._weather_keywords = self._build_weather_keywords()
        self._concept_keywords = self._build_concept_keywords()
    
    def is_theme_concept(self, tag: str) -> bool:
        """
        判斷是否為主題概念
        
        Args:
            tag: 標籤名稱（已小寫化）
        
        Returns:
            是否為主題概念
        """
        # 檢查是否匹配任何主題概念關鍵字
        if self._is_season(tag):
            return True
        if self._is_holiday(tag):
            return True
        if self._is_time(tag):
            return True
        if self._is_weather(tag):
            return True
        if self._is_concept(tag):
            return True
        
        return False
    
    def classify_sub(self, tag: str) -> Optional[str]:
        """
        對 THEME_CONCEPT 標籤進行副分類
        
        Args:
            tag: 標籤名稱（已小寫化）
        
        Returns:
            副分類代碼，或 None
        """
        # 優先級 1: 季節（明確）
        if self._is_season(tag):
            return 'SEASON'
        
        # 優先級 2: 節日（明確）
        if self._is_holiday(tag):
            return 'HOLIDAY'
        
        # 優先級 3: 時間（較明確）
        if self._is_time(tag):
            return 'TIME'
        
        # 優先級 4: 天氣（較明確）
        if self._is_weather(tag):
            return 'WEATHER'
        
        # 優先級 5: 概念（較模糊）
        if self._is_concept(tag):
            return 'CONCEPT'
        
        return None
    
    def _is_season(self, tag: str) -> bool:
        """判斷是否為季節"""
        return any(word in tag for word in self._season_keywords)
    
    def _is_holiday(self, tag: str) -> bool:
        """判斷是否為節日"""
        return any(word in tag for word in self._holiday_keywords)
    
    def _is_time(self, tag: str) -> bool:
        """判斷是否為時間"""
        return any(word in tag for word in self._time_keywords)
    
    def _is_weather(self, tag: str) -> bool:
        """判斷是否為天氣"""
        return any(word in tag for word in self._weather_keywords)
    
    def _is_concept(self, tag: str) -> bool:
        """判斷是否為抽象概念"""
        return any(word in tag for word in self._concept_keywords)
    
    # ========================================================================
    # 關鍵字集合構建
    # ========================================================================
    
    def _build_season_keywords(self) -> Set[str]:
        """構建季節關鍵字"""
        return {
            # 四季
            'spring', 'spring_season', 'springtime',
            'summer', 'summer_season', 'summertime',
            'autumn', 'fall', 'autumn_season', 'fall_season',
            'winter', 'winter_season', 'wintertime',
            # 季節相關
            'seasonal', 'season',
        }
    
    def _build_holiday_keywords(self) -> Set[str]:
        """構建節日關鍵字"""
        return {
            # 西方節日
            'christmas', 'xmas', 'santa',
            'halloween', 'jack-o-lantern',
            'valentine', 'valentines',
            'easter', 'easter_egg',
            'thanksgiving',
            # 其他節日
            'new_year', 'new_years',
            'birthday', 'anniversary',
            'wedding', 'graduation',
            # 節日相關
            'holiday', 'celebration', 'festival',
            'party', 'event',
        }
    
    def _build_time_keywords(self) -> Set[str]:
        """構建時間關鍵字"""
        return {
            # 時段（已在 ENVIRONMENT 中，這裡僅作為概念性標籤）
            'time', 'timeline',
            # 時期
            'past', 'present', 'future',
            'ancient', 'modern', 'contemporary',
            'medieval', 'futuristic',
            # 時間相關概念
            'temporal', 'chronological',
        }
    
    def _build_weather_keywords(self) -> Set[str]:
        """構建天氣關鍵字"""
        return {
            # 天氣狀況（部分與 ENVIRONMENT 重疊，但作為概念性標籤）
            'weather',
            # 特殊天氣
            'storm', 'stormy', 'lightning', 'thunder',
            'fog', 'foggy', 'mist', 'misty',
            'wind', 'windy', 'breeze',
            'humid', 'humidity',
        }
    
    def _build_concept_keywords(self) -> Set[str]:
        """構建抽象概念關鍵字"""
        return {
            # 情感概念
            'love', 'romance', 'romantic',
            'friendship', 'friends',
            'hate', 'hatred',
            'peace', 'peaceful',
            'war', 'battle', 'conflict',
            # 抽象概念（高頻）
            'dream', 'dreaming', 'nightmare',
            'fantasy', 'fantastical',
            'reality', 'real',
            'magic', 'magical',
            'mystery', 'mysterious',
            # 狀態概念
            'alternate_costume', 'alternate_outfit',
            'crossover', 'collaboration',
            'parody', 'reference',
            # 其他
            'concept', 'conceptual',
            'theme', 'themed',
            'style_parody',
        }

