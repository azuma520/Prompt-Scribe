# 規格文件：Prompt-Scribe Web Frontend

**規格編號 (Spec ID):** SPEC-2025-003

**版本 (Version):** 1.0.0

**狀態 (Status):** Draft

**作者 (Author):** AI Assistant

**建立日期 (Created):** 2025-10-17

**最後更新 (Last Updated):** 2025-10-17

---

## 憲法符合性檢查 (Constitution Compliance Check)

- [x] 符合「兩階段混合式架構」原則（屬於階段二的前端層）
- [x] 符合「LLM 職責分離」原則（前端不直接調用 LLM，通過 API）
- [x] 符合「規格驅動開發」原則（本規格先於實作）
- [x] 符合「模組化與可讀性」原則（組件化設計）
- [x] 符合「使用者體驗優先」原則（直觀、響應式、無障礙）

---

## 1. 概述 (Overview)

### 1.1 目標 (Objective)

為 Prompt-Scribe API 建立現代化、直觀的 Web 前端介面，讓使用者能夠輕鬆地搜尋、瀏覽和管理 AI 圖像生成的標籤（tags）。提供智能推薦、標籤驗證和組合建議等功能，提升 AI 創作者的工作效率。

**核心價值：**
- 降低使用門檻，讓非技術使用者也能輕鬆使用
- 提供視覺化的標籤瀏覽和搜尋體驗
- 即時反饋和智能建議，提升創作效率
- 美觀現代的介面，符合當代設計標準
- 跨裝置相容，支援桌面和移動端

### 1.2 範圍 (Scope)

**包含 (In Scope):**
- 標籤搜尋和瀏覽介面
- 智能標籤推薦功能（基於描述）
- 標籤組合建議和預覽
- Prompt 驗證和優化建議
- 標籤收藏和歷史記錄
- 響應式設計（桌面、平板、手機）
- 深色/淺色主題切換
- 多語言支援（繁體中文、英文）
- 無障礙設計（WCAG 2.1 AA 標準）
- PWA 支援（漸進式 Web 應用）

**不包含 (Out of Scope):**
- 使用者帳號系統（初期版本）
- 社群分享功能
- 標籤編輯和管理（僅限 API）
- 圖像生成功能
- 付費訂閱系統
- 即時協作功能

### 1.3 架構階段定位 (Architecture Stage)

- [ ] 階段一：本地資料管線
- [x] 階段二：雲端應用前端
- [ ] 跨階段（需說明如何解耦）

**說明：** 此功能屬於階段二的前端層，完全依賴已部署的 Prompt-Scribe API（https://prompt-scribe-api.vercel.app）。

---

## 2. 使用者場景 (User Scenarios)

### 2.1 主要場景：AI 創作者搜尋標籤

**角色：** AI 圖像創作者（AI Artist）

**前置條件：**
- 使用者訪問 Web 應用
- API 服務正常運行

**操作流程：**
1. 使用者在首頁看到搜尋框和精選標籤
2. 使用者輸入描述："cute girl in school uniform"
3. 系統即時顯示推薦標籤（1girl, solo, school_uniform, cute...）
4. 使用者點擊標籤查看詳細資訊（使用次數、分類、相關標籤）
5. 使用者將標籤添加到工作區
6. 系統顯示完整的 Prompt 預覽和優化建議
7. 使用者一鍵複製 Prompt

**預期結果：**
- 搜尋回應時間 < 1 秒
- 推薦標籤準確度 > 85%
- 使用者能快速找到需要的標籤
- 流暢的使用體驗，無卡頓

**異常處理：**
- API 失敗：顯示友好的錯誤訊息並提供重試選項
- 無結果：提供搜尋建議和熱門標籤
- 網路慢：顯示載入動畫和進度提示

### 2.2 次要場景：使用者探索標籤分類

**角色：** 新手使用者（Beginner User）

**前置條件：**
- 使用者首次訪問應用
- 不熟悉標籤系統

**操作流程：**
1. 使用者進入「分類瀏覽」頁面
2. 系統顯示標籤分類樹狀結構（角色、服裝、場景等）
3. 使用者點擊「角色相關」分類
4. 系統顯示該分類下的熱門標籤
5. 使用者點擊「1girl」查看詳情
6. 系統顯示標籤說明、使用次數、常見組合
7. 使用者添加標籤到工作區

**預期結果：**
- 清晰的分類結構
- 視覺化的標籤分佈
- 豐富的標籤資訊
- 引導式的學習體驗

### 2.3 次要場景：驗證和優化 Prompt

**角色：** 經驗豐富的創作者（Expert User）

**前置條件：**
- 使用者已有一組標籤
- 想要優化 Prompt 品質

**操作流程：**
1. 使用者在工作區輸入或貼上現有的 Prompt
2. 系統自動解析標籤並驗證
3. 系統顯示問題：衝突標籤（1girl, 2girls）、冗餘標籤
4. 系統提供優化建議和替代方案
5. 使用者應用建議
6. 系統顯示優化後的評分（75/100 → 92/100）
7. 使用者查看智能組合建議
8. 使用者一鍵應用完整組合

**預期結果：**
- 即時驗證和反饋
- 具體且可操作的建議
- 明顯的品質提升
- 學習價值（了解最佳實踐）

### 2.4 次要場景：移動端快速查詢

**角色：** 移動使用者（Mobile User）

**前置條件：**
- 使用者在手機上訪問應用
- 網路連線可能較慢

**操作流程：**
1. 使用者在手機上打開應用
2. 介面自動適應小螢幕
3. 使用者使用語音輸入描述
4. 系統快速返回推薦標籤
5. 使用者滑動瀏覽標籤卡片
6. 使用者長按複製標籤
7. 系統顯示複製成功提示

**預期結果：**
- 響應式設計完美適配
- 觸控友好的操作
- 離線支援（PWA）
- 流量優化（圖片和資源）

---

## 3. 需求 (Requirements)

### 3.1 功能需求 (Functional Requirements)

| ID | 需求描述 | 優先級 | 驗收標準 |
|----|----------|--------|----------|
| FR-01 | 系統應提供標籤搜尋功能 | High | 支援關鍵字、模糊搜尋、搜尋歷史 |
| FR-02 | 系統應顯示智能推薦標籤 | High | 基於描述推薦，準確度 > 85% |
| FR-03 | 系統應提供標籤分類瀏覽 | Medium | 清晰的分類結構，支援篩選 |
| FR-04 | 系統應顯示標籤詳細資訊 | High | 名稱、分類、使用次數、相關標籤 |
| FR-05 | 系統應提供工作區管理 | High | 添加、刪除、排序、保存標籤 |
| FR-06 | 系統應驗證 Prompt 品質 | High | 檢測衝突、冗餘、評分機制 |
| FR-07 | 系統應提供智能組合建議 | Medium | 10+ 預定義模式，自動推薦 |
| FR-08 | 系統應支援一鍵複製 Prompt | High | 複製到剪貼簿，格式化選項 |
| FR-09 | 系統應記錄搜尋歷史 | Medium | 本地存儲，快速訪問 |
| FR-10 | 系統應支援標籤收藏 | Low | 本地存儲，分類管理 |
| FR-11 | 系統應支援深色/淺色主題 | Medium | 自動檢測系統偏好，手動切換 |
| FR-12 | 系統應支援多語言 | Medium | 繁體中文、英文，動態切換 |
| FR-13 | 系統應提供響應式設計 | High | 桌面、平板、手機完美適配 |
| FR-14 | 系統應支援 PWA | Low | 可安裝、離線基本功能 |
| FR-15 | 系統應提供鍵盤快捷鍵 | Low | 搜尋、複製、導航快捷鍵 |

