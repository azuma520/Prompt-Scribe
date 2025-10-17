# 🔗 Inspire 功能整合說明

> **如何將 Inspire 功能整合到現有 Prompt-Scribe 系統**

**版本**: 1.0.0  
**更新日期**: 2025-10-17

---

## ⚠️ 重要說明

**Inspire 不是獨立系統，而是現有 Prompt-Scribe 的功能擴展！**

---

## 📊 現有系統概覽

### 已有的資源

#### 1. **資料庫**（Supabase）✅

```
現有資料表：
├── tags_final          (140,782 個標籤) ✅ 複用
├── tag_embeddings      (向量嵌入)      ✅ 複用  
└── migration_log       (遷移日誌)      ✅ 保留
```

**重要**：
- ✅ **tags_final** - Inspire 將直接查詢這個表獲取標籤
- ✅ **tag_embeddings** - Inspire 可用於語意搜尋相關標籤
- 🆕 **inspire_*** - 只新增 Inspire 專屬的 Session 和日誌表

#### 2. **API 端點**（Vercel）✅

```
現有 API (https://prompt-scribe-api.vercel.app):
├── /api/llm/recommend-tags        ✅ 複用：根據描述推薦標籤
├── /api/llm/validate-prompt       ✅ 複用：驗證 Prompt 品質
├── /api/llm/suggest-combinations  ✅ 複用：智能組合建議
├── /api/v1/tags                   ✅ 複用：標籤查詢
├── /api/v1/search                 ✅ 複用：關鍵字搜尋
└── /api/v1/categories             ✅ 複用：分類統計
```

**重要**：
- Inspire 主要複用 `/api/llm/recommend-tags` 來推薦標籤
- 新增 `/api/inspire/*` 端點處理 Inspire 特有邏輯
- 不需要重建標籤推薦系統

#### 3. **前端基礎**（規劃中）

```
已規劃的前端架構：
├── Next.js 14 + TypeScript    ✅ 共用框架
├── shadcn/ui + Tailwind       ✅ 共用 UI 系統
├── Zustand + React Query      ✅ 共用狀態管理
└── Vercel 部署                ✅ 共用部署平台
```

---

## 🔄 整合策略

### 方案 1: 功能模組化（推薦）⭐

```
Prompt-Scribe Web 專案結構：
├── app/
│   ├── page.tsx                    # 主首頁（導航到各功能）
│   ├── tags/                       # 標籤搜尋功能（原有）
│   │   ├── page.tsx
│   │   └── components/
│   ├── inspire/                    # 🆕 Inspire 功能（新增）
│   │   ├── page.tsx
│   │   └── components/
│   └── workspace/                  # 工作區功能（共用）
│       ├── page.tsx
│       └── components/
│
├── lib/
│   ├── api/
│   │   ├── tags.ts                 # 標籤相關 API（共用）
│   │   └── inspire.ts              # 🆕 Inspire 專屬 API
│   └── ...
│
└── components/
    ├── shared/                      # 共用組件
    │   ├── TagCard.tsx             # 標籤卡片（共用）
    │   ├── CopyButton.tsx          # 複製按鈕（共用）
    │   └── ...
    └── features/
        ├── tag-search/             # 標籤搜尋（原有）
        └── inspire/                # 🆕 Inspire（新增）
```

**優勢**：
- ✅ 模組清晰，職責分離
- ✅ 可獨立開發和測試
- ✅ 便於未來維護
- ✅ 符合 Next.js App Router 最佳實踐

---

## 🗄️ 資料庫整合

### 現有表 + 新增表

