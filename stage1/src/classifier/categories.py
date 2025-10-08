"""
分類類別定義

採用階段性副分類架構：
- 主分類：9 個（全部實作）
- 副分類：階段性添加（優先高價值類別）
"""

from typing import Dict, List, Optional

# ============================================================================
# 主分類定義（9 個）
# ============================================================================

MAIN_CATEGORIES = {
    # 內容維度
    'CHARACTER_RELATED': '人物相關',
    'OBJECTS': '物件道具',
    'ENVIRONMENT': '場景環境',
    
    # 表現維度
    'COMPOSITION': '構圖技法',
    'VISUAL_EFFECTS': '視覺效果',
    'ART_STYLE': '藝術風格',
    'ACTION_POSE': '動作姿態',
    
    # 元資訊維度
    'QUALITY': '品質等級',
    'TECHNICAL': '技術規格',
}

# ============================================================================
# 副分類定義（階段性實作）
# ============================================================================

SUB_CATEGORIES = {
    'CHARACTER_RELATED': {
        'CLOTHING': '服裝',           # 優先級：高
        'HAIR': '頭髮',               # 優先級：高
        'CHARACTER_COUNT': '角色數量', # 優先級：中
        'BODY_FEATURES': '身體特徵',   # 優先級：低（可選）
    },
    'ACTION_POSE': {
        'POSE': '姿勢',               # sitting, standing
        'EXPRESSION': '表情',         # smile, blush
    },
    # 其他主分類暫時沒有副分類，按需擴展
}

# ============================================================================
# 分類描述（用於說明和文件）
# ============================================================================

CATEGORY_DESCRIPTIONS = {
    'CHARACTER_RELATED': {
        'description': '描述人物本身及其外觀屬性的標籤',
        'examples': ['1girl', 'long_hair', 'school_uniform', 'blue_eyes'],
        'keywords': ['girl', 'boy', 'hair', 'dress', 'uniform', 'eyes'],
    },
    'OBJECTS': {
        'description': '描述獨立存在的物品，不是人物身體的一部分',
        'examples': ['sword', 'book', 'flower', 'chair'],
        'keywords': ['sword', 'weapon', 'book', 'flower', 'furniture'],
    },
    'ENVIRONMENT': {
        'description': '描述場景、地點、背景環境的標籤',
        'examples': ['indoors', 'forest', 'night', 'rain'],
        'keywords': ['indoors', 'outdoors', 'forest', 'city', 'weather'],
    },
    'COMPOSITION': {
        'description': '描述畫面如何取景、構圖、視角',
        'examples': ['from_above', 'close-up', 'looking_at_viewer'],
        'keywords': ['from_', 'close', 'full_body', 'looking', 'angle'],
    },
    'VISUAL_EFFECTS': {
        'description': '描述光影、色彩、特效等視覺呈現',
        'examples': ['backlighting', 'glowing', 'monochrome'],
        'keywords': ['lighting', 'light', 'shadow', 'glow', 'color'],
    },
    'ART_STYLE': {
        'description': '描述繪畫/藝術風格、技法、流派',
        'examples': ['anime', 'realistic', 'sketch', 'watercolor'],
        'keywords': ['anime', 'realistic', 'sketch', 'painting', 'style'],
    },
    'ACTION_POSE': {
        'description': '描述人物的姿勢、動作、表情、情緒',
        'examples': ['sitting', 'smile', 'walking', 'arms_up'],
        'keywords': ['sitting', 'standing', 'smile', 'walking', 'arms'],
    },
    'QUALITY': {
        'description': '描述圖像品質的主觀評價',
        'examples': ['masterpiece', 'best_quality', 'low_quality'],
        'keywords': ['quality', 'masterpiece', 'best', 'worst'],
    },
    'TECHNICAL': {
        'description': '描述圖像的技術參數和格式',
        'examples': ['highres', 'absurdres', '4k'],
        'keywords': ['res', 'resolution', 'detailed', '4k', '8k'],
    },
}

# ============================================================================
# 輔助函式
# ============================================================================

def get_main_category_name(code: str) -> Optional[str]:
    """取得主分類的中文名稱"""
    return MAIN_CATEGORIES.get(code)

def get_sub_category_name(main_code: str, sub_code: str) -> Optional[str]:
    """取得副分類的中文名稱"""
    if main_code in SUB_CATEGORIES:
        return SUB_CATEGORIES[main_code].get(sub_code)
    return None

def get_all_sub_categories(main_code: str) -> Dict[str, str]:
    """取得某主分類的所有副分類"""
    return SUB_CATEGORIES.get(main_code, {})

def has_sub_categories(main_code: str) -> bool:
    """檢查某主分類是否有副分類"""
    return main_code in SUB_CATEGORIES

def list_all_categories() -> List[tuple]:
    """列出所有分類（主分類 + 副分類）"""
    result = []
    for main_code, main_name in MAIN_CATEGORIES.items():
        result.append(('main', main_code, main_name, None))
        if main_code in SUB_CATEGORIES:
            for sub_code, sub_name in SUB_CATEGORIES[main_code].items():
                result.append(('sub', main_code, main_name, (sub_code, sub_name)))
    return result