### 3.2 非功能需求 (Non-Functional Requirements)

| ID | 類別 | 需求描述 | 標準 |
|----|------|----------|------|
| NFR-01 | 效能 (Performance) | 頁面載入時間應快速 | 首次載入 < 3 秒，後續 < 1 秒 |
| NFR-02 | 效能 (Performance) | 搜尋回應時間應即時 | < 1 秒 |
| NFR-03 | 效能 (Performance) | 介面操作應流暢 | 60 FPS，無卡頓 |
| NFR-04 | 可用性 (Usability) | 介面應直觀易用 | 新使用者 5 分鐘內上手 |
| NFR-05 | 可用性 (Usability) | 應符合無障礙標準 | WCAG 2.1 AA 級別 |
| NFR-06 | 相容性 (Compatibility) | 支援主流瀏覽器 | Chrome, Firefox, Safari, Edge 最新兩版 |
| NFR-07 | 相容性 (Compatibility) | 支援多裝置 | 桌面、平板、手機 |
| NFR-08 | 安全性 (Security) | 用戶資料應安全 | 本地存儲加密，HTTPS 通訊 |
| NFR-09 | 可維護性 (Maintainability) | 代碼應模組化 | 組件化架構，清晰的目錄結構 |
| NFR-10 | 可擴展性 (Scalability) | 支援未來功能擴展 | 插件式架構，易於添加新功能 |
| NFR-11 | SEO | 搜尋引擎友好 | 基本的 SEO 優化，Open Graph 支援 |
| NFR-12 | 分析 (Analytics) | 支援使用數據收集 | 隱私友好的匿名統計 |

---

## 4. 技術架構 (Technical Architecture)

### 4.1 技術棧選擇

#### 4.1.1 核心框架

**選項評估：**

| 框架 | 優勢 | 劣勢 | 適合度 |
|------|------|------|--------|
| **Next.js 14** | SSR/SSG、SEO 友好、Vercel 部署 | 學習曲線、檔案大小 | ⭐⭐⭐⭐⭐ |
| Vue 3 + Nuxt | 易學、輕量、中文社群 | 生態系統較小 | ⭐⭐⭐⭐ |
| React + Vite | 快速、靈活、生態豐富 | 需自行配置 SSR | ⭐⭐⭐ |
| Svelte + SvelteKit | 輕量、高效、新穎 | 社群較小、插件少 | ⭐⭐⭐ |

**推薦選擇：Next.js 14 (App Router)**

**理由：**
- ✅ 與 API 同平台（Vercel），部署最佳化
- ✅ 內建 SSR/SSG，SEO 友好
- ✅ React Server Components，效能優越
- ✅ 圖片優化、字型優化等內建功能
- ✅ 豐富的生態系統和 UI 庫支援
- ✅ TypeScript 原生支援
- ✅ 零配置部署到 Vercel

#### 4.1.2 UI 框架

**選項評估：**

| 框架 | 優勢 | 劣勢 | 適合度 |
|------|------|------|--------|
| **shadcn/ui + Tailwind** | 現代、可自訂、無依賴鎖定 | 需手動安裝組件 | ⭐⭐⭐⭐⭐ |
| MUI (Material-UI) | 成熟、完整、文檔豐富 | 檔案大、客製化困難 | ⭐⭐⭐ |
| Ant Design | 企業級、中文文檔 | 設計風格固定 | ⭐⭐⭐ |
| Chakra UI | 無障礙、易用 | 社群較小 | ⭐⭐⭐⭐ |

**推薦選擇：shadcn/ui + Tailwind CSS + shadcn MCP**

**理由：**
- ✅ 現代設計風格，符合當前趨勢
- ✅ 完全可自訂，複製即用
- ✅ Tailwind CSS 高效開發
- ✅ 優秀的無障礙支援
- ✅ TypeScript 支援
- ✅ 深色模式內建
- ✅ 社群活躍，持續更新
- ⚡ **shadcn MCP 加速開發**：可通過 AI 助手快速安裝和生成組件，節省 30-50% 開發時間

#### 4.1.3 狀態管理

**選項評估：**

| 方案 | 優勢 | 劣勢 | 適合度 |
|------|------|------|--------|
| **Zustand** | 輕量、簡單、Hook 友好 | 功能相對簡單 | ⭐⭐⭐⭐⭐ |
| Redux Toolkit | 成熟、強大、devtools 完善 | 複雜、樣板代碼多 | ⭐⭐⭐ |
| Jotai | 原子化、靈活 | 相對新、文檔較少 | ⭐⭐⭐⭐ |
| React Context | 內建、零依賴 | 效能問題、不適合複雜狀態 | ⭐⭐ |

**推薦選擇：Zustand + React Query**

**理由：**
- ✅ Zustand：輕量的全局狀態管理
- ✅ React Query：專業的伺服器狀態管理
- ✅ 簡單易用，學習曲線低
- ✅ 優秀的 TypeScript 支援
- ✅ 自動處理快取和重新載入

#### 4.1.4 API 請求

**推薦選擇：TanStack Query (React Query) v5**

**功能：**
- 自動快取和重新驗證
- 樂觀更新
- 請求去重
- 離線支援
- DevTools

### 4.2 專案結構

```
prompt-scribe-web/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # 根佈局
│   ├── page.tsx                 # 首頁
│   ├── search/                  # 搜尋頁面
│   ├── browse/                  # 分類瀏覽
│   ├── workspace/               # 工作區
│   └── api/                     # API Routes（如需代理）
│
├── components/                   # React 組件
│   ├── ui/                      # shadcn/ui 基礎組件
│   ├── features/                # 功能組件
│   │   ├── tag-search/
│   │   ├── tag-card/
│   │   ├── workspace/
│   │   ├── recommendation/
│   │   └── validation/
│   ├── layouts/                 # 佈局組件
│   └── shared/                  # 共用組件
│
├── lib/                          # 工具函數和配置
│   ├── api/                     # API 客戶端
│   │   ├── client.ts           # HTTP 客戶端
│   │   └── endpoints.ts        # API 端點定義
│   ├── hooks/                   # 自定義 Hooks
│   ├── store/                   # Zustand stores
│   ├── utils/                   # 工具函數
│   └── constants/               # 常數定義
│
├── types/                        # TypeScript 型別定義
│   ├── api.ts                   # API 型別
│   ├── tag.ts                   # 標籤型別
│   └── workspace.ts             # 工作區型別
│
├── styles/                       # 樣式文件
│   └── globals.css              # 全局樣式（Tailwind）
│
├── public/                       # 靜態資源
│   ├── images/
│   ├── icons/
│   └── manifest.json            # PWA manifest
│
├── locales/                      # 國際化
│   ├── zh-TW.json
│   └── en-US.json
│
├── tests/                        # 測試文件
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .env.local.example            # 環境變數範例
├── next.config.js                # Next.js 配置
├── tailwind.config.ts            # Tailwind 配置
├── tsconfig.json                 # TypeScript 配置
└── package.json                  # 專案依賴
```

### 4.3 核心組件設計

#### 4.3.1 TagSearch（標籤搜尋）

**責任：**
- 接收使用者輸入
- 調用推薦 API
- 顯示即時搜尋結果
- 管理搜尋歷史

**Props：**
```typescript
interface TagSearchProps {
  onTagSelect: (tag: Tag) => void;
  placeholder?: string;
  autoFocus?: boolean;
}
```

#### 4.3.2 TagCard（標籤卡片）

**責任：**
- 顯示標籤資訊
- 提供互動操作（添加、詳情）
- 視覺化使用頻率
- 顯示分類標籤

