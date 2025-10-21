# 🗄️ Inspire Agent 資料庫整合指南

**如何整合現有 Supabase 資料庫與 OpenAI Agents SDK**

**版本**: 1.0.0  
**日期**: 2025-10-21

---

## 📊 現狀分析

### 你已經擁有的資料庫

✅ **Supabase (PostgreSQL)**
- `tags_final` - 140K+ Danbooru 標籤
- `tag_embeddings` - 向量嵌入（語義搜尋用）
- `posts_final` - 貼文資料

✅ **資料庫連接**
- SupabaseService 已實現
- API 正常運作

---

## 🎯 整合策略：三層資料存儲

```
┌─────────────────────────────────────────┐
│ Layer 1: SDK Session (SQLite)           │
│ 用途：對話歷史（自動管理）               │
│ 位置：本地檔案 conversations.db          │
│ 管理：OpenAI Agents SDK                 │
└─────────────────────────────────────────┘
              ↓ 工具調用時讀寫
┌─────────────────────────────────────────┐
│ Layer 2: Supabase - 標籤資料（現有）     │
│ 用途：140K+ 標籤查詢、驗證、搜尋         │
│ 表：tags_final, tag_embeddings           │
│ 管理：現有 SupabaseService              │
└─────────────────────────────────────────┘
              ↓ 保存業務資料
┌─────────────────────────────────────────┐
│ Layer 3: Supabase - Session 元數據（新）  │
│ 用途：業務分析資料                       │
│ 表：inspire_sessions（新建）             │
│ 管理：InspireSessionManager（新建）      │
└─────────────────────────────────────────┘
```

---

## 🔧 實作步驟

### 步驟 1: 擴展現有資料庫 Schema

**執行 SQL Migration：**

```bash
# 使用 Supabase Dashboard 或 psql
psql -U postgres -h db.fumuvmbhmmzkenizksyq.supabase.co -d postgres -f scripts/08_inspire_agent_tables.sql
```

**這個 migration 會：**

1. ✅ 在 `tags_final` 添加新欄位：
   - `category` - Inspire 類別系統
   - `aliases` - 別名列表
   - `conflicts` - 互斥標籤
   - `nsfw_level` - 內容分級（P0）

2. ✅ 創建新表：
   - `tag_cooccur` - 標籤共現統計
   - `inspire_sessions` - Session 元數據

3. ✅ 創建物化視圖：
   - `popular_tags` - 熱門標籤（post_count >= 1000）
   - `conflict_pairs` - 衝突對

4. ✅ 初始化安全設置：
   - 標記封禁標籤（nsfw_level = 'blocked'）
   - 基於現有分類初始化 category

---

### 步驟 2: 創建資料庫服務包裝

**新檔案：** `src/api/services/inspire_db_service.py`

