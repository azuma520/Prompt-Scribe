"""
Tag 別名映射與快速調整控件配置
確保範例標籤與資料庫 canonical tags 一致
"""

# ============================================
# Tag 別名映射（教學詞 → 資料庫標準詞）
# ============================================

TAG_ALIAS_MAP = {
    # 外觀描述
    "beautiful_kimono": "kimono",
    "pink_theme": "pastel_colors",
    "cute_expression": "cute",
    "elegant_pose": "elegant",
    
    # 氛圍與情緒
    "magical": "magical_aura",
    "dreamy": "dreamy_atmosphere",
    "mysterious": "mysterious_atmosphere",
    "peaceful": "peaceful_atmosphere",
    "lonely": "melancholic",
    
    # 場景元素
    "starry_background": "starry_sky",
    "moonlit": "moonlight",
    "sunset_colors": "sunset",
    "forest_scene": "forest",
    
    # 風格
    "anime_art": "anime_style",
    "realistic_art": "photorealistic",
    "painterly": "painting_(medium)",
    "digital": "digital_art",
    
    # 品質詞
    "high_res": "highres",
    "detailed": "highly_detailed",
    "good_quality": "high_quality",
}


# ============================================
# 快速調整控件映射
# ============================================

QUICK_ADJUSTMENTS = {
    "更夢幻": {
        "add": [
            "light_particles",
            "soft_focus",
            "bloom_effect",
            "glowing",
            "ethereal",
            "dreamy_atmosphere"
        ],
        "remove": [
            "sharp_focus",
            "photorealistic"
        ],
        "adjust_params": {
            "cfg_scale": "+0.5",  # 增加 0.5
        }
    },
    
    "更寫實": {
        "add": [
            "photorealistic",
            "subsurface_scattering",
            "physically_based_rendering",
            "realistic",
            "detailed_skin"
        ],
        "remove": [
            "anime_style",
            "cel_shading",
            "bloom_effect"
        ],
        "adjust_params": {
            "cfg_scale": "-1.0",  # 降低 1.0
            "steps": "+5"
        }
    },
    
    "少人像": {
        "remove": [
            "1girl",
            "1boy",
            "portrait",
            "close-up",
            "face_focus"
        ],
        "add": [
            "scenery",
            "no_humans",
            "wide_shot",
            "landscape"
        ],
        "boost_categories": ["SCENE"],
        "reduce_categories": ["CHARACTER", "APPEARANCE"]
    },
    
    "加夜景": {
        "add": [
            "night",
            "night_sky",
            "stars",
            "moonlight",
            "dark",
            "moody_lighting"
        ],
        "remove": [
            "daylight",
            "sunny",
            "bright",
            "morning"
        ],
        "adjust_params": {
            "cfg_scale": "+0.5"
        }
    },
    
    "更明亮": {
        "add": [
            "bright",
            "sunny",
            "cheerful",
            "vivid_colors",
            "high_contrast"
        ],
        "remove": [
            "dark",
            "moody",
            "low_light",
            "desaturated"
        ]
    },
    
    "更柔和": {
        "add": [
            "soft_lighting",
            "pastel_colors",
            "gentle",
            "warm_colors",
            "low_contrast"
        ],
        "remove": [
            "high_contrast",
            "dramatic_lighting",
            "sharp",
            "vivid"
        ]
    }
}


# ============================================
# 固定負面 Prompt 模板
# ============================================

NEGATIVE_PROMPT_TEMPLATES = {
    "default": "nsfw, child, loli, shota, gore, lowres, bad_anatomy, bad_hands, cropped, worst_quality, jpeg_artifacts, blurry, grainy",
    
    "artistic": "nsfw, child, loli, shota, gore, lowres, bad_anatomy, cropped, worst_quality, jpeg_artifacts",
    
    "realistic": "nsfw, child, loli, shota, gore, lowres, bad_anatomy, bad_hands, deformed, cropped, worst_quality, jpeg_artifacts, blurry, overexposed, underexposed",
    
    "abstract": "nsfw, child, loli, shota, gore, lowres, cropped, worst_quality, jpeg_artifacts"
}


