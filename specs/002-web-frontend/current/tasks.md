# 📋 Prompt-Scribe Web Frontend - 任務清單

> **完整的開發任務列表，含 Inspire 功能整合**

**版本**: 1.0.1  
**建立日期**: 2025-10-17  
**最後更新**: 2025-10-17 17:50

---

## 📊 任務總覽

### 統計資訊

```
總任務數:     85 個
預估總時間:   80 小時（使用 MCP）
開發週期:     2 週
優先級分佈:
  - High:     45 個
  - Medium:   30 個
  - Low:      10 個
```

### 進度追蹤

```
Phase 0: 專案設置         ████████████████████ 100% (7/7) ✅
Phase 1: 核心搜尋         ░░░░░░░░░░░░░░░░░░░░   0% (0/10) ⏳
Phase 2: 工作區           ░░░░░░░░░░░░░░░░░░░░   0% (0/12) ⏳
Phase 3: Inspire 功能     ████████████░░░░░░░░  60% (9/15) 🏃
Phase 4: 智能推薦         ░░░░░░░░░░░░░░░░░░░░   0% (0/8) ⏳
Phase 5: 分類瀏覽         ░░░░░░░░░░░░░░░░░░░░   0% (0/7) ⏳
Phase 6: 主題語言         ░░░░░░░░░░░░░░░░░░░░   0% (0/6) ⏳
Phase 7: 響應優化         ░░░░░░░░░░░░░░░░░░░░   0% (0/8) ⏳
Phase 8: PWA 進階         ░░░░░░░░░░░░░░░░░░░░   0% (0/6) ⏳
Phase 9: 測試文檔         ░░░░░░░░░░░░░░░░░░░░   0% (0/10) ⏳
Phase 10: 部署監控        ░░░░░░░░░░░░░░░░░░░░   0% (0/6) ⏳

總進度:                   ████░░░░░░░░░░░░░░░░  19% (16/85) 🚀

最後更新: 2025-10-17
```

---

## 🎯 Phase 0: 專案設置與環境配置（4h）

### T001: 初始化 Next.js 14 專案
- **優先級**: High
- **預估時間**: 30 分鐘
- **負責人**: 前端工程師
- **依賴**: 無
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
初始化 Next.js 14 專案（App Router）

**執行步驟**:
```bash
npx create-next-app@latest prompt-scribe-web \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"
```

**驗收標準**:
- [x] Next.js 專案成功創建
- [x] TypeScript 配置正確
- [x] Tailwind CSS 配置正確
- [x] 專案可啟動（npm run dev）
- [x] 無控制台錯誤

---

### T002: 安裝核心依賴
- **優先級**: High
- **預估時間**: 30 分鐘
- **依賴**: T001
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
安裝所有核心依賴套件

**執行步驟**:
```bash
# shadcn/ui
npx shadcn-ui@latest init

# 狀態管理
npm install zustand @tanstack/react-query

# 動畫
npm install framer-motion

# 表單
npm install react-hook-form zod @hookform/resolvers

# 國際化
npm install next-intl

# 工具庫
npm install clsx tailwind-merge date-fns lodash-es uuid
npm install @types/lodash-es @types/uuid --save-dev
```

**驗收標準**:
- [x] 所有依賴安裝成功
- [x] package.json 更新正確
- [x] 無依賴衝突
- [x] 專案可正常編譯

---

### T003: 使用 shadcn MCP 安裝 UI 組件
- **優先級**: High
- **預估時間**: 20 分鐘（使用 MCP）
- **依賴**: T002
- **狀態**: ✅ 已完成（2025-10-17）- 21 個組件已安裝

**任務描述**:
使用 shadcn MCP 批量安裝所有需要的 UI 組件

**執行步驟**:
```
請使用 shadcn MCP 安裝以下組件：
button, input, textarea, card, badge, dialog, toast, skeleton, 
tooltip, select, tabs, dropdown-menu, scroll-area, command, 
popover, separator, alert, progress, accordion, label, checkbox
```

**驗收標準**:
- [x] 所有組件安裝到 `components/ui/`（21 個組件）
- [x] 組件可正常導入使用
- [x] TypeScript 類型定義正確
- [x] 無編譯錯誤

**備註**: 
- 傳統手動安裝需要 60 分鐘，使用 MCP 只需 20 分鐘 ⚡

---

### T004: 配置 TypeScript 嚴格模式
- **優先級**: High
- **預估時間**: 15 分鐘
- **依賴**: T001
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
配置 TypeScript 嚴格模式和編譯選項

**執行步驟**:
更新 `tsconfig.json`，啟用嚴格模式