**Props：**
```typescript
interface TagCardProps {
  tag: Tag;
  onAdd?: (tag: Tag) => void;
  onViewDetails?: (tag: Tag) => void;
  variant?: 'compact' | 'detailed';
}
```

#### 4.3.3 Workspace（工作區）

**責任：**
- 管理選中的標籤
- 拖拽排序
- Prompt 預覽
- 驗證和優化建議
- 一鍵複製

**State：**
```typescript
interface WorkspaceState {
  tags: Tag[];
  validation: ValidationResult;
  suggestions: TagCombination[];
  prompt: string;
}
```

#### 4.3.4 RecommendationPanel（推薦面板）

**責任：**
- 顯示智能組合建議
- 預覽完整 Prompt
- 應用建議到工作區

**Props：**
```typescript
interface RecommendationPanelProps {
  currentTags: Tag[];
  onApplySuggestion: (tags: Tag[]) => void;
}
```

### 4.4 API 整合

#### 4.4.1 API 客戶端配置

```typescript
// lib/api/client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 分鐘
      cacheTime: 10 * 60 * 1000, // 10 分鐘
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  'https://prompt-scribe-api.vercel.app';
```

#### 4.4.2 API 端點封裝

```typescript
// lib/api/endpoints.ts
import { API_BASE_URL } from './client';

export const apiEndpoints = {
  // 標籤推薦
  recommendTags: (description: string) => 
    `${API_BASE_URL}/api/llm/recommend-tags`,
  
  // 標籤搜尋
  searchTags: (query: string) => 
    `${API_BASE_URL}/api/v1/search`,
  
  // 驗證 Prompt
  validatePrompt: (tags: string[]) => 
    `${API_BASE_URL}/api/llm/validate-prompt`,
  
  // 智能組合建議
  suggestCombinations: (tags: string[]) => 
    `${API_BASE_URL}/api/llm/suggest-combinations`,
  
  // 標籤詳情
  getTag: (name: string) => 
    `${API_BASE_URL}/api/v1/tags?name=${encodeURIComponent(name)}`,
  
  // 分類統計
  getCategories: () => 
    `${API_BASE_URL}/api/v1/categories`,
};
```

#### 4.4.3 自定義 Hooks

```typescript
// lib/hooks/useTagRecommendation.ts
import { useQuery } from '@tanstack/react-query';
import { apiEndpoints } from '@/lib/api/endpoints';

export function useTagRecommendation(description: string) {
  return useQuery({
    queryKey: ['tagRecommendation', description],
    queryFn: async () => {
      const response = await fetch(apiEndpoints.recommendTags(description), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      
      if (!response.ok) throw new Error('推薦失敗');
      return response.json();
    },
    enabled: description.length > 2, // 至少 3 個字元才查詢
    staleTime: 5 * 60 * 1000,
  });
}
```

### 4.5 資料流向

```
使用者輸入
    ↓
組件觸發事件
    ↓
自定義 Hook (useTagRecommendation)
    ↓
React Query 管理請求
    ↓
API 客戶端發送 HTTP 請求
    ↓
Prompt-Scribe API (Vercel)
    ↓
回應資料
    ↓
React Query 快取
    ↓
組件更新顯示
    ↓
使用者互動
```

---

## 5. 介面設計 (UI/UX Design)

### 5.1 設計原則

**1. 簡潔優先 (Simplicity First)**
- 清晰的視覺層次
- 減少認知負擔
- 突出核心功能

**2. 響應即時 (Instant Feedback)**
- 即時搜尋結果
- 載入狀態提示
- 操作反饋動畫

**3. 引導式體驗 (Guided Experience)**
- 新手教學提示
- 空狀態引導
- 智能建議

**4. 無障礙設計 (Accessibility)**
- 鍵盤導航
- 螢幕閱讀器支援
- 適當的對比度

**5. 視覺美學 (Visual Aesthetics)**
- 現代設計風格
- 一致的色彩系統
- 流暢的動畫效果

### 5.2 頁面結構

#### 5.2.1 首頁 (Home Page)

**佈局：**
```
┌─────────────────────────────────────┐
│  Logo    搜尋框            主題 語言 │  ← Header
├─────────────────────────────────────┤
│                                     │
│    🎨 Prompt-Scribe                │
│    AI 標籤推薦系統                   │
│                                     │
│    [       搜尋標籤或描述場景      ] │  ← 主搜尋框
│                                     │
│    快速開始：                        │
│    [關鍵字搜尋] [分類瀏覽] [工作區]  │
│                                     │
│    🔥 熱門標籤                      │
│    [1girl] [solo] [long_hair] ...  │
│                                     │
│    📊 分類瀏覽                      │
│    [角色] [服裝] [場景] [風格] ... │
│                                     │
│    📝 最近搜尋                      │
│    1. cute girl in school uniform  │
│    2. cyberpunk city at night      │
│                                     │
└─────────────────────────────────────┘
```

#### 5.2.2 搜尋結果頁 (Search Results)

**佈局：**
```
┌─────────────────────────────────────┐
│  ← 返回   [搜尋框]         主題 語言 │
├─────────────────────────────────────┤
│                     │               │
│  🎯 推薦標籤 (8)    │   📋 工作區  │
│                     │               │
│  ┌──────┐ ┌──────┐ │   已選 (3)   │
│  │1girl │ │ solo │ │   [1girl]    │
│  │95%   │ │ 90%  │ │   [solo]     │
│  │15k   │ │ 12k  │ │   [cute]     │
│  └──────┘ └──────┘ │               │
│                     │   預覽：      │
│  ┌──────┐ ┌──────┐ │   1girl,...  │
│  │school│ │ cute │ │               │
│  │88%   │ │ 85%  │ │   [複製]     │
│  │8k    │ │ 10k  │ │   [驗證]     │
│  └──────┘ └──────┘ │   [優化]     │
│                     │               │
│  [載入更多...]      │               │
│                     │               │
└─────────────────────┴───────────────┘
```

#### 5.2.3 標籤詳情彈窗 (Tag Details Modal)

**佈局：**
```
┌─────────────────────────────────┐
│  school_uniform            [✕] │
├─────────────────────────────────┤
│                                 │
│  📊 基本資訊                    │
│  分類：角色相關 > 服裝          │
│  使用次數：8,234                │
│  信心度：88%                    │
│                                 │
│  📝 描述                        │
│  學生制服相關標籤，常用於校園場景 │
│                                 │
│  🔗 常見組合 (點擊添加)         │
│  [1girl] [solo] [student]      │
│  [skirt] [necktie] [bag]       │
│                                 │
│  💡 相似標籤                    │
│  [uniform] [seifuku] [sailor]  │
│                                 │
│  [添加到工作區] [收藏]          │
│                                 │
└─────────────────────────────────┘
```

#### 5.2.4 工作區頁面 (Workspace)

**佈局：**
```
┌─────────────────────────────────────┐
│  Logo  工作區              主題 語言 │
├─────────────────────────────────────┤
│                                     │
│  📋 我的 Prompt                     │
│                                     │
│  已選標籤 (5) [清空]                │
│  ┌────────────────────────────────┐│
│  │ [1girl ✕] [solo ✕] [long_hair]││  ← 可拖拽
│  │ [school_uniform ✕] [cute ✕]   ││
│  └────────────────────────────────┘│
│                                     │
│  ✨ Prompt 預覽                    │
│  ┌────────────────────────────────┐│
│  │ 1girl, solo, long_hair,        ││
│  │ school_uniform, cute           ││
│  │                         [複製] ││
│  └────────────────────────────────┘│
│                                     │
│  ✅ 品質檢查                        │
│  評分：92/100 ⭐⭐⭐⭐⭐            │
│  ✓ 無衝突標籤                      │
│  ✓ 無冗餘標籤                      │
│  ⚠ 建議添加背景標籤                │
│                                     │
│  💡 智能建議                        │
│  添加這些標籤可能更好：             │
│  [+smile] [+looking_at_viewer]    │
│  [+indoor] [+classroom]           │
│                                     │
│  🎨 完整組合                        │
│  [查看 10+ 預定義組合]             │
│                                     │
└─────────────────────────────────────┘
```

