# 🤖 LLM 整合方案

**文檔日期**: 2025-10-17  
**狀態**: 規劃中

---

## 📊 當前狀況

### ❌ 無真正 LLM 整合

**當前實作**:
- 使用關鍵字匹配（KeywordExpander）
- 資料庫查詢（Supabase）
- 同義詞擴展
- **不是真正的 AI 生成**

**優點**: 快速、免費、可預測  
**缺點**: 創意有限、無法理解複雜語意

---

## 🎯 整合目標

### Inspire 功能需求
1. 理解情緒描述（如「孤獨又夢幻」）
2. 生成創意組合
3. 提供多樣化建議
4. 支援反饋優化

### 其他功能擴展
1. 智能標籤組合
2. Prompt 品質評估
3. 自然語言轉標籤

---

## 🚀 方案選項

### 方案 1：OpenAI GPT-4/3.5（推薦）⭐

**技術棧**:
```python
import openai
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
```

**優點**:
- ✅ 強大的語言理解
- ✅ 豐富的 API 功能
- ✅ 良好的文檔支援
- ✅ 穩定性高

**缺點**:
- ❌ 需要付費（約 $0.002/1K tokens）
- ❌ 需要 API Key
- ❌ 有速率限制

**成本估算**:
- Inspire 單次生成：~500 tokens = $0.001
- 1000 次/月 = $1
- **非常便宜！**

**實作範例**:
```python
# src/api/services/llm_service.py

from openai import AsyncOpenAI
from config import settings
import json

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_inspiration_cards(
        self, 
        description: str,
        available_tags: list[str]
    ) -> list[dict]:
        """使用 GPT 生成靈感卡"""
        
        system_prompt = f"""你是一個 AI 圖像生成助手。
用戶會描述他們想要的感覺或主題，你需要：
1. 理解情緒和意圖
2. 從可用標籤中選擇合適的組合
3. 生成 3 張創意靈感卡

可用標籤庫：{', '.join(available_tags[:100])}...
（共 {len(available_tags)} 個標籤）

返回 JSON 格式：
{{
  "cards": [
    {{
      "subject": "主體描述",
      "scene": "場景描述",
      "style": "風格描述",
      "source_tags": ["tag1", "tag2", "tag3"],
      "confidence_score": 0.85
    }}
  ]
}}
"""
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",  # 或 gpt-4
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000
        )
        
        result = json.loads(response.choices[0].message.content)
        return result["cards"]
```

**配置**:
```python
# config.py
OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
```

```bash
# .env
OPENAI_API_KEY=sk-...your-key...
```

---

### 方案 2：Anthropic Claude（備選）

**優點**:
- ✅ 更好的創意能力
- ✅ 更長的上下文（200K tokens）
- ✅ 更好的指令遵循

**缺點**:
- ❌ 稍貴（約 $0.003/1K tokens）
- ❌ API 較新，文檔較少

**實作**:
```python
import anthropic

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

async def generate_with_claude(description: str):
    message = await client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": description}
        ]
    )
    return message.content
```

---

### 方案 3：本地 LLM（Ollama）

**技術**:
- Ollama + Llama 3.1 / Mistral
- 完全本地運行

**優點**:
- ✅ 完全免費
- ✅ 無 API 限制
- ✅ 資料隱私

**缺點**:
- ❌ 需要 GPU 伺服器
- ❌ 部署複雜
- ❌ 效能較差

**不推薦理由**:
- Zeabur/Vercel 無法運行
- 成本反而更高（需要 GPU 伺服器）

---

### 方案 4：混合模式（推薦用於生產）⭐⭐

**策略**:
1. **免費用戶**: 關鍵字匹配（當前方案）
2. **付費用戶**: GPT-3.5 生成
3. **高級用戶**: GPT-4 生成

**優點**:
- ✅ 成本可控
- ✅ 漸進式升級
- ✅ 保留備用方案

**實作**:
```python
async def generate_cards(description: str, user_tier: str):
    if user_tier == "free":
        # 當前方案：關鍵字匹配
        return await keyword_based_generation(description)
    elif user_tier == "pro":
        # GPT-3.5
        return await llm_generation(description, model="gpt-3.5-turbo")
    else:  # premium
        # GPT-4
        return await llm_generation(description, model="gpt-4")
```

