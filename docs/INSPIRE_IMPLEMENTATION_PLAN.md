# 🚀 Inspire Agent 實施計劃

**專案：** Prompt-Scribe  
**模組：** Inspire Creative Agent  
**版本：** 2.0.0  
**日期：** 2025-10-21  
**預計完成：** 2025-11-04 (2 週)  
**狀態：** 規劃階段

---

## 📋 目錄

1. [總體規劃](#總體規劃)
2. [技術架構](#技術架構)
3. [實施階段](#實施階段)
4. [API 設計](#api-設計)
5. [前端整合](#前端整合)
6. [測試策略](#測試策略)
7. [部署計劃](#部署計劃)

---

## 🎯 總體規劃

### 專案目標

將現有的 Inspire 標籤推薦功能升級為完整的 **AI 創作夥伴系統**：

**從：** 輸入描述 → 返回標籤列表  
**到：** 對話式創作 → 完整結構化 Prompt

### 關鍵成果（Deliverables）

- ✅ 後端 Inspire Agent 系統（Python + FastAPI）
- ✅ 5 個專門工具完整實現
- ✅ 4 層防護措施
- ✅ Session 管理系統
- ✅ 前端對話 UI（React + Next.js）
- ✅ 完整測試套件
- ✅ 監控和分析系統

### 時程概覽

```
Week 1: 後端 Agent 核心（40h）
├─ Day 1-2: Agent 框架和工具 (16h)
├─ Day 3: 搜尋系統整合 (8h)
├─ Day 4: 防護措施 (8h)
└─ Day 5: 後端測試 (8h)

Week 2: 前端整合與優化（40h）
├─ Day 6-7: 前端對話 UI (16h)
├─ Day 8: 完整流程測試 (8h)
├─ Day 9: 性能優化 (8h)
└─ Day 10: 文檔與部署 (8h)

總計：80 小時（2 週全職 or 4 週兼職）
```

---

## 🏗️ 技術架構

### 系統分層架構

```
┌─────────────────────────────────────────────────────┐
│                  前端層 (Next.js 15)                  │
├─────────────────────────────────────────────────────┤
│  /inspire 頁面                                       │
│  ├─ ConversationView (對話界面)                      │
│  ├─ DirectionCards (創意方向卡片)                    │
│  ├─ FinalPromptViewer (最終輸出展示)                 │
│  └─ useInspireAgent (Agent 互動 Hook)                │
└─────────────────────────────────────────────────────┘
                         ↓ HTTP/REST
┌─────────────────────────────────────────────────────┐
│                  API 層 (FastAPI)                     │
├─────────────────────────────────────────────────────┤
│  /api/inspire/start (POST)                           │
│  /api/inspire/continue (POST)                        │
│  /api/inspire/feedback (POST)                        │
│  /api/inspire/finalize (GET)                         │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Agent 協調層 (Python)                    │
├─────────────────────────────────────────────────────┤
│  InspireAgentSystem                                  │
│  ├─ Session 管理                                     │
│  ├─ 防護措施協調                                     │
│  ├─ Agent 循環控制                                   │
│  └─ 工具執行管理                                     │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                Agent 核心 (GPT-5 Mini)                │
├─────────────────────────────────────────────────────┤
│  - 自主決策（選擇工具和路徑）                        │
│  - 對話生成（自然語言回應）                          │
│  - 上下文管理（記住對話歷史）                        │
└─────────────────────────────────────────────────────┘
                         ↓
┌──────────┬──────────┬──────────┬──────────┬─────────┐
│ Tool 1   │ Tool 2   │ Tool 3   │ Tool 4   │ Tool 5  │
│ under-   │ search_  │ generate │ validate │finalize │
│ stand    │ examples │ _ideas   │ _quality │ _prompt │
└──────────┴──────────┴──────────┴──────────┴─────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                  資料與服務層                         │
├─────────────────────────────────────────────────────┤
│  - Supabase PostgreSQL (140K+ 標籤)                  │
│  - Redis (Session 快取)                              │
│  - OpenAI API (GPT-5 Mini)                           │
│  - Embedding Service (語義搜尋，可選)                 │
└─────────────────────────────────────────────────────┘
```

### 目錄結構

```
src/api/
├── routers/
│   └── inspire/
│       ├── __init__.py
│       ├── conversation.py        # API 端點
│       └── webhooks.py             # Webhook（可選）
│
├── services/
│   ├── inspire_agent.py            # 🆕 Agent 核心
│   ├── inspire_tools.py            # 🆕 工具實現
│   ├── inspire_session.py          # 🆕 Session 管理
│   ├── inspire_guardrails.py       # 🆕 防護措施
│   └── inspire_analytics.py        # 🆕 分析追蹤
│
├── models/
│   ├── inspire_models.py           # 🆕 資料模型
│   └── inspire_schemas.py          # 🆕 工具 Schemas
│
└── utils/
    └── inspire_helpers.py          # 🆕 輔助函數

prompt-scribe-web/
├── app/
│   └── inspire/
│       ├── page.tsx                # 主頁（需重構）
│       └── components/
│           ├── ConversationView.tsx      # 🆕 對話界面
│           ├── DirectionCards.tsx        # 🆕 方向卡片
│           ├── FinalPromptViewer.tsx     # 🆕 最終輸出
│           └── AgentThinking.tsx         # 🆕 思考動畫
│
└── lib/
    ├── hooks/
    │   └── useInspireAgent.ts      # 🆕 Agent Hook
    └── api/
        └── inspire-agent.ts        # 🆕 API Client
```

---

## 📅 實施階段

### Week 1: 後端 Agent 系統

#### Day 1: Agent 框架搭建（8h）

**任務清單：**
- [ ] 創建 `inspire_agent.py` 主文件
- [ ] 實現 `InspireAgent` 類別
  - [ ] 構造函數、初始化
  - [ ] `run_conversation()` 主循環
  - [ ] 工具調用框架
- [ ] 實現 `InspireSession` 資料模型
- [ ] 基礎單元測試

**技術重點：**
```python
# src/api/services/inspire_agent.py

class InspireAgent:
    """Inspire AI Agent - 創作夥伴"""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.model = "gpt-5-mini"
        self.tools = self._init_tools()
        self.system_prompt = INSPIRE_AGENT_SYSTEM_PROMPT
    
    async def run_conversation(
        self, 
        session: InspireSession,
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Agent 主循環
        實現 ReAct 模式：Reasoning + Acting
        """
        
        # 構建對話歷史
        messages = self._build_messages(session, user_message)
        
        # Agent 決策循環（最多 10 輪）
        for iteration in range(10):
            
            # 調用 GPT-5 讓 Agent 決策
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7
            )
            
            # 處理回應...
            # [詳細實現見完整代碼]
        
        return result
```

**測試：**
```python
# tests/test_inspire_agent_basic.py

async def test_agent_initialization():
    """測試 Agent 初始化"""
    agent = InspireAgent(client)
    assert agent.model == "gpt-5-mini"
    assert len(agent.tools) == 5

async def test_simple_conversation():
    """測試簡單對話"""
    session = InspireSession()
    result = await agent.run_conversation(
        session,
        user_message="櫻花樹下的和服少女"
    )
    
    assert result["type"] in ["message", "directions", "completed"]
    assert session.total_tool_calls > 0
```

**完成標準：**
- ✅ Agent 能啟動並運行
- ✅ 能處理簡單輸入
- ✅ 基礎測試通過

---

#### Day 2: 工具實現 - Part 1（8h）

**任務清單：**
- [ ] 實現 `understand_intent` 工具
- [ ] 實現 `search_examples` 工具
  - [ ] 關鍵字搜尋邏輯
  - [ ] 語義搜尋邏輯（使用 embeddings）
  - [ ] Auto 策略（Agent 自選）
- [ ] 工具單元測試

**understand_intent 實現：**
```python
# src/api/services/inspire_tools.py

class InspireTools:
    """Inspire Agent 工具集"""
    
    async def understand_intent(
        self, 
        args: Dict, 
        session: InspireSession
    ) -> Dict:
        """
        工具 1: 理解使用者意圖
        這個工具本身不調用 LLM，只是記錄 Agent 的理解結果
        """
        
        # 提取 Agent 傳來的理解結果
        core_mood = args["core_mood"]
        visual_elements = args.get("visual_elements", [])
        clarity_level = args["clarity_level"]
        confidence = args["confidence"]
        next_action = args["next_action"]
        
        # 保存到 Session
        session.extracted_intent = {
            "core_mood": core_mood,
            "visual_elements": visual_elements,
            "style_preference": args.get("style_preference"),
            "clarity_level": clarity_level,
            "confidence": confidence,
            "analyzed_at": datetime.now().isoformat()
        }
        
        session.current_phase = "understood"
        
        # 返回給 Agent 的確認
        return {
            "status": "understood",
            "summary": f"理解：{core_mood}，清晰度 {clarity_level}",
            "recommended_next_action": next_action,
            "confidence": confidence
        }
```

**search_examples 實現：**
```python
async def search_examples(
    self,
    args: Dict,
    session: InspireSession
) -> Dict:
    """
    工具 2: 搜尋參考案例
    從資料庫搜尋類似的標籤和組合
    """
    
    keywords = args["search_keywords"]
    purpose = args["search_purpose"]
    strategy = args.get("search_strategy", "auto")
    min_pop = args.get("min_popularity", 1000)
    max_results = args.get("max_results", 10)
    
    # 根據策略選擇搜尋方法
    if strategy == "auto":
        # Agent 讓我們自動決定
        # 判斷：關鍵字是具體詞彙還是抽象概念？
        strategy = self._determine_search_strategy(keywords)
    
    # 執行搜尋
    if strategy == "semantic":
        results = await self._semantic_search(keywords, min_pop, max_results)
    else:  # keyword
        results = await self._keyword_search(keywords, min_pop, max_results)
    
    # 分析結果，找出常見組合
    common_combos = await self._find_common_combinations(results)
    
    # 生成建議
    suggestions = self._generate_search_suggestions(
        results, 
        purpose, 
        session.extracted_intent
    )
    
    # 記錄搜尋
    session.record_tool_call("search_examples", {
        "keywords": keywords,
        "strategy": strategy,
        "found": len(results)
    })
    
    return {
        "found": len(results),
        "search_strategy_used": strategy,
        "examples": [
            {
                "tag": tag["name"],
                "category": tag["main_category"],
                "popularity": tag["post_count"],
                "usage_hint": self._get_tag_hint(tag)
            }
            for tag in results[:max_results]
        ],
        "common_combinations": common_combos,
        "suggestions": suggestions
    }

async def _semantic_search(
    self, 
    keywords: List[str], 
    min_pop: int, 
    limit: int
) -> List[Dict]:
    """語義搜尋（使用 embeddings）"""
    
    # 1. 將關鍵字轉為 embedding
    query_text = " ".join(keywords)
    query_embedding = await self.embedding_service.embed_text(query_text)
    
    # 2. 向量相似度搜尋
    results = await self.db.vector_search(
        table="tag_embeddings",
        embedding=query_embedding,
        limit=limit * 2,  # 多拿一些
        min_similarity=0.6
    )
    
    # 3. 過濾低流行度
    filtered = [r for r in results if r["post_count"] >= min_pop]
    
    return filtered[:limit]

async def _keyword_search(
    self,
    keywords: List[str],
    min_pop: int,
    limit: int
) -> List[Dict]:
    """關鍵字搜尋（PostgreSQL 全文搜尋）"""
    
    results = await self.db.search_tags_by_keywords(
        keywords=keywords,
        use_fuzzy=True,
        min_post_count=min_pop,
        limit=limit
    )
    
    return results
```

**完成標準：**
- ✅ 兩個工具能正常工作
- ✅ 搜尋結果準確相關
- ✅ 單元測試覆蓋率 >80%

---

#### Day 3: 工具實現 - Part 2（8h）

**任務清單：**
- [ ] 實現 `generate_ideas` 工具
- [ ] 實現 `validate_quality` 工具  
- [ ] 實現 `finalize_prompt` 工具
- [ ] 整合測試

**generate_ideas 實現重點：**

這個工具比較特殊 - 它本身就是讓 Agent 調用的，所以它的"實現"其實是記錄和處理 Agent 生成的創意方向。

```python
async def generate_ideas(
    self,
    args: Dict,
    session: InspireSession
) -> Dict:
    """
    工具 3: 生成創意方向
    Agent 會在這個工具的 parameters 中直接生成創意
    """
    
    ideas = args["ideas"]
    generation_basis = args.get("generation_basis", "")
    diversity = args.get("diversity_achieved", "moderate")
    
    # 驗證 ideas 格式
    for idea in ideas:
        # 確保必要欄位存在
        assert "title" in idea
        assert "main_tags" in idea
        assert len(idea["main_tags"]) >= 5
        
        # 驗證標籤有效性（快速檢查）
        invalid = await self._quick_validate_tags(idea["main_tags"])
        if invalid:
            logger.warning(f"方向 '{idea['title']}' 包含無效標籤: {invalid}")
    
    # 保存到 Session
    session.generated_directions = ideas
    session.current_phase = "direction_generated"
    
    # 記錄工具調用
    session.record_tool_call("generate_ideas", {
        "num_ideas": len(ideas),
        "diversity": diversity,
        "total_tags": sum(len(i["main_tags"]) for i in ideas)
    })
    
    return {
        "status": "generated",
        "num_directions": len(ideas),
        "ready_for_user_selection": True,
        "diversity_level": diversity
    }
```

**validate_quality 完整實現：**

```python
async def validate_quality(
    self,
    args: Dict,
    session: InspireSession
) -> Dict:
    """
    工具 4: 驗證 Prompt 品質
    執行多維度品質檢查
    """
    
    tags = args["tags_to_validate"]
    check_aspects = args["check_aspects"]
    strictness = args.get("strictness", "moderate")
    
    # 設置嚴格度閾值
    thresholds = {
        "lenient": {"min_score": 60, "max_issues": 5},
        "moderate": {"min_score": 70, "max_issues": 3},
        "strict": {"min_score": 80, "max_issues": 1}
    }[strictness]
    
    issues = []
    score = 100
    
    # 執行各項檢查
    for aspect in check_aspects:
        
        if aspect == "tag_validity":
            # 檢查標籤是否存在於資料庫
            check_result = await self._check_tag_validity(tags)
            if check_result["invalid_tags"]:
                score -= 15 * len(check_result["invalid_tags"])
                issues.append({
                    "type": "invalid_tags",
                    "severity": "high",
                    "affected_tags": check_result["invalid_tags"],
                    "suggestion": "這些標籤不在資料庫中，建議替換",
                    "fixes": check_result["suggested_replacements"]
                })
        
        elif aspect == "conflicts":
            # 檢查衝突標籤
            check_result = await self._check_conflicts(tags)
            if check_result["conflicts"]:
                score -= 20  # 衝突是嚴重問題
                issues.append({
                    "type": "conflicts",
                    "severity": "critical",
                    "conflicts": check_result["conflicts"],
                    "suggestion": "這些標籤互相衝突，只能保留一個",
                    "fixes": check_result["recommended_resolution"]
                })
        
        elif aspect == "redundancy":
            check_result = await self._check_redundancy(tags)
            if check_result["redundant_groups"]:
                score -= 5 * len(check_result["redundant_groups"])
                issues.append({
                    "type": "redundancy",
                    "severity": "low",
                    "redundant_groups": check_result["redundant_groups"],
                    "suggestion": "有些標籤過於相似，可以簡化"
                })
        
        elif aspect == "balance":
            check_result = await self._check_balance(tags)
            if check_result["balance_score"] < 50:
                score -= 10
                issues.append({
                    "type": "imbalanced",
                    "severity": "medium",
                    "current_distribution": check_result["distribution"],
                    "missing_categories": check_result["missing"],
                    "suggestion": f"建議添加 {check_result['missing']} 類標籤"
                })
        
        elif aspect == "popularity":
            check_result = await self._check_popularity(tags)
            if check_result["niche_ratio"] > 0.3:
                score -= 5
                issues.append({
                    "type": "too_niche",
                    "severity": "low",
                    "niche_tags": check_result["niche_tags"],
                    "suggestion": "部分標籤較冷門，生成效果可能不穩定"
                })
    
    # 計算最終分數
    final_score = max(0, min(100, score))
    is_valid = final_score >= thresholds["min_score"]
    
    # 找出優點
    strengths = await self._identify_strengths(tags)
    
    return {
        "is_valid": is_valid,
        "score": final_score,
        "issues": issues,
        "strengths": strengths,
        "quick_fixes": [issue["suggestion"] for issue in issues if issue["severity"] != "low"],
        "category_distribution": await self._get_category_stats(tags)
    }
```

**完成標準：**
- ✅ 所有 5 個工具實現完成
- ✅ 工具能正確被 Agent 調用
- ✅ 返回結果格式正確
- ✅ 單元測試通過

---

#### Day 4: 搜尋系統整合（8h）

**任務清單：**
- [ ] 整合現有 `supabase_client` 的搜尋功能
- [ ] 實現語義搜尋（如果 embeddings 可用）
- [ ] 實現混合搜尋策略
- [ ] 優化搜尋性能
- [ ] 搜尋結果快取

**語義搜尋實現：**
```python
# src/api/services/inspire_search.py

class InspireSearchService:
    """Inspire 專用搜尋服務"""
    
    def __init__(self, db: SupabaseService, openai_client: AsyncOpenAI):
        self.db = db
        self.openai_client = openai_client
        self.cache = {}  # 簡單的記憶體快取
    
    async def search(
        self,
        keywords: List[str],
        strategy: str = "auto",
        purpose: str = "general",
        **kwargs
    ) -> List[Dict]:
        """統一搜尋入口"""
        
        # 快取檢查
        cache_key = f"{'-'.join(sorted(keywords))}:{strategy}:{purpose}"
        if cache_key in self.cache:
            logger.info("Search cache hit")
            return self.cache[cache_key]
        
        # 決定策略
        if strategy == "auto":
            strategy = self._auto_select_strategy(keywords)
        
        # 執行搜尋
        if strategy == "semantic":
            results = await self._semantic_search(keywords, **kwargs)
        else:
            results = await self._keyword_search(keywords, **kwargs)
        
        # 根據 purpose 過濾和排序
        filtered = self._filter_by_purpose(results, purpose)
        
        # 快取結果
        self.cache[cache_key] = filtered
        
        return filtered
    
    def _auto_select_strategy(self, keywords: List[str]) -> str:
        """自動選擇搜尋策略"""
        
        # 檢查關鍵字類型
        abstract_indicators = [
            "感", "氛圍", "feeling", "atmosphere", "mood",
            "vibe", "essence", "tone"
        ]
        
        # 如果包含抽象詞，用語義搜尋
        for keyword in keywords:
            if any(indicator in keyword.lower() for indicator in abstract_indicators):
                return "semantic"
        
        # 如果都是具體詞彙，用關鍵字搜尋（更快）
        return "keyword"
    
    async def _semantic_search(
        self,
        keywords: List[str],
        min_popularity: int = 1000,
        limit: int = 10
    ) -> List[Dict]:
        """語義向量搜尋"""
        
        # 組合關鍵字
        query_text = ", ".join(keywords)
        
        # 生成 embedding
        embedding_response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        
        query_embedding = embedding_response.data[0].embedding
        
        # 向量搜尋（需要資料庫支援）
        # 使用 pgvector 擴展
        results = await self.db.execute_sql(f"""
            SELECT 
                t.name,
                t.main_category,
                t.sub_category,
                t.post_count,
                1 - (e.embedding <=> $1::vector) as similarity
            FROM tags_final t
            JOIN tag_embeddings e ON t.name = e.tag_name
            WHERE t.post_count >= $2
            ORDER BY e.embedding <=> $1::vector
            LIMIT $3
        """, [query_embedding, min_popularity, limit * 2])
        
        # 過濾相似度過低的
        filtered = [r for r in results if r["similarity"] > 0.6]
        
        return filtered[:limit]
```

**完成標準：**
- ✅ 兩種搜尋策略都能工作
- ✅ Auto 策略能正確選擇
- ✅ 搜尋性能 <2 秒
- ✅ 快取機制有效

---

#### Day 5: 防護措施實現（8h）

**任務清單：**
- [ ] 實現 4 層防護措施
- [ ] 整合到 Agent 循環
- [ ] 測試防護觸發
- [ ] 調整閾值參數

**防護措施完整實現：**

```python
# src/api/services/inspire_guardrails.py

class InspireGuardrailSystem:
    """Inspire 防護措施系統"""
    
    def __init__(self):
        self.input_guard = InputGuardrail()
        self.tool_guard = ToolUsageGuardrail()
        self.output_guard = OutputQualityGuardrail()
        self.cost_guard = CostControlGuardrail()
    
    async def check_all(
        self,
        stage: str,
        data: Any,
        session: InspireSession
    ) -> tuple[bool, Optional[str]]:
        """
        檢查所有相關防護
        
        Args:
            stage: "input" | "tool" | "output" | "cost"
            data: 要檢查的資料
            session: 當前 Session
        """
        
        if stage == "input":
            return await self.input_guard.validate(data)
        
        elif stage == "tool":
            tool_name = data
            # 檢查工具使用 + 成本
            tool_ok, tool_msg = await self.tool_guard.validate(tool_name, session)
            if not tool_ok:
                return False, tool_msg
            
            cost_ok, cost_err, cost_warn = await self.cost_guard.check(session)
            if not cost_ok:
                return False, cost_err
            
            return True, cost_warn  # 可能有警告但允許繼續
        
        elif stage == "output":
            return await self.output_guard.validate(data)
        
        elif stage == "cost":
            can_continue, error, warning = await self.cost_guard.check(session)
            return can_continue, error or warning
        
        return True, None
```

**完成標準：**
- ✅ 4 層防護都能正常工作
- ✅ 觸發時能優雅處理
- ✅ 測試覆蓋所有防護場景

---

#### Day 6: Session 管理與儲存（8h）

**任務清單：**
- [ ] 實現 Session 持久化
- [ ] Redis 快取整合
- [ ] Session 清理機制
- [ ] 分析資料收集

**Session 管理實現：**

```python
# src/api/services/inspire_session_manager.py

class InspireSessionManager:
    """Session 生命週期管理"""
    
    def __init__(self, db: SupabaseService, redis: RedisClient):
        self.db = db
        self.redis = redis
        self.active_sessions: Dict[str, InspireSession] = {}
    
    async def create_session(
        self,
        user_id: Optional[str] = None
    ) -> InspireSession:
        """創建新 Session"""
        
        session = InspireSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.now()
        )
        
        # 保存到記憶體
        self.active_sessions[session.id] = session
        
        # 保存到 Redis（快取）
        await self.redis.setex(
            f"inspire:session:{session.id}",
            3600,  # 1 小時 TTL
            session.json()
        )
        
        return session
    
    async def get_session(
        self,
        session_id: str
    ) -> Optional[InspireSession]:
        """獲取 Session"""
        
        # 1. 先查記憶體
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # 2. 查 Redis
        cached = await self.redis.get(f"inspire:session:{session_id}")
        if cached:
            session = InspireSession.parse_raw(cached)
            self.active_sessions[session_id] = session
            return session
        
        # 3. 查資料庫
        data = await self.db.execute_sql(
            "SELECT * FROM inspire_sessions WHERE id = $1",
            [session_id]
        )
        
        if data:
            session = InspireSession(**data[0])
            self.active_sessions[session_id] = session
            return session
        
        return None
    
    async def save_session(
        self,
        session: InspireSession,
        persist_to_db: bool = False
    ):
        """保存 Session"""
        
        session.updated_at = datetime.now()
        
        # 更新記憶體
        self.active_sessions[session.id] = session
        
        # 更新 Redis
        await self.redis.setex(
            f"inspire:session:{session.id}",
            3600,
            session.json()
        )
        
        # 如果完成，持久化到資料庫（用於分析）
        if persist_to_db or session.status in ["completed", "abandoned"]:
            await self._persist_to_database(session)
    
    async def cleanup_old_sessions(self):
        """清理過期 Session（背景任務）"""
        
        cutoff_time = datetime.now() - timedelta(hours=2)
        
        # 清理記憶體中的舊 Session
        to_remove = [
            sid for sid, sess in self.active_sessions.items()
            if sess.updated_at < cutoff_time
        ]
        
        for sid in to_remove:
            del self.active_sessions[sid]
            logger.info(f"Cleaned up session {sid}")
```

**資料庫 Schema：**

```sql
-- inspire_sessions 表
CREATE TABLE inspire_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'active',  -- active, completed, abandoned
    current_phase TEXT,
    
    -- 對話資料（JSONB）
    conversation_history JSONB DEFAULT '[]'::jsonb,
    tool_call_history JSONB DEFAULT '[]'::jsonb,
    
    -- 提取的資訊
    extracted_intent JSONB,
    generated_directions JSONB,
    selected_direction JSONB,
    final_output JSONB,
    
    -- 性能指標
    total_tokens_used INT DEFAULT 0,
    total_cost DECIMAL(10, 6) DEFAULT 0,
    processing_time_ms DECIMAL(10, 2),
    
    -- 品質指標
    quality_score INT,
    user_satisfaction INT,  -- 1-5
    completion_reason TEXT,
    
    -- 索引
    CONSTRAINT valid_status CHECK (status IN ('active', 'completed', 'abandoned')),
    CONSTRAINT valid_satisfaction CHECK (user_satisfaction BETWEEN 1 AND 5)
);

-- 索引
CREATE INDEX idx_inspire_sessions_user_id ON inspire_sessions(user_id);
CREATE INDEX idx_inspire_sessions_created_at ON inspire_sessions(created_at DESC);
CREATE INDEX idx_inspire_sessions_status ON inspire_sessions(status);

-- 分析用視圖
CREATE VIEW inspire_session_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_sessions,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_sessions,
    AVG(total_cost) as avg_cost,
    AVG(quality_score) as avg_quality,
    AVG(user_satisfaction) as avg_satisfaction,
    AVG(jsonb_array_length(tool_call_history)) as avg_tool_calls
FROM inspire_sessions
GROUP BY DATE(created_at);
```

---

### Week 2: 前端整合與優化

#### Day 7-8: 前端對話 UI（16h）

**任務清單：**
- [ ] 重構 `/inspire` 頁面為對話式
- [ ] 創建 `ConversationView` 組件
- [ ] 創建 `DirectionCards` 組件
- [ ] 創建 `FinalPromptViewer` 組件
- [ ] 實現 `useInspireAgent` Hook

**ConversationView 組件：**

```typescript
// app/inspire/components/ConversationView.tsx

'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Loader2, Send, Sparkles } from 'lucide-react'

interface Message {
  role: 'user' | 'agent'
  content: string
  timestamp: Date
  data?: any  // 可能包含方向卡片等結構化資料
}

export function ConversationView() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  
  const sendMessage = async () => {
    if (!input.trim()) return
    
    // 添加使用者訊息
    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsThinking(true)
    
    try {
      // 調用 API
      const endpoint = sessionId ? '/api/inspire/continue' : '/api/inspire/start'
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: input
        })
      })
      
      const data = await response.json()
      
      // 保存 session_id
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id)
      }
      
      // 添加 Agent 回應
      const agentMessage: Message = {
        role: 'agent',
        content: data.message,
        timestamp: new Date(),
        data: data.data  // 可能包含方向卡片
      }
      setMessages(prev => [...prev, agentMessage])
      
    } catch (error) {
      console.error('Agent error:', error)
      // 錯誤處理...
    } finally {
      setIsThinking(false)
    }
  }
  
  return (
    <div className="flex flex-col h-full">
      {/* 對話歷史 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))
        )}
        
        {isThinking && <AgentThinking />}
      </div>
      
      {/* 輸入區 */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="描述你想要的感覺..."
            className="flex-1"
            rows={2}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.ctrlKey) {
                sendMessage()
              }
            }}
          />
          <Button 
            onClick={sendMessage}
            disabled={!input.trim() || isThinking}
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Ctrl + Enter 發送 • 像和朋友聊天一樣自然 😊
        </p>
      </div>
    </div>
  )
}
```

**完成標準：**
- ✅ 對話界面流暢
- ✅ 訊息正確顯示
- ✅ Loading 狀態友好
- ✅ 支援結構化資料展示

---

#### Day 9: 完整流程測試（8h）

**測試範圍：**
- [ ] End-to-End 對話測試
- [ ] 所有 10 個場景測試
- [ ] 防護措施觸發測試
- [ ] 性能壓力測試
- [ ] 成本追蹤驗證

**E2E 測試框架：**

```python
# tests/test_inspire_e2e.py

@pytest.mark.asyncio
async def test_scenario_1_clear_input():
    """場景 1：清晰具體輸入"""
    
    # 開始對話
    response = await client.post("/api/inspire/start", json={
        "message": "櫻花樹下的和服少女，溫柔寧靜的氛圍"
    })
    
    assert response.status_code == 200
    data = response.json()
    session_id = data["session_id"]
    
    # 驗證 Agent 回應
    assert "方向" in data["message"]  # 應該生成方向
    assert len(data.get("directions", [])) in [2, 3]
    
    # 使用者選擇
    response = await client.post("/api/inspire/continue", json={
        "session_id": session_id,
        "message": "3"
    })
    
    # 驗證完成
    assert response.status_code == 200
    final_data = response.json()
    
    if final_data.get("type") == "completed":
        # 驗證最終輸出
        output = final_data["result"]["final_output"]
        assert "positive_prompt" in output
        assert "negative_prompt" in output
        assert output["quality_score"] >= 70
    
    # 獲取 Session 統計
    session = await get_session(session_id)
    assert session.total_tool_calls <= 6  # 快速路徑
    assert session.total_cost < 0.001  # 成本控制
    
    print(f"✅ 場景 1 通過")
    print(f"   工具調用: {session.total_tool_calls} 次")
    print(f"   總成本: ${session.total_cost:.6f}")
    print(f"   品質分數: {session.quality_score}/100")
```

---

#### Day 10: 文檔與部署（8h）

**任務清單：**
- [ ] API 文檔更新（Swagger）
- [ ] 使用者指南
- [ ] 開發者文檔
- [ ] 部署配置更新
- [ ] 環境變數文檔

---

## 🔌 API 設計

### 端點 1: `/api/inspire/start` - 開始對話

**請求：**
```json
POST /api/inspire/start
{
  "message": "使用者的初始輸入",
  "user_id": "optional_user_id",
  "preferences": {
    "language": "zh",
    "verbosity": "concise",
    "creative_freedom": 0.8
  }
}
```

**回應：**
```json
{
  "session_id": "uuid-here",
  "type": "message" | "directions" | "question",
  "message": "Agent 的回應訊息",
  "data": {
    // 如果是 directions
    "directions": [...],
    
    // 如果是 question  
    "question": "...",
    "options": [...]
  },
  "phase": "understanding" | "exploring" | "refining",
  "cost": 0.0003,
  "tokens_used": 1200
}
```

---

### 端點 2: `/api/inspire/continue` - 繼續對話

**請求：**
```json
POST /api/inspire/continue
{
  "session_id": "uuid",
  "message": "使用者的回應",
  "action": {
    "type": "select" | "feedback" | "refine",
    "data": {
      "selected_direction": 1,  // 如果是選擇
      "feedback": "更夢幻一點"    // 如果是反饋
    }
  }
}
```

**回應：** 同 start

---

### 端點 3: `/api/inspire/finalize` - 獲取最終結果

**請求：**
```json
GET /api/inspire/finalize/{session_id}
```

**回應：**
```json
{
  "session_id": "uuid",
  "final_output": {
    "title": "月下獨舞·夢幻版",
    "concept": "...",
    "positive_prompt": "...",
    "negative_prompt": "...",
    "structure": {...},
    "parameters": {...},
    "usage_tips": "..."
  },
  "quality_score": 88,
  "metadata": {
    "total_rounds": 6,
    "total_cost": 0.00072,
    "processing_time": "38.5s",
    "tools_used": ["understand_intent", "search_examples", "generate_ideas", "validate_quality", "finalize_prompt"]
  }
}
```

---

### 端點 4: `/api/inspire/feedback` - 提交反饋

**請求：**
```json
POST /api/inspire/feedback
{
  "session_id": "uuid",
  "satisfaction": 5,  // 1-5
  "feedback_text": "很棒！",
  "would_use_again": true
}
```

---

## 🎨 前端整合方案

### Hook: useInspireAgent

```typescript
// lib/hooks/useInspireAgent.ts

export function useInspireAgent() {
  const [session, setSession] = useState<Session | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isThinking, setIsThinking] = useState(false)
  const [currentPhase, setCurrentPhase] = useState<Phase>('idle')
  
  const startConversation = async (input: string) => {
    setIsThinking(true)
    
    try {
      const response = await fetch('/api/inspire/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })
      
      const data = await response.json()
      
      setSession({ id: data.session_id, ...data.metadata })
      setMessages([
        { role: 'user', content: input },
        { role: 'agent', content: data.message, data: data.data }
      ])
      setCurrentPhase(data.phase)
      
    } finally {
      setIsThinking(false)
    }
  }
  
  const continueConversation = async (message: string) => {
    // 類似實現...
  }
  
  const selectDirection = async (index: number) => {
    // 選擇創意方向...
  }
  
  const provideFeedback = async (feedback: string) => {
    // 提供反饋...
  }
  
  return {
    session,
    messages,
    isThinking,
    currentPhase,
    startConversation,
    continueConversation,
    selectDirection,
    provideFeedback
  }
}
```

---

## 🧪 測試策略

### 測試金字塔

```
        ┌────────────┐
        │  E2E 測試  │  10 個場景對話
        │   (10%)    │
        └────────────┘
       ┌──────────────┐
       │  整合測試     │  Agent + 工具 + 資料庫
       │   (30%)      │
       └──────────────┘
     ┌─────────────────┐
     │   單元測試       │  每個工具、每個防護措施
     │   (60%)         │
     └─────────────────┘
```

### 測試覆蓋目標

| 組件 | 目標覆蓋率 | 重點 |
|------|-----------|------|
| Agent 核心 | >85% | 決策邏輯、循環控制 |
| 工具實現 | >90% | 每個工具的正確性 |
| 防護措施 | >95% | 觸發條件、錯誤處理 |
| API 端點 | >80% | 請求處理、回應格式 |
| 前端組件 | >70% | UI 渲染、互動邏輯 |

### 性能測試

```python
# tests/test_inspire_performance.py

@pytest.mark.benchmark
async def test_performance_targets():
    """驗證性能目標"""
    
    # 目標 1: 快速路徑 <25 秒
    start = time.time()
    result = await run_scenario("清晰輸入")
    duration = time.time() - start
    
    assert duration < 25, f"快速路徑耗時 {duration}s，超過 25s 目標"
    
    # 目標 2: 標準路徑 <45 秒  
    start = time.time()
    result = await run_scenario("模糊輸入")
    duration = time.time() - start
    
    assert duration < 45, f"標準路徑耗時 {duration}s"
    
    # 目標 3: 成本控制
    assert result.total_cost < 0.0015, "成本超標"
```

---

## 🌍 部署計劃

### 環境變數更新

```bash
# .env 新增

# Inspire Agent 配置
INSPIRE_AGENT_ENABLED=true
INSPIRE_AGENT_MODEL=gpt-5-mini
INSPIRE_AGENT_TEMPERATURE=0.7
INSPIRE_MAX_ITERATIONS=10

# 搜尋配置
INSPIRE_ENABLE_SEMANTIC_SEARCH=true
INSPIRE_EMBEDDING_MODEL=text-embedding-3-small
INSPIRE_SEARCH_MIN_POPULARITY=1000

# 防護措施
INSPIRE_MAX_COST_PER_SESSION=0.015
INSPIRE_MAX_TOKENS_PER_SESSION=10000
INSPIRE_MAX_TOOL_CALLS=30

# Session 管理
INSPIRE_SESSION_TTL=3600
INSPIRE_MAX_ACTIVE_SESSIONS=1000
INSPIRE_CLEANUP_INTERVAL=300

# 品質控制
INSPIRE_MIN_QUALITY_SCORE=70
INSPIRE_AUTO_VALIDATE=true
```

### Zeabur 部署更新

```yaml
# zeabur.yaml 更新

services:
  api:
    env:
      # 現有環境變數...
      
      # Inspire Agent 新增
      - key: INSPIRE_AGENT_ENABLED
        value: "true"
      
      - key: INSPIRE_AGENT_MODEL
        value: "gpt-5-mini"
      
      - key: INSPIRE_ENABLE_SEMANTIC_SEARCH
        value: "true"
      
      - key: INSPIRE_MAX_COST_PER_SESSION
        value: "0.015"
    
    # 資源可能需要調整（Agent 比較耗資源）
    resources:
      memory: 1536  # 從 1024 增加到 1536
      cpu: 1.5      # 從 1 增加到 1.5
```

### 資料庫遷移

```sql
-- scripts/08_inspire_agent_tables.sql

-- Inspire Sessions 表
CREATE TABLE IF NOT EXISTS inspire_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'active',
    current_phase TEXT,
    conversation_history JSONB DEFAULT '[]'::jsonb,
    tool_call_history JSONB DEFAULT '[]'::jsonb,
    extracted_intent JSONB,
    generated_directions JSONB,
    final_output JSONB,
    total_tokens_used INT DEFAULT 0,
    total_cost DECIMAL(10, 6) DEFAULT 0,
    quality_score INT,
    user_satisfaction INT
);

-- 索引
CREATE INDEX idx_inspire_sessions_user ON inspire_sessions(user_id);
CREATE INDEX idx_inspire_sessions_created ON inspire_sessions(created_at DESC);

-- RLS 策略（如果需要）
ALTER TABLE inspire_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own sessions" ON inspire_sessions
    FOR SELECT USING (auth.uid()::text = user_id OR user_id IS NULL);
```

---

## 📊 監控與分析

### 需要追蹤的指標

**即時指標（Dashboard）：**
- 活躍 Session 數量
- 平均對話輪次
- 平均完成時間
- 即時成本消耗
- Agent 回應時間

**每日指標：**
- 總 Session 數
- 完成率
- 平均品質分數
- 平均使用者滿意度
- 總成本

**每週指標：**
- 最常用工具
- 最常見失敗原因
- 使用者行為模式
- 成本趨勢

### 分析查詢範例

```sql
-- 每日統計
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_sessions,
    AVG(CASE WHEN status = 'completed' THEN 1.0 ELSE 0 END) as completion_rate,
    AVG(quality_score) as avg_quality,
    AVG(user_satisfaction) as avg_satisfaction,
    AVG(total_cost) as avg_cost,
    SUM(total_cost) as daily_cost
FROM inspire_sessions
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 工具使用統計
SELECT 
    jsonb_array_elements_text(
        jsonb_path_query_array(tool_call_history, '$[*].tool_name')
    ) as tool_name,
    COUNT(*) as usage_count
FROM inspire_sessions
WHERE status = 'completed'
GROUP BY tool_name
ORDER BY usage_count DESC;

-- 失敗原因分析
SELECT 
    completion_reason,
    COUNT(*) as count,
    AVG(total_tool_calls) as avg_tools,
    AVG(total_cost) as avg_cost
FROM inspire_sessions
WHERE status = 'abandoned'
GROUP BY completion_reason
ORDER BY count DESC;
```

---

## 🎯 里程碑與檢查點

### Milestone 1: Agent 核心完成（Week 1 結束）

**驗收標準：**
- [ ] Agent 能處理簡單對話
- [ ] 5 個工具都能正常工作
- [ ] 防護措施能正確觸發
- [ ] 後端單元測試通過（>85% 覆蓋）
- [ ] 能用 Postman/curl 測試完整流程

**Demo：**
- 用 Postman 展示 3 個場景的完整對話
- 展示工具調用日誌
- 展示防護措施觸發

---

### Milestone 2: 前端整合完成（Week 2 Day 8）

**驗收標準：**
- [ ] 對話 UI 流暢自然
- [ ] 創意方向卡片美觀
- [ ] 最終輸出展示完整
- [ ] 前端測試通過
- [ ] 完整流程可在瀏覽器測試

**Demo：**
- 在瀏覽器演示 5 個典型場景
- 展示各種 UI 狀態（loading, error, success）
- 展示完整的使用者體驗

---

### Milestone 3: 生產就緒（Week 2 結束）

**驗收標準：**
- [ ] 所有測試通過（單元 + 整合 + E2E）
- [ ] 性能達標（時間、成本）
- [ ] 文檔完整
- [ ] 部署配置就緒
- [ ] 監控系統運行

**Go-Live 檢查清單：**
- [ ] 功能測試 100% 通過
- [ ] 性能測試達標
- [ ] 安全測試通過
- [ ] 成本控制驗證
- [ ] 備份策略就緒
- [ ] 回滾計劃準備
- [ ] 使用者文檔發布
- [ ] 監控 Dashboard 就緒

---

## 🔧 開發工作流

### Day 1-2 詳細任務分解

**Day 1 上午（4h）：Agent 框架**

```
09:00-10:00 創建檔案結構
├─ src/api/services/inspire_agent.py
├─ src/api/models/inspire_models.py
└─ tests/test_inspire_agent_basic.py

10:00-11:30 實現 InspireAgent 類別
├─ __init__() 方法
├─ _init_tools() 工具註冊
├─ _build_messages() 對話構建
└─ 基礎測試

11:30-13:00 實現 run_conversation() 框架
├─ 主循環邏輯
├─ 工具調用處理
├─ 錯誤處理
└─ 測試基礎對話
```

**Day 1 下午（4h）：工具框架**

```
14:00-15:30 創建工具定義
├─ inspire_schemas.py（5 個工具 schema）
├─ 驗證 schema 格式
└─ 文檔註解

15:30-17:00 實現 InspireTools 類別
├─ 工具執行框架
├─ 工具結果處理
└─ 基礎測試

17:00-18:00 整合測試
└─ Agent 能調用工具
```

**Day 2：工具實現**

```
全天 8h：
├─ understand_intent 實現 (1.5h)
├─ search_examples 實現 (3h)
│   ├─ 關鍵字搜尋 (1h)
│   ├─ 語義搜尋 (1.5h)
│   └─ Auto 策略 (0.5h)
├─ generate_ideas 實現 (1h)
├─ validate_quality 實現 (1.5h)
└─ finalize_prompt 實現 (1h)
```

---

## 💰 成本規劃

### 開發階段成本

**測試調用（開發期間）：**
- 單元測試：~500 次調用 = ~$0.25
- 整合測試：~200 次調用 = ~$0.15
- E2E 測試：~100 次完整對話 = ~$0.07
- 手動測試：~50 次 = ~$0.035
- **總計：** ~$0.50

### 生產階段成本（月度）

**預估使用量：**

| 用戶量級 | 月對話數 | 平均成本/對話 | 月度成本 |
|---------|---------|--------------|---------|
| 小型（100 用戶） | 1,000 | $0.0007 | $0.70 |
| 中型（500 用戶） | 5,000 | $0.0007 | $3.50 |
| 大型（2000 用戶） | 20,000 | $0.0007 | $14.00 |
| 超大（10000 用戶） | 100,000 | $0.0007 | $70.00 |

**成本優化策略：**
1. 快取常見搜尋結果（減少資料庫查詢）
2. 限制 Agent 迭代次數（防止無限循環）
3. 使用較小模型處理簡單任務（未來優化）
4. 批量處理 embedding 請求

---

## 🚨 風險與緩解

### 技術風險

**風險 1: Agent 不穩定（不可預測）**
- **機率：** 中
- **影響：** 高
- **緩解：**
  - 詳細的 System Prompt
  - 嚴格的工具 Schema
  - 完整的測試覆蓋
  - 防護措施兜底

**風險 2: 搜尋性能問題**
- **機率：** 中
- **影響：** 中
- **緩解：**
  - 資料庫索引優化
  - 結果快取
  - 限制搜尋頻率

**風險 3: 成本超標**
- **機率：** 低
- **影響：** 中
- **緩解：**
  - 成本防護措施
  - 即時監控
  - 用戶級別配額

### 產品風險

**風險 4: 使用者不習慣對話式**
- **機率：** 中
- **影響：** 中
- **緩解：**
  - 提供快速模式（跳過對話）
  - 清晰的引導和範例
  - 保留舊版標籤推薦作為備選

**風險 5: Agent 回應品質不穩定**
- **機率：** 中
- **影響：** 高
- **緩解：**
  - 詳細的對話範例（Few-shot）
  - 持續的 Prompt 優化
  - 使用者反饋循環
  - validate_quality 工具把關

---

## 📈 成功指標

### 上線第一週目標

| 指標 | 目標 | 備註 |
|------|------|------|
| 完成率 | >60% | 開始對話中成功完成的比例 |
| 平均品質分數 | >80/100 | validate_quality 評分 |
| 平均滿意度 | >3.8/5.0 | 使用者評分 |
| 平均時間 | <50s | 完整對話耗時 |
| 平均成本 | <$0.001 | 單次對話成本 |
| 錯誤率 | <5% | API 錯誤或 Agent 失敗 |

### 上線第一個月目標

| 指標 | 目標 | 備註 |
|------|------|------|
| 月活躍用戶 | 100+ | 至少用過一次 |
| 總對話數 | 500+ | - |
| 完成率 | >70% | 持續優化 |
| 平均品質分數 | >85/100 | - |
| 平均滿意度 | >4.0/5.0 | - |
| 總成本 | <$50 | 在預算內 |

---

## 🔄 迭代優化計劃

### Phase 1: MVP（Week 1-2）

**功能範圍：**
- ✅ 5 個核心工具
- ✅ 基礎防護措施
- ✅ 簡單對話 UI
- ❌ 高級功能暫不包含

### Phase 2: 優化（Week 3-4）

**基於 MVP 反饋：**
- [ ] 優化 Agent 對話品質
- [ ] 增強搜尋策略
- [ ] 添加高級工具（如 refine_specific_aspect）
- [ ] UI/UX 優化
- [ ] 性能優化

### Phase 3: 擴展（Month 2）

**新增功能：**
- [ ] 多語言支援（英文）
- [ ] 使用者偏好學習
- [ ] 風格預設（如"賽博龐克風格包"）
- [ ] 社群分享功能
- [ ] 批量生成模式

---

## 📝 檢查清單

### 開發前檢查

- [ ] 所有設計文檔已審閱確認
- [ ] 技術架構已確定
- [ ] 資料庫 schema 已設計
- [ ] API 合約已定義
- [ ] 測試策略已規劃
- [ ] 開發環境已準備

### 開發中檢查（每日）

- [ ] 代碼符合規範
- [ ] 單元測試通過
- [ ] 沒有新增 linter 錯誤
- [ ] Git commit 訊息清晰
- [ ] 重要變更有文檔
- [ ] 性能沒有明顯退化

### 上線前檢查

- [ ] 所有功能測試通過
- [ ] 性能測試達標
- [ ] 安全測試通過
- [ ] 文檔完整更新
- [ ] 部署配置驗證
- [ ] 回滾方案就緒
- [ ] 監控系統運行
- [ ] 成本追蹤啟用
- [ ] 利益相關者審閱通過

---

## 🎓 學習資源

### 開發期間參考

- [OpenAI Function Calling 文檔](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI Agent 構建指南](https://lewlh.github.io/2025/04/22/APracticalGuideToBuildingAgents/)
- [LangChain Agent 文檔](https://python.langchain.com/docs/modules/agents/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

### 參考項目

- **Cursor AI** - 對話式編程助手
- **ChatGPT** - 對話流程設計參考
- **Midjourney Bot** - Prompt 生成靈感

---

## 📞 後續支援

### 開發支援

**遇到問題時：**
1. 查閱設計文檔
2. 檢查對話範例
3. 查看實施計劃
4. 參考 OpenAI 指南

### 上線後支援

**監控 Dashboard：**
- Zeabur Dashboard（基礎監控）
- 自建分析頁面（詳細指標）
- Sentry（錯誤追蹤，可選）

**優化循環：**
```
收集數據（1週）
    ↓
分析失敗案例
    ↓
優化 System Prompt / 工具
    ↓
A/B 測試
    ↓
全量上線
    ↓
重複...
```

---

## 🎉 預期成果

### 2 週後你將擁有：

1. ✅ **功能完整的 AI 創作夥伴**
   - 能理解模糊情緒
   - 能生成多樣創意
   - 能迭代優化
   - 能輸出專業 Prompt

2. ✅ **技術紮實的系統**
   - 基於 OpenAI 最佳實踐
   - 完整的防護措施
   - 良好的測試覆蓋
   - 可擴展的架構

3. ✅ **使用者喜愛的產品**
   - 自然流暢的對話
   - 高品質的輸出
   - 簡潔友好的 UI
   - 新手友好

4. ✅ **可持續的運營**
   - 成本可控（<$50/月初期）
   - 性能穩定
   - 可監控可優化
   - 有成長空間

---

## 🚀 準備開始

### 立即行動

1. **審閱這 3 份文檔**
   - INSPIRE_AGENT_DESIGN.md
   - INSPIRE_CONVERSATION_EXAMPLES.md
   - INSPIRE_IMPLEMENTATION_PLAN.md（本文檔）

2. **確認最終方案**
   - 工具集：5 個工具 ✅
   - 搜尋策略：混合（Agent 自選）✅
   - 輸出格式：結構化 ✅
   - 對話風格：親切朋友 ✅

3. **準備開發環境**
   - 確保 GPT-5 API 可用
   - 確保資料庫 embeddings 表存在（如果用語義搜尋）
   - 準備測試資料

4. **開始編碼！** 🎯

---

**文檔版本：** 2.0.0  
**最後更新：** 2025-10-21  
**預計工時：** 80 小時  
**預計時程：** 2 週全職 / 4 週兼職  
**預計成本：** <$100/月運營