### 5.3 色彩系統

#### 5.3.1 淺色主題 (Light Theme)

```css
:root {
  /* 主色調 - 紫色系（創意、優雅） */
  --primary: 262 83% 58%;        /* #8B5CF6 */
  --primary-hover: 262 83% 50%;  /* #7C3AED */
  
  /* 次要色 - 藍色系（信任、專業） */
  --secondary: 217 91% 60%;      /* #3B82F6 */
  
  /* 強調色 - 粉色系（親和、活力） */
  --accent: 330 81% 60%;         /* #EC4899 */
  
  /* 成功 */
  --success: 142 71% 45%;        /* #10B981 */
  
  /* 警告 */
  --warning: 38 92% 50%;         /* #F59E0B */
  
  /* 錯誤 */
  --error: 0 84% 60%;            /* #EF4444 */
  
  /* 背景 */
  --background: 0 0% 100%;       /* #FFFFFF */
  --surface: 0 0% 98%;           /* #FAFAFA */
  
  /* 文字 */
  --text-primary: 0 0% 9%;       /* #171717 */
  --text-secondary: 0 0% 45%;    /* #737373 */
  
  /* 邊框 */
  --border: 0 0% 90%;            /* #E5E5E5 */
}
```

#### 5.3.2 深色主題 (Dark Theme)

```css
.dark {
  /* 主色調 */
  --primary: 262 83% 65%;        /* #A78BFA */
  --primary-hover: 262 83% 58%;  /* #8B5CF6 */
  
  /* 背景 */
  --background: 0 0% 9%;         /* #171717 */
  --surface: 0 0% 12%;           /* #1F1F1F */
  
  /* 文字 */
  --text-primary: 0 0% 98%;      /* #FAFAFA */
  --text-secondary: 0 0% 65%;    /* #A3A3A3 */
  
  /* 邊框 */
  --border: 0 0% 20%;            /* #333333 */
}
```

### 5.4 互動動畫

#### 5.4.1 標籤卡片懸停

```css
/* 柔和的提升效果 */
.tag-card {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.tag-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -6px rgba(0, 0, 0, 0.15);
}
```

#### 5.4.2 搜尋框聚焦

```css
/* 平滑的邊框動畫 */
.search-input {
  transition: box-shadow 0.3s ease;
}

.search-input:focus {
  box-shadow: 0 0 0 3px var(--primary-alpha-20);
}
```

#### 5.4.3 標籤添加動畫

```javascript
// Framer Motion 動畫配置
const tagAnimation = {
  initial: { scale: 0, opacity: 0 },
  animate: { scale: 1, opacity: 1 },
  exit: { scale: 0, opacity: 0 },
  transition: { type: 'spring', stiffness: 300, damping: 25 }
};
```

### 5.5 響應式斷點

```javascript
// Tailwind 斷點配置
const breakpoints = {
  'sm': '640px',   // 手機橫向
  'md': '768px',   // 平板
  'lg': '1024px',  // 小桌面
  'xl': '1280px',  // 桌面
  '2xl': '1536px'  // 大桌面
};
```

---

## 6. 成功標準 (Success Criteria)

### 6.1 功能完整性

| 標準 | 測量方式 | 目標值 |
|------|----------|--------|
| 核心功能覆蓋 | 檢查功能實作清單 | 100% (15/15 功能) |
| API 整合完整度 | 測試所有 API 端點 | 100% (8/8 端點) |
| 組件覆蓋率 | 計算已實作組件 | ≥ 90% |
| 頁面完整度 | 檢查所有定義頁面 | 100% (5/5 頁面) |

### 6.2 使用者體驗

| 標準 | 測量方式 | 目標值 |
|------|----------|--------|
| 頁面載入時間 | Lighthouse Performance | ≥ 90 分 |
| 首次內容繪製 (FCP) | Core Web Vitals | < 1.8 秒 |
| 最大內容繪製 (LCP) | Core Web Vitals | < 2.5 秒 |
| 累積佈局偏移 (CLS) | Core Web Vitals | < 0.1 |
| 互動到下一次繪製 (INP) | Core Web Vitals | < 200 毫秒 |
| 使用者滿意度 | 問卷調查 | ≥ 4.0/5.0 |
| 新手上手時間 | 使用者測試 | < 5 分鐘 |

### 6.3 技術品質

| 標準 | 測量方式 | 目標值 |
|------|----------|--------|
| TypeScript 覆蓋率 | tsconfig 嚴格模式 | 100% |
| 測試覆蓋率 | Jest + Testing Library | ≥ 80% |
| 無障礙評分 | Lighthouse Accessibility | ≥ 95 分 |
| SEO 評分 | Lighthouse SEO | ≥ 90 分 |
| 最佳實踐評分 | Lighthouse Best Practices | ≥ 90 分 |
| Bundle 大小 | 生產打包大小 | < 300 KB (gzipped) |
| 瀏覽器相容性 | BrowserStack 測試 | 100% 主流瀏覽器 |

### 6.4 營運就緒

| 標準 | 測量方式 | 目標值 |
|------|----------|--------|
| 文件完整性 | 檢查文件清單 | 100% |
| 部署自動化 | CI/CD 管線 | 完全自動化 |
| 錯誤監控 | Sentry 整合 | 已配置 |
| 分析追蹤 | Google Analytics 或替代方案 | 已配置 |
| 環境變數管理 | .env 文件和文檔 | 完整說明 |

---

## 7. 風險與對策 (Risks and Mitigation)

### 7.1 技術風險

| 風險 | 可能性 | 影響程度 | 對策 |
|------|--------|----------|------|
| API 速率限制或失敗 | Medium | High | 實作請求快取、錯誤重試、降級方案（離線模式） |
| 瀏覽器相容性問題 | Low | Medium | 使用 Polyfill、漸進增強、廣泛測試 |
| 效能瓶頸（大量標籤） | Medium | Medium | 虛擬化列表、懶加載、分頁 |
| Bundle 體積過大 | Medium | Low | 代碼分割、動態導入、樹搖優化 |
| SEO 不佳（CSR 問題） | Low | Medium | 使用 Next.js SSR/SSG、Meta 標籤優化 |

### 7.2 使用者體驗風險

| 風險 | 可能性 | 影響程度 | 對策 |
|------|--------|----------|------|
| 學習曲線過陡 | Medium | High | 新手教學、工具提示、清晰的 UI 引導 |
| 移動端體驗不佳 | Medium | High | 響應式設計、觸控優化、PWA 支援 |
| 搜尋結果不準確 | Low | High | 提供篩選選項、顯示信心度、反饋機制 |
| 載入時間過長 | Medium | High | 優化資源、預載入、骨架屏 |

### 7.3 專案風險

| 風險 | 可能性 | 影響程度 | 對策 |
|------|--------|----------|------|
| 開發時間超出預期 | Medium | Medium | MVP 優先、迭代開發、功能分級 |
| UI 設計不一致 | Medium | Low | 設計系統、組件庫、設計評審 |
| 第三方依賴問題 | Low | Medium | 鎖定版本、定期更新、有替代方案 |

---

## 8. 實作計畫 (Implementation Plan)

### 8.1 階段劃分