```python
"""
Inspire Agent 資料庫服務
包裝現有的 SupabaseService，提供 Inspire 專用查詢
"""

from typing import List, Dict, Optional
from services.supabase_client import get_supabase_service

class InspireDbService:
    """Inspire Agent 資料庫服務"""
    
    def __init__(self):
        self.supabase = get_supabase_service()
    
    # ============================================
    # 標籤查詢（利用現有 tags_final）
    # ============================================
    
    async def get_tags_by_names(self, tag_names: List[str]) -> List[Dict]:
        """
        批量獲取標籤資訊
        
        Returns:
            [{
                "tag": str,
                "category": str,
                "popularity": int,
                "nsfw_level": str
            }]
        """
        
        result = await self.supabase.execute_sql("""
            SELECT 
                name AS tag,
                category,
                post_count AS popularity,
                nsfw_level
            FROM tags_final
            WHERE name = ANY($1)
        """, [tag_names])
        
        return result
    
    async def search_tags_by_keyword(
        self, 
        keywords: List[str],
        category: Optional[str] = None,
        min_popularity: int = 1000,
        limit: int = 20
    ) -> List[Dict]:
        """
        關鍵字搜尋標籤（利用現有索引）
        
        Returns:
            [{
                "tag": str,
                "category": str,
                "popularity": int,
                "usage_hint": str
            }]
        """
        
        # 構建搜尋條件
        conditions = ["nsfw_level = 'all-ages'", f"post_count >= {min_popularity}"]
        
        if category:
            conditions.append(f"category = '{category}'")
        
        # 關鍵字匹配（使用 ILIKE）
        keyword_conditions = " OR ".join([
            f"name ILIKE '%{kw}%'" for kw in keywords
        ])
        
        conditions.append(f"({keyword_conditions})")
        
        where_clause = " AND ".join(conditions)
        
        result = await self.supabase.execute_sql(f"""
            SELECT 
                name AS tag,
                category,
                post_count AS popularity,
                CASE 
                    WHEN aliases IS NOT NULL AND array_length(aliases, 1) > 0 
                    THEN '別名: ' || array_to_string(aliases, ', ')
                    ELSE '常用標籤'
                END AS usage_hint
            FROM tags_final
            WHERE {where_clause}
            ORDER BY post_count DESC
            LIMIT {limit}
        """)
        
        return result
    
    async def search_tags_semantic(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        語義搜尋標籤（利用現有 tag_embeddings）
        
        使用 pgvector 相似度搜尋
        """
        
        # 先生成 query embedding（使用 OpenAI）
        from openai import AsyncOpenAI
        client = AsyncOpenAI()
        
        embedding_response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        
        query_embedding = embedding_response.data[0].embedding
        
        # 向量搜尋
        result = await self.supabase.execute_sql("""
            SELECT 
                te.tag_name AS tag,
                t.category,
                t.post_count AS popularity,
                (te.embedding <=> $1::vector) AS distance
            FROM tag_embeddings te
            JOIN tags_final t ON te.tag_name = t.name
            WHERE t.nsfw_level = 'all-ages'
              AND t.post_count >= 500
            ORDER BY te.embedding <=> $1::vector
            LIMIT $2
        """, [query_embedding, limit])
        
        # 添加 usage_hint
        for row in result:
            row["usage_hint"] = f"語義相關度：{1 - row['distance']:.2f}"
        
        return result
    
    # ============================================
    # 標籤驗證（利用現有資料）
    # ============================================
    
    async def validate_tags(self, tags: List[str]) -> Dict:
        """
        驗證標籤有效性
        
        Returns:
            {
                "valid": [str],
                "invalid": [str],
                "blocked": [str]
            }
        """
        
        result = await self.supabase.execute_sql("""
            SELECT name, nsfw_level
            FROM tags_final
            WHERE name = ANY($1)
        """, [tags])
        
        found_tags = {row["name"]: row["nsfw_level"] for row in result}
        
        valid = []
        invalid = []
        blocked = []
        
        for tag in tags:
            if tag not in found_tags:
                invalid.append(tag)
            elif found_tags[tag] == 'blocked':
                blocked.append(tag)
            else:
                valid.append(tag)
        
        return {
            "valid": valid,
            "invalid": invalid,
            "blocked": blocked
        }
    
    async def check_conflicts(self, tags: List[str]) -> List[tuple]:
        """
        檢查標籤衝突（利用 conflict_pairs 視圖）
        
        Returns:
            [(tag_a, tag_b), ...]
        """
        
        result = await self.supabase.execute_sql("""
            SELECT DISTINCT tag_a, tag_b
            FROM conflict_pairs
            WHERE tag_a = ANY($1) AND tag_b = ANY($1)
        """, [tags])
        
        return [(row["tag_a"], row["tag_b"]) for row in result]
    
    # ============================================
    # Session 管理（新表）
    # ============================================
    
    async def save_session_metadata(
        self,
        session_id: str,
        data: Dict
    ):
        """保存 Session 元數據"""
        
        await self.supabase.execute_sql("""
            INSERT INTO inspire_sessions (
                session_id, user_id, current_phase,
                extracted_intent, generated_directions,
                total_cost, total_tokens, tool_call_count,
                quality_score, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
            ON CONFLICT (session_id) DO UPDATE SET
                current_phase = EXCLUDED.current_phase,
                extracted_intent = EXCLUDED.extracted_intent,
                generated_directions = EXCLUDED.generated_directions,
                total_cost = EXCLUDED.total_cost,
                total_tokens = EXCLUDED.total_tokens,
                tool_call_count = EXCLUDED.tool_call_count,
                quality_score = EXCLUDED.quality_score,
                updated_at = NOW()
        """, [
            session_id,
            data.get("user_id"),
            data.get("current_phase", "understanding"),
            data.get("extracted_intent"),
            data.get("generated_directions"),
            data.get("total_cost", 0.0),
            data.get("total_tokens", 0),
            data.get("tool_call_count", {}),
            data.get("quality_score")
        ])
    
    async def get_session_metadata(self, session_id: str) -> Optional[Dict]:
        """讀取 Session 元數據"""
        
        result = await self.supabase.execute_sql("""
            SELECT * FROM inspire_sessions
            WHERE session_id = $1
        """, [session_id])
        
        return result[0] if result else None
```