---

## 🔧 實作步驟

### Step 1: 安裝依賴

```bash
cd src/api
pip install openai==1.3.0
```

更新 `requirements.txt`:
```
openai==1.3.0
```

---

### Step 2: 配置環境變數

```bash
# .env（後端）
OPENAI_API_KEY=sk-...your-api-key...

# 可選：選擇模型
OPENAI_MODEL=gpt-3.5-turbo  # 或 gpt-4
```

---

### Step 3: 創建 LLM 服務

創建 `src/api/services/llm_service.py`:

```python
"""
LLM 服務 - OpenAI GPT 整合
"""
from openai import AsyncOpenAI
from config import settings
import json
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """LLM 服務類"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = getattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo")
    
    async def generate_inspiration_cards(
        self,
        description: str,
        available_tags: list[dict],
        num_cards: int = 3
    ) -> list[dict]:
        """
        使用 GPT 生成靈感卡
        
        Args:
            description: 用戶輸入描述
            available_tags: 可用標籤列表（從資料庫查詢）
            num_cards: 生成卡片數量
        
        Returns:
            靈感卡列表
        """
        try:
            # 準備標籤資訊
            tag_summary = self._prepare_tag_summary(available_tags)
            
            # 構建 prompt
            system_prompt = self._build_system_prompt(tag_summary)
            
            # 調用 GPT
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"描述：{description}\n\n請生成 {num_cards} 張靈感卡。"}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1500
            )
            
            # 解析結果
            result = json.loads(response.choices[0].message.content)
            cards = result.get("cards", [])
            
            logger.info(f"成功生成 {len(cards)} 張靈感卡")
            return cards
            
        except Exception as e:
            logger.error(f"LLM 生成失敗: {e}")
            # 降級到關鍵字匹配
            return await self._fallback_generation(description, available_tags)
    
    def _prepare_tag_summary(self, tags: list[dict]) -> str:
        """準備標籤摘要"""
        # 按分類整理標籤
        by_category = {}
        for tag in tags[:50]:  # 只用前 50 個
            cat = tag.get("category", "OTHER")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tag["name"])
        
        # 格式化
        summary = []
        for cat, tag_names in by_category.items():
            summary.append(f"{cat}: {', '.join(tag_names[:10])}")
        
        return "\n".join(summary)
    
    def _build_system_prompt(self, tag_summary: str) -> str:
        """構建系統提示"""
        return f"""你是專業的 AI 圖像生成助手。

你的任務：
1. 理解用戶的情緒和主題描述
2. 從可用標籤中選擇合適的組合
3. 生成 3 張有創意且多樣化的靈感卡

可用標籤（按分類）：
{tag_summary}

輸出格式（JSON）：
{{
  "cards": [
    {{
      "subject": "主體描述（如 'lone girl, contemplative'）",
      "scene": "場景描述（如 'misty forest, dawn'）",
      "lighting": "光線描述（可選）",
      "style": "風格描述（如 'cinematic, dreamy'）",
      "source_tags": ["實際標籤1", "實際標籤2", "標籤3"],
      "confidence_score": 0.85
    }}
  ]
}}

要求：
- 3 張卡片要有多樣性（不同風格/場景/情緒）
- source_tags 必須來自提供的標籤庫
- confidence_score 在 0.6-0.95 之間
- 描述要具體且富有畫面感
"""
    
    async def _fallback_generation(
        self, 
        description: str, 
        tags: list[dict]
    ) -> list[dict]:
        """降級方案：關鍵字匹配"""
        # 使用現有的關鍵字匹配邏輯
        from services.keyword_analyzer import KeywordAnalyzer
        
        analyzer = KeywordAnalyzer()
        keywords = analyzer.extract_keywords(description)
        
        # 簡單組合成卡片
        return [
            {
                "subject": f"{keywords[0] if keywords else 'character'}",
                "scene": f"{keywords[1] if len(keywords) > 1 else 'scene'}",
                "style": "artistic",
                "source_tags": [t["name"] for t in tags[:5]],
                "confidence_score": 0.6
            }
        ]


# 單例
_llm_service = None

def get_llm_service() -> LLMService:
    """獲取 LLM 服務單例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
```

