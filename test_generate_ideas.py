#!/usr/bin/env python3
"""
測試 generate_ideas 工具
"""

import sys
import os
sys.path.append('src/api')

from tools.inspire_tools import generate_ideas, IdeaDirection

# 創建測試數據
test_ideas = [
    IdeaDirection(
        title="可愛貓咪",
        concept="一隻可愛的貓咪在陽光下",
        vibe="溫暖、可愛、溫馨",
        main_tags=["1cat", "cute", "sunlight", "warm", "kitten", "fluffy", "adorable", "cozy", "soft lighting", "happy", "playful", "innocent", "sweet", "gentle", "peaceful"],
        quick_preview="1cat, cute, sunlight, warm, fluffy, adorable",
        uniqueness="溫暖陽光照耀下的可愛小貓"
    ),
    IdeaDirection(
        title="神秘貓咪",
        concept="夜晚的神秘貓咪",
        vibe="神秘、優雅、深邃",
        main_tags=["1cat", "mysterious", "night", "elegant", "moonlight", "shadow", "graceful", "mystical", "dark", "silhouette", "majestic", "enigmatic", "sophisticated", "atmospheric", "dramatic"],
        quick_preview="1cat, mysterious, night, elegant, moonlight, shadow",
        uniqueness="月光下的神秘優雅貓咪"
    ),
    IdeaDirection(
        title="夢幻貓咪",
        concept="夢境中的奇幻貓咪",
        vibe="夢幻、奇幻、超現實",
        main_tags=["1cat", "fantasy", "dreamy", "magical", "surreal", "ethereal", "whimsical", "enchanting", "otherworldly", "celestial", "mystical", "fairy tale", "imaginative", "wonderful", "fantastical"],
        quick_preview="1cat, fantasy, dreamy, magical, surreal, ethereal",
        uniqueness="夢境中的奇幻魔法貓咪"
    )
]

# 測試工具
try:
    result = generate_ideas(
        ideas=test_ideas,
        generation_basis="測試可愛貓咪的創意方向",
        diversity_achieved="high"
    )
    
    print("✅ generate_ideas 工具測試成功！")
    print(f"結果: {result}")
    
    # 檢查是否有 directions 字段
    if "directions" in result:
        print(f"✅ 找到 directions 字段，包含 {len(result['directions'])} 個方向")
        for i, direction in enumerate(result["directions"]):
            print(f"  方向 {i+1}: {direction['title']}")
    else:
        print("❌ 沒有找到 directions 字段")
        
except Exception as e:
    print(f"❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()