| 階段 | 任務 | 預估時間 | 優先級 | 交付物 |
|------|------|----------|--------|--------|
| **Phase 0** | 專案設置與環境配置 | 4 小時 | High | 初始專案、開發環境 |
| **Phase 1** | 核心搜尋功能 | 16 小時 | High | 搜尋介面、API 整合 |
| **Phase 2** | 標籤展示與工作區 | 20 小時 | High | 標籤卡片、工作區管理 |
| **Phase 3** | 智能推薦與驗證 | 16 小時 | High | 推薦系統、驗證功能 |
| **Phase 4** | 分類瀏覽與詳情 | 12 小時 | Medium | 分類頁面、詳情彈窗 |
| **Phase 5** | 主題與國際化 | 8 小時 | Medium | 深色模式、多語言 |
| **Phase 6** | 響應式與優化 | 12 小時 | High | 移動端、效能優化 |
| **Phase 7** | PWA 與進階功能 | 8 小時 | Low | PWA、快捷鍵、收藏 |
| **Phase 8** | 測試與文檔 | 12 小時 | High | 測試套件、使用文檔 |
| **Phase 9** | 部署與監控 | 4 小時 | High | CI/CD、分析、監控 |

**總預估時間：** 112 小時（約 14 工作天，2-3 週）

### 8.2 詳細任務清單

#### Phase 0: 專案設置 (4h)

- [ ] **T001**: 初始化 Next.js 14 專案 (App Router)
- [ ] **T002**: 安裝核心依賴（Tailwind, shadcn/ui, React Query, Zustand）
- [ ] **T003**: 配置 TypeScript 嚴格模式
- [ ] **T004**: 設置 ESLint 和 Prettier
- [ ] **T005**: 配置環境變數和 API 連線
- [ ] **T006**: 建立專案目錄結構
- [ ] **T007**: 設置 Git hooks (Husky + lint-staged)

#### Phase 1: 核心搜尋功能 (16h)

- [ ] **T101**: 建立首頁佈局和 Header
- [ ] **T102**: 實作搜尋框組件（TagSearchInput）
- [ ] **T103**: 整合標籤推薦 API (useTagRecommendation)
- [ ] **T104**: 實作即時搜尋結果顯示
- [ ] **T105**: 實作搜尋歷史管理（Local Storage）
- [ ] **T106**: 實作熱門標籤展示
- [ ] **T107**: 實作搜尋結果頁面佈局
- [ ] **T108**: 添加載入狀態和錯誤處理

#### Phase 2: 標籤展示與工作區 (20h)

- [ ] **T201**: 設計並實作 TagCard 組件（多種變體）
- [ ] **T202**: 實作工作區組件（Workspace）
- [ ] **T203**: 實作標籤添加/移除功能
- [ ] **T204**: 實作標籤拖拽排序（DnD Kit）
- [ ] **T205**: 實作 Prompt 預覽和複製功能
- [ ] **T206**: 實作工作區狀態管理（Zustand）
- [ ] **T207**: 實作工作區本地持久化
- [ ] **T208**: 實作批量操作（清空、複製全部）

#### Phase 3: 智能推薦與驗證 (16h)

- [ ] **T301**: 整合 Prompt 驗證 API
- [ ] **T302**: 實作驗證結果顯示組件
- [ ] **T303**: 實作評分系統和視覺化
- [ ] **T304**: 整合智能組合建議 API
- [ ] **T305**: 實作組合建議面板
- [ ] **T306**: 實作一鍵應用建議功能
- [ ] **T307**: 實作優化建議提示
- [ ] **T308**: 添加互動式教學提示

#### Phase 4: 分類瀏覽與詳情 (12h)

- [ ] **T401**: 建立分類瀏覽頁面
- [ ] **T402**: 整合分類統計 API
- [ ] **T403**: 實作分類樹狀導航
- [ ] **T404**: 實作標籤詳情彈窗（Modal）
- [ ] **T405**: 實作標籤詳細資訊顯示
- [ ] **T406**: 實作相關標籤和常見組合
- [ ] **T407**: 實作標籤收藏功能

#### Phase 5: 主題與國際化 (8h)

- [ ] **T501**: 實作深色/淺色主題切換
- [ ] **T502**: 配置主題色彩系統
- [ ] **T503**: 設置 next-intl 國際化
- [ ] **T504**: 翻譯所有介面文字（繁中、英文）
- [ ] **T505**: 實作語言切換功能
- [ ] **T506**: 實作主題和語言偏好持久化

#### Phase 6: 響應式與優化 (12h)

- [ ] **T601**: 實作響應式佈局（所有頁面）
- [ ] **T602**: 優化移動端觸控體驗
- [ ] **T603**: 實作虛擬化列表（大量標籤）
- [ ] **T604**: 優化圖片和字型載入
- [ ] **T605**: 實作代碼分割和懶加載
- [ ] **T606**: 優化 Bundle 大小
- [ ] **T607**: 實作骨架屏和載入動畫
- [ ] **T608**: 效能測試和優化（Lighthouse）

#### Phase 7: PWA 與進階功能 (8h)

- [ ] **T701**: 配置 PWA manifest
- [ ] **T702**: 實作 Service Worker（離線支援）
- [ ] **T703**: 實作鍵盤快捷鍵
- [ ] **T704**: 實作快速操作（快捷選單）
- [ ] **T705**: 實作收藏管理頁面
- [ ] **T706**: 實作匯出/匯入功能
- [ ] **T707**: 實作設定頁面

#### Phase 8: 測試與文檔 (12h)

- [ ] **T801**: 設置 Jest 和 Testing Library
- [ ] **T802**: 編寫組件單元測試（核心組件）
- [ ] **T803**: 編寫 API Hook 測試
- [ ] **T804**: 編寫整合測試（主要流程）
- [ ] **T805**: 設置 E2E 測試（Playwright）
- [ ] **T806**: 無障礙測試（axe-core）
- [ ] **T807**: 編寫使用者文檔
- [ ] **T808**: 編寫開發者文檔
- [ ] **T809**: 編寫部署指南

#### Phase 9: 部署與監控 (4h)

- [ ] **T901**: 設置 Vercel 部署
- [ ] **T902**: 配置環境變數
- [ ] **T903**: 設置 CI/CD（GitHub Actions）
- [ ] **T904**: 整合 Sentry 錯誤監控
- [ ] **T905**: 整合 Google Analytics 或 Plausible
- [ ] **T906**: 配置 SEO（Meta 標籤、sitemap）
- [ ] **T907**: 執行最終測試和檢查
- [ ] **T908**: 正式發布

### 8.3 里程碑 (Milestones)

**M1: MVP 可用（Week 1）**
- 基本搜尋功能
- 標籤展示和工作區
- API 整合完成
- 桌面端可用

**M2: 功能完整（Week 2）**
- 智能推薦和驗證
- 分類瀏覽
- 主題和國際化
- 響應式設計

**M3: 生產就緒（Week 3）**
- PWA 支援
- 測試完成（≥80% 覆蓋率）
- 效能優化（Lighthouse ≥90）
- 文檔完整

**M4: 正式發布（Week 3 末）**
- 部署到生產環境
- 監控和分析配置
- 使用者文檔發布
- 宣傳和推廣

---

## 9. 測試策略 (Testing Strategy)

### 9.1 測試金字塔

```
    /\
   /E2E\      少量 E2E 測試（關鍵流程）
  /------\
 /Integration\  適量整合測試（組件交互）
/----------\
/Unit Tests\  大量單元測試（組件、函數）
/------------\
```

### 9.2 單元測試

**工具：** Jest + Testing Library

**覆蓋目標：** ≥ 80%

**測試內容：**
- 組件渲染
- 使用者交互（點擊、輸入）
- 條件渲染
- Props 傳遞
- 自定義 Hooks
- 工具函數

