# ⚡ shadcn MCP 使用指南

> **使用 AI 助手加速 shadcn/ui 組件開發**

**文檔版本**: 1.0.0  
**更新日期**: 2025-10-17  
**適用專案**: Prompt-Scribe Web Frontend

---

## 📋 目錄

1. [什麼是 shadcn MCP](#什麼是-shadcn-mcp)
2. [基本使用](#基本使用)
3. [常見場景](#常見場景)
4. [最佳實踐](#最佳實踐)
5. [開發流程優化](#開發流程優化)
6. [故障排除](#故障排除)
7. [實戰範例](#實戰範例)

---

## 🎯 什麼是 shadcn MCP

### 簡介

**shadcn MCP (Model Context Protocol)** 是一個讓 AI 助手能夠直接操作 shadcn/ui 組件的工具。它可以：

- 🎨 **自動安裝組件** - 無需手動執行 CLI 命令
- 📦 **批量處理** - 一次安裝多個組件
- 🔧 **自動配置** - 處理依賴和導入
- 💡 **生成範例** - 提供使用示範代碼
- ✨ **智能組合** - 創建複雜的組合組件

### 核心優勢

| 傳統方式 | MCP 方式 | 節省時間 |
|---------|---------|---------|
| 逐一安裝組件（1-2分鐘/個） | 批量安裝（10秒） | **90%** ⚡ |
| 查閱文檔（5-10分鐘） | 自動生成範例 | **80%** ⚡ |
| 手動撰寫代碼（20-30分鐘） | AI 生成骨架（5分鐘） | **75%** ⚡ |
| 調整和除錯（10-15分鐘） | 微調即可（3-5分鐘） | **60%** ⚡ |

**總體開發效率提升：30-50%** 🚀

---

## 🚀 基本使用

### 1. 安裝單個組件

**提示語（Prompt）：**
```
請使用 shadcn MCP 安裝 button 組件
```

**MCP 會自動：**
- ✅ 執行 `npx shadcn-ui@latest add button`
- ✅ 安裝到 `components/ui/button.tsx`
- ✅ 處理所有依賴
- ✅ 提供使用範例

### 2. 批量安裝組件

**提示語：**
```
請使用 shadcn MCP 安裝以下組件：
button, input, card, badge, dialog, toast
```

**MCP 會自動：**
- ✅ 批量安裝所有組件
- ✅ 優化安裝順序（處理依賴關係）
- ✅ 提供每個組件的使用範例

### 3. 安裝並獲取使用範例

**提示語：**
```
請用 shadcn MCP 安裝 dialog 組件，並給我一個使用範例
```

**預期回應：**
- 組件安裝完成確認
- 完整的使用範例代碼
- 主要屬性說明
- 常見用法提示

### 4. 查詢可用組件

**提示語：**
```
請列出 shadcn MCP 支援的所有組件
```

---

## 📚 常見場景

### 場景 1: 專案初始化

**任務**: 設置新專案，安裝所有基礎組件

**提示語：**
```
請使用 shadcn MCP 為 Prompt-Scribe 專案安裝所有需要的基礎組件：

基礎互動：button, input, textarea, checkbox, radio-group
佈局容器：card, dialog, sheet, tabs, separator
反饋提示：toast, alert, skeleton, progress, spinner
導航選擇：dropdown-menu, select, combobox, command
進階功能：popover, tooltip, scroll-area, accordion

請批量安裝並確認。
```

**預期時間**: 1-2 分鐘（vs 傳統 15-20 分鐘）⚡

### 場景 2: 創建搜尋介面

**任務**: 實作帶下拉建議的搜尋框

**提示語：**
```
請用 shadcn MCP 幫我創建一個智能搜尋組件：

需求：
1. 安裝 command, popover, input 組件
2. 創建 TagSearchInput 組件
3. 功能：
   - 即時搜尋建議
   - 鍵盤導航（↑↓ Enter）
   - 搜尋歷史
   - 載入狀態

請生成完整的 TypeScript 代碼。
```

**預期回應：**
- 組件安裝確認
- 完整的 `TagSearchInput.tsx` 代碼
- Props 介面定義
- 使用範例

**預期時間**: 5-10 分鐘（vs 傳統 30-45 分鐘）⚡

### 場景 3: 創建表單驗證

**任務**: 實作帶驗證的表單

**提示語：**
```
用 shadcn MCP 創建一個表單組件：

需求：
1. 安裝 form, input, button, label 組件
2. 整合 react-hook-form 和 zod
3. 包含：
   - 輸入驗證
   - 錯誤提示
   - 提交按鈕
   - 載入狀態

請提供完整範例。
```

### 場景 4: 創建標籤卡片

**任務**: 實作標籤展示卡片

**提示語：**
```
請用 shadcn MCP 創建 TagCard 組件：

需求：
1. 安裝 card, badge, button, tooltip 組件
2. 顯示：
   - 標籤名稱
   - 分類（使用 Badge）
   - 使用次數
   - 添加按鈕（使用 Tooltip）
3. 支援 hover 動畫
4. TypeScript 類型完整

請生成代碼。
```

### 場景 5: 創建工作區面板

**任務**: 實作可拖拽的標籤工作區

**提示語：**
```
用 shadcn MCP 創建 Workspace 組件：

需求：
1. 安裝 card, button, scroll-area, separator, progress 組件
2. 功能：
   - 顯示已選標籤列表
   - 支援拖拽排序（整合 @dnd-kit/core）
   - Prompt 預覽
   - 品質評分（Progress）
   - 清空和複製按鈕
3. 響應式設計

請提供完整實作。
```

---

## 💡 最佳實踐

### DO ✅ - 應該做

#### 1. 明確描述需求

**好的提示語：**
```
用 shadcn MCP 創建標籤搜尋組件：
- 使用 Command 組件
- 支援即時搜尋
- 顯示分類標籤
- 鍵盤導航
- TypeScript 類型完整
```

**為什麼好：**
- 明確列出所有需求
- 指定使用的組件
- 包含技術要求
- 清晰且可執行

#### 2. 分階段請求

**階段 1: 安裝組件**
```
請用 shadcn MCP 安裝 dialog, button, input 組件
```

**階段 2: 生成骨架**
```
基於已安裝的組件，創建 ConfirmDialog 組件骨架
```

**階段 3: 完善功能**
```
為 ConfirmDialog 添加：
- 取消和確認按鈕
- 自定義標題和內容
- 載入狀態
```

#### 3. 請求完整類型定義

**好的提示語：**
```
創建 TagCard 組件，包含：
1. Props 介面（TypeScript）
2. 組件實作
3. 使用範例
4. 導出語句
```

#### 4. 請求使用範例

**好的提示語：**
```
安裝 dropdown-menu 組件後，
提供 3 個實際使用範例：
1. 基礎下拉選單
2. 帶圖標的選單
3. 帶子選單的複雜選單
```

#### 5. 批量處理相關組件

**好的提示語：**
```
為搜尋功能安裝所有需要的組件：
command, popover, input, badge, separator
並提供整合範例
```

### DON'T ❌ - 不應該做

#### 1. 過於簡略的請求

**不好的提示語：**
```
安裝 button
```

**為什麼不好：**
- 缺少上下文
- 沒有說明用途
- 可能需要多次來回

**改進版：**
```
用 shadcn MCP 安裝 button 組件，
用於 TagCard 的添加按鈕，
需要 primary 和 outline 兩種變體的範例
```

#### 2. 一次請求過多複雜功能

**不好的提示語：**
```
創建完整的標籤管理系統，包含搜尋、篩選、分類、
工作區、驗證、推薦、歷史記錄和設定頁面
```

**為什麼不好：**
- 範圍過大
- 難以一次完成
- 容易出錯

**改進版（分階段）：**
```
階段 1: 創建標籤搜尋組件
階段 2: 創建工作區管理組件
階段 3: 整合驗證功能
...
```

#### 3. 沒有指定 TypeScript

**不好的提示語：**
```
創建一個卡片組件
```

**改進版：**
```
用 shadcn MCP 創建 TagCard 組件：
- TypeScript 類型完整
- Props 介面定義
- 組件導出類型
```

#### 4. 忽略專案上下文

**不好的提示語：**
```
創建一個表單
```

**改進版：**
```
為 Prompt-Scribe 專案創建標籤搜尋表單：
- 符合專案設計風格
- 整合現有的 API 客戶端
- 使用專案的類型定義
```

---

## 🔄 開發流程優化

### 傳統開發流程

```
1. 查閱 shadcn/ui 文檔         (5 分鐘)
   ↓
2. 手動執行安裝命令            (2 分鐘)
   ↓
3. 查看組件 API 文檔           (5 分鐘)
   ↓
4. 編寫組件代碼                (20 分鐘)
   ↓
5. 調整樣式和邏輯              (10 分鐘)
   ↓
6. 測試和除錯                  (10 分鐘)
   ↓
總計: 52 分鐘
```

### MCP 優化流程

```
1. 描述需求給 AI               (2 分鐘)
   ↓
2. MCP 自動安裝組件            (30 秒)
   ↓
3. MCP 生成組件骨架            (30 秒)
   ↓
4. 審查和微調代碼              (5 分鐘)
   ↓
5. 整合到專案                  (3 分鐘)
   ↓
6. 測試和驗證                  (5 分鐘)
   ↓
總計: 16 分鐘 ⚡ (節省 69% 時間)
```

### Phase-by-Phase 時間節省

| 階段 | 傳統時間 | MCP 時間 | 節省 |
|------|---------|---------|------|
| **Phase 1: 核心搜尋** | 16h | 11h | 31% ⚡ |
| **Phase 2: 工作區** | 20h | 14h | 30% ⚡ |
| **Phase 3: 智能推薦** | 16h | 11h | 31% ⚡ |
| **Phase 4: 分類瀏覽** | 12h | 8h | 33% ⚡ |
| **Phase 5: 主題語言** | 8h | 6h | 25% ⚡ |
| **Phase 6: 響應優化** | 12h | 9h | 25% ⚡ |
| **Phase 7: PWA 進階** | 8h | 6h | 25% ⚡ |
| **總計** | **112h** | **80h** | **29%** |

**從 2-3 週縮短到 2 週！** 🎉

---

## 🛠️ 故障排除

### 問題 1: MCP 找不到組件

**症狀：**
```
錯誤: 組件 'xxx' 不存在於 shadcn/ui
```

**解決方案：**
1. 確認組件名稱正確（使用 kebab-case）
2. 檢查 shadcn/ui 版本
3. 查看可用組件列表：
   ```
   請列出所有 shadcn MCP 支援的組件
   ```

### 問題 2: 組件安裝失敗

**症狀：**
```
安裝失敗，依賴問題
```

**解決方案：**
1. 確認 Next.js 和 Tailwind 已正確配置
2. 檢查 `components.json` 是否存在
3. 手動初始化：
   ```bash
   npx shadcn-ui@latest init
   ```
4. 重試 MCP 安裝

### 問題 3: 生成的代碼有錯誤

**症狀：**
- TypeScript 報錯
- 導入路徑錯誤
- 樣式不正確

**解決方案：**
1. **明確指定專案配置：**
   ```
   為 Prompt-Scribe 專案創建組件，
   使用 @/ 作為導入別名，
   遵循專案的 TypeScript 配置
   ```

2. **請求修正：**
   ```
   上面的組件有 TypeScript 錯誤，
   請修正導入路徑和類型定義
   ```

3. **提供更多上下文：**
   ```
   專案使用以下配置：
   - Next.js 14 App Router
   - TypeScript 5.0+
   - Tailwind CSS 3.4+
   請重新生成組件
   ```

### 問題 4: 組件樣式不符合預期

**症狀：**
- 顏色不對
- 間距不對
- 動畫不對

**解決方案：**
```
請調整 TagCard 組件的樣式：
- 使用 primary 主色（紫色）
- 卡片間距 p-4
- hover 時提升 4px
- 添加平滑過渡動畫
```

### 問題 5: MCP 回應太慢

**症狀：**
等待時間過長

**解決方案：**
1. **分解請求：**
   ```
   # 不好：一次要求所有
   創建完整的搜尋系統
   
   # 好：分步驟
   步驟 1: 安裝 command, input 組件
   步驟 2: 創建搜尋框組件
   步驟 3: 添加搜尋建議功能
   ```

2. **優先安裝組件：**
   ```
   先用 MCP 安裝所有需要的組件，
   然後再逐一創建功能組件
   ```

---

## 💻 實戰範例

### 範例 1: 標籤搜尋輸入框

**完整提示語：**
```
請用 shadcn MCP 為 Prompt-Scribe 創建 TagSearchInput 組件：

技術棧：
- Next.js 14 (App Router)
- TypeScript
- shadcn/ui + Tailwind CSS

需求：
1. 安裝需要的組件：command, popover, input, badge, scroll-area

2. 組件功能：
   - 即時搜尋建議
   - 顯示標籤名稱和分類（Badge）
   - 鍵盤導航（↑↓ Enter Esc）
   - 搜尋歷史（最近 5 條）
   - 載入狀態
   - 空狀態提示

3. Props 介面：
   ```typescript
   interface TagSearchInputProps {
     onTagSelect: (tag: Tag) => void;
     placeholder?: string;
     autoFocus?: boolean;
     className?: string;
   }
   ```

4. API 整合：
   使用 React Query 調用 /api/llm/recommend-tags

5. 樣式要求：
   - 使用 primary 主色
   - 圓角 md
   - 陰影 sm
   - hover 時提升

請生成完整的 TypeScript 代碼，
包含：
- TagSearchInput.tsx
- 使用範例
- 類型定義
```

**預期回應結構：**
1. 組件安裝確認
2. 完整組件代碼
3. Props 介面定義
4. React Query Hook
5. 使用範例
6. 樣式說明

### 範例 2: 標籤卡片組件

**完整提示語：**
```
用 shadcn MCP 創建 TagCard 組件：

安裝組件：
card, badge, button, tooltip

組件結構：
```
<Card>
  <CardHeader>
    <CardTitle>{tag.name}</CardTitle>
    <Badge>{tag.category}</Badge>
  </CardHeader>
  <CardContent>
    <p>使用次數: {tag.post_count}</p>
    <p>信心度: {tag.confidence}%</p>
  </CardContent>
  <CardFooter>
    <Tooltip content="添加到工作區">
      <Button onClick={onAdd}>
        <PlusIcon />
      </Button>
    </Tooltip>
  </CardFooter>
</Card>
```

Props：
```typescript
interface TagCardProps {
  tag: Tag;
  onAdd?: (tag: Tag) => void;
  onViewDetails?: (tag: Tag) => void;
  variant?: 'compact' | 'detailed';
  className?: string;
}
```

樣式：
- hover 時提升 4px
- 過渡動畫 200ms
- 陰影 hover:shadow-lg
- 響應式（mobile 優化）

請生成完整代碼。
```

### 範例 3: 工作區面板

**完整提示語：**
```
用 shadcn MCP 創建 Workspace 組件：

需要的組件：
card, button, scroll-area, separator, progress, badge, toast

功能需求：
1. 已選標籤列表
   - 支援拖拽排序（使用 @dnd-kit/core）
   - 每個標籤可刪除
   - 顯示標籤分類（Badge）

2. Prompt 預覽
   - 格式化顯示
   - 一鍵複製（使用 Toast 提示）

3. 品質評分
   - Progress 進度條
   - 評分等級（0-100）
   - 顏色漸變（紅→黃→綠）

4. 操作按鈕
   - 清空全部（帶確認）
   - 複製 Prompt
   - 驗證品質
   - 查看建議

Props：
```typescript
interface WorkspaceProps {
  tags: Tag[];
  onTagRemove: (tagId: string) => void;
  onTagReorder: (tags: Tag[]) => void;
  onClear: () => void;
  onValidate: () => void;
  validationScore?: number;
  className?: string;
}
```

請提供：
1. 完整組件代碼
2. 拖拽整合示例
3. Toast 配置
4. 使用範例
```

### 範例 4: 驗證面板

**完整提示語：**
```
用 shadcn MCP 創建 ValidationPanel 組件：

安裝組件：
card, alert, progress, badge, accordion, separator

功能：
1. 品質評分
   - Progress 進度條
   - 分數顯示（0-100）
   - 評級（差/良好/優秀）

2. 問題列表
   - Alert 顯示衝突標籤
   - Alert 顯示冗餘標籤
   - 可點擊查看詳情

3. 建議列表
   - Accordion 展開/收合
   - 每條建議可應用
   - Badge 顯示建議類型

4. 詳細分析
   - 標籤平衡分析
   - 分類分佈
   - 熱度評估

Props：
```typescript
interface ValidationPanelProps {
  validation: ValidationResult;
  onApplySuggestion: (suggestion: string) => void;
  onFixIssue: (issue: string) => void;
  className?: string;
}

interface ValidationResult {
  overall_score: number;
  grade: 'poor' | 'good' | 'excellent';
  issues: ValidationIssue[];
  suggestions: ValidationSuggestion[];
  analysis: {
    balance: number;
    categories: Record<string, number>;
    popularity: number;
  };
}
```

請生成完整實作。
```

---

## 📊 效能對比

### 各階段時間節省明細

#### Phase 1: 核心搜尋功能（16h → 11h）

| 任務 | 傳統 | MCP | 節省 |
|------|------|-----|------|
| 安裝組件 | 1h | 0.2h | 80% |
| 創建搜尋框 | 4h | 2h | 50% |
| 結果展示 | 3h | 2h | 33% |
| API 整合 | 4h | 3h | 25% |
| 搜尋歷史 | 2h | 1.5h | 25% |
| 測試除錯 | 2h | 2.3h | -15% |
| **總計** | **16h** | **11h** | **31%** |

#### Phase 2: 工作區管理（20h → 14h）

| 任務 | 傳統 | MCP | 節省 |
|------|------|-----|------|
| TagCard | 4h | 2.5h | 38% |
| Workspace | 5h | 3.5h | 30% |
| 拖拽功能 | 4h | 3h | 25% |
| Prompt 預覽 | 3h | 2h | 33% |
| 本地持久化 | 2h | 1.5h | 25% |
| 測試 | 2h | 1.5h | 25% |
| **總計** | **20h** | **14h** | **30%** |

### 整體專案時間節省

```
原估總時間:  112 小時
MCP 優化後:   80 小時
────────────────────
節省時間:     32 小時 (29%)
節省週數:     0.8 週 (約 4 工作天)
```

**價值評估：**
- 💰 節省開發成本：假設時薪 $50，節省 $1,600
- 🚀 加快上線時間：提前 4 天發布
- 🎯 提高開發體驗：減少重複工作，專注業務邏輯
- ✨ 提升代碼品質：AI 生成的代碼通常更規範

---

## 🎯 總結與建議

### 何時使用 MCP

**✅ 強烈推薦使用：**
- 安裝和配置 shadcn/ui 組件
- 生成標準 UI 組件骨架
- 創建表單和驗證邏輯
- 實作常見 UI 模式

**✅ 推薦使用：**
- 調整組件樣式和變體
- 添加動畫效果
- 整合第三方庫

**⚠️ 謹慎使用：**
- 複雜的業務邏輯
- 專案特定的狀態管理
- 性能優化代碼

**❌ 不推薦使用：**
- 核心 API 整合
- 安全相關代碼
- 複雜的算法實作

### 開發建議

1. **初期（Phase 0-1）**
   - 大量使用 MCP 快速搭建基礎
   - 建立組件庫
   - 定義統一風格

2. **中期（Phase 2-4）**
   - 使用 MCP 生成功能組件骨架
   - 手動完善業務邏輯
   - 平衡 AI 和手動開發

3. **後期（Phase 5-9）**
   - 主要手動開發
   - MCP 輔助快速添加新組件
   - 專注優化和測試

### 學習資源

- **shadcn/ui 官方文檔**: https://ui.shadcn.com/
- **Tailwind CSS 文檔**: https://tailwindcss.com/docs
- **Next.js 文檔**: https://nextjs.org/docs
- **MCP 協議**: https://modelcontextprotocol.io/

---

## 📞 獲取幫助

### 遇到問題？

1. **查看本指南** - 檢查故障排除章節
2. **詢問 AI 助手** - 描述問題並請求幫助
3. **查閱官方文檔** - shadcn/ui 文檔
4. **提交 Issue** - 專案 GitHub Issues

### 反饋與建議

如果您有任何關於 MCP 使用的建議或發現更好的實踐方法，歡迎：
- 更新本文檔
- 分享給團隊
- 提交 Pull Request

---

**使用 shadcn MCP，讓 AI 成為您的開發夥伴！** ⚡

---

**文檔版本**: 1.0.0  
**最後更新**: 2025-10-17  
**維護者**: Prompt-Scribe Team

