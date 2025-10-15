# LLM 整合指南

**版本**: 2.0.0  
**建立日期**: 2025-01-14  
**專案**: PLAN-2025-005

---

## 📖 目錄

1. [概述](#概述)
2. [快速開始](#快速開始)
3. [GPT-4 整合](#gpt-4-整合)
4. [Claude 整合](#claude-整合)
5. [API 端點詳解](#api-端點詳解)
6. [最佳實踐](#最佳實踐)
7. [常見問題](#常見問題)

---

## 概述

Prompt-Scribe API 專為 LLM 設計，提供一站式的標籤推薦服務。

### 核心理念

**讓 API 承擔複雜性，讓 LLM 保持簡單**

### 關鍵優勢

- ✅ **一次調用完成**: 無需多個 API 調用
- ✅ **結構化回應**: 包含詳細解釋和使用建議
- ✅ **高容錯性**: 清晰的錯誤訊息
- ✅ **快速響應**: < 500ms (P95)

---

## 快速開始

### 基本工作流程

```
用戶輸入
    ↓
LLM 調用 /api/llm/recommend-tags
    ↓
獲得推薦標籤和建議
    ↓
LLM 生成最終 prompt
```

### 最小範例

```python
import requests

# 用戶輸入
user_input = "a lonely girl in cyberpunk city at night"

# LLM 調用 API
response = requests.post(
    "https://your-api.com/api/llm/recommend-tags",
    json={
        "description": user_input,
        "max_tags": 10
    }
)

result = response.json()

# 使用推薦
final_prompt = result["suggested_prompt"]
print(final_prompt)
# 輸出: "1girl, solo, cyberpunk, city, night, ..."
```

---

## GPT-4 整合

### Function Calling 定義

```json
{
  "name": "recommend_image_tags",
  "description": "根據用戶的圖像描述推薦最適合的 Danbooru 標籤組合，用於 AI 圖像生成",
  "parameters": {
    "type": "object",
    "properties": {
      "description": {
        "type": "string",
        "description": "用戶對想要生成圖像的自然語言描述，例如：'一個孤獨的女孩在賽博龐克城市的夜晚'"
      },
      "max_tags": {
        "type": "integer",
        "description": "最多返回的標籤數量",
        "default": 10,
        "minimum": 1,
        "maximum": 50
      },
      "exclude_adult": {
        "type": "boolean",
        "description": "是否排除成人內容標籤",
        "default": true
      }
    },
    "required": ["description"]
  }
}
```

### 完整範例

```python
from openai import OpenAI
import requests

client = OpenAI()

# 定義工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "recommend_image_tags",
            "description": "推薦適合 AI 圖像生成的標籤",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "圖像描述"
                    },
                    "max_tags": {
                        "type": "integer",
                        "default": 10
                    }
                },
                "required": ["description"]
            }
        }
    }
]

# 用戶對話
messages = [
    {
        "role": "user",
        "content": "我想要生成一張孤獨的女孩在賽博龐克城市夜晚的圖片"
    }
]

# GPT-4 處理
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# 處理工具調用
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    
    # 調用 API
    function_args = json.loads(tool_call.function.arguments)
    api_response = requests.post(
        "https://your-api.com/api/llm/recommend-tags",
        json=function_args
    )
    
    result = api_response.json()
    
    # 將結果返回給 GPT-4
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result)
    })
    
    # 獲得最終回應
    final_response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages
    )
    
    print(final_response.choices[0].message.content)
```

---

## Claude 整合

### Tool Definition

```json
{
  "name": "recommend_image_tags",
  "description": "Recommend Danbooru tags for AI image generation based on user's natural language description. Returns structured tag recommendations with explanations.",
  "input_schema": {
    "type": "object",
    "properties": {
      "description": {
        "type": "string",
        "description": "Natural language description of the desired image"
      },
      "max_tags": {
        "type": "integer",
        "description": "Maximum number of tags to return",
        "default": 10
      },
      "exclude_adult": {
        "type": "boolean",
        "description": "Whether to exclude adult content tags",
        "default": true
      }
    },
    "required": ["description"]
  }
}
```

### 完整範例

```python
import anthropic
import requests
import json

client = anthropic.Anthropic()

# 定義工具
tools = [
    {
        "name": "recommend_image_tags",
        "description": "Recommend tags for AI image generation",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Image description"
                },
                "max_tags": {
                    "type": "integer",
                    "default": 10
                }
            },
            "required": ["description"]
        }
    }
]

# 用戶對話
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": "I want to generate an image of a lonely girl in a cyberpunk city at night"
        }
    ]
)

# 處理工具使用
if message.stop_reason == "tool_use":
    tool_use = next(
        block for block in message.content 
        if block.type == "tool_use"
    )
    
    # 調用 API
    api_response = requests.post(
        "https://your-api.com/api/llm/recommend-tags",
        json=tool_use.input
    )
    
    result = api_response.json()
    
    # 返回給 Claude
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Generate image tags..."},
            {"role": "assistant", "content": message.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps(result)
                    }
                ]
            }
        ]
    )
    
    print(response.content[0].text)
```

---

## API 端點詳解

### 1. POST /api/llm/recommend-tags

**最常用的端點** - 智能標籤推薦

**請求**:
```json
{
  "description": "a lonely girl in cyberpunk city at night",
  "max_tags": 10,
  "exclude_adult": true,
  "min_popularity": 100,
  "balance_categories": true
}
```

**回應**:
```json
{
  "query": "a lonely girl in cyberpunk city at night",
  "recommended_tags": [
    {
      "tag": "1girl",
      "confidence": 0.98,
      "popularity_tier": "very_popular",
      "post_count": 5234567,
      "category": "CHARACTER",
      "match_reason": "直接對應 'girl' 關鍵字",
      "usage_context": "核心標籤，用於指定單一女性角色",
      "weight": 10
    }
  ],
  "category_distribution": {
    "CHARACTER": 2,
    "ART_STYLE": 1,
    "ENVIRONMENT": 2
  },
  "quality_assessment": {
    "overall_score": 92,
    "balance_score": 88,
    "popularity_score": 95,
    "warnings": []
  },
  "suggested_prompt": "1girl, solo, cyberpunk, city, night",
  "metadata": {
    "processing_time_ms": 145,
    "total_candidates": 89,
    "algorithm": "keyword_matching_v1"
  }
}
```

### 2. POST /api/llm/validate-prompt

**標籤品質驗證**

**請求**:
```json
{
  "tags": ["1girl", "solo", "school_uniform"],
  "strict_mode": false
}
```

**回應**:
```json
{
  "overall_score": 85,
  "validation_result": "good",
  "issues": [],
  "suggestions": {
    "recommended_fixes": [],
    "improved_prompt": "1girl, solo, school_uniform"
  },
  "category_analysis": {
    "distribution": {
      "CHARACTER": 2,
      "CHARACTER_RELATED": 1
    },
    "balance_score": 75,
    "recommendations": [
      "考慮添加環境或動作標籤以豐富畫面"
    ]
  }
}
```

### 3. POST /api/llm/search-by-keywords

**智能關鍵字搜尋**

**請求**:
```json
{
  "keywords": "lonely cyberpunk girl",
  "max_results": 10
}
```

### 4. GET /api/llm/popular-by-category

**分類熱門標籤**

**參數**:
- `category`: 分類名稱 (可選)
- `limit`: 返回數量 (預設 20)

---

## 最佳實踐

### 1. 工作流程設計

**推薦流程**:
```
1. 用戶輸入描述
2. LLM 調用 recommend-tags
3. (可選) LLM 調用 validate-prompt 驗證
4. LLM 向用戶呈現結果和建議
5. 用戶確認或調整
6. 生成最終 prompt
```

### 2. 錯誤處理

```python
try:
    response = requests.post(api_url, json=params, timeout=10)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.Timeout:
    # 處理超時
    print("API 請求超時，請稍後再試")
except requests.exceptions.HTTPError as e:
    # 處理 HTTP 錯誤
    print(f"API 錯誤: {e.response.status_code}")
except Exception as e:
    # 處理其他錯誤
    print(f"未預期的錯誤: {e}")
```

### 3. 回應解讀

**重要欄位**:
- `suggested_prompt`: 可直接使用的 prompt
- `quality_assessment.overall_score`: 整體品質分數 (0-100)
- `category_distribution`: 檢查分類是否平衡
- `warnings`: 注意警告訊息

### 4. 參數優化

**常用配置**:
```python
# 平衡品質和多樣性
{
  "max_tags": 8-12,
  "min_popularity": 100,
  "balance_categories": True
}

# 追求極致品質
{
  "max_tags": 6-8,
  "min_popularity": 1000,
  "balance_categories": True
}

# 允許更多創意
{
  "max_tags": 15-20,
  "min_popularity": 10,
  "balance_categories": False
}
```

---

## 常見問題

### Q1: API 回應太慢怎麼辦？

**A**: 
- 檢查網路連接
- 減少 `max_tags` 數量
- API 有快取機制，重複查詢會更快

### Q2: 推薦的標籤不夠精確？

**A**:
- 使用更具體的描述
- 增加關鍵詞
- 檢查 `confidence` 分數，過濾低信心度標籤

### Q3: 如何處理多語言輸入？

**A**:
- API 支援中英文輸入
- 建議使用英文獲得最佳效果
- 中文會自動轉換為對應的英文標籤

### Q4: 可以緩存 API 結果嗎？

**A**:
- 可以緩存常見查詢
- 建議 TTL 設置為 1 小時
- API 本身也有快取

### Q5: 如何獲得更好的分類平衡？

**A**:
- 設置 `balance_categories: true`
- 在描述中包含多種元素
- 檢查 `category_distribution` 調整

---

## 技術支援

- 📖 **API 文檔**: https://your-api.com/docs
- 🐛 **問題回報**: GitHub Issues
- 💬 **討論區**: GitHub Discussions

---

**建立日期**: 2025-01-14  
**最後更新**: 2025-01-14  
**版本**: 1.0.0