---

### 步驟 3: 創建 Session 管理器（雙存儲協調）

**新檔案：** `src/api/services/inspire_session_manager.py`

```python
"""
Inspire Agent Session 管理器
協調 SDK Session（對話歷史）和 Supabase（業務資料）
"""

from agents import SQLiteSession
from contextvars import ContextVar
from typing import Dict, Optional
import time

# Context 變數（工具間共享）
session_context = ContextVar('inspire_session', default={})

class InspireSessionManager:
    """
    Inspire Session 管理器
    
    職責：
    1. 協調 SDK Session（對話歷史）
    2. 管理 Supabase metadata（業務資料）
    3. 提供 Context 給工具使用
    """
    
    def __init__(self, db_service):
        self.db = db_service
        self.conversations_db_path = "data/inspire_conversations.db"
    
    async def start_session(
        self,
        user_id: Optional[str] = None
    ) -> tuple[str, SQLiteSession]:
        """
        開始新 Session
        
        Returns:
            (session_id, sdk_session)
        """
        
        import uuid
        session_id = f"inspire_{user_id or 'anon'}_{int(time.time())}"
        
        # 1. SDK Session（對話歷史）
        sdk_session = SQLiteSession(
            session_id=session_id,
            db_path=self.conversations_db_path
        )
        
        # 2. 初始化 Context（工具間共享）
        session_context.set({
            "session_id": session_id,
            "user_id": user_id,
            "start_time": time.time(),
            "total_cost": 0.0,
            "tool_calls": {}
        })
        
        # 3. 創建 Supabase 記錄
        await self.db.save_session_metadata(session_id, {
            "user_id": user_id,
            "current_phase": "understanding",
            "created_at": "NOW()"
        })
        
        return session_id, sdk_session
    
    async def continue_session(
        self,
        session_id: str
    ) -> SQLiteSession:
        """
        繼續現有 Session
        
        Returns:
            sdk_session（已載入歷史）
        """
        
        # 1. SDK Session（自動載入對話歷史）
        sdk_session = SQLiteSession(
            session_id=session_id,
            db_path=self.conversations_db_path
        )
        
        # 2. 從 Supabase 讀取業務資料
        metadata = await self.db.get_session_metadata(session_id)
        
        if not metadata:
            raise ValueError(f"Session {session_id} not found")
        
        # 3. 恢復 Context
        session_context.set({
            "session_id": session_id,
            "user_id": metadata.get("user_id"),
            "start_time": time.time(),
            "total_cost": float(metadata.get("total_cost", 0.0)),
            "tool_calls": metadata.get("tool_call_count", {}),
            # 恢復業務資料
            "extracted_intent": metadata.get("extracted_intent"),
            "generated_directions": metadata.get("generated_directions")
        })
        
        return sdk_session
    
    async def save_context_to_db(self, session_id: str):
        """
        將 Context 中的資料保存到 Supabase
        （在 Agent 執行完成後調用）
        """
        
        ctx = session_context.get()
        
        await self.db.save_session_metadata(session_id, {
            "user_id": ctx.get("user_id"),
            "current_phase": ctx.get("current_phase", "understanding"),
            "extracted_intent": ctx.get("extracted_intent"),
            "generated_directions": ctx.get("generated_directions"),
            "selected_direction_index": ctx.get("selected_direction"),
            "final_output": ctx.get("final_output"),
            "total_cost": ctx.get("total_cost", 0.0),
            "total_tokens": ctx.get("total_tokens", 0),
            "tool_call_count": ctx.get("tool_calls", {}),
            "quality_score": ctx.get("quality_score")
        })
```

