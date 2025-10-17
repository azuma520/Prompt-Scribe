# 🎨 Prompt-Scribe Web Frontend

> **現代化、直觀的 AI 標籤推薦系統前端介面**

[![Status](https://img.shields.io/badge/status-planning-yellow.svg)](spec.md)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![Framework](https://img.shields.io/badge/framework-Next.js_14-black.svg)](https://nextjs.org/)
[![UI](https://img.shields.io/badge/ui-shadcn%2Fui-violet.svg)](https://ui.shadcn.com/)
[![TypeScript](https://img.shields.io/badge/language-TypeScript-blue.svg)](https://www.typescriptlang.org/)

---

## 🎯 專案概述

Prompt-Scribe Web Frontend 是一個為 AI 圖像創作者設計的現代化 Web 應用，提供智能標籤搜尋、推薦和 Prompt 建立功能。

### 核心特色

- ✨ **智能推薦** - 基於描述自動推薦相關標籤
- 🎨 **視覺化工作區** - 拖拽排序，即時預覽
- ✅ **品質驗證** - 自動檢測衝突和冗餘標籤
- 💡 **智能組合** - 10+ 預定義組合模式
- 🌓 **深色模式** - 舒適的視覺體驗
- 🌐 **多語言** - 繁體中文、英文
- 📱 **響應式** - 完美支援所有裝置
- ♿ **無障礙** - WCAG 2.1 AA 標準

---

## 📸 介面預覽

> 注意：以下為設計概念，實際介面以實作為準

### 首頁 (Home Page)

```
┌─────────────────────────────────────┐
│  🎨 Prompt-Scribe                  │
│  AI 標籤推薦系統                    │
│                                     │
│  [       搜尋標籤或描述場景      ]  │
│                                     │
│  🔥 熱門標籤                        │
│  [1girl] [solo] [long_hair] ...   │
│                                     │
│  📊 分類瀏覽                        │
│  [角色] [服裝] [場景] [風格] ...  │
└─────────────────────────────────────┘
```

### 搜尋結果 (Search Results)

```
┌─────────────────────────────────────┐
│  🎯 推薦標籤     │   📋 工作區       │
│  [1girl] 95%    │   已選 (3)        │
│  [solo] 90%     │   [1girl]         │
│  [cute] 88%     │   [solo]          │
│                 │   [cute]          │
│                 │   預覽：          │
│                 │   1girl, solo,... │
│                 │   [複製] [驗證]   │
└─────────────────────────────────────┘
```

---

## 🚀 快速開始

### 方式 1: 查看線上 Demo（未來）

```bash
# 訪問線上版本（開發中）
# https://prompt-scribe-web.vercel.app
```

### 方式 2: 本地開發（未來）

```bash
# 1. 克隆專案
git clone https://github.com/azuma520/Prompt-Scribe.git
cd Prompt-Scribe/prompt-scribe-web

# 2. 安裝依賴
npm install

# 3. 配置環境變數
cp .env.example .env.local
# 編輯 .env.local 設置 API URL

# 4. 啟動開發伺服器
npm run dev

# 5. 訪問應用
# http://localhost:3000
```

---

## 📚 文檔導航

### 🌟 **新手推薦閱讀路徑**

1. **本檔案（README.md）** - 了解專案概況 ⏱ 5 分鐘
2. **[spec.md](spec.md)** - 閱讀完整功能規格 ⏱ 60 分鐘
3. **[QUICKSTART.md](current/QUICKSTART.md)** - 快速開始開發 ⏱ 10 分鐘

### 📖 完整文檔清單

| 文檔 | 說明 | 狀態 |
|------|------|------|
| [INDEX.md](INDEX.md) | 文檔索引和導覽 | ✅ 完成 |
| [spec.md](spec.md) | 完整功能規格（19 章節） | ✅ 完成 |
| [current/plan.md](current/plan.md) | 詳細開發計畫 | 🚧 待建立 |
| [current/tasks.md](current/tasks.md) | 80+ 任務清單 | 🚧 待建立 |
| [current/research.md](current/research.md) | 技術研究和決策 | 🚧 待建立 |
| [contracts/design-system.md](contracts/design-system.md) | 設計系統 | 🚧 待建立 |
| [contracts/components.md](contracts/components.md) | 組件規格 | 🚧 待建立 |

---

## 🏗️ 技術棧

### 核心框架

- **Next.js 14** - React 框架（App Router）
- **TypeScript** - 類型安全
- **Tailwind CSS** - 樣式框架
- **shadcn/ui** - UI 組件庫

### 狀態管理

- **Zustand** - 本地狀態管理
- **TanStack Query** - 伺服器狀態管理

### 其他工具

- **Framer Motion** - 動畫庫
- **next-intl** - 國際化
- **React Hook Form** - 表單管理
- **Zod** - 資料驗證

### 開發工具

- **ESLint** - 代碼檢查
- **Prettier** - 代碼格式化
- **Jest** - 單元測試
- **Playwright** - E2E 測試
- **Storybook** - 組件文檔（可選）
- **shadcn MCP** - AI 輔助組件開發（推薦）⚡

---

## 📊 專案狀態

### 當前階段

🚧 **Phase 0: 規劃完成，準備開發**

- [x] 完整規格文檔（80+ 頁）
- [x] 技術棧選擇和評估
- [x] 目錄結構設計
- [x] API 整合規劃
- [ ] 專案初始化
- [ ] 開發環境設置

### 開發進度

```
Phase 0: 規劃        ████████████████████ 100%
Phase 1: 核心搜尋    ░░░░░░░░░░░░░░░░░░░░   0%
Phase 2: 工作區      ░░░░░░░░░░░░░░░░░░░░   0%
Phase 3: 智能推薦    ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4-9: 其他      ░░░░░░░░░░░░░░░░░░░░   0%

總進度:              ██░░░░░░░░░░░░░░░░░░  10%
```

### 預估時程

| 階段 | 時間 | 狀態 |
|------|------|------|
| Phase 0: 專案設置 | 4h | ✅ 規劃完成 |
| Phase 1: 核心搜尋 | 16h | 🚧 準備中 |
| Phase 2: 工作區 | 20h | ⏳ 待開始 |
| Phase 3: 智能推薦 | 16h | ⏳ 待開始 |
| Phase 4-9: 其他 | 56h | ⏳ 待開始 |
| **總計** | **112h (2-3 週)** | **10%** |

---

## 🎯 核心功能

### 1. 智能搜尋

- 關鍵字搜尋
- 描述式搜尋（"cute girl in school uniform"）
- 即時搜尋結果
- 搜尋歷史

### 2. 標籤管理

- 視覺化標籤卡片
- 拖拽排序
- 批量操作
- 標籤收藏

### 3. 工作區

- Prompt 建立和編輯
- 即時預覽
- 品質評分
- 一鍵複製

### 4. 智能推薦

- 基於描述推薦
- 相關標籤推薦
- 完整組合建議
- 優化建議

### 5. 驗證功能

- 衝突檢測
- 冗餘檢測
- 品質評分
- 改進建議

### 6. 分類瀏覽

- 樹狀分類結構
- 熱門標籤
- 統計資訊
- 視覺化圖表

---

## 🎨 設計原則

### 1. 簡潔優先 (Simplicity First)

清晰的視覺層次，減少認知負擔

### 2. 響應即時 (Instant Feedback)

即時搜尋結果，操作反饋動畫

### 3. 引導式體驗 (Guided Experience)

新手教學提示，智能建議

### 4. 無障礙設計 (Accessibility)

WCAG 2.1 AA 標準，鍵盤導航

### 5. 視覺美學 (Visual Aesthetics)

現代設計風格，流暢動畫

---

## 📈 效能目標

### Core Web Vitals

| 指標 | 目標值 | 現況 |
|------|--------|------|
| LCP (最大內容繪製) | < 2.5s | 🚧 待測試 |
| FID (首次輸入延遲) | < 100ms | 🚧 待測試 |
| CLS (累積佈局偏移) | < 0.1 | 🚧 待測試 |

### Lighthouse 評分

| 類別 | 目標 | 現況 |
|------|------|------|
| Performance | ≥ 90 | 🚧 待測試 |
| Accessibility | ≥ 95 | 🚧 待測試 |
| Best Practices | ≥ 90 | 🚧 待測試 |
| SEO | ≥ 90 | 🚧 待測試 |

### 其他指標

- 首次載入 < 3 秒
- Bundle 大小 < 300 KB (gzipped)
- 測試覆蓋率 ≥ 80%

---

## 🛠️ API 整合

### 整合的 API 端點

| 端點 | 用途 | 狀態 |
|------|------|------|
| `/api/llm/recommend-tags` | 標籤推薦 | ✅ 已規劃 |
| `/api/llm/validate-prompt` | Prompt 驗證 | ✅ 已規劃 |
| `/api/llm/suggest-combinations` | 組合建議 | ✅ 已規劃 |
| `/api/v1/tags` | 標籤查詢 | ✅ 已規劃 |
| `/api/v1/search` | 關鍵字搜尋 | ✅ 已規劃 |
| `/api/v1/categories` | 分類統計 | ✅ 已規劃 |
| `/health` | 健康檢查 | ✅ 已規劃 |
| `/cache/stats` | 快取統計 | ✅ 已規劃 |

### API 配置

```typescript
// lib/api/config.ts
export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 
    'https://prompt-scribe-api.vercel.app',
  timeout: 30000,
  retries: 3,
};
```

---

## 🧪 測試策略

### 測試金字塔

```
    /\
   /E2E\      5-10 個關鍵流程
  /------\
 /Integration\  適量整合測試
/----------\
/Unit Tests\  大量單元測試
/------------\
```

### 測試覆蓋率目標

- **總體**: ≥ 80%
- **組件**: ≥ 85%
- **Hooks**: ≥ 90%
- **工具函數**: ≥ 95%

---

## 🚀 部署

### 推薦平台

**Vercel**（與 API 同平台）

**優勢**:
- ✅ 零配置部署
- ✅ 自動 HTTPS
- ✅ 全球 CDN
- ✅ 預覽部署
- ✅ 分析和監控

### 環境

```
開發環境:  http://localhost:3000
預覽環境:  <branch>-prompt-scribe-web.vercel.app
生產環境:  prompt-scribe-web.vercel.app
```

---

## 📝 開發指南

### 代碼風格

- 遵循 ESLint 配置
- 使用 Prettier 格式化
- TypeScript 嚴格模式
- 組件使用 PascalCase
- 檔案使用 kebab-case

### Git 工作流

```bash
# 1. 創建功能分支
git checkout -b feature/tag-search

# 2. 提交變更
git add .
git commit -m "feat: implement tag search component"

# 3. 推送並創建 PR
git push origin feature/tag-search
```

### 提交訊息規範

```
feat: 新功能
fix: 修復 bug
docs: 文檔更新
style: 代碼格式（不影響功能）
refactor: 重構
test: 測試相關
chore: 其他變更
```

---

## 🤝 貢獻指南

我們歡迎貢獻！請遵循以下步驟：

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 推送到分支
5. 開啟 Pull Request

### 貢獻前檢查清單

- [ ] 閱讀 [spec.md](spec.md) 了解規格
- [ ] 遵循代碼風格指南
- [ ] 添加相應的測試
- [ ] 更新相關文檔
- [ ] 確保所有測試通過
- [ ] 檢查無 lint 錯誤

---

## 📞 支援與聯繫

### 文檔資源

- **完整規格**: [spec.md](spec.md)
- **文檔索引**: [INDEX.md](INDEX.md)
- **快速開始**: [QUICKSTART.md](current/QUICKSTART.md)

### 技術支援

- **GitHub Issues**: [提交問題](https://github.com/azuma520/Prompt-Scribe/issues)
- **GitHub Discussions**: [社群討論](https://github.com/azuma520/Prompt-Scribe/discussions)

---

## 📜 授權

本專案採用 MIT 授權 - 查看 [LICENSE](../../LICENSE) 文件了解詳情

---

## 🙏 致謝

- [Next.js](https://nextjs.org/) - 優秀的 React 框架
- [shadcn/ui](https://ui.shadcn.com/) - 美觀的 UI 組件
- [Tailwind CSS](https://tailwindcss.com/) - 強大的樣式框架
- [Vercel](https://vercel.com/) - 卓越的部署平台
- [Prompt-Scribe API](https://prompt-scribe-api.vercel.app) - 強大的後端支援

---

## 🎉 狀態總結

**規劃階段已完成！**

- ✅ 完整的功能規格（80+ 頁）
- ✅ 詳細的技術選型和評估
- ✅ 清晰的開發計畫（9 個階段，80+ 任務）
- ✅ 完善的文檔結構
- 🚧 準備開始開發

**下一步**: 初始化 Next.js 專案，開始 Phase 1 開發！

---

<div align="center">

**⭐ 如果這個專案對你有幫助，請給我們一顆星！**

Made with ❤️ by Prompt-Scribe Team

[🏠 專案主頁](https://github.com/azuma520/Prompt-Scribe) • [📖 API 文檔](https://prompt-scribe-api.vercel.app/docs) • [🚀 開始使用](current/QUICKSTART.md)

</div>