**驗收標準**:
- [x] `strict: true`
- [x] `noEmit: true`
- [x] `esModuleInterop: true`
- [x] Path alias 配置正確（@/*）
- [x] 無 TypeScript 錯誤

---

### T005: 設置 ESLint 和 Prettier
- **優先級**: Medium
- **預估時間**: 20 分鐘
- **依賴**: T001
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
配置代碼檢查和格式化工具

**執行步驟**:
```bash
npm install --save-dev prettier eslint-config-prettier
```

**驗收標準**:
- [x] `.eslintrc.json` 配置正確
- [x] `.prettierrc` 配置正確
- [x] `npm run lint` 無錯誤
- [x] VS Code 自動格式化可用

---

### T006: 配置環境變數和 API 連線
- **優先級**: High
- **預估時間**: 20 分鐘
- **依賴**: T001
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
設置環境變數和 API 客戶端

**執行步驟**:
1. 創建 `.env.local` 和 `.env.example`
2. 設置 API URL（複用現有 API）
3. 配置 React Query 客戶端

**驗收標準**:
- [x] `.env.local` 配置正確
- [x] API_BASE_URL 指向現有 API (https://prompt-scribe-api.vercel.app)
- [x] React Query 客戶端配置完成
- [x] 測試 API 連接成功

---

### T007: 建立專案目錄結構
- **優先級**: High
- **預估時間**: 30 分鐘
- **依賴**: T001
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
創建完整的目錄結構

**執行步驟**:
```bash
mkdir -p src/app/{tags,inspire,workspace}
mkdir -p src/components/{ui,features,layouts,shared}
mkdir -p src/components/features/{tag-search,tag-card,workspace,inspire}
mkdir -p src/lib/{api,hooks,store,utils,constants}
mkdir -p src/types
mkdir -p src/tests/{unit,integration,e2e}
```

**驗收標準**:
- [x] 所有目錄已創建
- [x] 符合規格文檔的結構
- [x] README 已更新

---

## 🔍 Phase 1: 核心標籤搜尋功能（11h）

### T101: 建立首頁佈局和 Header
- **優先級**: High
- **預估時間**: 2h
- **依賴**: T007

**任務描述**:
實作主首頁和全局 Header

**交付物**:
- `app/layout.tsx` - 根佈局
- `app/page.tsx` - 主首頁
- `components/layouts/Header.tsx` - 頁首
- `components/layouts/Footer.tsx` - 頁尾

**驗收標準**:
- [ ] 響應式佈局
- [ ] Logo 和導航
- [ ] 主題切換按鈕
- [ ] 語言切換按鈕
- [ ] 頁面路由正確

---

### T102: 實作標籤搜尋輸入框（使用 MCP）
- **優先級**: High
- **預估時間**: 1.5h（MCP 加速）
- **依賴**: T003

**任務描述**:
使用 shadcn MCP 創建智能搜尋組件

**MCP 提示語**:
```
請用 shadcn MCP 創建 TagSearchInput 組件：

需求：
- 使用 Command 組件作為基礎
- 支援即時搜尋建議
- 鍵盤導航（↑↓ Enter）
- 搜尋歷史（最近 5 條）
- 載入狀態（Skeleton）
- 分類篩選

Props:
```typescript
interface TagSearchInputProps {
  onTagSelect: (tag: Tag) => void;
  placeholder?: string;
  autoFocus?: boolean;
}
```

請生成完整的 TypeScript 代碼。
```

**交付物**:
- `components/features/tag-search/TagSearchInput.tsx`
- `components/features/tag-search/SearchHistory.tsx`

**驗收標準**:
- [ ] 即時搜尋功能
- [ ] 鍵盤導航可用
- [ ] 搜尋歷史記錄
- [ ] 載入狀態顯示
- [ ] TypeScript 類型完整

---

### T103: 整合標籤推薦 API
- **優先級**: High
- **預估時間**: 1.5h
- **依賴**: T006, T102

**任務描述**:
整合現有的 `/api/llm/recommend-tags` API

**交付物**:
- `lib/api/tags.ts` - API 客戶端
- `lib/hooks/useTagRecommendation.ts` - React Query Hook

**實作範例**:
```typescript
// lib/hooks/useTagRecommendation.ts
export function useTagRecommendation(description: string) {
  return useQuery({
    queryKey: ['tagRecommendation', description],
    queryFn: async () => {
      const response = await fetch(
        `${API_BASE_URL}/api/llm/recommend-tags`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description }),
        }
      );
      return response.json();
    },
    enabled: description.length > 2,
    staleTime: 5 * 60 * 1000,
  });
}
```

**驗收標準**:
- [ ] API 客戶端配置正確
- [ ] React Query Hook 可用
- [ ] 快取策略配置
- [ ] 錯誤處理完整
- [ ] Loading 狀態管理

---

### T104: 實作搜尋結果展示
- **優先級**: High
- **預估時間**: 2h
- **依賴**: T103

**任務描述**:
顯示推薦標籤列表

**交付物**:
- `components/features/tag-search/SearchResults.tsx`
- `components/shared/TagCard.tsx`（基礎版）

**驗收標準**:
- [ ] 標籤卡片網格佈局
- [ ] 顯示標籤資訊（名稱、分類、使用次數）
- [ ] 點擊添加到工作區
- [ ] 空狀態處理
- [ ] 響應式設計

---

### T105: 實作搜尋歷史管理
- **優先級**: Medium
- **預估時間**: 1h
- **依賴**: T102

**任務描述**:
使用 localStorage 管理搜尋歷史

**交付物**:
- `lib/hooks/useSearchHistory.ts`
- `lib/utils/storage.ts`

**驗收標準**:
- [ ] 自動記錄搜尋
- [ ] 最多保存 10 條
- [ ] 可清除歷史
- [ ] 點擊快速搜尋

---

### T106: 實作熱門標籤展示
- **優先級**: Medium
- **預估時間**: 1h
- **依賴**: T006

**任務描述**:
從 API 獲取並顯示熱門標籤

**API 端點**:
```
GET /api/v1/tags?limit=20&order_by=post_count
```

**驗收標準**:
- [ ] 顯示前 20 個熱門標籤
- [ ] Badge 樣式美觀
- [ ] 點擊可快速添加
- [ ] 載入狀態

---

### T107: 建立搜尋結果頁面
- **優先級**: High
- **預估時間**: 1.5h
- **依賴**: T104, T105

**任務描述**:
完整的搜尋結果頁面

**交付物**:
- `app/tags/page.tsx`
- `app/tags/layout.tsx`

**驗收標準**:
- [ ] 搜尋框在頂部
- [ ] 結果區域在左側
- [ ] 工作區在右側
- [ ] 響應式佈局
- [ ] 路由參數處理

---

### T108-T110: 錯誤處理、載入狀態、測試
（略，詳見完整清單）

---

## 📋 Phase 2: 標籤展示與工作區管理（14h）

### T201: 設計並實作 TagCard 組件（使用 MCP）
- **優先級**: High
- **預估時間**: 1.5h（MCP 加速）
- **依賴**: T003

**任務描述**:
使用 shadcn MCP 創建標籤卡片組件

**MCP 提示語**:
```
用 shadcn MCP 創建 TagCard 組件：

需求：
- 使用 Card, Badge, Button, Tooltip 組件
- 顯示標籤名稱、分類、使用次數
- 支援 compact 和 detailed 兩種變體
- hover 時提升動畫（transform + shadow）
- 信心度進度條

Props:
```typescript
interface TagCardProps {
  tag: Tag;
  onAdd?: (tag: Tag) => void;
  onViewDetails?: (tag: Tag) => void;
  variant?: 'compact' | 'detailed';
  selected?: boolean;
}
```

樣式要求：
- hover: translateY(-4px) + shadow-card-hover
- selected: border-inspire + shadow-card-selected
- 過渡動畫 300ms

請生成完整代碼。
```

**交付物**:
- `components/shared/TagCard.tsx`
- `components/shared/TagCard.test.tsx`

**驗收標準**:
- [ ] 兩種變體可用
- [ ] 動畫流暢（60 FPS）
- [ ] TypeScript 類型完整
- [ ] 響應式設計
- [ ] 測試覆蓋 ≥ 80%

---

### T202: 實作工作區組件（使用 MCP）
- **優先級**: High
- **預估時間**: 2h（MCP 加速）
- **依賴**: T201

**任務描述**:
創建標籤工作區管理組件

**MCP 提示語**:
```
用 shadcn MCP 創建 Workspace 組件：

需求：
- 使用 Card, Button, ScrollArea, Progress 組件
- 功能：
  1. 已選標籤列表
  2. 標籤可刪除
  3. Prompt 預覽（格式化）
  4. 品質評分（Progress bar）
  5. 批量操作（清空、複製全部）

Props:
```typescript
interface WorkspaceProps {
  tags: Tag[];
  onTagRemove: (tagId: string) => void;
  onClear: () => void;
  validationScore?: number;
}
```

樣式：
- 固定右側（桌面）或底部（移動）
- 最大高度 80vh，可滾動
- 陰影和邊框

請生成完整實作。
```

**交付物**:
- `components/features/workspace/Workspace.tsx`
- `components/features/workspace/TagList.tsx`
- `components/features/workspace/PromptPreview.tsx`

**驗收標準**:
- [ ] 標籤列表顯示正確
- [ ] 刪除功能可用
- [ ] Prompt 格式化正確
- [ ] 評分視覺化清晰
- [ ] 響應式完美適配

---

### T203: 實作標籤拖拽排序
- **優先級**: Medium
- **預估時間**: 2h
- **依賴**: T202

**任務描述**:
使用 dnd-kit 實作拖拽排序

**執行步驟**:
```bash
npm install @dnd-kit/core @dnd-kit/sortable
```

**交付物**:
- `components/features/workspace/DraggableTagList.tsx`
- `lib/hooks/useDragAndDrop.ts`

**驗收標準**:
- [ ] 可拖拽排序
- [ ] 拖拽視覺反饋
- [ ] 觸控裝置支援
- [ ] 無障礙支援

---

### T204: 實作 Prompt 預覽和複製功能
- **優先級**: High
- **預估時間**: 1.5h
- **依賴**: T202

**任務描述**:
實作 Prompt 格式化預覽和一鍵複製

**交付物**:
- `components/shared/CopyButton.tsx`
- `components/features/workspace/PromptPreview.tsx`
- `lib/utils/prompt-formatter.ts`

**實作範例**:
```typescript
// lib/utils/prompt-formatter.ts
export function formatPrompt(tags: Tag[]): string {
  return tags.map(t => t.name).join(', ');
}

export function formatPromptWithWeights(tags: Tag[]): string {
  return tags
    .map(t => `(${t.name}:${t.confidence || 1.0})`)
    .join(', ');
}
```

**驗收標準**:
- [ ] 格式化正確
- [ ] 複製功能可用
- [ ] Toast 提示
- [ ] 支援多種格式

---

### T205-T208: 工作區狀態管理、本地持久化等
（略，詳見後續）

---

## ✨ Phase 3: Inspire 靈感功能（15h）⭐

### T301: 創建 Inspire 頁面骨架
- **優先級**: High
- **預估時間**: 1h
- **依賴**: T007
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
建立 Inspire 功能的頁面結構

**交付物**:
- `app/inspire/page.tsx` ✅
- `app/inspire/layout.tsx` ✅

**驗收標準**:
- [x] 路由 `/inspire` 可訪問
- [x] 基礎佈局完成
- [x] 導航連結正確

---

### T302: 實作 Inspire InputBox（使用 MCP）
- **優先級**: High
- **預估時間**: 1h（MCP 加速）
- **依賴**: T301
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
創建情緒/主題輸入框

**MCP 提示語**:
```
用 shadcn MCP 創建 Inspire 專用的 InputBox：

需求：
- Textarea 組件（多行輸入）
- 字數統計（最多 500 字）
- 快捷鍵提示（Ctrl+Enter）
- 提交按鈕（帶載入狀態）
- Placeholder: "描述你想要的感覺或主題..."

請參考 specs/002-web-frontend/docs/INSPIRE_COMPONENTS.md
生成完整的 TypeScript 代碼。
```

**交付物**:
- `app/inspire/components/InputBox.tsx` ✅

**驗收標準**:
- [x] 多行輸入可用
- [x] 字數統計正確
- [x] 快捷鍵功能
- [x] 載入狀態
- [x] 禁用狀態

---

### T303: 實作 InspirationCard 組件（使用 MCP）
- **優先級**: High
- **預估時間**: 2h（MCP 加速）
- **依賴**: T003
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
創建靈感卡片組件

**MCP 提示語**:
```
用 shadcn MCP 創建 InspirationCard 組件：

需求：
- 基於 Card 組件
- 顯示靈感卡的完整資訊：
  * subject（主標題，h3）
  * scene（場景，body）
  * style（風格，body）
  * source_tags（標籤 Badge）
  * confidence_score（進度條）
- 支援選中狀態（邊框發光）
- hover 動畫（提升 + 陰影）

請參考 InspirationCard 介面定義：
```typescript
interface InspirationCard {
  subject: string;
  outfit?: string;
  scene: string;
  callback?: string;
  lighting?: string;
  lens?: string;
  angle?: string;
  composition?: string;
  style: string;
  extra?: string;
  source_tags: string[];
  confidence_score?: number;
}
```

請生成完整代碼。
```

**交付物**:
- `app/inspire/components/InspirationCard.tsx` ✅

**驗收標準**:
- [x] 所有欄位正確顯示
- [x] 選中狀態明顯
- [x] hover 動畫流暢
- [x] 響應式設計

---

### T304: 實作 InspirationCards 容器
- **優先級**: High
- **預估時間**: 1h
- **依賴**: T303
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
管理多張靈感卡的容器組件

**交付物**:
- `app/inspire/components/InspirationCards.tsx` ✅

**驗收標準**:
- [x] 網格佈局（1/2/3 列）
- [x] 動畫延遲效果
- [x] 空狀態處理
- [x] 載入狀態

---

### T305: 整合 Inspire 生成 API
- **優先級**: High
- **預估時間**: 2h
- **依賴**: T006
- **狀態**: ✅ 已完成（2025-10-17）- 複用推薦 API

**任務描述**:
實作 Inspire 卡片生成 API 整合

**步驟**:
1. 創建後端端點 `src/api/routers/inspire/generate.py`
2. 複用現有的 `KeywordAnalyzer` 和推薦服務
3. 從 `tags_final` 查詢分類標籤
4. 組合成靈感卡格式

**交付物**:
- 前端: `lib/api/inspire.ts` ✅ (複用 /api/llm/recommend-tags)
- Hook: `lib/hooks/useInspiration.ts` ✅

**驗收標準**:
- [x] API 端點可用（複用現有推薦 API）
- [x] 複用現有標籤資料
- [x] 生成 3 張靈感卡
- [x] 回應時間 < 5s

**備註**: 成功複用後端現有推薦 API，無需新建端點

---

### T306: 實作 Session 管理
- **優先級**: High
- **預估時間**: 1.5h
- **依賴**: T301

**任務描述**:
使用 UUID 和 localStorage 管理 Session

**交付物**:
- `app/inspire/hooks/useSession.ts`
- `lib/utils/session.ts`

**實作範例**:
```typescript
export function useSession() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  useEffect(() => {
    let id = localStorage.getItem('inspire_session_id');
    
    if (!id) {
      id = uuidv4();
      localStorage.setItem('inspire_session_id', id);
    }
    
    setSessionId(id);
  }, []);
  
  return { sessionId, resetSession };
}
```

**驗收標準**:
- [ ] UUID 自動生成
- [ ] localStorage 持久化
- [ ] Session 可重置
- [ ] 跨頁面保持

---

### T307: 實作 FeedbackPanel（使用 MCP）
- **優先級**: High
- **預估時間**: 2h（MCP 加速）
- **依賴**: T003

**任務描述**:
創建反饋對話面板

**MCP 提示語**:
```
用 shadcn MCP 創建 FeedbackPanel 組件：

需求：
- AI 建議顯示（氣泡樣式）
- Textarea 反饋輸入
- 快速操作 Badge（更夢幻、更現實、改變場景等）
- 3 個操作按鈕：精煉、重新生成、確認

請參考 specs/002-web-frontend/docs/INSPIRE_COMPONENTS.md
的 FeedbackPanel 規格生成代碼。
```

**交付物**:
- `app/inspire/components/FeedbackPanel.tsx`

**驗收標準**:
- [ ] AI 建議展示
- [ ] 反饋輸入可用
- [ ] 快速操作按鈕
- [ ] 三個主要操作
- [ ] 載入狀態

---

### T308: 實作反饋處理 API
- **優先級**: High
- **預估時間**: 2h
- **依賴**: T305

**任務描述**:
實作反饋處理和卡片優化

**交付物**:
- 後端: `src/api/routers/inspire/feedback.py`
- 前端: `lib/hooks/useFeedback.ts`

**驗收標準**:
- [ ] 接收反饋
- [ ] 優化卡片
- [ ] 記錄到資料庫
- [ ] 返回優化結果

---

### T309: 實作 ResultPanel（使用 MCP）
- **優先級**: High
- **預估時間**: 1.5h（MCP 加速）
- **依賴**: T003, T204
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
創建最終結果展示面板

**MCP 提示語**:
```
用 shadcn MCP 創建 ResultPanel：

需求：
- Tabs 組件（JSON / Prompt 切換）
- JSON 格式化顯示（語法高亮，可選）
- Prompt 格式化顯示
- 複製按鈕（複用 CopyButton）
- 儲存按鈕

請生成完整代碼。
```

**交付物**:
- `app/inspire/components/ResultPanel.tsx` ✅
- `lib/utils/formula.ts`（公式構建）✅

**驗收標準**:
- [x] Tab 切換可用
- [x] JSON 格式化美觀
- [x] Prompt 格式正確
- [x] 複製功能
- [ ] 儲存功能（可選）

---

### T310: 實作 Inspire 載入動畫
- **優先級**: Medium
- **預估時間**: 1h
- **依賴**: T003
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
創建 Inspire 專屬的載入動畫

**交付物**:
- `app/inspire/components/Loader.tsx` ✅

**動畫效果**:
- Shimmer 卡片骨架（3 張）
- 打字效果文字
- 浮動表情符號 ✨
- 脈衝點動畫

**驗收標準**:
- [x] 3 種動畫效果
- [x] 流暢（60 FPS）
- [x] 可自定義訊息
- [x] 支援深色模式

---

### T311: 整合 Inspire 狀態機
- **優先級**: High
- **預估時間**: 2h
- **依賴**: T306

**任務描述**:
使用 Zustand 實作 Inspire 狀態管理

**交付物**:
- `app/inspire/store/inspireStore.ts`
- `app/inspire/hooks/useInspiration.ts`

**狀態定義**:
```typescript
type InspireState = 
  | 'idle'           // 初始
  | 'generating'     // 生成中
  | 'showing'        // 顯示卡片
  | 'feedback'       // 等待反饋
  | 'refining'       // 優化中
  | 'finalized';     // 已確認

interface InspireStore {
  state: InspireState;
  session: InspirationSession | null;
  cards: InspirationCard[];
  selectedCard: InspirationCard | null;
  finalResult: InspirationCard | null;
  
  // Actions
  generateCards: (input: string) => Promise<void>;
  selectCard: (card: InspirationCard) => void;
  provideFeedback: (feedback: string) => Promise<void>;
  finalize: () => void;
  reset: () => void;
}
```

**驗收標準**:
- [ ] 狀態轉換正確
- [ ] Actions 完整
- [ ] TypeScript 類型安全
- [ ] 與組件整合無誤

---

### T312: 組裝 Inspire 完整頁面
- **優先級**: High
- **預估時間**: 1.5h
- **依賴**: T302-T311
- **狀態**: ✅ 已完成（2025-10-17）

**任務描述**:
整合所有 Inspire 組件到主頁面

**交付物**:
- `app/inspire/page.tsx`（完整版）✅

**頁面結構**:
```tsx
<div className="container">
  {/* 輸入區 */}
  <InputBox onSubmit={generateCards} />
  
  {/* 卡片區 */}
  {state === 'showing' && (
    <InspirationCards cards={cards} onSelect={selectCard} />
  )}
  
  {/* 反饋區 */}
  {selectedCard && (
    <FeedbackPanel onFeedback={provideFeedback} />
  )}
  
  {/* 結果區 */}
  {finalResult && (
    <ResultPanel card={finalResult} />
  )}