```sql
-- =====================================================
-- 現有資料表（複用，不修改）
-- =====================================================

-- ✅ 已存在：tags_final (140,782 筆)
--    用途：Inspire 從這裡查詢標籤資料
--    查詢範例：
--      SELECT name, main_category, post_count 
--      FROM tags_final 
--      WHERE main_category = 'SCENE' 
--      ORDER BY post_count DESC 
--      LIMIT 10;

-- ✅ 已存在：tag_embeddings
--    用途：Inspire 可用於語意搜尋相關標籤
--    查詢範例：
--      SELECT tag_name, 
--             1 - (embedding <=> query_embedding) AS similarity
--      FROM tag_embeddings
--      ORDER BY similarity DESC
--      LIMIT 10;

-- =====================================================
-- 新增資料表（Inspire 專屬）
-- =====================================================

-- 🆕 新增：inspire_sessions
--    用途：追蹤 Inspire 使用 Session

-- 🆕 新增：inspire_rounds
--    用途：記錄每輪對話

-- 🆕 新增：inspire_generation_logs
--    用途：追蹤生成事件

-- 🆕 新增：inspire_usage_logs
--    用途：使用者行為分析

-- 🆕 新增：inspire_feedback_logs
--    用途：反饋數據收集
```

### 整合查詢範例

```sql
-- Inspire 如何查詢現有標籤資料：

-- 1. 根據分類獲取標籤
SELECT name, post_count, main_category, sub_category
FROM tags_final
WHERE main_category IN ('SCENE', 'LIGHTING', 'STYLE')
  AND post_count > 100
ORDER BY post_count DESC
LIMIT 50;

-- 2. 語意搜尋相關標籤（如果需要）
SELECT t.name, t.main_category, t.post_count,
       1 - (e.embedding <=> $1::vector) AS similarity
FROM tags_final t
JOIN tag_embeddings e ON t.name = e.tag_name
WHERE main_category IN ('SCENE', 'STYLE')
ORDER BY similarity DESC
LIMIT 10;

-- 3. 結合 Inspire Session 的完整查詢
SELECT 
    s.session_id,
    s.mode,
    r.cards_generated,
    array_agg(DISTINCT t.main_category) as categories_used
FROM inspire_sessions s
JOIN inspire_rounds r ON s.session_id = r.session_id
CROSS JOIN LATERAL unnest(r.tags_used) AS tag_name
JOIN tags_final t ON t.name = tag_name
WHERE s.created_at >= NOW() - INTERVAL '7 days'
GROUP BY s.session_id, s.mode, r.cards_generated;
```

---

## 🔌 API 整合

### 現有 API + 新增端點

#### **複用現有 API**

```typescript
// lib/api/existing.ts

import { API_BASE_URL } from './client';

// ✅ 複用：推薦標籤（Inspire 的核心）
export async function recommendTags(description: string) {
  const response = await fetch(`${API_BASE_URL}/api/llm/recommend-tags`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ description }),
  });
  return response.json();
}

// ✅ 複用：搜尋標籤
export async function searchTags(query: string, category?: string) {
  const params = new URLSearchParams({ query });
  if (category) params.append('category', category);
  
  const response = await fetch(
    `${API_BASE_URL}/api/v1/search?${params}`
  );
  return response.json();
}

// ✅ 複用：驗證 Prompt
export async function validatePrompt(tags: string[]) {
  const response = await fetch(`${API_BASE_URL}/api/llm/validate-prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tags }),
  });
  return response.json();
}
```

#### **新增 Inspire 專屬端點**

```typescript
// lib/api/inspire.ts

import { recommendTags, searchTags } from './existing';

// 🆕 新增：生成靈感卡（封裝現有 API）
export async function generateInspirationCards(
  input: string,
  sessionId: string
): Promise<InspireGenerateResponse> {
  // 步驟 1: 使用現有的推薦 API 獲取標籤
  const tagsResponse = await recommendTags(input);
  
  // 步驟 2: 根據標籤查詢分類資訊
  const sceneTagsResponse = await searchTags('', 'SCENE');
  const styleTagsResponse = await searchTags('', 'STYLE');
  const lightingTagsResponse = await searchTags('', 'LIGHTING');
  
  // 步驟 3: 組合成靈感卡（調用 LLM 或後端邏輯）
  const response = await fetch(`${API_BASE_URL}/api/inspire/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input,
      session_id: sessionId,
      recommended_tags: tagsResponse.recommended_tags,
      scene_tags: sceneTagsResponse.tags,
      style_tags: styleTagsResponse.tags,
      lighting_tags: lightingTagsResponse.tags,
    }),
  });
  
  return response.json();
}

// 🆕 新增：提交反饋
export async function submitFeedback(
  sessionId: string,
  selectedCard: InspirationCard,
  feedback: string,
  action: FeedbackAction
) {
  const response = await fetch(`${API_BASE_URL}/api/inspire/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      selected_card: selectedCard,
      feedback,
      next_action: action,
    }),
  });
  
  return response.json();
}
```

---

## 🏗️ 後端實作整合

### 新增後端邏輯（FastAPI）

在現有的 `src/api/` 中新增：

```python
# src/api/routers/inspire/__init__.py

