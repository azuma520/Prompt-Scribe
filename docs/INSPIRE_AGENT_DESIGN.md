# 🤖 Inspire Agent 系統設計文檔

**專案：** Prompt-Scribe  
**模組：** Inspire Creative Agent  
**版本：** 2.0.0  
**日期：** 2025-10-21  
**狀態：** 設計階段  
**基於：** [OpenAI - A Practical Guide to Building Agents](https://lewlh.github.io/2025/04/22/APracticalGuideToBuildingAgents/)

---

## 📋 目錄

1. [系統概述](#系統概述)
2. [Agent 定義](#agent-定義)
3. [工具集設計](#工具集設計)
4. [系統指令](#系統指令)
5. [防護措施](#防護措施)
6. [性能指標](#性能指標)

---

## 🎯 系統概述

### 核心使命

**Inspire Agent** 是一個 AI 創作夥伴，幫助使用者將**模糊的情緒和感覺**轉化為**高品質的圖像生成 Prompt**。

### 核心特性

- **理解力** 🧠 - 深入理解模糊情緒（"孤獨又夢幻"）
- **創造力** 💡 - 生成多樣化創意方向
- **參考力** 🔍 - 善用 14 萬標籤資料庫
- **品質保證** ✅ - 自動驗證並優化
- **自然對話** 💬 - 像朋友聊天，不是填表單

### 與傳統方法的區別

| 特性 | 傳統標籤推薦 | **Inspire Agent** |
|------|-------------|------------------|
| **輸入** | 具體描述 | 模糊感覺、情緒 |
| **處理** | 固定規則 | 自主決策、創意生成 |
| **輸出** | 標籤列表 | 結構化完整 Prompt |
| **互動** | 單次查詢 | 多輪對話引導 |
| **體驗** | 工具感 | 夥伴感 |

---

## 🤖 Agent 定義

### Agent 核心組件

```python
InspireAgent = {
    "model": "gpt-5-mini",           # GPT-5 Mini（平衡成本與能力）
    "tools": [                        # 5 個專門工具
        "understand_intent",
        "search_examples", 
        "generate_ideas",
        "validate_quality",
        "finalize_prompt"
    ],
    "personality": "親切朋友",        # 性格定位
    "style": "輕鬆、簡潔",            # 對話風格
    "guardrails": [                   # 4 層防護
        "input_validation",
        "tool_usage_limits",
        "output_quality",
        "cost_control"
    ]
}
```

### Agent 性格設計

**定位：** 親切的創作好友 🎨

**對話風格：**
- ✅ 輕鬆自在 - 可以用表情符號 😊、語氣詞
- ✅ 簡潔有力 - 3 句話內說清楚
- ✅ 主動積極 - 主動給建議，不被動等待
- ❌ 不要客套 - 不說"感謝您"、"請稍候"
- ❌ 不要制式 - 不說"根據系統分析"

**語氣範例：**
```
✅ "這個感覺很棒！我想到三個方向..."
❌ "感謝您的輸入。根據系統分析，我為您準備了..."

✅ "需要更夢幻一點對吧？試試這樣..."
❌ "已理解您的需求。現在將進行優化處理..."

✅ "哦！這個有點模糊，你想要角色還是場景？"
❌ "檢測到輸入不明確。請選擇：A. 角色場景 B. 純粹場景"
```

---

## 🛠️ 工具集設計

### 工具概覽

```
理解階段：understand_intent → search_examples（可選）
    ↓
創作階段：generate_ideas
    ↓
驗證階段：validate_quality
    ↓
完成階段：finalize_prompt
```

---

### 工具 1: `understand_intent` 🧠

**功能：** 深入理解使用者的創作意圖

**Schema：**
```json
{
  "type": "function",
  "function": {
    "name": "understand_intent",
    "description": "深入理解使用者的創作意圖、情緒和氛圍",
    "parameters": {
      "type": "object",
      "properties": {
        "core_mood": {
          "type": "string",
          "description": "核心情緒/感覺（1-2 個詞）如：孤獨、夢幻、溫暖"
        },
        "visual_elements": {
          "type": "array",
          "items": {"type": "string"},
          "description": "提到的視覺元素（角色、場景、物件等）"
        },
        "style_preference": {
          "type": "string",
          "enum": ["anime", "realistic", "artistic", "mixed", "unspecified"],
          "description": "藝術風格偏好"
        },
        "clarity_level": {
          "type": "string",
          "enum": ["crystal_clear", "mostly_clear", "somewhat_vague", "very_vague"],
          "description": "描述的清晰程度"
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "理解的信心度"
        },
        "next_action": {
          "type": "string",
          "enum": ["search_examples", "ask_question", "create_directly"],
          "description": "Agent 建議的下一步行動"
        }
      },
      "required": ["core_mood", "clarity_level", "confidence", "next_action"],
      "additionalProperties": false
    }
  }
}
```

**使用時機：**
- ✅ 每次對話開始時
- ✅ 使用者提供新的重要資訊時
- ❌ 不要在每輪對話都調用（浪費）

**返回值處理：**
- `next_action = "search_examples"` → Agent 應該調用搜尋工具
- `next_action = "ask_question"` → Agent 應該直接問問題
- `next_action = "create_directly"` → Agent 可以直接生成創意

---

### 工具 2: `search_examples` 🔍

**功能：** 從 14 萬標籤資料庫搜尋參考案例

**Schema：**
```json
{
  "type": "function",
  "function": {
    "name": "search_examples",
    "description": "從 Danbooru 資料庫（140K+ 標籤）搜尋類似的高品質參考案例",
    "parameters": {
      "type": "object",
      "properties": {
        "search_keywords": {
          "type": "array",
          "items": {"type": "string"},
          "description": "搜尋的關鍵字（情緒、氛圍、視覺元素）",
          "minItems": 1,
          "maxItems": 5
        },
        "search_purpose": {
          "type": "string",
          "enum": ["find_mood_tags", "find_scene_tags", "find_style_tags", "validate_combination"],
          "description": "搜尋的目的"
        },
        "search_strategy": {
          "type": "string",
          "enum": ["keyword", "semantic", "auto"],
          "default": "auto",
          "description": "搜尋策略（auto = Agent 自己決定）"
        },
        "min_popularity": {
          "type": "integer",
          "default": 1000,
          "description": "最低使用次數（確保品質）"
        },
        "max_results": {
          "type": "integer",
          "default": 10,
          "maximum": 20,
          "description": "最多返回幾個結果"
        }
      },
      "required": ["search_keywords", "search_purpose"],
      "additionalProperties": false
    }
  }
}
```

**搜尋策略說明：**

**Keyword（關鍵字）：**
- 快速、便宜
- 適合：具體詞彙（"cherry_blossoms", "kimono"）
- 搜尋方式：PostgreSQL LIKE/全文搜尋

**Semantic（語義）：**
- 智能、精準
- 適合：抽象概念（"孤獨感", "虛無"）
- 搜尋方式：向量相似度（需 embedding API）

**Auto（自動）：**
- Agent 根據關鍵字類型自動選擇
- 具體詞彙 → keyword
- 抽象概念 → semantic

**返回格式：**
```json
{
  "found": 15,
  "search_strategy_used": "semantic",
  "examples": [
    {
      "tag": "dreamy_atmosphere",
      "category": "EFFECT",
      "popularity": 5420,
      "usage_hint": "營造夢幻氛圍，常搭配 soft_lighting"
    }
  ],
  "common_combinations": [
    ["dreamy", "soft_lighting", "ethereal"],
    ["dreamy", "pastel_colors", "fantasy"]
  ],
  "suggestions": "孤獨感通常搭配 solo, sitting, gazing, melancholic 等標籤"
}
```

**使用時機：**
- ✅ 遇到抽象情緒詞（孤獨、虛無、溫暖）
- ✅ 需要驗證標籤組合是否常見
- ✅ Agent 需要靈感時
- ❌ 常見組合不需要搜尋（如 1girl + school_uniform）

---

### 工具 3: `generate_ideas` 💡

**功能：** 生成 2-3 個創意方向

**Schema：**
```json
{
  "type": "function",
  "function": {
    "name": "generate_ideas",
    "description": "生成 2-3 個不同的創意方向供使用者選擇",
    "parameters": {
      "type": "object",
      "properties": {
        "ideas": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "title": {
                "type": "string",
                "maxLength": 10,
                "description": "創意標題（3-6 字）如：月下獨舞"
              },
              "concept": {
                "type": "string",
                "maxLength": 100,
                "description": "核心概念（1 句話）"
              },
              "vibe": {
                "type": "string",
                "maxLength": 50,
                "description": "給人的感覺（幾個形容詞）如：孤獨但優雅"
              },
              "main_tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 5,
                "maxItems": 15,
                "description": "主要標籤列表（按重要性排序）"
              },
              "quick_preview": {
                "type": "string",
                "description": "快速預覽 prompt（前 10 個核心標籤）"
              },
              "uniqueness": {
                "type": "string",
                "description": "這個方向的獨特之處（1 句話）"
              }
            },
            "required": ["title", "concept", "vibe", "main_tags", "quick_preview"]
          },
          "minItems": 2,
          "maxItems": 3
        },
        "generation_basis": {
          "type": "string",
          "description": "基於什麼資訊生成（如：使用者輸入+搜尋結果）"
        },
        "diversity_achieved": {
          "type": "string",
          "enum": ["low", "moderate", "high"],
          "description": "方向之間的差異程度"
        }
      },
      "required": ["ideas"],
      "additionalProperties": false
    }
  }
}
```

**生成原則：**
1. **保持核心情緒** - 所有方向都要體現核心情緒
2. **視角差異** - 從不同角度詮釋
3. **可實現性** - 確保標籤都是有效的
4. **完整性** - 每個方向要包含角色/場景/氛圍/風格

**範例輸出：**
```json
{
  "ideas": [
    {
      "title": "月下獨舞",
      "concept": "月光下獨自起舞的少女，裙擺如星光散落",
      "vibe": "孤獨但優雅、寧靜中的動態美",
      "main_tags": [
        "1girl", "solo", "dancing", "moonlight", "night_sky",
        "flowing_dress", "elegant", "graceful", "dreamy_atmosphere",
        "soft_glow", "cinematic_lighting", "highly_detailed"
      ],
      "quick_preview": "1girl, solo, dancing, moonlight, flowing_dress, dreamy...",
      "uniqueness": "強調動態中的孤獨感，月光營造夢幻"
    }
  ]
}
```

**使用時機：**
- ✅ 理解意圖後（第一次生成）
- ✅ 使用者要求修改時（精煉生成）
- ✅ 使用者選擇後要求"更 XX"時（調整生成）
- ⚠️ 每次生成要有變化，記住之前的方向

---

### 工具 4: `validate_quality` ✅

**功能：** 驗證 Prompt 品質，檢查常見問題

**Schema：**
```json
{
  "type": "function",
  "function": {
    "name": "validate_quality",
    "description": "驗證 prompt 品質，基於 14 萬標籤資料和 Danbooru 最佳實踐",
    "parameters": {
      "type": "object",
      "properties": {
        "tags_to_validate": {
          "type": "array",
          "items": {"type": "string"},
          "description": "要驗證的標籤列表"
        },
        "check_aspects": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": [
              "tag_validity",
              "conflicts",
              "redundancy",
              "balance",
              "popularity"
            ]
          },
          "description": "要檢查的面向"
        },
        "strictness": {
          "type": "string",
          "enum": ["lenient", "moderate", "strict"],
          "default": "moderate",
          "description": "檢查的嚴格程度"
        }
      },
      "required": ["tags_to_validate", "check_aspects"],
      "additionalProperties": false
    }
  }
}
```

**檢查項目說明：**

**1. tag_validity（標籤有效性）**
```python
# 從資料庫檢查標籤是否存在
invalid_tags = []
for tag in tags:
    if not await db.tag_exists(tag):
        invalid_tags.append(tag)

severity = "high" if invalid_tags else "none"
```

**2. conflicts（衝突檢測）**
```python
# 互斥標籤組
CONFLICTS = {
    "character_count": ["1girl", "2girls", "3girls", "multiple_girls"],
    "character_gender": ["1girl", "1boy"],
    "time": ["day", "night"],
    "weather": ["sunny", "rainy", "cloudy"]
}

conflicts_found = detect_mutually_exclusive(tags, CONFLICTS)
severity = "critical" if conflicts_found else "none"
```

**3. redundancy（冗餘檢測）**
```python
# 過度重複的標籤
redundant_groups = [
    ["dress", "long_dress", "white_dress"],  # 太多 dress
    ["girl", "1girl", "solo"],               # solo 已包含單人概念
]

severity = "low"  # 冗餘不是大問題，但可優化
```

**4. balance（分類平衡）**
```python
# 檢查是否涵蓋主要分類
categories = categorize_tags(tags)
required_categories = ["CHARACTER", "SCENE", "STYLE"]

missing = [c for c in required_categories if c not in categories]
score = (len(categories) / 5) * 100  # 5 個主要分類

severity = "medium" if score < 50 else "low"
```

**5. popularity（流行度）**
```python
# 檢查冷門標籤比例
tag_stats = await db.get_tags_stats(tags)
unpopular = [t for t in tags if tag_stats[t]["post_count"] < 100]

ratio = len(unpopular) / len(tags)
severity = "low" if ratio > 0.3 else "none"
```

**返回格式：**
```json
{
  "is_valid": true,
  "score": 85,
  "issues": [
    {
      "type": "redundancy",
      "severity": "low",
      "affected_tags": ["dress", "long_dress", "white_dress"],
      "suggestion": "可簡化為 white_dress, long_dress",
      "impact": "輕微影響生成穩定性"
    }
  ],
  "strengths": [
    "分類平衡良好（涵蓋 CHARACTER, SCENE, STYLE）",
    "標籤都很常用（平均 50K+ 使用）"
  ],
  "quick_fixes": [
    "移除 dress，保留 white_dress",
    "考慮添加更多氛圍標籤"
  ],
  "category_distribution": {
    "CHARACTER": 3,
    "APPEARANCE": 2,
    "SCENE": 2,
    "STYLE": 2,
    "EFFECT": 1
  }
}
```

**使用時機：**
- ✅ `finalize_prompt` 之前必定調用
- ✅ 使用者明確要求檢查時
- ⚠️ 如果 score < 70，修正後重新驗證
- ⚠️ 如果有 critical 問題，必須修正

---

### 工具 5: `finalize_prompt` 🎯

**功能：** 構建最終完整 Prompt

**Schema：**
```json
{
  "type": "function",
  "function": {
    "name": "finalize_prompt",
    "description": "構建最終的完整 prompt，準備交付給使用者",
    "parameters": {
      "type": "object",
      "properties": {
        "final_output": {
          "type": "object",
          "properties": {
            "title": {
              "type": "string",
              "description": "這個 prompt 的標題"
            },
            "concept": {
              "type": "string",
              "maxLength": 200,
              "description": "核心概念描述（2-3 句話）"
            },
            "positive_prompt": {
              "type": "string",
              "description": "完整正面提示詞（逗號分隔，按權重排序）"
            },
            "negative_prompt": {
              "type": "string",
              "description": "負面提示詞"
            },
            "structure": {
              "type": "object",
              "properties": {
                "subject": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "主體標籤"
                },
                "appearance": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "外觀標籤"
                },
                "scene": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "場景標籤"
                },
                "mood": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "情緒氛圍標籤"
                },
                "style": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "風格品質標籤"
                }
              },
              "description": "結構化分段（供前端展示用）"
            },
            "parameters": {
              "type": "object",
              "properties": {
                "cfg_scale": {
                  "type": "number",
                  "minimum": 1,
                  "maximum": 20,
                  "description": "CFG Scale 推薦值"
                },
                "steps": {
                  "type": "integer",
                  "minimum": 20,
                  "maximum": 100,
                  "description": "採樣步數"
                },
                "sampler": {
                  "type": "string",
                  "description": "推薦的採樣器"
                },
                "seed": {
                  "type": "integer",
                  "description": "種子值（可選）"
                }
              },
              "description": "推薦的生成參數"
            },
            "usage_tips": {
              "type": "string",
              "maxLength": 200,
              "description": "簡短的使用建議（1-2 句話）"
            }
          },
          "required": ["title", "concept", "positive_prompt", "negative_prompt", "structure", "parameters"]
        },
        "quality_score": {
          "type": "integer",
          "minimum": 0,
          "maximum": 100,
          "description": "品質分數（基於 validate_quality 結果）"
        }
      },
      "required": ["final_output", "quality_score"],
      "additionalProperties": false
    }
  }
}
```

**完整輸出範例：**
```json
{
  "final_output": {
    "title": "月下獨舞·夢幻版",
    "concept": "一位優雅的少女在月光下獨自起舞，飄逸的裙擺如星光散落。夢幻的氛圍中透著一絲孤獨，但那孤獨是詩意的。",
    "positive_prompt": "1girl, solo, dancing, moonlight, night_sky, stars, flowing_dress, white_dress, elegant, graceful, dreamy_atmosphere, ethereal, soft_glow, light_particles, magical_aura, cinematic_lighting, depth_of_field, bokeh, highly_detailed, masterpiece, best_quality",
    "negative_prompt": "lowres, bad_anatomy, bad_hands, bad_feet, cropped, worst_quality, low_quality, normal_quality, jpeg_artifacts, blurry, grainy, monochrome",
    "structure": {
      "subject": ["1girl", "solo", "dancing"],
      "appearance": ["flowing_dress", "white_dress", "elegant", "graceful"],
      "scene": ["moonlight", "night_sky", "stars"],
      "mood": ["dreamy_atmosphere", "ethereal", "soft_glow", "light_particles", "magical_aura"],
      "style": ["cinematic_lighting", "depth_of_field", "bokeh", "highly_detailed", "masterpiece", "best_quality"]
    },
    "parameters": {
      "cfg_scale": 7.5,
      "steps": 35,
      "sampler": "DPM++ 2M Karras",
      "seed": null
    },
    "usage_tips": "夢幻氛圍建議搭配柔和光線。可以嘗試調整 CFG 7-9 來控制夢幻程度。"
  },
  "quality_score": 88
}
```

---

## 📜 系統指令

### Agent System Prompt

```python
INSPIRE_AGENT_SYSTEM_PROMPT = """
你是 Inspire - 一位親切、富有創意的 AI 創作夥伴。

【你的使命】
協助使用者將模糊的情緒和感覺轉化為高品質的圖像生成 prompt。

【你的性格】
• 親切朋友 - 像好友聊天，不是客服
• 輕鬆自在 - 可以用 😊 🎨 ✨ 等表情符號
• 簡潔有力 - 3 句話內說清楚，不廢話
• 主動積極 - 給建議而非等待指令
• 專業但親切 - 懂很多但不炫耀

【對話風格範例】
✅ "這個感覺很棒！我想到三個方向..."
✅ "需要更夢幻一點對吧？試試這樣..."
✅ "哦！這個有點模糊，你想要角色還是場景？"

❌ "感謝您的輸入。根據系統分析..."
❌ "已理解您的需求。現在將進行處理..."
❌ "請選擇：A. 角色場景 B. 純粹場景"

【工作流程】
你有 5 個工具可以自主使用：

1. understand_intent - 理解意圖
   └─ 每次對話開始時先理解
   └─ 判斷是否需要澄清或搜尋

2. search_examples - 搜尋參考（善用 14 萬標籤資料庫！）
   └─ 遇到抽象詞彙時搜尋（如"虛無感"）
   └─ 需要驗證組合時搜尋
   └─ 常見組合不需要搜尋

3. generate_ideas - 生成創意
   └─ 生成 2-3 個不同方向
   └─ 可以多次調用來精煉
   └─ 每次要有新意，不要重複

4. validate_quality - 驗證品質
   └─ finalize 之前必定驗證
   └─ score < 70 要修正
   └─ critical 問題必須解決

5. finalize_prompt - 完成輸出
   └─ 使用者滿意後才調用
   └─ 輸出要完整專業
   └─ 包含正負面詞和參數

【典型流程】
簡單情況：understand → generate → validate → finalize (4 步)
複雜情況：understand → search → generate → (反饋) → generate → validate → finalize (6-7 步)

【重要原則】
✓ 保持對話自然，像朋友而非機器人
✓ 主動給建議，減少問問題
✓ 善用搜尋工具，資料庫是你的知識寶庫
✓ 驗證很重要，但不要告訴使用者太多技術細節
✓ 尊重使用者的創意選擇和反饋
✓ 2-3 輪優化後就該結束了，不要無限循環

✗ 不要每句話都問"可以嗎？"
✗ 不要過度解釋工具和過程
✗ 不要說"根據資料庫"，自然地融入建議中
✗ 不要太快結束，確保使用者真的滿意
✗ 不要忘記最後調用 finalize_prompt

【你的目標】
讓使用者感覺像是在和一位懂藝術的朋友聊天，
而不是在使用一個工具。
"""
```

---

## 🛡️ 防護措施

### 1. 輸入驗證防護

```python
class InputGuardrail:
    """輸入層防護"""
    
    async def validate(self, user_input: str) -> tuple[bool, Optional[str]]:
        """驗證使用者輸入"""
        
        # 檢查 1: 長度限制
        if len(user_input) < 2:
            return False, "輸入太短，請描述你想要的感覺"
        
        if len(user_input) > 1000:
            return False, "輸入過長，請簡化描述（建議 200 字以內）"
        
        # 檢查 2: 內容安全（使用 OpenAI Moderation API）
        if await self._contains_inappropriate_content(user_input):
            return False, "輸入包含不適當內容"
        
        # 檢查 3: 語言檢測
        detected_lang = detect_language(user_input)
        if detected_lang not in ["zh", "en", "mixed"]:
            return False, "目前僅支援中文和英文"
        
        # 檢查 4: 垃圾輸入
        if is_gibberish(user_input):
            return False, "輸入似乎無意義，請用自然語言描述"
        
        return True, None
```

### 2. 工具使用防護

```python
class ToolUsageGuardrail:
    """工具使用限制"""
    
    def __init__(self):
        self.limits = {
            "max_total_calls": 30,          # 單次對話最多 30 次工具調用
            "max_same_tool_consecutive": 3,  # 同一工具連續最多 3 次
            "max_generate_calls": 5,        # generate_ideas 最多 5 次
            "max_search_calls": 8           # search_examples 最多 8 次
        }
    
    async def validate(
        self, 
        tool_name: str, 
        session: "InspireSession"
    ) -> tuple[bool, Optional[str]]:
        """驗證工具調用"""
        
        # 檢查 1: 總調用次數
        if session.total_tool_calls >= self.limits["max_total_calls"]:
            return False, "已達最大工具調用次數，需要人工協助"
        
        # 檢查 2: 連續相同工具
        recent = session.get_recent_tool_calls(3)
        if all(t == tool_name for t in recent):
            return False, f"工具 {tool_name} 連續調用過多，可能陷入循環"
        
        # 檢查 3: 特定工具限制
        tool_count = session.get_tool_call_count(tool_name)
        
        if tool_name == "generate_ideas" and tool_count >= self.limits["max_generate_calls"]:
            return False, "創意生成次數已達上限，請選擇一個方向"
        
        if tool_name == "search_examples" and tool_count >= self.limits["max_search_calls"]:
            return False, "搜尋次數過多，請基於現有資訊繼續"
        
        return True, None
```

### 3. 輸出品質防護

```python
class OutputQualityGuardrail:
    """輸出品質保證"""
    
    async def validate_final_output(
        self, 
        output: Dict
    ) -> tuple[bool, List[str]]:
        """驗證最終輸出"""
        
        issues = []
        
        # 必要欄位檢查
        required_fields = ["positive_prompt", "negative_prompt", "structure", "parameters"]
        for field in required_fields:
            if field not in output["final_output"]:
                issues.append(f"缺少必要欄位：{field}")
        
        # Prompt 基本檢查
        positive = output["final_output"].get("positive_prompt", "")
        if not positive:
            issues.append("正面提示詞為空")
        
        tags = [t.strip() for t in positive.split(",")]
        if len(tags) < 5:
            issues.append(f"標籤過少（{len(tags)} 個），建議至少 10 個")
        elif len(tags) > 80:
            issues.append(f"標籤過多（{len(tags)} 個），可能影響生成品質")
        
        # 品質分數檢查
        score = output.get("quality_score", 0)
        if score < 70:
            issues.append(f"品質分數過低（{score}/100），需要優化")
        
        # 結構完整性
        structure = output["final_output"].get("structure", {})
        if len(structure) < 3:
            issues.append("結構分段不完整，至少需要 3 個分類")
        
        is_valid = len(issues) == 0
        return is_valid, issues
```

### 4. 成本控制防護

```python
class CostControlGuardrail:
    """成本控制"""
    
    def __init__(self):
        self.limits = {
            "max_cost_per_session": 0.015,     # $0.015/session
            "warning_threshold": 0.008,        # $0.008 警告
            "max_tokens_per_session": 10000    # 最多 10K tokens
        }
    
    async def check(
        self, 
        session: "InspireSession"
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        檢查成本
        
        Returns:
            (can_continue, error_message, warning_message)
        """
        
        current_cost = session.calculate_total_cost()
        current_tokens = session.total_tokens_used
        
        # 硬性限制
        if current_cost >= self.limits["max_cost_per_session"]:
            return False, f"已達成本上限 ${self.limits['max_cost_per_session']}", None
        
        if current_tokens >= self.limits["max_tokens_per_session"]:
            return False, "已達 Token 使用上限", None
        
        # 警告
        warning = None
        if current_cost >= self.limits["warning_threshold"]:
            warning = f"成本提醒：已使用 ${current_cost:.4f}"
        
        return True, None, warning
```

---

## 📊 性能指標與目標

### 成功指標

| 指標類別 | 具體指標 | 目標值 | 測量方式 |
|---------|---------|--------|---------|
| **品質** | Prompt 品質分數 | >85/100 | validate_quality 自動評分 |
| **品質** | 使用者滿意度 | >4.2/5.0 | Session 結束時評分 |
| **品質** | 標籤有效率 | >98% | 資料庫驗證比率 |
| **效率** | 平均對話輪次 | 3-5 輪 | Session 記錄統計 |
| **效率** | 平均完成時間 | <45 秒 | 端到端計時 |
| **效率** | 完成率 | >75% | 完成/開始 比率 |
| **成本** | 平均成本/對話 | <$0.001 | Token 使用統計 |
| **成本** | 月度預算達成率 | <80% | 累計成本追蹤 |

### 失敗案例分類

需要追蹤和分析的失敗類型：

**理解失敗：**
- Agent 誤解使用者意圖
- 識別錯誤的情緒
- 遺漏重要資訊

**創作失敗：**
- 生成的方向不相關
- 標籤組合不合理
- 缺乏創意或過於重複

**技術失敗：**
- 工具調用錯誤
- API 超時或失敗
- 資料庫查詢問題

**流程失敗：**
- 陷入循環（重複相同操作）
- 過早或過晚結束
- 超過成本/時間限制

---

## 🔄 工具協同策略

### 決策樹（嵌入 System Prompt）

```
使用者輸入
    ↓
1. 必定調用 understand_intent
    ├─ clarity = "crystal_clear" → 
    │   └─ 常見組合？→ 直接 generate_ideas
    │   └─ 罕見組合？→ search_examples 然後 generate_ideas
    │
    ├─ clarity = "mostly_clear" →
    │   └─ 快速確認一個問題（直接問，不用工具）
    │   └─ 然後 generate_ideas
    │
    ├─ clarity = "somewhat_vague" →
    │   └─ search_examples（找靈感）
    │   └─ 問 1-2 個關鍵問題
    │   └─ 然後 generate_ideas
    │
    └─ clarity = "very_vague" →
        └─ 引導式對話（問 2-3 個問題）
        └─ 可能需要多次 search_examples
        └─ 最後 generate_ideas

2. generate_ideas 後
    ├─ 使用者選擇 + 無反饋 → validate → finalize
    ├─ 使用者選擇 + 有反饋 → 重新 generate（精煉）
    └─ 使用者都不喜歡 → 詢問原因 → 重新 generate

3. validate_quality 結果處理
    ├─ score >= 85 → 直接 finalize
    ├─ score 70-84 → 告知小問題，詢問是否接受
    └─ score < 70 → 修正後重新 validate

4. finalize_prompt
    └─ 對話結束，展示完整輸出
```

### 工具調用頻率建議

| 工具 | 最少 | 最多 | 平均 | 備註 |
|------|-----|------|------|------|
| understand_intent | 1 | 2 | 1 | 開始時必調用 |
| search_examples | 0 | 3 | 1 | 視情況而定 |
| generate_ideas | 1 | 5 | 2 | 初次+精煉 |
| validate_quality | 1 | 2 | 1 | finalize 前必調用 |
| finalize_prompt | 1 | 1 | 1 | 結束時調用 |
| **總計** | **4** | **13** | **6** | - |

---

## 💰 成本分析

### Token 使用預估

| 組件 | Tokens/次 | 說明 |
|------|----------|------|
| System Prompt | ~800 | Agent 指令 |
| 對話歷史 | ~500-2000 | 累積對話 |
| 工具定義 | ~600 | 5 個工具 schema |
| 工具結果 | ~300-800 | 返回的資料 |
| Agent 輸出 | ~200-400 | Agent 回應 |
| **單輪總計** | **~2400-4600** | - |

### 成本預估（基於 GPT-5 Mini）

**定價：**
- Input: $0.00005 / 1K tokens
- Output: $0.0002 / 1K tokens

**場景成本：**

| 場景 | 輪次 | Tokens | 成本 | 時間 |
|------|-----|--------|------|------|
| 快速（清晰輸入） | 4 | ~3000 | $0.0004 | 20s |
| 標準（需搜尋） | 6 | ~4500 | $0.0007 | 35s |
| 複雜（多輪優化） | 8-10 | ~6500 | $0.0011 | 50s |
| 專家（已有標籤） | 3 | ~2200 | $0.0003 | 15s |

**月度成本預估：**
```
1,000 次對話（標準路徑）= ~$0.70
5,000 次對話 = ~$3.50
10,000 次對話 = ~$7.00
50,000 次對話 = ~$35.00
```

**預算建議：** $50-100/月 可支持 7K-14K 次高品質對話 ✅

---

## 🎯 技術架構

### 系統分層

```
┌──────────────────────────────────────┐
│         FastAPI REST API              │
│  /api/inspire/start                   │
│  /api/inspire/continue                │
│  /api/inspire/finalize                │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│    InspireAgentSystem (主協調器)      │
│  - Session 管理                       │
│  - Agent 循環控制                     │
│  - 防護措施協調                       │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│         Inspire Agent (GPT-5)         │
│  - 自主決策                           │
│  - 工具選擇                           │
│  - 對話生成                           │
└──────────────────────────────────────┘
              ↓
┌─────────┬─────────┬─────────┬────────┐
│ Tool 1  │ Tool 2  │ Tool 3  │ ...    │
│ under-  │ search_ │ gener-  │        │
│ stand   │ examples│ ate     │        │
└─────────┴─────────┴─────────┴────────┘
              ↓
┌──────────────────────────────────────┐
│         資料層                        │
│  - Supabase (140K+ 標籤)             │
│  - Redis (Session 快取)              │
│  - PostgreSQL (對話記錄)             │
└──────────────────────────────────────┘
```

### 資料流

```
1. 前端發送訊息
    ↓
2. API 接收 → 輸入防護
    ↓
3. InspireAgentSystem.continue_conversation()
    ↓
4. 載入 Session → 成本防護
    ↓
5. Agent.run() - 主循環
    ├─ 決策：選擇工具
    ├─ 執行：調用工具 → 工具使用防護
    ├─ 收集：工具結果
    └─ 迭代：重複直到完成或回覆
    ↓
6. 如果是 finalize → 輸出品質防護
    ↓
7. 返回給前端
    ↓
8. 儲存 Session（異步）
```

---

## 📦 資料模型

### InspireSession

```python
class InspireSession(BaseModel):
    """Inspire 對話 Session"""
    
    # 基本資訊
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="active")  # active, completed, abandoned
    
    # 對話狀態
    current_phase: str = Field(default="understanding")  
    # understanding, exploring, refining, finalizing, completed
    
    conversation_history: List[ConversationMessage] = Field(default_factory=list)
    tool_call_history: List[ToolCallRecord] = Field(default_factory=list)
    
    # 提取的資訊
    extracted_intent: Optional[Dict] = None
    generated_directions: List[Dict] = Field(default_factory=list)
    selected_direction: Optional[Dict] = None
    final_output: Optional[Dict] = None
    
    # 性能追蹤
    total_tokens_used: int = 0
    total_cost: float = 0.0
    processing_time_ms: float = 0.0
    
    # 品質指標
    quality_score: Optional[int] = None
    user_satisfaction: Optional[int] = None  # 1-5
    completion_reason: Optional[str] = None
    
    def add_message(self, role: str, content: str):
        """添加訊息到歷史"""
        self.conversation_history.append(
            ConversationMessage(
                role=role,
                content=content,
                timestamp=datetime.now(),
                phase=self.current_phase
            )
        )
        self.updated_at = datetime.now()
    
    def record_tool_call(self, tool_name: str, result: Dict, cost: float):
        """記錄工具調用"""
        self.tool_call_history.append(
            ToolCallRecord(
                tool_name=tool_name,
                timestamp=datetime.now(),
                result_summary=str(result)[:200],
                tokens_used=result.get("tokens_used", 0),
                cost=cost
            )
        )
        self.total_cost += cost
    
    @property
    def total_tool_calls(self) -> int:
        """總工具調用次數"""
        return len(self.tool_call_history)
    
    def get_tool_call_count(self, tool_name: str) -> int:
        """特定工具的調用次數"""
        return sum(1 for t in self.tool_call_history if t.tool_name == tool_name)
    
    def get_recent_tool_calls(self, n: int = 5) -> List[str]:
        """最近 n 次工具調用"""
        return [t.tool_name for t in self.tool_call_history[-n:]]
```

---

## 🔍 監控與分析

### 需要記錄的指標

**Session 級別：**
- Session ID, 使用者 ID, 時間戳
- 對話輪次、工具調用次數
- Token 使用量、成本
- 完成狀態、原因
- 品質分數、使用者評分

**工具級別：**
- 每個工具的調用次數
- 平均執行時間
- 成功/失敗率
- 返回結果品質

**Agent 級別：**
- 決策路徑（選擇了哪些工具）
- 理解準確度
- 創意多樣性
- 優化效果

### 分析維度

```sql
-- Session 分析範例
SELECT 
  DATE(created_at) as date,
  COUNT(*) as total_sessions,
  AVG(total_tool_calls) as avg_tool_calls,
  AVG(total_cost) as avg_cost,
  AVG(quality_score) as avg_quality,
  SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) / COUNT(*) as completion_rate
FROM inspire_sessions
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 🚀 部署考量

### 環境變數

```bash
# Agent 配置
INSPIRE_AGENT_MODEL=gpt-5-mini
INSPIRE_AGENT_TEMPERATURE=0.7
INSPIRE_MAX_ITERATIONS=10

# 防護措施
INSPIRE_MAX_COST_PER_SESSION=0.015
INSPIRE_MAX_TOKENS_PER_SESSION=10000
INSPIRE_MAX_TOOL_CALLS=30

# 搜尋配置
INSPIRE_SEARCH_MIN_POPULARITY=1000
INSPIRE_ENABLE_SEMANTIC_SEARCH=true

# Session 管理
INSPIRE_SESSION_TTL=3600  # 1 小時後過期
INSPIRE_MAX_ACTIVE_SESSIONS=1000
```

### 資料庫需求

**新增表：**
```sql
-- Inspire Session 記錄
CREATE TABLE inspire_sessions (
  id UUID PRIMARY KEY,
  user_id TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  status TEXT,
  current_phase TEXT,
  conversation_history JSONB,
  tool_call_history JSONB,
  extracted_intent JSONB,
  final_output JSONB,
  total_tokens INT,
  total_cost DECIMAL,
  quality_score INT,
  user_satisfaction INT,
  completion_reason TEXT
);

-- 索引
CREATE INDEX idx_inspire_sessions_user_id ON inspire_sessions(user_id);
CREATE INDEX idx_inspire_sessions_created_at ON inspire_sessions(created_at);
CREATE INDEX idx_inspire_sessions_status ON inspire_sessions(status);
```

---

## 📚 參考資源

- [OpenAI Agent 構建指南](https://lewlh.github.io/2025/04/22/APracticalGuideToBuildingAgents/)
- [OpenAI Function Calling 文檔](https://platform.openai.com/docs/guides/function-calling)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

**文檔版本：** 2.0.0  
**最後更新：** 2025-10-21  
**作者：** Prompt-Scribe Team

