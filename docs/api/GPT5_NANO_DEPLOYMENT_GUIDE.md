# 🚀 GPT-5 Nano 部署準備指南

## 📋 部署前準備清單

### 1. 🔑 API 金鑰設置
```bash
# 1. 前往 OpenAI 平台獲取 API 金鑰
# https://platform.openai.com/api-keys

# 2. 設置環境變數
export OPENAI_API_KEY="your_api_key_here"
```

### 2. 📦 依賴安裝
```bash
# 安裝 OpenAI Python 客戶端
pip install openai

# 或更新到最新版本
pip install --upgrade openai
```

### 3. 🔧 環境配置
```bash
# 在 .env 文件中添加
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-nano
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7
OPENAI_TIMEOUT=30
```

## 🏗️ 技術特性

### GPT-5 Nano 優勢
- ✅ **最快速度** - 最優用戶體驗
- ✅ **最具成本效益** - 適合預算控制
- ✅ **400,000 tokens 上下文窗口** - 支持大型對話
- ✅ **針對明確定義任務優化** - 完美適合標籤推薦

### 適用場景
- 🎯 標籤推薦和分類
- 🎯 快速回應任務
- 🎯 成本敏感的應用
- 🎯 移動端和邊緣計算

## 💻 代碼集成範例

### 1. 基礎 API 調用
```python
import openai
import os
from typing import Dict, List

class GPT5NanoClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = "gpt-5-nano"
        self.max_tokens = 500
        self.temperature = 0.7
    
    async def generate_tags(self, description: str) -> Dict:
        """生成標籤推薦"""
        try:
            response = await self.client.chat.completions.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一個專業的標籤推薦助手。根據用戶的描述，推薦最相關的標籤組合。
                        
                        請以 JSON 格式返回：
                        {
                            "tags": ["標籤1", "標籤2", "標籤3"],
                            "categories": ["分類1", "分類2"],
                            "confidence": 0.95,
                            "reasoning": "推薦理由"
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"請為以下描述推薦標籤：{description}"
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=30
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"GPT-5 Nano API 調用失敗: {e}")
            return None
```

### 2. 與現有系統集成
```python
# 在 src/api/routers/llm/recommendations.py 中集成
from .gpt5_nano_client import GPT5NanoClient

@router.post("/recommend-tags")
async def recommend_tags(
    request: LLMRecommendRequest,
    db: SupabaseService = Depends(get_supabase_service)
):
    # 初始化 GPT-5 Nano 客戶端
    gpt5_client = GPT5NanoClient()
    
    # 調用 GPT-5 Nano API
    gpt5_response = await gpt5_client.generate_tags(request.description)
    
    if gpt5_response:
        # 解析 GPT-5 回應
        import json
        try:
            tags_data = json.loads(gpt5_response)
            return TagRecommendationResponse(
                recommended_tags=tags_data.get("tags", []),
                categories=tags_data.get("categories", []),
                confidence=tags_data.get("confidence", 0.8),
                reasoning=tags_data.get("reasoning", "")
            )
        except json.JSONDecodeError:
            # 回退到現有邏輯
            pass
    
    # 回退到現有的關鍵字匹配邏輯
    return await fallback_keyword_matching(request, db)
```

## 💰 成本優化策略

### 1. Token 使用優化
```python
def optimize_prompt(description: str) -> str:
    """優化提示詞以減少 token 使用"""
    # 移除冗餘文字
    cleaned = description.strip()
    
    # 限制長度
    if len(cleaned) > 1000:
        cleaned = cleaned[:1000] + "..."
    
    return cleaned
```

### 2. 快取機制
```python
import redis
from functools import lru_cache

# 設置 Redis 快取
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=1000)
async def cached_tag_recommendation(description_hash: str):
    """快取標籤推薦結果"""
    cached_result = redis_client.get(f"tags:{description_hash}")
    if cached_result:
        return json.loads(cached_result)
    return None
```

### 3. 批量處理
```python
async def batch_process_descriptions(descriptions: List[str]):
    """批量處理多個描述以降低成本"""
    # 合併多個描述到一個請求中
    combined_prompt = "請為以下描述分別推薦標籤：\n" + "\n".join(descriptions)
    
    response = await gpt5_client.generate_tags(combined_prompt)
    return response
```

## 🧪 測試策略

### 1. 單元測試
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_gpt5_nano_tag_generation():
    """測試 GPT-5 Nano 標籤生成"""
    client = GPT5NanoClient()
    
    with patch.object(client.client.chat.completions, 'acreate') as mock_create:
        mock_create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content='{"tags": ["美食", "餐廳"], "confidence": 0.9}'))]
        )
        
        result = await client.generate_tags("我想找好吃的餐廳")
        assert result is not None
```

### 2. 集成測試
```python
@pytest.mark.asyncio
async def test_api_integration():
    """測試 API 集成"""
    test_request = {
        "description": "美食推薦"
    }
    
    response = await client.post("/api/llm/recommend-tags", json=test_request)
    assert response.status_code == 200
    assert "recommended_tags" in response.json()
```

## 📊 監控和日誌

### 1. 性能監控
```python
import time
import logging

async def monitored_api_call(description: str):
    """監控 API 調用性能"""
    start_time = time.time()
    
    try:
        result = await gpt5_client.generate_tags(description)
        duration = time.time() - start_time
        
        logging.info(f"GPT-5 Nano 調用成功 - 耗時: {duration:.2f}s")
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        logging.error(f"GPT-5 Nano 調用失敗 - 耗時: {duration:.2f}s, 錯誤: {e}")
        raise
```

### 2. 成本追蹤
```python
def track_token_usage(response):
    """追蹤 token 使用量"""
    if hasattr(response, 'usage'):
        logging.info(f"Token 使用 - 輸入: {response.usage.prompt_tokens}, "
                    f"輸出: {response.usage.completion_tokens}, "
                    f"總計: {response.usage.total_tokens}")
```

## 🚀 部署步驟

### 1. 準備階段
- [ ] 獲取 OpenAI API 金鑰
- [ ] 安裝 OpenAI 客戶端庫
- [ ] 設置環境變數
- [ ] 創建 GPT5NanoClient 類別

### 2. 開發階段
- [ ] 實現基礎 API 調用
- [ ] 集成到現有推薦系統
- [ ] 添加錯誤處理和回退機制
- [ ] 實現快取和優化

### 3. 測試階段
- [ ] 單元測試
- [ ] 集成測試
- [ ] 性能測試
- [ ] 成本測試

### 4. 部署階段
- [ ] 生產環境配置
- [ ] 監控設置
- [ ] 日誌配置
- [ ] 性能優化

## 📚 相關資源

- [OpenAI API 文檔](https://platform.openai.com/docs)
- [GPT-5 系列介紹](https://openai.com/gpt-5)
- [Python 客戶端庫](https://github.com/openai/openai-python)
- [最佳實踐指南](https://platform.openai.com/docs/guides/production-best-practices)

## 🎯 下一步行動

1. **立即開始**: 設置 API 金鑰和基礎環境
2. **開發集成**: 實現 GPT5NanoClient 類別
3. **測試驗證**: 進行全面測試
4. **部署上線**: 逐步部署到生產環境

準備好了嗎？讓我們開始 GPT-5 Nano 的集成！🚀