---

### 步驟 4: 實作 Inspire 工具（連接資料庫）

**範例：understand_intent 工具**

```python
from agents import function_tool
from services.inspire_db_service import InspireDbService
from services.inspire_session_manager import session_context

# 初始化資料庫服務
db_service = InspireDbService()

@function_tool
def understand_intent(
    input_text: str,
    core_mood: str,
    visual_elements: list[str],
    style_preference: str,
    clarity_level: str,
    confidence: float,
    next_action: str
) -> dict:
    """
    理解使用者創作意圖
    
    這個工具會：
    1. 從 Context 讀取 session 資訊
    2. 保存理解結果到 Context（供其他工具使用）
    3. 返回結構化結果給 Agent
    """
    
    # 從 Context 獲取 session 資訊
    ctx = session_context.get()
    
    # 構建返回資料
    intent_data = {
        "core_mood": core_mood,
        "visual_elements": visual_elements,
        "style_preference": style_preference,
        "clarity_level": clarity_level,
        "confidence": confidence,
        "next_action": next_action
    }
    
    # 保存到 Context（其他工具可讀取）
    ctx["extracted_intent"] = intent_data
    session_context.set(ctx)
    
    # 返回給 Agent
    return {
        "status": "understood",
        "summary": f"理解：{core_mood}，清晰度 {clarity_level}",
        "next_action": next_action,
        "confidence": confidence
    }
```

---

**範例：search_examples 工具（訪問 tags_final）**

```python
@function_tool
def search_examples(
    search_keywords: list[str],
    search_purpose: str,
    search_strategy: str = "auto",
    min_popularity: int = 1000,
    max_results: int = 10
) -> dict:
    """
    搜尋參考案例（從 tags_final）
    
    這個工具會：
    1. 根據 strategy 決定搜尋方式
    2. 訪問 Supabase tags_final 表
    3. 返回嚴格格式的結果
    """
    
    import asyncio
    
    # 決定搜尋策略
    if search_strategy == "auto":
        # 具體關鍵字 → keyword
        # 抽象概念 → semantic
        is_abstract = any(kw in ["孤獨", "虛無", "dreamy", "lonely"] for kw in search_keywords)
        strategy = "semantic" if is_abstract else "keyword"
    else:
        strategy = search_strategy
    
    # 執行搜尋（同步包裝）
    if strategy == "keyword":
        results = asyncio.run(
            db_service.search_tags_by_keyword(
                keywords=search_keywords,
                min_popularity=min_popularity,
                limit=max_results
            )
        )
    else:  # semantic
        query_text = " ".join(search_keywords)
        results = asyncio.run(
            db_service.search_tags_semantic(
                query=query_text,
                limit=max_results
            )
        )
    
    # 嚴格格式化（只四個鍵）
    examples = [
        {
            "tag": row["tag"],
            "category": row["category"],
            "popularity": row["popularity"],
            "usage_hint": row.get("usage_hint", "")
        }
        for row in results
    ]
    
    return {
        "examples": examples,
        "search_strategy_used": strategy,
        "found": len(examples)
    }
```

---

**範例：validate_quality 工具（驗證標籤）**