from fastapi import APIRouter, Depends
from typing import List
from ...models.inspire import (
    GenerateRequest, 
    GenerateResponse,
    InspirationCard
)
from ...services.supabase_client import get_supabase_client
from ...services.keyword_analyzer import KeywordAnalyzer  # 複用現有服務
from ...services.tag_combination_analyzer import TagCombinationAnalyzer  # 複用

router = APIRouter(prefix="/api/inspire", tags=["inspire"])

@router.post("/generate", response_model=GenerateResponse)
async def generate_inspiration(request: GenerateRequest):
    """
    生成靈感卡
    
    整合策略：
    1. 使用現有的 KeywordAnalyzer 分析輸入
    2. 從 tags_final 查詢相關標籤（按分類）
    3. 使用 LLM 組合成結構化的靈感卡
    4. 記錄到 inspire_rounds 表
    """
    supabase = get_supabase_client()
    analyzer = KeywordAnalyzer()
    
    # 步驟 1: 分析輸入（複用現有邏輯）
    keywords = analyzer.extract_keywords(request.input)
    
    # 步驟 2: 從現有資料庫查詢標籤（按分類）
    scene_tags = supabase.table('tags_final')\
        .select('name, post_count')\
        .eq('main_category', 'SCENE')\
        .order('post_count', desc=True)\
        .limit(20)\
        .execute()
    
    style_tags = supabase.table('tags_final')\
        .select('name, post_count')\
        .eq('main_category', 'STYLE')\
        .order('post_count', desc=True)\
        .limit(20)\
        .execute()
    
    lighting_tags = supabase.table('tags_final')\
        .select('name, post_count')\
        .eq('main_category', 'LIGHTING')\
        .order('post_count', desc=True)\
        .limit(10)\
        .execute()
    
    # 步驟 3: 組合成靈感卡（LLM 或規則引擎）
    cards = await build_inspiration_cards(
        input=request.input,
        keywords=keywords,
        scene_tags=scene_tags.data,
        style_tags=style_tags.data,
        lighting_tags=lighting_tags.data,
    )
    
    # 步驟 4: 記錄到 Inspire 表
    supabase.table('inspire_rounds').insert({
        'session_id': request.session_id,
        'round_number': request.round,
        'user_input': request.input,
        'cards_generated': cards,
        'cards_count': len(cards),
        'tags_used': extract_all_tags(cards),
    }).execute()
    
    return GenerateResponse(
        mode=determine_mode(request.input),
        round=request.round,
        cards=cards,
    )
```

---

## 🔀 資料流整合

### 完整資料流

```
使用者輸入
    ↓
前端 (Next.js)
    ↓
API: /api/inspire/generate
    ↓
┌─────────────────────────────────┐
│  後端處理（整合現有系統）        │
│                                  │
│  1. 分析輸入 ────────────────┐  │
│     (KeywordAnalyzer 複用)    │  │
│                                │  │
│  2. 查詢現有標籤 ─────────────┤  │
│     FROM tags_final (複用)    │  │
│     - SCENE 標籤             │  │
│     - STYLE 標籤             │  │
│     - LIGHTING 標籤          │  │
│                                │  │
│  3. LLM 組合靈感卡 ──────────┤  │
│     (新邏輯)                  │  │
│                                │  │
│  4. 記錄到 inspire_rounds ───┤  │
│     (新表)                    │  │
│                                │  │
└──────────────────────────────┬─┘
                                ↓
                          返回靈感卡
                                ↓
                           前端展示
