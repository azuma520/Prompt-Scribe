"""
Tag Combination Analyzer
標籤組合分析服務 - 分析和建議標籤組合模式
"""
from typing import List, Dict, Set, Tuple, Optional
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


# 預定義的標籤組合模式（基於 Danbooru 常見模式）
COMBINATION_PATTERNS = {
    # 角色相關組合
    'character_basic': {
        'name': '基礎角色',
        'tags': ['1girl', 'solo'],
        'description': '單一女性角色的基礎設定',
        'popularity': 'very_popular',
        'optional_add': ['long_hair', 'smile', 'looking_at_viewer']
    },
    'character_duo': {
        'name': '雙人角色',
        'tags': ['1girl', '1boy'],
        'description': '一男一女的組合',
        'popularity': 'popular',
        'optional_add': ['couple', 'holding_hands', 'facing_each_other']
    },
    'character_group_girls': {
        'name': '多位女孩',
        'tags': ['2girls', 'yuri'],
        'description': '兩位女性角色',
        'popularity': 'popular',
        'optional_add': ['holding_hands', 'looking_at_another', 'smile']
    },
    
    # 場景組合
    'school_scene': {
        'name': '校園場景',
        'tags': ['school_uniform', 'classroom'],
        'description': '學校教室場景',
        'popularity': 'very_popular',
        'optional_add': ['desk', 'window', 'blackboard', 'sitting']
    },
    'outdoor_nature': {
        'name': '戶外自然',
        'tags': ['outdoors', 'nature'],
        'description': '戶外自然場景',
        'popularity': 'popular',
        'optional_add': ['tree', 'grass', 'sky', 'day']
    },
    'city_night': {
        'name': '城市夜景',
        'tags': ['city', 'night', 'cityscape'],
        'description': '城市夜晚場景',
        'popularity': 'moderate',
        'optional_add': ['city_lights', 'neon', 'street', 'building']
    },
    
    # 風格組合
    'cyberpunk_style': {
        'name': '賽博龐克風格',
        'tags': ['cyberpunk', 'neon', 'futuristic'],
        'description': '賽博龐克科幻風格',
        'popularity': 'moderate',
        'optional_add': ['city', 'night', 'glowing', 'technology']
    },
    'fantasy_style': {
        'name': '奇幻風格',
        'tags': ['fantasy', 'magical'],
        'description': '魔法奇幻風格',
        'popularity': 'moderate',
        'optional_add': ['castle', 'dragon', 'sword', 'mystical']
    },
    
    # 氛圍組合
    'romantic_mood': {
        'name': '浪漫氛圍',
        'tags': ['romantic', 'sunset', 'couple'],
        'description': '浪漫場景設定',
        'popularity': 'moderate',
        'optional_add': ['flower', 'smile', 'holding_hands', 'pink']
    },
    'action_scene': {
        'name': '動作場景',
        'tags': ['action', 'dynamic'],
        'description': '充滿動感的場景',
        'popularity': 'moderate',
        'optional_add': ['running', 'fighting', 'weapon', 'motion_blur']
    },
}


# 分類標籤清單（用於平衡檢查）
CATEGORY_TAGS = {
    'CHARACTER': ['1girl', '1boy', 'solo', '2girls', 'multiple_girls'],
    'CHARACTER_RELATED': ['long_hair', 'short_hair', 'blue_eyes', 'smile', 'breasts'],
    'CLOTHING': ['school_uniform', 'dress', 'casual', 'formal'],
    'ENVIRONMENT': ['city', 'room', 'outdoors', 'classroom', 'beach'],
    'TIME': ['night', 'day', 'sunset', 'morning'],
    'STYLE': ['cyberpunk', 'anime', 'realistic', 'fantasy'],
    'ACTION': ['sitting', 'standing', 'running', 'looking_at_viewer'],
    'QUALITY': ['highres', 'masterpiece', 'best_quality', 'detailed'],
}


def analyze_tag_balance(tags: List[str]) -> Dict:
    """
    分析標籤的分類平衡
    
    Returns:
        分類分佈和建議
    """
    # 統計各分類的標籤數
    category_counts = defaultdict(int)
    tag_categories = {}
    
    tags_lower = [t.lower() for t in tags]
    
    for tag in tags_lower:
        for category, category_tags in CATEGORY_TAGS.items():
            if tag in [ct.lower() for ct in category_tags]:
                category_counts[category] += 1
                tag_categories[tag] = category
                break
    
    # 計算平衡分數
    num_categories = len(category_counts)
    balance_score = min(num_categories * 20, 100)  # 每個分類 +20 分
    
    # 生成建議
    suggestions = []
    
    if category_counts.get('CHARACTER', 0) == 0:
        suggestions.append("建議添加角色標籤（如 1girl, 1boy）")
    
    if category_counts.get('ENVIRONMENT', 0) == 0:
        suggestions.append("建議添加環境標籤（如 city, room, outdoors）")
    
    if category_counts.get('STYLE', 0) == 0 and len(tags) > 5:
        suggestions.append("可考慮添加風格標籤（如 anime, realistic）")
    
    return {
        'category_distribution': dict(category_counts),
        'balance_score': balance_score,
        'num_categories': num_categories,
        'suggestions': suggestions
    }