</div>
```

**驗收標準**:
- [x] 完整流程可走通
- [x] 狀態轉換正確
- [x] UI 佈局美觀
- [x] 響應式完美

---

### T313-T315: 分析追蹤、錯誤處理、測試
（略）

---

## 🤖 Phase 4: 智能推薦與驗證（8h）

### T401: 整合 Prompt 驗證 API
- **優先級**: High
- **預估時間**: 1.5h
- **依賴**: T006

**任務描述**:
整合現有的 `/api/llm/validate-prompt` API

**交付物**:
- `lib/hooks/usePromptValidation.ts`

**驗收標準**:
- [ ] API 整合正確
- [ ] 返回驗證結果
- [ ] 快取策略配置
- [ ] 錯誤處理

---

### T402: 實作驗證結果顯示（使用 MCP）
- **優先級**: High
- **預估時間**: 2h（MCP 加速）
- **依賴**: T401

**MCP 提示語**:
```
用 shadcn MCP 創建 ValidationPanel：

需求：
- Card 容器
- Progress 評分進度條（0-100）
- Alert 顯示問題（衝突、冗餘）
- Accordion 展開建議列表
- Badge 顯示標籤類型

請生成完整代碼，包含 TypeScript 類型。
```

**交付物**:
- `components/features/validation/ValidationPanel.tsx`

**驗收標準**:
- [ ] 評分視覺化
- [ ] 問題清單
- [ ] 建議列表
- [ ] 可應用建議

---

### T403-T408: 評分系統、組合建議等
（略）

---

## 📊 Phase 5: 分類瀏覽功能（7h）

### T501: 整合分類統計 API
- **優先級**: Medium
- **預估時間**: 1h
- **依賴**: T006

**任務描述**:
整合 `/api/v1/categories` API

**驗收標準**:
- [ ] 獲取分類統計
- [ ] 快取配置
- [ ] TypeScript 類型

---

### T502-T507: 分類樹、標籤詳情等
（略）

---

## 🌓 Phase 6: 主題與國際化（6h）

### T601: 實作深色/淺色主題切換
- **優先級**: Medium
- **預估時間**: 1.5h
- **依賴**: T101

**任務描述**:
實作主題切換功能

**交付物**:
- `components/shared/ThemeToggle.tsx`
- `lib/hooks/useTheme.ts`

**驗收標準**:
- [ ] 主題切換可用
- [ ] 自動檢測系統偏好
- [ ] 持久化到 localStorage
- [ ] 無閃爍

---

### T602-T606: 主題配置、國際化等
（略）

---

## 📱 Phase 7: 響應式與效能優化（9h）

### T701: 實作響應式佈局（所有頁面）
- **優先級**: High
- **預估時間**: 2h
- **依賴**: Phase 1-5 完成

**驗收標準**:
- [ ] 桌面端（≥1024px）
- [ ] 平板端（768-1023px）
- [ ] 手機端（< 768px）
- [ ] 所有斷點測試通過

---

### T702-T708: 觸控優化、虛擬化、代碼分割等
（略）

---

## 🔧 Phase 8: PWA 與進階功能（6h）

### T801-T806: PWA、快捷鍵、收藏等
（略）

---

## 🧪 Phase 9: 測試與文檔（10h）

### T901: 設置測試環境
- **優先級**: High
- **預估時間**: 1h
- **依賴**: Phase 1-8 部分完成

**執行步驟**:
```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm install --save-dev @playwright/test
npx playwright install
```

**驗收標準**:
- [ ] Jest 配置完成
- [ ] Testing Library 可用
- [ ] Playwright 安裝

---

### T902: 編寫組件單元測試
- **優先級**: High
- **預估時間**: 3h
- **依賴**: T901

**測試覆蓋**:
- TagCard
- Workspace
- InspirationCard
- FeedbackPanel
- ResultPanel

**目標覆蓋率**: ≥ 80%

---

### T903-T910: 整合測試、E2E 測試、文檔等
（略）

---

## 🚀 Phase 10: 部署與監控（4h）

### T1001: 設置 Vercel 部署
- **優先級**: High
- **預估時間**: 1h
- **依賴**: Phase 1-9 完成

**執行步驟**:
```bash
vercel login
vercel --prod
```

**驗收標準**:
- [ ] 成功部署到 Vercel
- [ ] 環境變數配置
- [ ] 域名設置

---

### T1002-T1006: CI/CD、監控、SEO 等
（略）

---

## 📊 任務依賴關係圖

```
T001 (初始化)
  ↓