```python
@function_tool
def validate_quality(
    tags: list[str],
    check_aspects: list[str],
    strictness: str = "moderate"
) -> dict:
    """
    驗證標籤品質（訪問 tags_final）
    
    這個工具會：
    1. 檢查標籤是否存在（tags_final）
    2. 檢查衝突（conflict_pairs 視圖）
    3. 檢查類別平衡
    4. 生成 quick_fixes
    """
    
    import asyncio
    
    score = 100
    issues = []
    quick_fixes = {"remove": [], "add": [], "replace": {}}
    
    # 檢查 1: 有效性
    if "validity" in check_aspects:
        validation = asyncio.run(db_service.validate_tags(tags))
        
        if validation["invalid"]:
            score -= 35
            issues.append({
                "type": "invalid_tag",
                "severity": "critical",
                "description": f"{len(validation['invalid'])} 個無效標籤",
                "affected_tags": validation["invalid"]
            })
            quick_fixes["remove"].extend(validation["invalid"])
        
        if validation["blocked"]:
            score -= 50  # 封禁標籤更嚴重
            issues.append({
                "type": "blocked_content",
                "severity": "critical",
                "description": "包含封禁標籤",
                "affected_tags": validation["blocked"]
            })
            quick_fixes["remove"].extend(validation["blocked"])
    
    # 檢查 2: 衝突
    if "conflicts" in check_aspects:
        conflicts = asyncio.run(db_service.check_conflicts(tags))
        
        if conflicts:
            score -= 25
            for tag_a, tag_b in conflicts:
                issues.append({
                    "type": "conflict",
                    "severity": "warning",
                    "description": f"'{tag_a}' 與 '{tag_b}' 衝突",
                    "affected_tags": [tag_a, tag_b]
                })
                # 移除流行度較低的（稍後實現）
                quick_fixes["remove"].append(tag_b)  # 簡化版
    
    # 檢查 3: 平衡（類別分佈）
    if "balance" in check_aspects:
        tags_info = asyncio.run(db_service.get_tags_by_names(tags))
        
        categories = set(t["category"] for t in tags_info if t.get("category"))
        
        if len(categories) < 3:
            score -= 20
            issues.append({
                "type": "imbalance",
                "severity": "warning",
                "description": f"類別不足（{len(categories)}/5）"
            })
    
    return {
        "is_valid": score >= 70,
        "score": score,
        "issues": issues,
        "quick_fixes": quick_fixes
    }
```

---

### 步驟 5: 創建 FastAPI 端點（整合所有層）

**新檔案：** `src/api/routers/inspire/agent.py`

```python
"""
Inspire Agent API 端點
整合 SDK + Supabase + Context
"""

from fastapi import APIRouter, HTTPException
from agents import Agent, Runner
from services.inspire_session_manager import InspireSessionManager
from services.inspire_db_service import InspireDbService
from prompts.inspire_agent_instructions import INSPIRE_SYSTEM_PROMPT

# 導入所有工具
from tools.inspire_tools import (
    understand_intent,
    search_examples,
    generate_ideas,
    validate_quality,
    finalize_prompt
)

router = APIRouter(prefix="/api/inspire", tags=["inspire-agent"])

# 初始化服務
db_service = InspireDbService()
session_manager = InspireSessionManager(db_service)

# 創建 Inspire Agent
inspire_agent = Agent(
    name="Inspire",
    instructions=INSPIRE_SYSTEM_PROMPT,
    tools=[
        understand_intent,
        search_examples,
        generate_ideas,
        validate_quality,
        finalize_prompt
    ],
    model="gpt-5-mini"
)

@router.post("/start")
async def start_inspire_conversation(request: dict):
    """開始新的 Inspire 對話"""
    
    user_message = request.get("message", "")
    user_id = request.get("user_id")
    
    # 1. 創建 Session（雙存儲）
    session_id, sdk_session = await session_manager.start_session(user_id)
    
    # 2. 運行 Agent（SDK 處理對話循環）
    result = await Runner.run(
        agent=inspire_agent,
        input=user_message,
        session=sdk_session,  # SDK 自動管理對話歷史
        max_turns=15
    )
    
    # 3. 保存 Context 到 Supabase（業務資料）
    await session_manager.save_context_to_db(session_id)
    
    # 4. 返回結果
    return {
        "session_id": session_id,
        "response": result.final_output,
        "phase": session_context.get().get("current_phase", "unknown")
    }

@router.post("/continue")
async def continue_inspire_conversation(request: dict):
    """繼續現有對話"""
    
    session_id = request.get("session_id")
    user_message = request.get("message", "")
    
    # 1. 恢復 Session（從兩個存儲載入）
    sdk_session = await session_manager.continue_session(session_id)
    
    # 2. 運行 Agent（SDK 自動包含歷史）
    result = await Runner.run(
        agent=inspire_agent,
        input=user_message,
        session=sdk_session,
        max_turns=15
    )
    
    # 3. 保存更新的 Context 到 Supabase
    await session_manager.save_context_to_db(session_id)
    
    # 4. 返回結果
    return {
        "session_id": session_id,
        "response": result.final_output,
        "phase": session_context.get().get("current_phase", "unknown")
    }
```

