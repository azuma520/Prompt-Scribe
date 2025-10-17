# 🚀 Prompt-Scribe Web Frontend - 快速開始指南

> **5 分鐘快速設置開發環境並開始開發**

---

## 📋 前置需求

### 必需工具

- ✅ **Node.js** 18+ ([下載](https://nodejs.org/))
- ✅ **npm** 或 **pnpm** (推薦 pnpm)
- ✅ **Git** ([下載](https://git-scm.com/))
- ✅ **VS Code** 或其他編輯器 (推薦 VS Code)

### VS Code 推薦擴充套件

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "PKief.material-icon-theme",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

---

## 🎯 步驟 1: 專案初始化（10 分鐘）

### 1.1 創建 Next.js 專案

```bash
# 在專案根目錄執行
npx create-next-app@latest prompt-scribe-web \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"

cd prompt-scribe-web
```

**安裝選項**:
- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes
- `src/` directory: Yes
- App Router: Yes
- Import alias: Yes (@/*)

### 1.2 安裝核心依賴

```bash
# UI 組件庫
npx shadcn-ui@latest init

# 狀態管理
npm install zustand
npm install @tanstack/react-query

# 動畫
npm install framer-motion

# 表單處理
npm install react-hook-form zod @hookform/resolvers

# 國際化
npm install next-intl

# 工具庫
npm install clsx tailwind-merge
npm install date-fns
npm install lodash-es
npm install @types/lodash-es --save-dev
```

### 1.3 安裝開發工具

```bash
# 測試工具
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm install --save-dev @playwright/test

# 代碼品質
npm install --save-dev prettier eslint-config-prettier
npm install --save-dev @typescript-eslint/eslint-plugin

# Git hooks
npm install --save-dev husky lint-staged
npx husky install
```

---

## ⚙️ 步驟 2: 專案配置（5 分鐘）

### 2.1 環境變數設置

創建 `.env.local` 文件：

```bash
# API 配置
NEXT_PUBLIC_API_URL=https://prompt-scribe-api.vercel.app
NEXT_PUBLIC_API_TIMEOUT=30000

# 功能開關
NEXT_PUBLIC_ENABLE_PWA=false
NEXT_PUBLIC_ENABLE_ANALYTICS=false

# 除錯模式
NEXT_PUBLIC_DEBUG=true
```

創建 `.env.example` 作為範本：

```bash
cp .env.local .env.example
```

### 2.2 TypeScript 配置

更新 `tsconfig.json`：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 2.3 Tailwind 配置

更新 `tailwind.config.ts`：

```typescript
import type { Config } from "tailwindcss"

const config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        // ... 其他顏色
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config
```

### 2.4 ESLint 配置

更新 `.eslintrc.json`：

```json
{
  "extends": [
    "next/core-web-vitals",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "warn",
    "@typescript-eslint/no-explicit-any": "warn",
    "react/no-unescaped-entities": "off"
  }
}
```

### 2.5 Prettier 配置

創建 `.prettierrc`：

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "tabWidth": 2,
  "useTabs": false,
  "printWidth": 80,
  "arrowParens": "avoid"
}
```

---

## 📁 步驟 3: 目錄結構（5 分鐘）

### 3.1 創建基礎目錄

```bash
cd src

# 創建目錄結構
mkdir -p app/{search,browse,workspace}
mkdir -p components/{ui,features,layouts,shared}
mkdir -p components/features/{tag-search,tag-card,workspace,recommendation,validation}
mkdir -p lib/{api,hooks,store,utils,constants}
mkdir -p types
mkdir -p styles
mkdir -p tests/{unit,integration,e2e}
mkdir -p locales

cd ..
```

### 3.2 目錄說明

```
src/
├── app/                  # Next.js App Router
│   ├── layout.tsx       # 根佈局
│   ├── page.tsx         # 首頁
│   ├── search/          # 搜尋頁面
│   ├── browse/          # 分類瀏覽
│   └── workspace/       # 工作區
│
├── components/          # React 組件
│   ├── ui/             # shadcn/ui 基礎組件
│   ├── features/       # 功能組件
│   ├── layouts/        # 佈局組件
│   └── shared/         # 共用組件
│
├── lib/                # 工具和配置
│   ├── api/           # API 客戶端
│   ├── hooks/         # 自定義 Hooks
│   ├── store/         # Zustand stores
│   ├── utils/         # 工具函數
│   └── constants/     # 常數定義
│
├── types/             # TypeScript 型別
├── styles/            # 全局樣式
├── tests/             # 測試文件
└── locales/           # 國際化
```

---

## 🔧 步驟 4: 基礎配置文件（5 分鐘）

### 4.1 API 客戶端設置

創建 `src/lib/api/client.ts`：

```typescript
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

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 
  'https://prompt-scribe-api.vercel.app';
```

### 4.2 API 端點定義

創建 `src/lib/api/endpoints.ts`：

```typescript
import { API_BASE_URL } from './client';

export const apiEndpoints = {
  // 標籤推薦
  recommendTags: () => `${API_BASE_URL}/api/llm/recommend-tags`,
  
  // 標籤搜尋
  searchTags: () => `${API_BASE_URL}/api/v1/search`,
  
  // 驗證 Prompt
  validatePrompt: () => `${API_BASE_URL}/api/llm/validate-prompt`,
  
  // 智能組合建議
  suggestCombinations: () => 
    `${API_BASE_URL}/api/llm/suggest-combinations`,
  
  // 標籤詳情
  getTag: (name: string) => 
    `${API_BASE_URL}/api/v1/tags?name=${encodeURIComponent(name)}`,
  
  // 分類統計
  getCategories: () => `${API_BASE_URL}/api/v1/categories`,
  
  // 健康檢查
  health: () => `${API_BASE_URL}/health`,
};
```

### 4.3 TypeScript 型別定義

創建 `src/types/api.ts`：

```typescript
export interface Tag {
  id: string;
  name: string;
  danbooru_cat: number;
  post_count: number;
  main_category: string | null;
  sub_category: string | null;
  confidence: number | null;
  classification_source: string | null;
}

export interface RecommendTagsRequest {
  description: string;
  top_k?: number;
}

export interface RecommendTagsResponse {
  recommended_tags: Array<{
    tag: string;
    confidence: number;
    category?: string;
  }>;
  description: string;
  execution_time: number;
}

export interface ValidationResult {
  overall_score: number;
  issues: string[];
  suggestions: string[];
  conflict_tags?: string[][];
  redundant_tags?: string[];
}

export interface TagCombination {
  theme: string;
  basic: string;
  extended: string;
  popularity: string;
}
```

### 4.4 工具函數

創建 `src/lib/utils.ts`：

```typescript
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}
```

---

## 🎨 步驟 5: 安裝 shadcn/ui 組件（5 分鐘）

### 5.1 初始化 shadcn/ui

```bash
npx shadcn-ui@latest init
```

選擇以下選項：
- Style: Default
- Base color: Slate
- CSS variables: Yes

### 5.2 安裝常用組件

```bash
# 基礎組件
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add tooltip
npx shadcn-ui@latest add select
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add scroll-area
```

---

## 🚀 步驟 6: 創建第一個組件（10 分鐘）

### 6.1 根佈局

更新 `src/app/layout.tsx`：

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/api/client';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Prompt-Scribe - AI 標籤推薦系統',
  description: '智能 AI 圖像生成標籤推薦工具',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-TW">
      <body className={inter.className}>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </body>
    </html>
  );
}
```

### 6.2 首頁

更新 `src/app/page.tsx`：

```typescript
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-secondary/20">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold tracking-tight mb-4">
            🎨 Prompt-Scribe
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            AI 標籤推薦系統
          </p>
          
          <div className="relative max-w-2xl mx-auto">
            <Input
              type="text"
              placeholder="搜尋標籤或描述場景..."
              className="h-14 text-lg px-6"
            />
            <Button
              className="absolute right-2 top-2"
              size="lg"
            >
              搜尋
            </Button>
          </div>

          <div className="mt-12 grid grid-cols-3 gap-4">
            <Button variant="outline" size="lg" className="h-20">
              🔍 關鍵字搜尋
            </Button>
            <Button variant="outline" size="lg" className="h-20">
              📊 分類瀏覽
            </Button>
            <Button variant="outline" size="lg" className="h-20">
              📋 工作區
            </Button>
          </div>
        </div>
      </div>
    </main>
  );
}
```

---

## ✅ 步驟 7: 驗證設置（2 分鐘）

### 7.1 啟動開發伺服器

```bash
npm run dev
```

訪問 http://localhost:3000

### 7.2 檢查清單

- [ ] 頁面正常載入
- [ ] Tailwind CSS 樣式生效
- [ ] 組件正確渲染
- [ ] 無控制台錯誤
- [ ] TypeScript 無錯誤
- [ ] ESLint 無錯誤

### 7.3 測試 API 連接

創建測試頁面 `src/app/api-test/page.tsx`：

```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { apiEndpoints } from '@/lib/api/endpoints';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function APITest() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await fetch(apiEndpoints.health());
      return response.json();
    },
    enabled: false,
  });

  return (
    <div className="container mx-auto p-8">
      <Card className="p-6">
        <h1 className="text-2xl font-bold mb-4">API 連接測試</h1>
        
        <Button onClick={() => refetch()}>
          測試 API 連接
        </Button>

        {isLoading && <p className="mt-4">載入中...</p>}
        {error && (
          <p className="mt-4 text-red-500">
            錯誤: {error.message}
          </p>
        )}
        {data && (
          <pre className="mt-4 p-4 bg-muted rounded">
            {JSON.stringify(data, null, 2)}
          </pre>
        )}
      </Card>
    </div>
  );
}
```

訪問 http://localhost:3000/api-test 測試 API 連接。

---

## 📝 步驟 8: Git 設置（3 分鐘）

### 8.1 初始化 Git

```bash
git init
git add .
git commit -m "chore: initial project setup"
```

### 8.2 設置 Git Hooks

創建 `.husky/pre-commit`：

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

更新 `package.json` 添加 lint-staged：

```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md}": [
      "prettier --write"
    ]
  }
}
```

### 8.3 創建 .gitignore

確保 `.gitignore` 包含：

```
# Dependencies
/node_modules
/.pnp
.pnp.js

# Testing
/coverage

# Next.js
/.next/
/out/

# Production
/build

# Misc
.DS_Store
*.pem

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local env files
.env*.local
.env

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts
```

---

## 🎉 完成！

### ✅ 你已經完成

- ✅ Next.js 專案初始化
- ✅ 核心依賴安裝
- ✅ 專案配置完成
- ✅ 目錄結構建立
- ✅ 基礎組件設置
- ✅ API 整合配置
- ✅ Git 工作流設置

### 🚀 下一步

1. **閱讀完整規格**: 查看 [spec.md](../spec.md)
2. **查看任務清單**: 查看 [tasks.md](tasks.md)（待建立）
3. **開始開發**: 從 Phase 1 任務開始

### 📚 推薦閱讀

- [Next.js 文檔](https://nextjs.org/docs)
- [shadcn/ui 文檔](https://ui.shadcn.com/)
- [TanStack Query 文檔](https://tanstack.com/query/latest)
- [Tailwind CSS 文檔](https://tailwindcss.com/docs)

---

## 🆘 常見問題

### Q1: npm install 失敗

```bash
# 清除快取
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Q2: TypeScript 錯誤

```bash
# 重新生成型別
npx next build
```

### Q3: 端口被占用

```bash
# 更換端口
npm run dev -- -p 3001
```

### Q4: API 連接失敗

檢查 `.env.local` 中的 `NEXT_PUBLIC_API_URL` 是否正確設置。

---

## 💡 實用命令

```bash
# 開發
npm run dev          # 啟動開發伺服器
npm run build        # 建置生產版本
npm run start        # 啟動生產伺服器
npm run lint         # 執行 ESLint
npm run type-check   # TypeScript 類型檢查

# 測試
npm test            # 執行單元測試
npm run test:e2e    # 執行 E2E 測試

# 格式化
npm run format      # 格式化代碼（Prettier）
```

---

**準備好開始開發了！** 🎊

有任何問題請參考 [spec.md](../spec.md) 或提交 Issue。