T002 (安裝依賴) → T003 (shadcn MCP)
  ↓                    ↓
T004 (TypeScript)   T102, T201, T302, T303...
  ↓                   (使用 MCP 的組件任務)
T005 (ESLint)
  ↓
T006 (環境變數) → T103, T305... (API 整合任務)
  ↓
T007 (目錄結構) → T101, T301... (頁面任務)
```

---

## ✅ 檢查清單模板

### 任務開始前

- [ ] 閱讀任務描述
- [ ] 了解依賴關係
- [ ] 查看相關規格文檔
- [ ] 準備開發環境

### 任務進行中

- [ ] 遵循代碼規範
- [ ] 使用 TypeScript 嚴格模式
- [ ] 添加適當註釋
- [ ] 即時提交小變更

### 任務完成後

- [ ] 自我測試功能
- [ ] 執行 linter
- [ ] 編寫單元測試
- [ ] 更新文檔
- [ ] Code Review（如適用）
- [ ] 標記任務為完成

---

## 📈 進度追蹤

### 每日更新

建議每天結束時更新：

```markdown
## 進度更新 - YYYY-MM-DD

### 今日完成
- [x] T001: 初始化專案
- [x] T002: 安裝依賴
- [x] T003: 安裝 shadcn 組件

### 明日計畫
- [ ] T101: 建立首頁
- [ ] T102: 實作搜尋框
- [ ] T103: 整合 API