```

---

## 📦 部署整合

### 統一部署架構

```
┌─────────────────────────────────────────┐
│           Vercel 前端部署                │
│                                          │
│  ┌────────────┐      ┌────────────┐    │
│  │   標籤搜尋  │      │  Inspire   │    │
│  │   /tags    │      │  /inspire  │    │
│  └────────────┘      └────────────┘    │
│         │                    │           │
│         └────────┬───────────┘          │
└──────────────────┼──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│       Vercel API 部署（共用）            │
│  https://prompt-scribe-api.vercel.app   │
│                                          │
│  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │ 標籤 API │  │ LLM API │  │Inspire │ │
│  │   複用   │  │   複用   │  │  新增  │ │
│  └─────────┘  └─────────┘  └────────┘ │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│          Supabase 資料庫（共用）         │
│                                          │
│  ┌──────────┐  ┌──────────┐  ┌───────┐│
│  │tags_final│  │embeddings│  │inspire││
│  │   複用   │  │   複用   │  │  新增 ││
│  └──────────┘  └──────────┘  └───────┘│
└─────────────────────────────────────────┘
```

**關鍵點**：
- ✅ 同一個 Supabase 專案
- ✅ 同一個 API 伺服器
- ✅ 同一個前端專案（不同路由）
- 🆕 只新增 Inspire 專屬的表和端點

---

## 🔧 實作步驟

### Phase 1: 資料庫擴展

```bash
# 在現有的 Supabase 專案中執行

# 步驟 1: 檢查現有表
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
# 預期看到：tags_final, tag_embeddings, migration_log

# 步驟 2: 執行 Inspire 擴展腳本
psql -f specs/002-web-frontend/contracts/inspire-db-schema.sql

# 步驟 3: 驗證新表
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' AND tablename LIKE 'inspire_%';
# 預期看到：inspire_sessions, inspire_rounds, ...
```

### Phase 2: API 擴展

```python
# src/api/main.py

from routers.inspire import generate, feedback  # 新增 Inspire 路由

# 註冊 Inspire 路由
app.include_router(
    generate.router,
    prefix="/api/inspire",
    tags=["inspire"]
)
```

### Phase 3: 前端整合

```tsx
// app/page.tsx (主首頁)

export default function HomePage() {
  return (
    <div className="container">
      <h1>🎨 Prompt-Scribe</h1>
      
      <div className="grid grid-cols-2 gap-6">
        {/* 原有功能 */}
        <Link href="/tags">
          <Card>
            <h2>🔍 標籤搜尋</h2>
            <p>搜尋和瀏覽 140,000+ 標籤</p>
          </Card>
        </Link>
        
        {/* 🆕 新增功能 */}
        <Link href="/inspire">
          <Card>
            <h2>✨ Inspire 靈感</h2>
            <p>AI 靈感卡生成，對話式引導</p>
          </Card>
        </Link>
      </div>
    </div>
  );
}
```

---

## 🧩 組件複用

### 可複用的現有組件

```typescript
// 以下組件可在標籤搜尋和 Inspire 之間共用：

// 1. TagCard（標籤卡片）
import { TagCard } from '@/components/shared/TagCard';
// ✅ 用於：顯示 source_tags
// ✅ 用於：展示相關標籤

// 2. CopyButton（複製按鈕）
import { CopyButton } from '@/components/shared/CopyButton';
// ✅ 用於：複製 JSON
// ✅ 用於：複製 Prompt

// 3. ToastProvider（Toast 通知）
import { ToastProvider } from '@/components/shared/ToastProvider';
// ✅ 用於：複製成功提示
// ✅ 用於：錯誤提示

// 4. LoadingSpinner（載入動畫）
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
// ✅ 用於：API 請求載入狀態
```

### Inspire 專屬組件

```typescript
// 以下是 Inspire 專屬的新組件：

// app/inspire/components/
├── InputBox.tsx              # 情緒/主題輸入框
├── InspirationCards.tsx      # 靈感卡容器
├── InspirationCard.tsx       # 單張靈感卡（不同於 TagCard）
├── FeedbackPanel.tsx         # 反饋對話面板
├── ResultPanel.tsx           # 結果展示
└── Loader.tsx                # Inspire 專屬載入動畫
```

---

## ⚙️ 環境變數整合

### 共用配置

```bash
# .env.local（前後端共用）