**範例測試案例：**

```typescript
// components/features/tag-search/__tests__/TagSearchInput.test.tsx
describe('TagSearchInput', () => {
  it('應該正確渲染搜尋框', () => {
    render(<TagSearchInput />);
    expect(screen.getByPlaceholderText(/搜尋標籤/i)).toBeInTheDocument();
  });

  it('應該在輸入時觸發搜尋', async () => {
    const onSearch = jest.fn();
    render(<TagSearchInput onSearch={onSearch} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'cute girl');
    
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('cute girl');
    });
  });

  it('應該顯示搜尋歷史', async () => {
    render(<TagSearchInput />);
    
    const input = screen.getByRole('textbox');
    await userEvent.click(input);
    
    expect(screen.getByText(/最近搜尋/i)).toBeInTheDocument();
  });
});
```

### 9.3 整合測試

**工具：** Testing Library

**測試內容：**
- 多組件協作
- API 請求流程
- 狀態管理
- 路由導航

**範例測試案例：**

```typescript
// tests/integration/search-flow.test.tsx
describe('搜尋流程', () => {
  it('應該完成完整的搜尋和添加流程', async () => {
    render(<App />);
    
    // 1. 輸入搜尋
    const input = screen.getByPlaceholderText(/搜尋標籤/i);
    await userEvent.type(input, 'cute girl');
    
    // 2. 等待結果
    await waitFor(() => {
      expect(screen.getByText('1girl')).toBeInTheDocument();
    });
    
    // 3. 添加標籤
    const addButton = screen.getByRole('button', { name: /添加 1girl/i });
    await userEvent.click(addButton);
    
    // 4. 驗證工作區
    expect(screen.getByText(/已選 \(1\)/i)).toBeInTheDocument();
    
    // 5. 驗證 Prompt 預覽
    expect(screen.getByText(/1girl/i)).toBeInTheDocument();
  });
});
```

### 9.4 E2E 測試

**工具：** Playwright

**覆蓋目標：** 5-10 個關鍵流程

**測試場景：**
- 首次訪問和搜尋
- 完整的標籤選擇流程
- Prompt 建立和複製
- 主題切換
- 語言切換
- 響應式測試（移動端）

**範例測試案例：**

```typescript
// tests/e2e/search-and-copy.spec.ts
import { test, expect } from '@playwright/test';

test('完整的搜尋和複製流程', async ({ page }) => {
  // 1. 訪問首頁
  await page.goto('http://localhost:3000');
  
  // 2. 輸入搜尋
  await page.fill('[data-testid="search-input"]', 'cute girl');
  
  // 3. 等待結果
  await page.waitForSelector('[data-testid="tag-card"]');
  
  // 4. 點擊第一個標籤
  await page.click('[data-testid="tag-card"]:first-child');
  
  // 5. 驗證工作區
  await expect(page.locator('[data-testid="workspace-tag"]')).toHaveCount(1);
  
  // 6. 點擊複製按鈕
  await page.click('[data-testid="copy-prompt-button"]');
  
  // 7. 驗證複製成功提示
  await expect(page.locator('[data-testid="toast"]')).toContainText('已複製');
});
```

### 9.5 無障礙測試

**工具：** axe-core + jest-axe

**標準：** WCAG 2.1 AA

**測試內容：**
- 鍵盤導航
- 螢幕閱讀器支援
- 顏色對比度
- ARIA 標籤

**範例測試案例：**

```typescript
// tests/a11y/search-page.test.tsx
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('搜尋頁面無障礙測試', () => {
  it('應該沒有無障礙違規', async () => {
    const { container } = render(<SearchPage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('應該支援鍵盤導航', async () => {
    render(<SearchPage />);
    
    const input = screen.getByRole('textbox');
    input.focus();
    
    // Tab 到第一個結果
    await userEvent.tab();
    
    const firstCard = screen.getAllByRole('button')[0];
    expect(firstCard).toHaveFocus();
    
    // Enter 選擇
    await userEvent.keyboard('{Enter}');
    
    expect(screen.getByText(/已添加/i)).toBeInTheDocument();
  });
});
```

### 9.6 效能測試

**工具：** Lighthouse CI + Custom Scripts

**測試內容：**
- Core Web Vitals
- Bundle 大小
- 請求數量和大小
- 渲染效能

**自動化測試：**

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: treosh/lighthouse-ci-action@v10
        with:
          urls: |
            http://localhost:3000
            http://localhost:3000/search
          temporaryPublicStorage: true
          runs: 3
```

---

## 10. 部署策略 (Deployment Strategy)

### 10.1 部署平台

**推薦：Vercel（與 API 同平台）**

**理由：**
- ✅ 零配置部署
- ✅ 自動 HTTPS
- ✅ 全球 CDN
- ✅ 預覽部署（PR）
- ✅ 邊緣函數支援
- ✅ 分析和監控
- ✅ 與 Next.js 完美整合

### 10.2 環境配置

#### 10.2.1 開發環境 (.env.local)

```bash
# API 配置
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000

# 功能開關
NEXT_PUBLIC_ENABLE_PWA=false
NEXT_PUBLIC_ENABLE_ANALYTICS=false

# 除錯
NEXT_PUBLIC_DEBUG=true
```

#### 10.2.2 生產環境 (Vercel 環境變數)

```bash
# API 配置
NEXT_PUBLIC_API_URL=https://prompt-scribe-api.vercel.app
NEXT_PUBLIC_API_TIMEOUT=30000

# 功能開關
NEXT_PUBLIC_ENABLE_PWA=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true

# 分析
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=https://...

# 除錯
NEXT_PUBLIC_DEBUG=false
```

### 10.3 部署流程

#### 10.3.1 手動部署

```bash
# 1. 安裝 Vercel CLI
npm i -g vercel

# 2. 登入
vercel login

# 3. 部署到預覽環境
vercel

# 4. 部署到生產環境
vercel --prod
```

#### 10.3.2 自動部署（CI/CD）

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests
        run: npm test
        
      - name: Build
        run: npm run build
        
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### 10.4 域名配置

**建議域名結構：**

```
生產環境：  prompt-scribe.vercel.app 或 自定義域名
預覽環境：  <branch>-prompt-scribe.vercel.app
本地環境：  localhost:3000
```

### 10.5 CDN 和快取策略

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Cache-Control', value: 'no-store' },
        ],
      },
      {
        source: '/_next/static/:path*',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
        ],
      },
      {
        source: '/images/:path*',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=86400' },
        ],
      },
    ];
  },
};
```

---

## 11. 監控與分析 (Monitoring & Analytics)

### 11.1 錯誤監控

**工具：Sentry**

**配置：**

```typescript
// lib/sentry.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  
  beforeSend(event, hint) {
    // 過濾敏感資訊
    if (event.request) {
      delete event.request.cookies;
      delete event.request.headers;
    }
    return event;
  },
});
```

**監控內容：**
- JavaScript 錯誤
- API 請求失敗
- 效能問題
- 使用者反饋

### 11.2 使用者分析

**工具：Plausible（隱私友好）或 Google Analytics**

**追蹤事件：**

```typescript
// lib/analytics.ts
export const trackEvent = (
  name: string,
  properties?: Record<string, any>
) => {
  if (typeof window.plausible !== 'undefined') {
    window.plausible(name, { props: properties });
  }
};

// 使用範例
trackEvent('tag_search', {
  query: 'cute girl',
  results_count: 8,
});

trackEvent('tag_add', {
  tag_name: '1girl',
  confidence: 0.95,
});

trackEvent('prompt_copy', {
  tags_count: 5,
  quality_score: 92,
});
```