---

### Step 4: 更新 Inspire 端點

修改 `src/api/routers/llm/recommendations.py`:

```python
from services.llm_service import get_llm_service, LLMService

@router.post("/inspire/generate")
async def generate_inspiration(
    request: InspireRequest,
    db: SupabaseService = Depends(get_supabase_service),
    llm: LLMService = Depends(get_llm_service)
):
    """生成靈感卡（使用真正的 LLM）"""
    
    try:
        # 1. 從資料庫獲取候選標籤
        tags = await db.search_tags_by_keywords(
            keywords=extract_keywords(request.description),
            limit=100
        )
        
        # 2. 使用 LLM 生成
        cards = await llm.generate_inspiration_cards(
            description=request.description,
            available_tags=tags,
            num_cards=3
        )
        
        return {
            "mode": detect_mode(request.description),
            "round": 1,
            "cards": cards,
            "suggestions": ["選擇你最喜歡的", "或重新描述"]
        }
        
    except Exception as e:
        logger.error(f"生成失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Step 5: 更新前端 API 客戶端

修改 `prompt-scribe-web/src/lib/api/inspire.ts`:

```typescript
export async function generateInspirationCards(
  input: string,
  sessionId: string
): Promise<InspireGenerateResponse> {
  try {
    // 調用新的 LLM 端點
    const response = await fetch(
      `${API_BASE_URL}/api/llm/inspire/generate`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          description: input,
          session_id: sessionId 
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`API 請求失敗 (${response.status})`);
    }

    return await response.json();
  } catch (error) {
    console.error('生成靈感卡時發生錯誤:', error);
    throw error;
  }
}
```

---

## 💰 成本分析

### OpenAI GPT-3.5 Turbo

| 項目 | 成本 |
|------|------|
| 輸入 | $0.0005 / 1K tokens |
| 輸出 | $0.0015 / 1K tokens |
| **單次 Inspire 生成** | **~$0.001** |
| 1000 次/月 | $1 |
| 10000 次/月 | $10 |

### OpenAI GPT-4

| 項目 | 成本 |
|------|------|
| 輸入 | $0.01 / 1K tokens |
| 輸出 | $0.03 / 1K tokens |
| **單次生成** | **~$0.02** |
| 1000 次/月 | $20 |

**結論**: GPT-3.5 非常便宜，完全可以接受！

---

## 🎯 推薦方案

### 🥇 最佳方案：混合模式

```python
# 配置
LLM_ENABLED = True  # 是否啟用 LLM
LLM_FREE_TIER_LIMIT = 5  # 免費用戶每日限制
LLM_PAID_TIER_UNLIMITED = True  # 付費無限制

# 邏輯
if user.is_paid or (user.daily_llm_count < FREE_TIER_LIMIT):
    # 使用 LLM
    cards = await llm.generate()
    user.daily_llm_count += 1
else:
    # 降級到關鍵字匹配
    cards = await keyword_match()
```

**優點**:
- ✅ 免費用戶有基本體驗
- ✅ 成本完全可控
- ✅ 付費轉換動機
- ✅ 保留降級方案

---

## 📝 實作檢查清單

### 後端
- [ ] 安裝 `openai` 套件
- [ ] 創建 `LLMService` 類
- [ ] 添加環境變數 `OPENAI_API_KEY`
- [ ] 創建新端點 `/api/llm/inspire/generate`
- [ ] 實作降級機制
- [ ] 添加速率限制
- [ ] 測試 API

### 前端
- [ ] 更新 API 客戶端
- [ ] 添加 loading 狀態
- [ ] 處理錯誤情況
- [ ] 測試完整流程

### 部署
- [ ] 配置 Zeabur 環境變數
- [ ] 測試生產環境
- [ ] 監控成本

---

## 📚 參考資源

- [OpenAI API 文檔](https://platform.openai.com/docs)
- [OpenAI Pricing](https://openai.com/pricing)
- [Best Practices](https://platform.openai.com/docs/guides/gpt-best-practices)

---

**最後更新**: 2025-10-17  
**狀態**: ✅ 方案規劃完成，待實作