def suggest_tag_combinations(
    base_tags: List[str],
    max_combinations: int = 5
) -> List[Dict]:
    """
    基於基礎標籤建議組合
    
    Args:
        base_tags: 已有的標籤
        max_combinations: 最多返回幾個組合
        
    Returns:
        建議的組合列表
    """
    suggestions = []
    base_tags_lower = [t.lower() for t in base_tags]
    base_tags_set = set(base_tags_lower)
    
    # 檢查每個預定義模式
    for pattern_id, pattern in COMBINATION_PATTERNS.items():
        # 計算匹配度
        pattern_tags = set(t.lower() for t in pattern['tags'])
        matching_tags = pattern_tags.intersection(base_tags_set)
        
        # 如果有部分匹配，建議完整模式
        if len(matching_tags) > 0 and len(matching_tags) < len(pattern_tags):
            # 計算還需要的標籤
            missing_tags = pattern_tags - base_tags_set
            
            combo = {
                'id': pattern_id,
                'name': pattern['name'],
                'description': pattern['description'],
                'existing_tags': list(matching_tags),
                'suggested_adds': list(missing_tags),
                'optional_adds': pattern.get('optional_add', []),
                'popularity': pattern['popularity'],
                'match_rate': len(matching_tags) / len(pattern_tags),
                'complete_combo': list(pattern_tags)
            }
            
            suggestions.append(combo)
    
    # 按匹配率排序
    suggestions.sort(key=lambda x: x['match_rate'], reverse=True)
    
    return suggestions[:max_combinations]


def suggest_complementary_tags(
    existing_tags: List[str],
    all_tags_data: Optional[List[Dict]] = None
) -> Dict[str, List[str]]:
    """
    建議互補標籤
    
    基於已有標籤，建議可以添加的標籤以豐富畫面
    
    Args:
        existing_tags: 已有的標籤
        all_tags_data: 所有可用標籤的數據（可選）
        
    Returns:
        {category: [suggested_tags]} 字典
    """
    balance = analyze_tag_balance(existing_tags)
    suggestions = {
        'character': [],
        'environment': [],
        'style': [],
        'action': [],
        'quality': []
    }
    
    # 根據缺失的分類建議
    existing_categories = set(balance['category_distribution'].keys())
    
    if 'CHARACTER' not in existing_categories:
        suggestions['character'] = ['1girl', '1boy', 'solo']
    
    if 'ENVIRONMENT' not in existing_categories:
        suggestions['environment'] = ['outdoors', 'city', 'room', 'beach']
    
    if 'STYLE' not in existing_categories:
        suggestions['style'] = ['anime', 'realistic', 'cyberpunk', 'fantasy']
    
    if 'ACTION' not in existing_categories:
        suggestions['action'] = ['looking_at_viewer', 'smile', 'sitting', 'standing']
    
    if 'QUALITY' not in existing_categories and len(existing_tags) > 3:
        suggestions['quality'] = ['highres', 'masterpiece', 'best_quality']
    
    # 移除空列表
    suggestions = {k: v for k, v in suggestions.items() if v}
    
    return suggestions


def build_complete_prompts(
    base_tags: List[str],
    combinations: List[Dict]
) -> List[Dict]:
    """
    建立完整的 prompt 建議
    
    Args:
        base_tags: 基礎標籤
        combinations: 建議的組合
        
    Returns:
        完整的 prompt 建議列表
    """
    prompts = []
    
    for combo in combinations:
        # 建立完整標籤列表
        all_tags = base_tags + combo['suggested_adds']
        
        # 基礎版本
        basic_prompt = ', '.join(all_tags)
        
        # 擴展版本（添加可選標籤）
        extended_tags = all_tags + combo['optional_adds'][:3]
        extended_prompt = ', '.join(extended_tags)
        
        prompts.append({
            'theme': combo['name'],
            'basic': basic_prompt,
            'extended': extended_prompt,
            'description': combo['description'],
            'popularity': combo['popularity']
        })
    
    return prompts


# 測試和範例
if __name__ == "__main__":
    # 測試範例
    test_tags = ["1girl", "long_hair"]
    
    print(f"基礎標籤: {test_tags}")
    print("\n=== 平衡分析 ===")
    balance = analyze_tag_balance(test_tags)
    print(f"分類分佈: {balance['category_distribution']}")
    print(f"平衡分數: {balance['balance_score']}")
    print(f"建議: {balance['suggestions']}")
    
    print("\n=== 組合建議 ===")
    combos = suggest_tag_combinations(test_tags)
    for combo in combos:
        print(f"\n{combo['name']} ({combo['popularity']}):")
        print(f"  描述: {combo['description']}")
        print(f"  需要添加: {combo['suggested_adds']}")
        print(f"  可選: {combo['optional_adds'][:3]}")
    
    print("\n=== 互補標籤 ===")
    complementary = suggest_complementary_tags(test_tags)
    for category, tags in complementary.items():
        print(f"{category}: {tags[:3]}")