**關鍵指標：**
- 頁面瀏覽量
- 使用者會話時長
- 搜尋次數
- 標籤添加次數
- Prompt 複製次數
- 轉換率（訪問 → 使用）

### 11.3 效能監控

**工具：Vercel Analytics + Web Vitals**

```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

**監控指標：**
- Core Web Vitals (LCP, FID, CLS)
- 頁面載入時間
- API 請求時間
- 資源大小

---

## 12. 安全性 (Security)

### 12.1 前端安全最佳實踐

**1. XSS 防護**
- 使用 React 的自動轉義
- 避免使用 `dangerouslySetInnerHTML`
- 驗證和清理使用者輸入

**2. CSRF 防護**
- API 使用 CORS 設定
- 不在前端存儲敏感資料

**3. 依賴安全**
- 定期更新依賴
- 使用 `npm audit` 檢查漏洞
- 鎖定依賴版本

**4. 內容安全策略 (CSP)**

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline' *.vercel-analytics.com;
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self' data:;
      connect-src 'self' ${process.env.NEXT_PUBLIC_API_URL};
    `.replace(/\s{2,}/g, ' ').trim()
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'Referrer-Policy',
    value: 'origin-when-cross-origin'
  },
];
```

### 12.2 資料隱私

**1. 本地存儲加密**

```typescript
// lib/storage.ts
import { AES, enc } from 'crypto-js';

const SECRET_KEY = 'your-secret-key';

export const secureStorage = {
  set(key: string, value: any) {
    const encrypted = AES.encrypt(
      JSON.stringify(value),
      SECRET_KEY
    ).toString();
    localStorage.setItem(key, encrypted);
  },
  
  get(key: string) {
    const encrypted = localStorage.getItem(key);
    if (!encrypted) return null;
    
    const decrypted = AES.decrypt(encrypted, SECRET_KEY).toString(enc.Utf8);
    return JSON.parse(decrypted);
  },
};
```

**2. 隱私政策**
- 明確告知資料收集
- 提供退出選項
- 匿名化分析資料

---

## 13. 無障礙設計 (Accessibility)

### 13.1 WCAG 2.1 AA 標準遵循

**關鍵要求：**

1. **可感知 (Perceivable)**
   - 文字替代：所有圖片提供 alt 文字
   - 時序媒體：影片提供字幕
   - 可調整：文字可縮放至 200%
   - 可辨識：對比度至少 4.5:1

2. **可操作 (Operable)**
   - 鍵盤存取：所有功能可用鍵盤操作
   - 充足時間：無自動超時
   - 癲癇症：避免閃爍內容
   - 導航：提供跳過連結、清晰標題

3. **可理解 (Understandable)**
   - 可讀：語言屬性設定正確
   - 可預測：一致的導航和功能
   - 輸入協助：錯誤訊息清晰、提供建議

4. **強健 (Robust)**
   - 相容性：使用語意化 HTML
   - 名稱、角色、值：正確的 ARIA 屬性

### 13.2 實作檢查清單

**HTML 結構：**
- [ ] 使用語意化標籤（`<nav>`, `<main>`, `<section>`）
- [ ] 正確的標題層級（h1-h6）
- [ ] 所有表單輸入有 `<label>`
- [ ] 按鈕使用 `<button>` 而非 `<div>`

**ARIA 屬性：**
- [ ] 互動元素有 `role` 屬性
- [ ] 動態內容使用 `aria-live`
- [ ] 展開/收合使用 `aria-expanded`
- [ ] 隱藏內容使用 `aria-hidden`

**鍵盤導航：**
- [ ] Tab 順序邏輯清晰
- [ ] 焦點指示器明顯可見
- [ ] Escape 關閉彈窗
- [ ] 方向鍵導航列表

**顏色和對比：**
- [ ] 文字對比度 ≥ 4.5:1
- [ ] 不僅依賴顏色傳達資訊
- [ ] 焦點指示器對比度 ≥ 3:1

**測試工具：**
- [ ] axe DevTools 檢查
- [ ] NVDA/JAWS 螢幕閱讀器測試
- [ ] 鍵盤導航測試
- [ ] Lighthouse 無障礙評分 ≥ 95

---

## 14. 國際化 (Internationalization)

### 14.1 支援語言

**Phase 1：**
- 繁體中文（zh-TW）- 預設
- 英文（en-US）

**Future：**
- 簡體中文（zh-CN）
- 日文（ja-JP）

### 14.2 實作方案

**工具：next-intl**

**配置：**

```typescript
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';

