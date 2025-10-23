"""
DeepSeek / OpenRouter 配置和測試
"""

import os

# 允許用環境變數覆寫
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek/deepseek-chat")
OPENROUTER_REFERER = os.environ.get("OPENROUTER_REFERER", "")
OPENROUTER_TITLE = os.environ.get("OPENROUTER_TITLE", "")

# OpenRouter API 配置
DEEPSEEK_CONFIG = {
    "model": DEEPSEEK_MODEL,
    "base_url": "https://openrouter.ai/api/v1/chat/completions",
    "max_tokens": 4000,
    "temperature": 0.1,
    "timeout": 60,
    "batch_size": 50,  # 每批處理的標籤數
    "max_retries": 3,
    "retry_delay": 2,  # 重試延遲（秒）
    "referer": OPENROUTER_REFERER,
    "title": OPENROUTER_TITLE,
}

# 測試標籤（不同頻率層級）
TEST_TAGS = {
    "高頻": [
        "1girl", "long_hair", "dress", "smile", "solo"
    ],
    "中頻": [
        "orchard", "broken_staff", "cossack_dance", "fencing_suit", "record_store"
    ],
    "低頻": [
        "ghibli_redraw_challenge", "newton's_cradle", "shishi_odoshi", 
        "musical_note_brooch", "pen_behind_ear"
    ]
}

# 預期分類結果（用於驗證）
EXPECTED_CLASSIFICATIONS = {
    "1girl": ("CHARACTER_RELATED", "CHARACTER_COUNT"),
    "long_hair": ("CHARACTER_RELATED", "HAIR"),
    "dress": ("CHARACTER_RELATED", "CLOTHING"),
    "smile": ("ACTION_POSE", "EXPRESSION"),
    "solo": ("CHARACTER_RELATED", "CHARACTER_COUNT"),
    "orchard": ("ENVIRONMENT", "NATURE"),
    "broken_staff": ("OBJECTS", "WEAPONS"),
    "cossack_dance": ("ACTION_POSE", "BODY_POSE"),
    "fencing_suit": ("CHARACTER_RELATED", "CLOTHING"),
    "record_store": ("ENVIRONMENT", "INDOOR"),
}

def get_test_prompt():
    """獲取測試用的 prompt"""
    return """你是 Danbooru 標籤分類專家。請將以下標籤分類到適當的主分類和副分類。

主分類選項：
- CHARACTER_RELATED: 人物相關
- ACTION_POSE: 動作姿勢
- OBJECTS: 物件道具
- ENVIRONMENT: 環境場景
- COMPOSITION: 構圖視角
- VISUAL_EFFECTS: 視覺效果
- ART_STYLE: 藝術風格
- ADULT_CONTENT: 成人內容
- THEME_CONCEPT: 主題概念
- TECHNICAL: 技術標籤

副分類選項：
  CHARACTER_RELATED:
    - CLOTHING: 服裝
    - HAIR: 頭髮
    - BODY_PARTS: 身體部位
    - ACCESSORIES: 配飾
    - CHARACTER_COUNT: 角色數量
  ACTION_POSE:
    - EXPRESSION: 表情
    - GESTURE: 手勢
    - BODY_POSE: 身體姿勢
    - INTERACTION: 互動
  OBJECTS:
    - WEAPONS: 武器
    - VEHICLES: 載具
    - FURNITURE: 家具
    - FOOD: 食物
    - ANIMALS: 動物
    - MISCELLANEOUS: 雜項
  ENVIRONMENT:
    - INDOOR: 室內
    - OUTDOOR: 室外
    - NATURE: 自然
    - URBAN: 都市
    - FANTASY: 奇幻

標籤列表：1girl, long_hair, dress, smile, solo, orchard, broken_staff, cossack_dance, fencing_suit, record_store

請以 JSON 格式回答，格式如下：
{
  "classifications": [
    {
      "tag": "標籤名稱",
      "main_category": "主分類代碼",
      "sub_category": "副分類代碼或null",
      "confidence": 0.95,
      "reasoning": "分類理由"
    }
  ]
}"""