# ============================================
# 參數建議（基於風格）
# ============================================

PARAMETER_PRESETS = {
    "anime_dreamy": {
        "cfg_scale": 8.0,
        "steps": 35,
        "sampler": "DPM++ 2M Karras",
        "description": "動漫夢幻風格",
        "cfg_range": "7-9",
        "steps_range": "30-40"
    },
    
    "realistic": {
        "cfg_scale": 6.0,
        "steps": 32,
        "sampler": "DPM++ 2M Karras",
        "description": "寫實風格",
        "cfg_range": "5-7",
        "steps_range": "28-36"
    },
    
    "abstract_surreal": {
        "cfg_scale": 7.5,
        "steps": 45,
        "sampler": "Euler a",
        "description": "抽象超現實",
        "cfg_range": "6-9",
        "steps_range": "40-60",
        "note": "抽象主題建議多試幾次"
    },
    
    "artistic_painterly": {
        "cfg_scale": 7.0,
        "steps": 35,
        "sampler": "DPM++ 2M Karras",
        "description": "藝術繪畫風格",
        "cfg_range": "6-8",
        "steps_range": "30-40"
    }
}


# ============================================
# 工具函數
# ============================================

def resolve_tag_alias(tag: str) -> str:
    """解析別名為 canonical tag"""
    return TAG_ALIAS_MAP.get(tag.lower(), tag)

def apply_quick_adjustment(
    current_tags: List[str],
    adjustment: str
) -> Tuple[List[str], dict]:
    """
    應用快速調整
    
    Returns:
        (updated_tags, param_adjustments)
    """
    
    if adjustment not in QUICK_ADJUSTMENTS:
        return current_tags, {}
    
    config = QUICK_ADJUSTMENTS[adjustment]
    
    # 移除標籤
    updated_tags = [t for t in current_tags if t not in config.get("remove", [])]
    
    # 添加標籤
    tags_to_add = [t for t in config.get("add", []) if t not in updated_tags]
    updated_tags.extend(tags_to_add)
    
    # 參數調整
    param_adjustments = config.get("adjust_params", {})
    
    return updated_tags, param_adjustments

def get_parameter_preset(style: str) -> dict:
    """獲取參數預設值"""
    
    # 檢測風格
    if "anime" in style.lower() or "dreamy" in style.lower():
        return PARAMETER_PRESETS["anime_dreamy"]
    elif "realistic" in style.lower() or "photo" in style.lower():
        return PARAMETER_PRESETS["realistic"]
    elif "abstract" in style.lower() or "surreal" in style.lower():
        return PARAMETER_PRESETS["abstract_surreal"]
    elif "artistic" in style.lower() or "painting" in style.lower():
        return PARAMETER_PRESETS["artistic_painterly"]
    else:
        return PARAMETER_PRESETS["anime_dreamy"]  # 預設

def get_negative_prompt(style: str) -> str:
    """獲取負面 Prompt"""
    
    if "abstract" in style.lower():
        return NEGATIVE_PROMPT_TEMPLATES["abstract"]
    elif "realistic" in style.lower():
        return NEGATIVE_PROMPT_TEMPLATES["realistic"]
    elif "artistic" in style.lower():
        return NEGATIVE_PROMPT_TEMPLATES["artistic"]
    else:
        return NEGATIVE_PROMPT_TEMPLATES["default"]


# ============================================
# 使用範例
# ============================================

if __name__ == "__main__":
    # 測試別名解析
    print(resolve_tag_alias("beautiful_kimono"))  # -> "kimono"
    
    # 測試快速調整
    tags = ["1girl", "daylight", "anime_style"]
    new_tags, params = apply_quick_adjustment(tags, "加夜景")
    print(new_tags)  # 移除 "daylight"，添加夜景相關
    
    # 測試參數預設
    preset = get_parameter_preset("anime dreamy")
    print(preset["cfg_scale"])  # -> 8.0

