# 🎨 Prompt-Scribe Web Frontend

> **AI 標籤推薦系統 - 現代化 Web 介面（含 Inspire 靈感生成）**

## 🚀 快速開始

### 本地開發

```bash
# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev

# 訪問應用
# http://localhost:3000
```

### 建置

```bash
# 建置生產版本
npm run build

# 啟動生產伺服器
npm run start
```

## ✨ 已實作功能（MVP）

### Phase 0: 基礎設置 ✅
- [x] Next.js 14 專案初始化
- [x] TypeScript 嚴格模式
- [x] Tailwind CSS 配置
- [x] shadcn/ui 組件庫（21 個組件）
- [x] React Query 狀態管理
- [x] 環境變數配置

### Phase 3: Inspire 靈感功能 ✅
- [x] 輸入框組件（InputBox）
- [x] 靈感卡片組件（InspirationCard）
- [x] 卡片容器（InspirationCards）
- [x] 結果面板（ResultPanel）
- [x] 載入動畫（Loader）
- [x] 完整頁面（/inspire）

## 🎯 功能演示

### Inspire 使用流程

1. 訪問 http://localhost:3000
2. 點擊「Inspire 靈感」卡片
3. 輸入描述：「孤獨又夢幻的感覺」
4. 等待 AI 生成 3 張靈感卡
5. 選擇喜歡的卡片
6. 查看 JSON/Prompt 格式
7. 一鍵複製使用

## 🏗️ 技術棧

- **框架**: Next.js 15
- **語言**: TypeScript
- **樣式**: Tailwind CSS
- **UI**: shadcn/ui
- **狀態**: Zustand + React Query
- **動畫**: Framer Motion

## 📁 專案結構

```
src/
├── app/
│   ├── layout.tsx          # 根佈局
│   ├── page.tsx            # 首頁
│   ├── providers.tsx       # React Query Provider
│   └── inspire/            # Inspire 功能
│       ├── page.tsx
│       └── components/
│           ├── InputBox.tsx
│           ├── InspirationCard.tsx
│           ├── InspirationCards.tsx
│           ├── ResultPanel.tsx
│           └── Loader.tsx
├── components/
│   ├── ui/                 # shadcn/ui 組件（21 個）
│   └── shared/             # 共用組件
├── lib/
│   ├── api/                # API 客戶端
│   ├── hooks/              # 自定義 Hooks
│   └── utils/              # 工具函數
└── types/                  # TypeScript 型別
```

## 🔌 API 整合

### 現有 API（複用）

- ✅ `POST /api/llm/recommend-tags` - 標籤推薦
- ✅ API URL: https://prompt-scribe-api.zeabur.app (Zeabur 部署)
- ✅ 備用 URL: https://prompt-scribe-api.vercel.app (Vercel 部署)

### 環境變數

```bash
# .env.local
NEXT_PUBLIC_API_URL=https://prompt-scribe-api.zeabur.app
NEXT_PUBLIC_API_TIMEOUT=30000
```

**設置步驟**:
```bash
# 1. 複製範例檔案
cp .env.example .env.local

# 2. 如需修改，編輯 .env.local
# （預設已指向 Zeabur 生產環境）
```

## 🧪 測試

```bash
# 執行測試（待實作）
npm test

# 類型檢查
npm run type-check
```

## 📊 開發進度

```
✅ Phase 0: 專案設置（完成）
✅ Phase 3: Inspire MVP（完成）
🚧 Phase 1: 標籤搜尋（規劃中）
🚧 Phase 2: 工作區（規劃中）
🚧 Phase 4-10: 其他功能（規劃中）
```

## 📝 開發指南

詳細規格和文檔請參考：
- 完整規格: `../specs/002-web-frontend/spec.md`
- 任務清單: `../specs/002-web-frontend/current/tasks.md`
- 快速開始: `../specs/002-web-frontend/current/QUICKSTART.md`
- MCP 指南: `../specs/002-web-frontend/MCP_USAGE_GUIDE.md`

## 🚀 部署

```bash
# 部署到 Vercel
vercel --prod
```

## 📞 支援

- 文檔: `../specs/002-web-frontend/`
- API 文檔: https://prompt-scribe-api.vercel.app/docs
- GitHub: https://github.com/azuma520/Prompt-Scribe

---

**Made with ❤️ by Prompt-Scribe Team**