---

## 📊 資料流示意圖

### 完整的資料流

```
使用者輸入 "櫻花樹下的和服少女"
    ↓
FastAPI 端點 /api/inspire/start
    ↓
┌─────────────────────────────────────────┐
│ InspireSessionManager.start_session()   │
│ 1. 創建 SDK Session (SQLite)            │
│ 2. 初始化 Context                       │
│ 3. 創建 Supabase 記錄                   │
└─────────────────────────────────────────┘
    ↓
Runner.run(inspire_agent, input, session)
    ↓
┌─────────────────────────────────────────┐
│ Agent 決策循環（SDK 自動）               │
│ ↓                                       │
│ Agent 決定：調用 understand_intent      │
│ ↓                                       │
│ understand_intent 工具執行：             │
│   - 從 Context 讀取 session_id          │
│   - 解析使用者輸入                      │
│   - 保存 intent 到 Context              │
│   - 返回結果給 Agent                    │
│ ↓                                       │
│ Agent 決定：調用 search_examples        │
│ ↓                                       │
│ search_examples 工具執行：               │
│   - 從 Context 讀取 intent              │
│   - 訪問 Supabase tags_final ← 現有資料 │
│   - 返回標籤列表給 Agent                │
│ ↓                                       │
│ Agent 決定：調用 generate_ideas         │
│ ↓                                       │
│ ... 繼續循環                            │
│ ↓                                       │
│ 最終：finalize_prompt                   │
└─────────────────────────────────────────┘
    ↓
Runner.run() 返回 result
    ↓
InspireSessionManager.save_context_to_db()
    ↓
┌─────────────────────────────────────────┐
│ 保存到兩個地方：                         │
│ 1. SDK Session (SQLite)                 │
│    - 對話歷史已自動保存 ✅               │
│                                         │
│ 2. Supabase (PostgreSQL)                │
│    - extracted_intent                   │
│    - generated_directions               │
│    - total_cost                         │
│    - quality_score                      │
└─────────────────────────────────────────┘
    ↓
返回給前端
```

---

## 🎯 關鍵整合點

### 1. 利用現有 tags_final（不需要重建）

```python
# 你已經有的資料（140K+ 標籤）
tags_final:
- name (標籤名稱)
- post_count (流行度) ✅ 已有！
- main_category (主類別) ✅ 已有！

# 我們添加的欄位（不影響現有資料）
- category (Inspire 類別系統)
- aliases (別名)
- conflicts (衝突)
- nsfw_level (安全分級)
```

**Migration 是安全的：**
- ✅ 只添加欄位（ALTER TABLE ADD COLUMN）
- ✅ 不修改現有資料
- ✅ 不刪除任何東西
- ✅ 可回退

---

### 2. 雙存儲協調（自動化）