# ✅ 現有配置（保留）
NEXT_PUBLIC_API_URL=https://prompt-scribe-api.vercel.app
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 🆕 Inspire 專屬配置（新增，可選）
NEXT_PUBLIC_INSPIRE_MAX_ROUNDS=5
NEXT_PUBLIC_INSPIRE_CARDS_PER_ROUND=3
NEXT_PUBLIC_INSPIRE_ENABLE_ANALYTICS=true

# 後端 LLM 配置（如果需要）
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
```

---

## 📊 效能考量

### 複用現有快取

```typescript
// lib/api/client.ts（已有）

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // ✅ Inspire 也使用相同快取策略
      cacheTime: 10 * 60 * 1000,
      retry: 3,
    },
  },
});

// Inspire 查詢會自動受益於 React Query 的快取機制
// 例如：相同的標籤查詢會命中快取
```

### 最佳化查詢

```sql
-- 為 Inspire 常用查詢創建專用索引（可選）

-- 按分類 + 使用次數查詢（已有，無需新增）
-- CREATE INDEX idx_tags_category_count 
-- ON tags_final(main_category, post_count DESC);

-- 如果 Inspire 頻繁使用特定分類，可添加部分索引
CREATE INDEX IF NOT EXISTS idx_tags_inspire_scene 
ON tags_final(name, post_count DESC)
WHERE main_category = 'SCENE';

CREATE INDEX IF NOT EXISTS idx_tags_inspire_style 
ON tags_final(name, post_count DESC)
WHERE main_category = 'STYLE';

CREATE INDEX IF NOT EXISTS idx_tags_inspire_lighting 
ON tags_final(name, post_count DESC)
WHERE main_category = 'LIGHTING';
```

---

## ✅ 整合檢查清單

### 資料庫整合

- [ ] 確認現有資料庫包含 tags_final 和 tag_embeddings
- [ ] 驗證資料完整性（140,782 筆標籤）
- [ ] 執行 inspire-db-schema.sql（僅新增表）
- [ ] 驗證外鍵關聯無誤
- [ ] 測試跨表查詢效能

### API 整合

- [ ] 確認現有 API 正常運行
- [ ] 測試現有端點（recommend-tags, search, validate）
- [ ] 新增 Inspire 路由到 main.py
- [ ] 實作 Inspire 端點（複用現有服務）
- [ ] 測試 API 整合無誤

### 前端整合

- [ ] 在同一個 Next.js 專案中開發
- [ ] 複用共用組件（TagCard, CopyButton 等）
- [ ] 複用 API 客戶端配置
- [ ] 複用狀態管理設置
- [ ] 測試路由導航（/tags ↔ /inspire）

### 部署整合

- [ ] 確認前後端使用同一個 Supabase 專案
- [ ] 確認 API 使用同一個 Vercel 部署
- [ ] 環境變數統一管理
- [ ] CI/CD 管線整合

---

## 🎯 關鍵整合點

### 1. 標籤資料來源

**✅ 複用現有：**
```sql
-- Inspire 查詢標籤時，直接從現有表查詢
SELECT * FROM tags_final WHERE main_category = 'SCENE';
```

**❌ 不要：**
```sql
-- ❌ 不要創建新的標籤表
CREATE TABLE inspire_tags (...);  -- 錯誤！
```

### 2. API 端點設計

**✅ 複用 + 擴展：**
```
/api/llm/recommend-tags          ← 現有，Inspire 內部調用
/api/inspire/generate            ← 新增，封裝現有 API
```

**❌ 不要：**
```
/api/inspire/recommend-tags      ← 不要重複實作
```

### 3. 前端路由

**✅ 模組化：**
```
/                  ← 主首頁（導航）
/tags              ← 標籤搜尋（原有）
/inspire           ← Inspire 功能（新增）
/workspace         ← 工作區（共用）
```

### 4. 共用組件

**✅ 複用組件庫：**
- shadcn/ui 組件（共用）
- CopyButton（共用）
- TagCard（可能需要變體，但共用基礎）
- ToastProvider（共用）

**🆕 Inspire 專屬：**
- InputBox（情緒/主題輸入，與標籤搜尋不同）
- InspirationCard（靈感卡，結構不同於 TagCard）
- FeedbackPanel（對話引導）

---

## 📋 修正後的開發計畫

### 時間估算調整

| 任務 | 原估時間 | 整合後 | 說明 |
|------|---------|--------|------|
| 資料庫設置 | 4h | **1h** ⬇️ | 只需執行擴展腳本 |
| API 開發 | 8h | **6h** ⬇️ | 複用現有服務 |
| 標籤查詢 | 4h | **1h** ⬇️ | 直接用現有 API |
| 組件開發 | 12h | **12h** ➡️ | 需要新組件 |
| 測試整合 | 8h | **6h** ⬇️ | 部分可複用 |
| **總計** | **54h** | **38h** | **節省 30%** ⚡ |

---

## 🚀 快速開始（整合版）

### 步驟 1: 確認現有系統

```bash
# 1. 確認 API 運行
curl https://prompt-scribe-api.vercel.app/health