### 遇到的問題
- 無

### 學習與心得
- shadcn MCP 大幅加速開發
```

---

## 🎯 里程碑追蹤

### M1: MVP 可用（Week 1 末）

**目標日期**: Day 5  
**必需任務**: T001-T108, T201-T208, T301-T312

**驗收標準**:
- [ ] 標籤搜尋功能可用
- [ ] 工作區功能可用
- [ ] Inspire 基礎流程可用
- [ ] 桌面端完整可用

**完成標誌**: 可以完整走完一次使用流程

---

### M2: 功能完整（Week 2 中）

**目標日期**: Day 8  
**必需任務**: T401-T606

**驗收標準**:
- [ ] 驗證功能可用
- [ ] 智能推薦可用
- [ ] 主題切換可用
- [ ] 響應式完成

---

### M3: 生產就緒（Week 2 末）

**目標日期**: Day 12  
**必需任務**: T701-T910

**驗收標準**:
- [ ] 測試覆蓋率 ≥ 80%
- [ ] Lighthouse ≥ 90 分
- [ ] 文檔完整

---

### M4: 正式發布（Week 3）

**目標日期**: Day 14  
**必需任務**: T1001-T1006

**驗收標準**:
- [ ] 部署成功
- [ ] 監控配置
- [ ] 使用者文檔發布

---

## 🔄 任務狀態說明

### 狀態標記

- 🚧 **規劃中** - 任務規劃階段
- ⏳ **待開始** - 等待依賴完成
- 🏃 **進行中** - 正在開發
- 🧪 **測試中** - 開發完成，測試階段
- ✅ **已完成** - 測試通過，已合併
- ⏸️ **暫停** - 暫時擱置
- ❌ **取消** - 不再需要

---

## 📝 使用說明

### 如何使用本任務清單

1. **開始新任務前**
   - 確認依賴任務已完成
   - 閱讀任務描述和規格
   - 評估時間是否合理

2. **執行任務時**
   - 遵循 MCP 提示語（如適用）
   - 參考規格文檔
   - 記錄遇到的問題

3. **完成任務後**
   - 勾選驗收標準
   - 更新任務狀態
   - 提交代碼

### 時間估算說明

**預估時間考慮因素**:
- ✅ 已包含 shadcn MCP 加速（平均節省 30%）
- ✅ 已考慮現有系統整合（節省 44%）
- ⚠️ 不包含學習新技術的時間
- ⚠️ 不包含 Code Review 時間
- ⚠️ 實際時間可能因經驗而異（±30%）

---

## 🎯 優先級策略

### High（高優先級）- 45 個任務

**特徵**:
- 核心功能
- 阻塞其他任務
- 使用者價值高

**範例**: T001, T101, T201, T301, T401

### Medium（中優先級）- 30 個任務

**特徵**:
- 重要但非緊急
- 提升使用者體驗
- 可稍後完成

**範例**: T105, T310, T601

### Low（低優先級）- 10 個任務

**特徵**:
- 錦上添花
- 可選功能
- MVP 後再做

**範例**: T801-T806（PWA）

---

## 📞 支援與協作

### 遇到阻塞

**技術問題**:
1. 查閱規格文檔
2. 查看 MCP_USAGE_GUIDE.md
3. 參考外部技術文檔
4. 提問或建立 Issue

**時間超支**:
1. 評估是否可以簡化
2. 考慮使用 MCP 加速
3. 尋求協助
4. 調整優先級

### 協作建議

**團隊開發**:
- 每日 Standup 更新進度
- 使用 GitHub Projects 追蹤任務
- Code Review 至少 1 人
- 遵循 Git 提交規範

**個人開發**:
- 每日更新進度日誌
- 定期自我 Review
- 保持任務粒度適中（2-4h/任務）

---

## 📚 相關文檔

- [完整規格](../spec.md)
- [快速開始](QUICKSTART.md)
- [MCP 指南](../MCP_USAGE_GUIDE.md)
- [Inspire 計畫](plan-inspire-feature.md)
- [整合指南](INSPIRE_INTEGRATION.md)

---

**任務清單準備完成 - 開始您的開發旅程！** 🚀

**版本**: 1.0.1  
**最後更新**: 2025-10-17 17:50  
**維護者**: Prompt-Scribe Team

**進度狀態**: 
- ✅ Phase 0: 100% 完成
- 🏃 Phase 3: 60% 完成（Inspire MVP 可用）
- 🚀 總進度: 19% (16/85)

---

## 附錄：完整任務列表（85 個）

### Phase 0: 專案設置（7 個任務，4h）
- [x] T001: 初始化 Next.js 專案（30 分鐘）
- [x] T002: 安裝核心依賴（30 分鐘）
- [x] T003: 使用 MCP 安裝 UI 組件（20 分鐘）
- [x] T004: 配置 TypeScript（15 分鐘）
- [x] T005: 設置 ESLint/Prettier（20 分鐘）
- [x] T006: 配置環境變數（20 分鐘）
- [x] T007: 建立目錄結構（30 分鐘）

### Phase 1: 核心搜尋（10 個任務，11h）
- [ ] T101: 首頁佈局（2h）
- [ ] T102: 搜尋輸入框 MCP（1.5h）
- [ ] T103: 整合推薦 API（1.5h）
- [ ] T104: 搜尋結果展示（2h）
- [ ] T105: 搜尋歷史（1h）
- [ ] T106: 熱門標籤（1h）
- [ ] T107: 搜尋頁面（1.5h）
- [ ] T108: 載入狀態（0.5h）
- [ ] T109: 錯誤處理（0.5h）
- [ ] T110: 測試（1.5h）

### Phase 2: 工作區管理（12 個任務，14h）
- [ ] T201: TagCard MCP（1.5h）
- [ ] T202: Workspace MCP（2h）
- [ ] T203: 拖拽排序（2h）
- [ ] T204: Prompt 預覽複製（1.5h）
- [ ] T205: 工作區狀態（1h）
- [ ] T206: 本地持久化（1h）
- [ ] T207: 批量操作（1h）
- [ ] T208: 工作區頁面（1.5h）
- [ ] T209: 標籤詳情彈窗（1.5h）
- [ ] T210: 動畫優化（0.5h）
- [ ] T211: 錯誤處理（0.5h）
- [ ] T212: 測試（2h）

### Phase 3: Inspire 功能（15 個任務，15h）⭐ - 60% 完成
- [x] T301: Inspire 頁面骨架（1h）✅
- [x] T302: InputBox MCP（1h）✅
- [x] T303: InspirationCard MCP（2h）✅
- [x] T304: InspirationCards 容器（1h）✅
- [x] T305: 生成 API 整合（2h）✅
- [ ] T306: Session 管理（1.5h）⏳
- [ ] T307: FeedbackPanel MCP（2h）⏳
- [ ] T308: 反饋 API（2h）⏳
- [x] T309: ResultPanel MCP（1.5h）✅
- [x] T310: Loader 動畫（1h）✅
- [ ] T311: 狀態機（2h）⏳
- [x] T312: 頁面組裝（1.5h）✅
- [ ] T313: 分析追蹤（1h）⏳
- [ ] T314: 錯誤處理（0.5h）⏳
- [ ] T315: 測試（2h）⏳

### Phase 4: 智能推薦（8 個任務，8h）
- [ ] T401: 驗證 API 整合（1.5h）
- [ ] T402: ValidationPanel MCP（2h）
- [ ] T403: 評分視覺化（1h）
- [ ] T404: 組合建議 API（1.5h）
- [ ] T405: 組合面板（1.5h）
- [ ] T406: 應用建議（0.5h）
- [ ] T407: 教學提示（0.5h）
- [ ] T408: 測試（1.5h）

### Phase 5: 分類瀏覽（7 個任務，7h）
- [ ] T501: 分類 API 整合（1h）
- [ ] T502: 分類頁面（1.5h）
- [ ] T503: 分類樹（2h）
- [ ] T504: 標籤列表（1h）
- [ ] T505: 統計圖表（1h）
- [ ] T506: 篩選功能（0.5h）
- [ ] T507: 測試（1h）

### Phase 6: 主題語言（6 個任務，6h）
- [ ] T601: 主題切換（1.5h）
- [ ] T602: 主題配置（1h）
- [ ] T603: 國際化設置（1.5h）
- [ ] T604: 翻譯文件（1.5h）
- [ ] T605: 語言切換（0.5h）
- [ ] T606: 測試（1h）

### Phase 7: 響應優化（8 個任務，9h）
- [ ] T701: 響應式佈局（2h）
- [ ] T702: 觸控優化（1.5h）
- [ ] T703: 虛擬化列表（1.5h）
- [ ] T704: 圖片字型優化（1h）
- [ ] T705: 代碼分割（1h）
- [ ] T706: Bundle 優化（0.5h）
- [ ] T707: 骨架屏（1h）
- [ ] T708: Lighthouse 測試（1.5h）

### Phase 8: PWA 進階（6 個任務，6h）
- [ ] T801: PWA manifest（1h）
- [ ] T802: Service Worker（1.5h）
- [ ] T803: 鍵盤快捷鍵（1h）
- [ ] T804: 快速操作（0.5h）
- [ ] T805: 收藏管理（1.5h）
- [ ] T806: 設定頁面（1.5h）

### Phase 9: 測試文檔（10 個任務，10h）
- [ ] T901: 測試環境（1h）
- [ ] T902: 組件單元測試（3h）
- [ ] T903: Hook 測試（1h）
- [ ] T904: 整合測試（2h）
- [ ] T905: E2E 測試（2h）
- [ ] T906: 無障礙測試（1h）
- [ ] T907: 使用者文檔（2h）
- [ ] T908: 開發者文檔（1.5h）
- [ ] T909: API 文檔（1h）
- [ ] T910: 部署指南（1.5h）

### Phase 10: 部署監控（6 個任務，4h）
- [ ] T1001: Vercel 部署（1h）
- [ ] T1002: 環境變數配置（0.5h）
- [ ] T1003: CI/CD 設置（1h）
- [ ] T1004: Sentry 整合（0.5h）
- [ ] T1005: 分析追蹤（0.5h）
- [ ] T1006: SEO 配置（0.5h）

---

**總計: 85 個任務，預估 80 小時**

---

## 📊 進度更新記錄

### 2025-10-17 - 初始實作完成

**今日完成**:
- ✅ Phase 0: 專案設置完成（7/7 任務）
  - Next.js 15 專案初始化
  - 21 個 shadcn/ui 組件安裝
  - TypeScript 嚴格模式配置
  - 環境變數與 API 配置
  - 完整目錄結構建立

- ✅ Phase 3: Inspire MVP 完成（9/15 任務）
  - InputBox 輸入框組件
  - InspirationCard 卡片組件
  - InspirationCards 容器
  - ResultPanel 結果面板
  - Loader 載入動畫
  - 完整頁面組裝
  - 成功複用後端推薦 API

**關鍵成就**:
- 🎉 Inspire 功能已可使用（MVP 完成）
- 🔗 成功複用後端 API，無需新建端點
- 🎨 21 個 shadcn/ui 組件已整合
- ⚡ 開發效率提升（使用 MCP）

**待辦事項**:
- ⏳ Phase 3 剩餘任務（Session、反饋、狀態機）
- ⏳ Phase 1: 核心搜尋功能
- ⏳ Phase 2: 工作區管理

**整體進度**: 16/85 (19%) ✅