```python
# 開發者視角：超簡單

# 開始對話
session_id, sdk_session = await session_manager.start_session(user_id)

# 運行 Agent（SDK 處理一切）
result = await Runner.run(agent, input, session=sdk_session)

# 保存業務資料（一行）
await session_manager.save_context_to_db(session_id)

# 完成！

# 背後發生的事：
# - SDK 自動保存對話歷史到 SQLite
# - 工具自動保存業務資料到 Context
# - SessionManager 自動同步 Context 到 Supabase
```

---

### 3. 工具訪問現有資料（透明）

```python
# 工具內部訪問 Supabase
@function_tool
def search_examples(...):
    # 直接查詢現有的 tags_final
    results = asyncio.run(
        db_service.search_tags_by_keyword(...)
    )
    
    # tags_final 的 140K+ 標籤資料立即可用 ✅
    return results
```

---

## 📁 需要創建的新檔案

### 1. SQL Migration

```
scripts/08_inspire_agent_tables.sql ✅（已創建）
```

### 2. Python 服務

```
src/api/services/
├── inspire_db_service.py       （新建）
├── inspire_session_manager.py  （新建）
└── inspire_tools.py            （新建，包含 5 個工具）
```

### 3. API 端點

```
src/api/routers/inspire/
├── __init__.py
└── agent.py                    （新建）
```

---

## 🚀 立即可做（今晚，2-3 小時）

### 行動 1: 執行 SQL Migration

```bash
# 使用 Supabase Dashboard SQL Editor
# 或本地連接（如果有權限）

# 複製 scripts/08_inspire_agent_tables.sql 的內容
# 貼到 Supabase Dashboard → SQL Editor
# 執行
```

**這會：**
- ✅ 擴展 tags_final（添加 4 個新欄位）
- ✅ 創建 inspire_sessions 表
- ✅ 創建 popular_tags 視圖
- ✅ 初始化封禁標籤

**預估時間：** 30 分鐘

---

### 行動 2: 創建基礎服務檔案

**我可以幫你創建：**
1. `inspire_db_service.py`（包裝 Supabase 查詢）
2. `inspire_session_manager.py`（協調雙存儲）
3. `inspire_tools.py`（5 個工具骨架）

**預估時間：** 1-2 小時

---

### 行動 3: 測試整合

```python
# 測試資料庫連接
python test_inspire_db_integration.py

# 測試應該：
# 1. 連接到 Supabase ✅
# 2. 查詢 tags_final ✅
# 3. 創建 Session ✅
# 4. 保存資料 ✅
```

**預估時間：** 30 分鐘

---

## 💡 優勢分析

### 為什麼這個整合方案好？

#### 1. 充分利用現有資料 ✅

```
你已有的 140K+ 標籤：
├─ 直接用於 search_examples
├─ 直接用於 validate_quality
└─ 不需要重新建立或遷移
```

#### 2. 最小化改動 ✅

```
現有資料庫：
├─ 只添加欄位（不修改現有資料）
├─ 新增 2 個表（inspire_sessions, tag_cooccur）
└─ 新增 2 個視圖（加速查詢）

不影響現有功能 ✅
```

#### 3. 清晰的職責分工 ✅

```
SDK Session (SQLite):
└─ 對話歷史（SDK 自動管理）

Supabase tags_final:
└─ 標籤資料（已有，直接用）

Supabase inspire_sessions:
└─ 業務分析（新建，可選）

Context 變數:
└─ 執行時共享（臨時）
```

---

## 🎯 下一步

### 選項 A: 我現在幫你創建所有整合檔案（推薦）

**我會創建：**
1. `inspire_db_service.py`（完整實現）
2. `inspire_session_manager.py`（完整實現）
3. `inspire_tools.py`（5 個工具骨架）
4. 測試腳本

**你只需要：**
- 執行 SQL migration
- 測試運行

**預估時間：** 我 30 分鐘，你 30 分鐘測試

---

### 選項 B: 先執行 SQL Migration，明天再做整合

**今晚：**
- 執行 `08_inspire_agent_tables.sql`
- 驗證資料庫

**明天：**
- 實作整合服務
- 測試

---

**你想選哪個？** 我可以立即幫你創建所有整合代碼！🚀