# 2. 確認資料庫
# 登入 Supabase Dashboard 檢查 tags_final 表

# 3. 確認標籤數量
SELECT COUNT(*) FROM tags_final;
-- 預期：140,782
```

### 步驟 2: 擴展資料庫

```bash
# 在 Supabase SQL Editor 中執行
cat specs/002-web-frontend/contracts/inspire-db-schema.sql
# 複製內容到 Supabase Dashboard > SQL Editor > 執行
```

### 步驟 3: 開發 Inspire API

```bash
# 在現有的 src/api/ 中新增
cd src/api
mkdir -p routers/inspire
mkdir -p models/inspire

# 創建 Inspire 路由（複用現有服務）
# 參考上面的 Python 範例
```

### 步驟 4: 開發前端

```bash
# 在前端專案中新增 Inspire 模塊
cd prompt-scribe-web/app
mkdir inspire

# 開發組件（複用共用組件）
```

---

## 💡 重要提醒

### ✅ DO（應該做）

1. **複用現有標籤資料** - 從 tags_final 查詢
2. **複用現有 API** - 調用 /api/llm/recommend-tags
3. **複用共用組件** - CopyButton, TagCard 等
4. **統一部署** - 同一個 Vercel 專案
5. **統一監控** - 使用相同的分析工具

### ❌ DON'T（不應該做）

1. **不要重建標籤表** - 已有 140,782 個標籤
2. **不要重複實作推薦邏輯** - 已有完整 API
3. **不要創建獨立專案** - 應該是同一個專案的不同路由
4. **不要重複部署** - 使用現有的部署配置

---

## 📚 相關文檔

### 現有系統文檔

- [API 文檔](https://prompt-scribe-api.vercel.app/docs)
- [資料庫 Schema](../../specs/001-sqlite-ags-db/contracts/database_schema.sql)
- [資料模型](../../specs/001-sqlite-ags-db/data-model.md)
- [部署指南](../../DEPLOYMENT_GUIDE.md)

### Inspire 文檔

- [Inspire 開發計畫](./plan-inspire-feature.md)
- [Inspire API 規格](../contracts/inspire-api-spec.yaml)
- [Inspire 資料庫擴展](../contracts/inspire-db-schema.sql)
- [組件規格](../docs/INSPIRE_COMPONENTS.md)

---

## 🎯 總結

### 整合原則

1. **最大化複用** - 利用現有的 140,782 個標籤
2. **最小化新增** - 只新增必要的 Inspire 專屬邏輯
3. **保持一致** - 統一的技術棧和部署策略
4. **模組清晰** - 功能分離但資料共享

### 預期成果

- ✅ Inspire 功能完整
- ✅ 無需重複資料
- ✅ 開發時間縮短 30%
- ✅ 維護成本降低
- ✅ 使用者體驗統一

---

**整合文檔完成 - 確保 Inspire 與現有系統完美配合！** 🔗

**版本**: 1.0.0  
**最後更新**: 2025-10-17  
**維護者**: Prompt-Scribe Team