export default async function LocaleLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const messages = await getMessages();

  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      {children}
    </NextIntlClientProvider>
  );
}
```

**翻譯文件：**

```json
// messages/zh-TW.json
{
  "common": {
    "search": "搜尋",
    "loading": "載入中...",
    "error": "發生錯誤",
    "copy": "複製",
    "copied": "已複製"
  },
  "search": {
    "placeholder": "搜尋標籤或描述場景...",
    "no_results": "未找到相關標籤",
    "recent": "最近搜尋"
  },
  "workspace": {
    "title": "我的 Prompt",
    "empty": "尚未添加標籤",
    "clear": "清空",
    "quality_score": "品質評分"
  }
}
```

```json
// messages/en-US.json
{
  "common": {
    "search": "Search",
    "loading": "Loading...",
    "error": "An error occurred",
    "copy": "Copy",
    "copied": "Copied"
  },
  "search": {
    "placeholder": "Search tags or describe a scene...",
    "no_results": "No tags found",
    "recent": "Recent searches"
  },
  "workspace": {
    "title": "My Prompt",
    "empty": "No tags added yet",
    "clear": "Clear",
    "quality_score": "Quality Score"
  }
}
```

---

## 15. 驗收標準 (Acceptance Criteria)

### 15.1 必要驗收項目

**功能完整性：**
- [ ] 所有 15 個核心功能已實作
- [ ] 所有 8 個 API 端點已整合
- [ ] 5 個主要頁面已完成
- [ ] 所有組件已測試

**使用者體驗：**
- [ ] Lighthouse Performance ≥ 90
- [ ] Lighthouse Accessibility ≥ 95
- [ ] Lighthouse SEO ≥ 90
- [ ] Core Web Vitals 全綠
- [ ] 響應式設計完美適配（桌面、平板、手機）

**技術品質：**
- [ ] TypeScript 無錯誤（嚴格模式）
- [ ] ESLint 無警告
- [ ] 測試覆蓋率 ≥ 80%
- [ ] Bundle 大小 < 300 KB (gzipped)
- [ ] 無安全漏洞（npm audit）

**文檔完整性：**
- [ ] README 完整（安裝、使用、部署）
- [ ] 組件文檔（Storybook 或類似）
- [ ] API 整合文檔
- [ ] 部署指南

**部署就緒：**
- [ ] 成功部署到 Vercel
- [ ] 環境變數配置正確
- [ ] CI/CD 管線運作
- [ ] 錯誤監控配置（Sentry）
- [ ] 分析追蹤配置

### 15.2 選擇性驗收項目

- [ ] PWA 可安裝和離線使用
- [ ] 鍵盤快捷鍵完整
- [ ] 收藏功能可用
- [ ] 匯出/匯入功能可用
- [ ] 多語言完整翻譯
- [ ] Storybook 或組件文檔
- [ ] E2E 測試覆蓋關鍵流程

### 15.3 使用者驗收測試

**測試場景：**

1. **新手使用者首次訪問**
   - 能在 5 分鐘內完成第一次搜尋和複製
   - 介面直觀，無需說明文檔

2. **經驗使用者日常使用**
   - 搜尋流程順暢，無卡頓
   - 推薦結果準確，有用

3. **移動端使用者**
   - 手機上操作流暢
   - 觸控體驗良好

4. **無障礙使用者**
   - 螢幕閱讀器可用
   - 鍵盤導航完整

---

## 16. 風險假設與依賴 (Assumptions and Dependencies)

### 16.1 假設 (Assumptions)

- API 服務穩定可用（99.9% uptime）
- API 回應時間 < 2 秒
- 使用者瀏覽器支援現代 Web 標準（ES2020+）
- 使用者網路連線穩定（3G 以上）
- Vercel 部署平台持續可用

### 16.2 依賴 (Dependencies)

**前置依賴：**
- Prompt-Scribe API 已部署並可用
- API 端點穩定，不頻繁變動
- API 文檔完整且最新

**技術依賴：**
- Node.js 18+
- npm 或 pnpm
- 現代瀏覽器（Chrome 90+, Firefox 88+, Safari 14+, Edge 90+）

**第三方服務：**
- Vercel（部署）
- Sentry（錯誤監控，可選）
- Plausible 或 Google Analytics（分析，可選）

---

## 17. 未來擴展 (Future Enhancements)

### 17.1 V1.1（短期）

- 使用者帳號系統（登入、註冊）
- 雲端同步（收藏、歷史）
- 更多語言支援（簡中、日文）
- 高級篩選功能
- 標籤比較功能

### 17.2 V2.0（中期）

- 社群功能（分享 Prompt、評論）
- Prompt 模板庫
- 圖像預覽（整合圖像生成 API）
- 個人化推薦（機器學習）
- Chrome 擴充套件

### 17.3 V3.0（長期）

- 即時協作（多人編輯）
- Prompt 版本控制
- AI 助手（對話式建立 Prompt）
- 與主流 AI 工具整合（SD WebUI、ComfyUI）
- 付費進階功能

---

## 18. 變更記錄 (Change Log)

| 版本 | 日期 | 變更內容 | 作者 |
|------|------|----------|------|
| 1.0.0 | 2025-10-17 | 初始版本，完整前端規格 | AI Assistant |

---

## 19. 參考資料 (References)

### 19.1 內部文檔

- [Prompt-Scribe API 規格](../001-sqlite-ags-db/spec.md)
- [API 端點文檔](../001-sqlite-ags-db/contracts/api_endpoints_llm_optimized.yaml)
- [專案 README](../../README.md)
- [部署指南](../../DEPLOYMENT_GUIDE.md)

### 19.2 技術文檔

- [Next.js 14 文檔](https://nextjs.org/docs)
- [React 文檔](https://react.dev/)
- [Tailwind CSS 文檔](https://tailwindcss.com/docs)
- [shadcn/ui 文檔](https://ui.shadcn.com/)
- [TanStack Query 文檔](https://tanstack.com/query/latest)
- [Zustand 文檔](https://docs.pmnd.rs/zustand/getting-started/introduction)

### 19.3 設計資源

- [Material Design 指南](https://m3.material.io/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [WCAG 2.1 標準](https://www.w3.org/WAI/WCAG21/quickref/)
- [Web Vitals](https://web.dev/vitals/)

### 19.4 工具和服務

- [Vercel 文檔](https://vercel.com/docs)
- [Sentry 文檔](https://docs.sentry.io/)
- [Plausible 文檔](https://plausible.io/docs)
- [Playwright 文檔](https://playwright.dev/)

---

**規格結束 (End of Specification)**

---

## 附錄 A：技術決策記錄 (ADR)

### ADR-001: 選擇 Next.js 14 App Router

**日期：** 2025-10-17  
**狀態：** 接受

**背景：**
需要選擇前端框架來建立 Web 應用。

**決策：**
使用 Next.js 14 (App Router) 作為主框架。

**理由：**
1. 與 API 同平台（Vercel），部署最佳化
2. 內建 SSR/SSG，SEO 友好
3. React Server Components，效能優越
4. 豐富的生態系統
5. TypeScript 原生支援

**後果：**
- ✅ 優秀的開發體驗
- ✅ 自動優化和最佳實踐
- ⚠️ 學習曲線（App Router 較新）

---

### ADR-002: 選擇 shadcn/ui + Tailwind CSS

**日期：** 2025-10-17  
**狀態：** 接受

**背景：**
需要選擇 UI 框架來快速建立介面。

**決策：**
使用 shadcn/ui + Tailwind CSS。

**理由：**
1. 完全可自訂，無依賴鎖定
2. 現代設計風格
3. 優秀的無障礙支援
4. TypeScript 支援
5. 複製即用，靈活整合

**後果：**
- ✅ 完全控制 UI 組件
- ✅ 輕量級（無額外依賴）
- ⚠️ 需手動安裝組件

---

### ADR-003: 選擇 Zustand + React Query

**日期：** 2025-10-17  
**狀態：** 接受

**背景：**
需要狀態管理方案。

**決策：**
使用 Zustand 管理本地狀態，React Query 管理伺服器狀態。

**理由：**
1. Zustand 輕量且簡單
2. React Query 專業處理伺服器狀態
3. 減少樣板代碼
4. 優秀的 TypeScript 支援
5. 良好的開發工具

**後果：**
- ✅ 簡單易用
- ✅ 專業的快取管理
- ✅ 減少冗餘代碼

---

## 附錄 B：組件清單

### 核心組件（必需）

1. **TagSearchInput** - 搜尋輸入框
2. **TagCard** - 標籤卡片
3. **Workspace** - 工作區
4. **TagList** - 標籤列表
5. **PromptPreview** - Prompt 預覽
6. **ValidationPanel** - 驗證面板
7. **RecommendationPanel** - 推薦面板
8. **CategoryTree** - 分類樹
9. **TagDetailModal** - 標籤詳情彈窗
10. **Header** - 頁首
11. **Footer** - 頁尾
12. **ThemeToggle** - 主題切換
13. **LanguageSelector** - 語言選擇器
14. **LoadingSpinner** - 載入動畫
15. **ErrorBoundary** - 錯誤邊界

### UI 組件（shadcn/ui）

1. **Button**
2. **Input**
3. **Card**
4. **Badge**
5. **Dialog**
6. **Toast**
7. **Skeleton**
8. **Tooltip**
9. **Select**
10. **Tabs**
11. **Dropdown Menu**
12. **Scroll Area**

---

## 附錄 C：API 整合檢查清單

- [ ] `/api/llm/recommend-tags` - 標籤推薦
- [ ] `/api/llm/validate-prompt` - Prompt 驗證
- [ ] `/api/llm/suggest-combinations` - 組合建議
- [ ] `/api/v1/tags` - 標籤查詢
- [ ] `/api/v1/search` - 關鍵字搜尋
- [ ] `/api/v1/categories` - 分類統計
- [ ] `/health` - 健康檢查
- [ ] `/cache/stats` - 快取統計

---

## 附錄 D：效能優化檢查清單

**資源優化：**
- [ ] 圖片使用 Next.js Image 組件
- [ ] 字型使用 Next.js Font 優化
- [ ] CSS 最小化和提取關鍵 CSS
- [ ] JavaScript 分割和懶加載

**渲染優化：**
- [ ] 使用 React.memo 避免不必要的重渲染
- [ ] 虛擬化長列表（react-window）
- [ ] 防抖和節流輸入事件
- [ ] Suspense 和 Loading 狀態

**網路優化：**
- [ ] API 請求快取（React Query）
- [ ] 請求去重
- [ ] 預載入關鍵資源
- [ ] CDN 和邊緣快取

**Bundle 優化：**
- [ ] 代碼分割（動態導入）
- [ ] 樹搖優化（Tree Shaking）
- [ ] 移除未使用的依賴
- [ ] 壓縮和最小化

---

**完整規格文檔結束**

