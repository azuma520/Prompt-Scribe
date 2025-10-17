# 🎨 Tailwind 樣式指南 - Inspire 模塊

> **Prompt-Scribe Inspire 的完整樣式系統設計**

**版本**: 1.0.0  
**更新日期**: 2025-10-17

---

## 📋 目錄

1. [設計哲學](#設計哲學)
2. [Tailwind Config 結構](#tailwind-config-結構)
3. [語意 Token 系統](#語意-token-系統)
4. [樣式應用範例](#樣式應用範例)
5. [最佳實踐](#最佳實踐)

---

## 🎯 設計哲學

### 核心原則

**1. 語意優先 (Semantic-First)**
- 使用語意化的 Token 名稱，而非硬編 HEX 色碼
- `bg-card` 優於 `bg-white`
- `text-muted-foreground` 優於 `text-gray-500`

**2. 系統化管理 (Systematic)**
- 所有樣式皆以 Token 管理
- 顏色、字體、陰影、間距統一定義
- 成為「樣式層資料結構（Style Schema）」的一環

**3. 可維護性 (Maintainable)**
- 後期改主色或主題時不需修改組件
- 一處修改，全局生效
- 降低維護成本

**4. 擴展性 (Extensible)**
- 使用 `extend` 而非覆寫內建設定
- 讓升級 Tailwind 版本時不破壞結構
- 預留未來擴展空間

---

## 🧩 Tailwind Config 結構

### 完整配置文件

```typescript
// tailwind.config.ts

import type { Config } from "tailwindcss"
import { fontFamily } from "tailwindcss/defaultTheme"

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      // ========================================
      // 色彩系統 (Color System)
      // ========================================
      colors: {
        // 品牌色（Inspire 專用）
        inspire: {
          DEFAULT: "#4CC9F0",     // 主色：夢幻藍
          light: "#90E0EF",       // 淺藍
          dark: "#3A0CA3",        // 深紫藍
          accent: "#F72585",      // 強調色：粉紅
          muted: "#CDB4DB",       // 柔和色：淡紫
        },
        
        // 基礎色（shadcn 標準）
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        
        // 組件色
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      
      // ========================================
      // 字體系統 (Typography)
      // ========================================
      fontFamily: {
        sans: ["Inter", "Noto Sans TC", ...fontFamily.sans],
        mono: ["JetBrains Mono", "Consolas", ...fontFamily.mono],
        display: ["Outfit", ...fontFamily.sans],  // 用於標題
      },
      
      fontSize: {
        'display-1': ['4rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'display-2': ['3rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        'heading-1': ['2.5rem', { lineHeight: '1.2' }],
        'heading-2': ['2rem', { lineHeight: '1.3' }],
        'heading-3': ['1.5rem', { lineHeight: '1.4' }],
        'body-large': ['1.125rem', { lineHeight: '1.6' }],
        'body': ['1rem', { lineHeight: '1.6' }],
        'body-small': ['0.875rem', { lineHeight: '1.5' }],
        'caption': ['0.75rem', { lineHeight: '1.4' }],
      },
      
      // ========================================
      // 間距系統 (Spacing)
      // ========================================
      spacing: {
        '18': '4.5rem',   // 72px
        '88': '22rem',    // 352px
        '128': '32rem',   // 512px
      },
      
      // ========================================
      // 陰影系統 (Shadows)
      // ========================================
      boxShadow: {
        'card': '0 2px 10px rgba(0, 0, 0, 0.08)',
        'card-hover': '0 8px 30px rgba(76, 201, 240, 0.3)',
        'card-selected': '0 0 0 3px rgba(76, 201, 240, 0.5)',
        'glow': '0 0 20px rgba(76, 201, 240, 0.6)',
        'glow-strong': '0 0 30px rgba(76, 201, 240, 0.8)',
        'inner-glow': 'inset 0 0 20px rgba(76, 201, 240, 0.2)',
      },
      
      // ========================================
      // 圓角系統 (Border Radius)
      // ========================================
      borderRadius: {
        'card': '1rem',      // 16px
        'button': '0.5rem',  // 8px
        'input': '0.5rem',   // 8px
        'xl': '1.5rem',      // 24px
        '2xl': '2rem',       // 32px
      },
      
      // ========================================
      // 漸層系統 (Gradients)
      // ========================================
      backgroundImage: {
        'inspire-gradient': 'linear-gradient(135deg, #4CC9F0 0%, #3A0CA3 100%)',
        'inspire-gradient-reverse': 'linear-gradient(135deg, #3A0CA3 0%, #4CC9F0 100%)',
        'card-gradient': 'linear-gradient(180deg, #FFFFFF 0%, #F8F9FA 100%)',
        'card-gradient-dark': 'linear-gradient(180deg, #18181B 0%, #27272A 100%)',
        'shimmer': 'linear-gradient(90deg, transparent, rgba(76, 201, 240, 0.3), transparent)',
        'glow-radial': 'radial-gradient(circle, rgba(76, 201, 240, 0.3) 0%, transparent 70%)',
      },
      
      // ========================================
      // 動畫系統 (Animations)
      // ========================================
      animation: {
        // 基礎動畫
        'fade-in': 'fadeIn 0.6s ease-in-out',
        'fade-out': 'fadeOut 0.6s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-down': 'slideDown 0.4s ease-out',
        'slide-left': 'slideLeft 0.4s ease-out',
        'slide-right': 'slideRight 0.4s ease-out',
        
        // Inspire 專用動畫
        'float-slow': 'float 6s ease-in-out infinite',
        'float-fast': 'float 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'typing': 'typing 2s steps(40, end)',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite',
        
        // 互動動畫
        'scale-in': 'scaleIn 0.3s ease-out',
        'scale-out': 'scaleOut 0.3s ease-in',
        'bounce-subtle': 'bounceSubtle 1s ease-in-out',
      },
      
      keyframes: {
        // 淡入淡出
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        fadeOut: {
          from: { opacity: '1' },
          to: { opacity: '0' },
        },
        
        // 滑動
        slideUp: {
          from: {
            opacity: '0',
            transform: 'translateY(20px)',
          },
          to: {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        slideDown: {
          from: {
            opacity: '0',
            transform: 'translateY(-20px)',
          },
          to: {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        slideLeft: {
          from: {
            opacity: '0',
            transform: 'translateX(20px)',
          },
          to: {
            opacity: '1',
            transform: 'translateX(0)',
          },
        },
        slideRight: {
          from: {
            opacity: '0',
            transform: 'translateX(-20px)',
          },
          to: {
            opacity: '1',
            transform: 'translateX(0)',
          },
        },
        
        // 浮動
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        
        // 閃爍載入
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        
        // 打字效果
        typing: {
          from: { width: '0' },
          to: { width: '100%' },
        },
        
        // 發光效果
        glow: {
          '0%, 100%': { 
            boxShadow: '0 0 20px rgba(76, 201, 240, 0.4)',
          },
          '50%': { 
            boxShadow: '0 0 30px rgba(76, 201, 240, 0.8)',
          },
        },
        
        // 縮放
        scaleIn: {
          from: {
            opacity: '0',
            transform: 'scale(0.95)',
          },
          to: {
            opacity: '1',
            transform: 'scale(1)',
          },
        },
        scaleOut: {
          from: {
            opacity: '1',
            transform: 'scale(1)',
          },
          to: {
            opacity: '0',
            transform: 'scale(0.95)',
          },
        },
        
        // 柔和彈跳
        bounceSubtle: {
          '0%, 100%': {
            transform: 'translateY(0)',
          },
          '50%': {
            transform: 'translateY(-4px)',
          },
        },
      },
      
      // ========================================
      // 其他擴展
      // ========================================
      
      // 斷點擴展
      screens: {
        'xs': '475px',
        '3xl': '1920px',
      },
      
      // 容器擴展
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',
          sm: '2rem',
          lg: '4rem',
          xl: '5rem',
          '2xl': '6rem',
        },
        screens: {
          sm: '640px',
          md: '768px',
          lg: '1024px',
          xl: '1280px',
          '2xl': '1400px',
        },
      },
      
      // Z-index 系統
      zIndex: {
        'modal': '1000',
        'dropdown': '900',
        'header': '800',
        'toast': '1100',
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/forms"),
    require("tailwindcss-animate"),
  ],
} satisfies Config

export default config
```

---

## 🎨 語意 Token 系統

### Token 分類與用途

#### 主色系 (Brand Colors)

| Token | HEX | 用途 | 範例 |
|-------|-----|------|------|
| `inspire` | #4CC9F0 | 主按鈕、連結、強調元素 | CTA 按鈕、選中狀態 |
| `inspire-light` | #90E0EF | 淺色背景、hover 狀態 | 按鈕 hover、標籤背景 |
| `inspire-dark` | #3A0CA3 | 深色文字、邊框 | 標題、重要文字 |
| `inspire-accent` | #F72585 | 強調、警示、互動 | 通知、特殊標記 |
| `inspire-muted` | #CDB4DB | 柔和背景、禁用狀態 | 禁用按鈕、輔助背景 |

**使用範例：**
```tsx
<button className="bg-inspire hover:bg-inspire-light text-white">
  生成靈感卡
</button>
```

#### 卡片系統 (Card System)

| Token | 淺色模式 | 深色模式 | 用途 |
|-------|---------|---------|------|
| `bg-card` | #FFFFFF | #18181B | 卡片背景 |
| `border-border` | #E4E4E7 | #333333 | 卡片邊框 |
| `shadow-card` | 見陰影系統 | - | 卡片陰影 |

**使用範例：**
```tsx
<div className="bg-card border border-border rounded-card shadow-card">
  {/* 卡片內容 */}
</div>
```

#### 文字系統 (Text System)

| Token | 用途 | 範例 |
|-------|------|------|
| `text-foreground` | 主要文字 | 標題、正文 |
| `text-muted-foreground` | 次要文字 | 說明、輔助資訊 |
| `text-inspire` | 品牌色文字 | 強調文字、連結 |
| `text-inspire-dark` | 深色品牌文字 | 重要標題 |

**使用範例：**
```tsx
<h2 className="text-heading-2 text-inspire-dark font-bold">
  靈感卡片
</h2>
<p className="text-body text-muted-foreground">
  選擇一張你最喜歡的卡片
</p>
```

---

## 📐 globals.css 結構

### 完整樣式定義

```css
/* globals.css */

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ==========================================
   CSS 變數定義 (Light Mode)
   ========================================== */
:root {
  /* 圓角 */
  --radius: 0.5rem;
  
  /* 基礎色彩（HSL 格式） */
  --background: 0 0% 100%;
  --foreground: 0 0% 9%;
  
  --card: 0 0% 100%;
  --card-foreground: 0 0% 9%;
  
  --popover: 0 0% 100%;
  --popover-foreground: 0 0% 9%;
  
  --primary: 262 83% 58%;
  --primary-foreground: 0 0% 100%;
  
  --secondary: 0 0% 96%;
  --secondary-foreground: 0 0% 9%;
  
  --muted: 0 0% 96%;
  --muted-foreground: 0 0% 45%;
  
  --accent: 0 0% 96%;
  --accent-foreground: 0 0% 9%;
  
  --destructive: 0 84% 60%;
  --destructive-foreground: 0 0% 98%;
  
  --border: 0 0% 90%;
  --input: 0 0% 90%;
  --ring: 262 83% 58%;
}

/* ==========================================
   CSS 變數定義 (Dark Mode)
   ========================================== */
.dark {
  --background: 0 0% 9%;
  --foreground: 0 0% 98%;
  
  --card: 0 0% 12%;
  --card-foreground: 0 0% 98%;
  
  --popover: 0 0% 12%;
  --popover-foreground: 0 0% 98%;
  
  --primary: 262 83% 65%;
  --primary-foreground: 0 0% 9%;
  
  --secondary: 0 0% 15%;
  --secondary-foreground: 0 0% 98%;
  
  --muted: 0 0% 15%;
  --muted-foreground: 0 0% 65%;
  
  --accent: 0 0% 15%;
  --accent-foreground: 0 0% 98%;
  
  --destructive: 0 62% 30%;
  --destructive-foreground: 0 0% 98%;
  
  --border: 0 0% 20%;
  --input: 0 0% 20%;
  --ring: 262 83% 65%;
}

/* ==========================================
   全局樣式
   ========================================== */
html {
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  @apply bg-background text-foreground antialiased;
  font-feature-settings: 'cv11', 'ss01';
}

/* ==========================================
   自定義組件樣式
   ========================================== */

/* 靈感卡片基礎樣式 */
.inspire-card {
  @apply bg-card border border-border shadow-card rounded-2xl p-6;
  @apply transition-all duration-300 ease-out;
  @apply hover:shadow-card-hover hover:scale-105;
}

.inspire-card.selected {
  @apply shadow-card-selected border-inspire;
}

/* 輸入框樣式 */
.inspire-input {
  @apply bg-background border border-input rounded-lg px-4 py-3;
  @apply text-foreground placeholder:text-muted-foreground;
  @apply focus:outline-none focus:ring-2 focus:ring-inspire focus:border-inspire;
  @apply transition-all duration-200;
}

/* 按鈕樣式 */
.inspire-button-primary {
  @apply bg-inspire hover:bg-inspire-dark text-white;
  @apply px-6 py-3 rounded-button font-medium;
  @apply transition-all duration-200;
  @apply hover:shadow-glow;
}

.inspire-button-secondary {
  @apply bg-secondary hover:bg-secondary/80 text-secondary-foreground;
  @apply px-6 py-3 rounded-button font-medium;
  @apply transition-all duration-200;
}

/* 載入動畫 */
.shimmer-effect {
  @apply bg-muted relative overflow-hidden;
}

.shimmer-effect::after {
  content: '';
  @apply absolute inset-0 bg-shimmer;
  animation: shimmer 2s linear infinite;
}

/* 打字效果 */
.typing-effect {
  @apply overflow-hidden whitespace-nowrap;
  border-right: 2px solid;
  animation: typing 2s steps(40, end), blink 0.75s step-end infinite;
}

@keyframes blink {
  from, to { border-color: transparent; }
  50% { border-color: currentColor; }
}

/* 浮動效果 */
.float-element {
  @apply animate-float-slow;
}

/* 發光效果 */
.glow-element {
  @apply animate-glow;
}

/* ==========================================
   響應式輔助類
   ========================================== */

/* 移動端優化 */
@screen sm {
  .inspire-card {
    @apply p-8;
  }
}

/* 桌面端優化 */
@screen lg {
  .inspire-card {
    @apply p-10;
  }
}

/* ==========================================
   無障礙樣式
   ========================================== */

/* 鍵盤聚焦指示器 */
*:focus-visible {
  @apply outline-none ring-2 ring-inspire ring-offset-2 ring-offset-background;
}

/* 高對比度模式支援 */
@media (prefers-contrast: high) {
  .inspire-card {
    @apply border-2;
  }
}

/* 減少動畫（尊重用戶偏好） */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* ==========================================
   列印樣式
   ========================================== */
@media print {
  .inspire-card {
    @apply shadow-none border border-gray-300;
  }
  
  .no-print {
    @apply hidden;
  }
}
```

---

## 🎯 樣式應用範例

### 範例 1: 靈感卡片

```tsx
// components/inspire/InspirationCard.tsx

export function InspirationCard({ 
  card, 
  selected, 
  onSelect 
}: InspirationCardProps) {
  return (
    <div 
      className={cn(
        "inspire-card cursor-pointer",
        selected && "selected",
        "group"  // 用於 hover 效果
      )}
      onClick={onSelect}
    >
      {/* 主標題 */}
      <h3 className="text-heading-3 text-inspire-dark font-bold mb-2 
                     group-hover:text-inspire transition-colors">
        {card.subject}
      </h3>
      
      {/* 場景描述 */}
      <p className="text-body text-muted-foreground mb-4">
        {card.scene}
      </p>
      
      {/* 標籤列表 */}
      <div className="flex flex-wrap gap-2 mb-4">
        {card.source_tags.map((tag) => (
          <span 
            key={tag}
            className="bg-inspire-light/20 text-inspire-dark 
                       px-3 py-1 rounded-full text-body-small
                       border border-inspire/30"
          >
            {tag}
          </span>
        ))}
      </div>
      
      {/* 信心度 */}
      {card.confidence_score && (
        <div className="flex items-center gap-2">
          <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className="h-full bg-inspire transition-all duration-500"
              style={{ width: `${card.confidence_score * 100}%` }}
            />
          </div>
          <span className="text-caption text-muted-foreground">
            {Math.round(card.confidence_score * 100)}%
          </span>
        </div>
      )}
    </div>
  );
}
```

### 範例 2: 輸入框

```tsx
// components/inspire/InputBox.tsx

export function InputBox({ onSubmit, loading }: InputBoxProps) {
  return (
    <div className="relative w-full max-w-3xl mx-auto">
      <textarea
        className="inspire-input w-full min-h-[120px] resize-none"
        placeholder="描述你想要的感覺或主題..."
        disabled={loading}
      />
      
      <button
        className="inspire-button-primary absolute bottom-4 right-4
                   disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={onSubmit}
        disabled={loading}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="animate-spin">⏳</span>
            生成中...
          </span>
        ) : (
          '生成靈感卡 ✨'
        )}
      </button>
    </div>
  );
}
```

### 範例 3: 載入動畫

```tsx
// components/inspire/Loader.tsx

export function Loader() {
  return (
    <div className="flex flex-col items-center justify-center p-12">
      {/* Shimmer 效果 */}
      <div className="w-full max-w-md space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="shimmer-effect h-48 rounded-2xl" />
        ))}
      </div>
      
      {/* 文字提示（打字效果） */}
      <p className="mt-8 text-inspire-dark typing-effect">
        正在為您生成靈感卡...
      </p>
      
      {/* 浮動圖標 */}
      <div className="mt-4 text-4xl float-element">
        ✨
      </div>
    </div>
  );
}
```

### 範例 4: 結果面板

```tsx
// components/inspire/ResultPanel.tsx

export function ResultPanel({ card }: ResultPanelProps) {
  const prompt = buildPromptFromCard(card);
  
  return (
    <div className="bg-card border border-border rounded-2xl p-6 
                    animate-slide-up">
      {/* 標題 */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-heading-3 text-inspire-dark font-bold">
          📋 最終結果
        </h3>
        <button className="inspire-button-secondary">
          新增一組
        </button>
      </div>
      
      {/* JSON 輸出 */}
      <div className="bg-muted rounded-lg p-4 mb-4 font-mono text-body-small
                      max-h-64 overflow-auto">
        <pre className="text-foreground">
          {JSON.stringify(card, null, 2)}
        </pre>
      </div>
      
      {/* Prompt 輸出 */}
      <div className="bg-inspire-light/10 border border-inspire/30 
                      rounded-lg p-4 mb-4">
        <p className="text-body text-foreground whitespace-pre-wrap">
          {prompt}
        </p>
      </div>
      
      {/* 操作按鈕 */}
      <div className="flex gap-3">
        <button className="inspire-button-primary flex-1">
          <span className="mr-2">📋</span>
          複製 JSON
        </button>
        <button className="inspire-button-primary flex-1">
          <span className="mr-2">✨</span>
          複製 Prompt
        </button>
        <button className="inspire-button-secondary">
          💾 儲存
        </button>
      </div>
    </div>
  );
}
```

---

## ✅ 最佳實踐

### DO ✅

1. **使用語意 Token**
   ```tsx
   // 好 ✅
   <div className="bg-card border-border text-foreground">
   
   // 不好 ❌
   <div className="bg-white border-gray-200 text-gray-900">
   ```

2. **組合基礎 Utility Classes**
   ```tsx
   // 好 ✅
   <div className="inspire-card">  {/* 預定義的組合 */}
   
   // 可以，但較冗長
   <div className="bg-card border border-border shadow-card rounded-2xl p-6">
   ```

3. **響應式設計**
   ```tsx
   // 好 ✅
   <div className="p-4 sm:p-6 lg:p-8">
   
   // 好 ✅（移動端優先）
   <div className="text-base lg:text-lg">
   ```

4. **狀態變化**
   ```tsx
   // 好 ✅
   <button className="bg-inspire hover:bg-inspire-dark 
                      disabled:opacity-50 disabled:cursor-not-allowed
                      transition-all duration-200">
   ```

5. **使用 cn() 工具函數**
   ```tsx
   import { cn } from '@/lib/utils';
   
   // 好 ✅
   <div className={cn(
     "inspire-card",
     selected && "selected",
     loading && "opacity-50"
   )}>
   ```

### DON'T ❌

1. **硬編色碼**
   ```tsx
   // 不好 ❌
   <div style={{ backgroundColor: '#4CC9F0' }}>
   
   // 好 ✅
   <div className="bg-inspire">
   ```

2. **內聯樣式（除非必要）**
   ```tsx
   // 不好 ❌
   <div style={{ padding: '24px', borderRadius: '16px' }}>
   
   // 好 ✅
   <div className="p-6 rounded-2xl">
   ```

3. **過度嵌套**
   ```tsx
   // 不好 ❌
   <div className="flex items-center justify-center w-full h-full">
     <div className="flex flex-col items-center justify-center">
       <div className="flex items-center gap-2">
   
   // 好 ✅ - 簡化結構
   <div className="flex flex-col items-center justify-center gap-2 w-full h-full">
   ```

4. **忽略深色模式**
   ```tsx
   // 不好 ❌
   <div className="bg-white text-black">
   
   // 好 ✅
   <div className="bg-card text-foreground">
   ```

---

## 🎨 設計 Token 速查表

### 快速參考

#### 背景色
```
bg-background      # 頁面背景
bg-card            # 卡片背景
bg-muted           # 次要背景
bg-inspire         # 品牌色背景
bg-inspire-light   # 淺品牌色背景
```

#### 文字色
```
text-foreground           # 主要文字
text-muted-foreground     # 次要文字
text-inspire              # 品牌色文字
text-inspire-dark         # 深品牌色文字
```

#### 邊框
```
border-border      # 標準邊框
border-inspire     # 品牌色邊框
border-input       # 輸入框邊框
```

#### 陰影
```
shadow-card             # 卡片陰影
shadow-card-hover       # 卡片 hover 陰影
shadow-card-selected    # 選中卡片陰影
shadow-glow             # 發光陰影
```

#### 圓角
```
rounded-card       # 卡片圓角（1rem）
rounded-button     # 按鈕圓角（0.5rem）
rounded-input      # 輸入框圓角（0.5rem）
```

#### 動畫
```
animate-fade-in         # 淡入
animate-slide-up        # 向上滑入
animate-float-slow      # 緩慢浮動
animate-shimmer         # 閃爍載入
animate-typing          # 打字效果
animate-glow            # 發光效果
```

---

## 📝 維護建議

### 新增 Token 時

1. **評估是否真的需要**
   - 是否能重用現有 Token？
   - 是否符合設計系統？

2. **遵循命名規範**
   - 使用語意化名稱
   - 保持命名一致性

3. **同時定義淺色和深色模式**
   - 確保兩種模式都可用
   - 測試對比度

4. **更新本文檔**
   - 記錄新 Token 的用途
   - 提供使用範例

### 修改 Token 時

1. **評估影響範圍**
   - 搜尋所有使用該 Token 的組件
   - 確保修改不會破壞現有樣式

2. **測試所有場景**
   - 淺色/深色模式
   - 不同斷點
   - 各種狀態（hover, focus, disabled）

3. **文檔同步更新**
   - 更新本指南
   - 更新組件文檔

---

## 🔄 版本管理

### 變更記錄

| 版本 | 日期 | 變更內容 |
|------|------|----------|
| 1.0.0 | 2025-10-17 | 初始版本，完整樣式系統 |

---

## 📞 支援

如有任何樣式相關問題：
- 查看本指南
- 參考 shadcn/ui 文檔
- 參考 Tailwind CSS 文檔
- 提交 Issue

---

**Tailwind 樣式指南完成 - 讓樣式成為系統化資料的一部分！** 🎨

**維護者**: Prompt-Scribe Team  
**最後更新**: 2025-10-17

