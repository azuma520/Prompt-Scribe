# 🚀 本地開發快速指南

## ✅ 開發伺服器已運行！

### 訪問應用

```
主頁:     http://localhost:3000
Inspire:  http://localhost:3000/inspire
```

---

## 💻 常用命令

### 在正確目錄中執行

```bash
# ⚠️ 重要：必須在 prompt-scribe-web 目錄中執行

cd d:\Prompt-Scribe\prompt-scribe-web
```

### 開發命令

```bash
# 啟動開發伺服器
npm run dev

# 建置生產版本
npm run build

# 啟動生產伺服器
npm run start

# 類型檢查
npm run build

# Linter 檢查
npm run lint
```

---

## 🎯 Inspire 功能測試

### 測試步驟

1. **訪問首頁**
   ```
   http://localhost:3000
   ```

2. **進入 Inspire**
   - 點擊「✨ Inspire 靈感」卡片

3. **輸入描述**
   - 例如：「孤獨又夢幻的感覺」
   - 例如：「賽博龐克城市夜景」
   - 例如：「櫻花樹下的女孩」

4. **查看靈感卡**
   - 等待 3-5 秒生成
   - 查看 3 張精美卡片
   - 每張卡片顯示：主體、場景、風格、標籤、信心度

5. **選擇卡片**
   - 點擊喜歡的卡片
   - 卡片會顯示選中狀態（藍色邊框發光）

6. **複製使用**
   - 切換 Prompt / JSON 格式
   - 點擊複製按鈕
   - 查看 Toast 提示

7. **重新開始**
   - 點擊「重新開始」按鈕
   - 輸入新的描述

---

## 🐛 故障排除

### 問題 1: 開發伺服器啟動失敗

**症狀**:
```
npm error code ENOENT
npm error path D:\Prompt-Scribe\package.json
```

**原因**: 在錯誤的目錄

**解決**:
```bash
# 必須在 prompt-scribe-web 目錄中
cd d:\Prompt-Scribe\prompt-scribe-web
npm run dev
```

### 問題 2: 端口被占用

**症狀**:
```
Port 3000 is already in use
```

**解決**:
```bash
# 使用不同端口
npm run dev -- -p 3001
```

### 問題 3: API 連接失敗

**原因**: 環境變數配置問題

**解決**:
```bash
# 檢查 .env.local 文件
cat .env.local

# 應該包含:
# NEXT_PUBLIC_API_URL=https://prompt-scribe-api.vercel.app
```

---

## 📊 專案狀態

### ✅ 已完成

- Phase 0: 專案設置（100%）
- Phase 3: Inspire 核心（53%）
- MVP: 基本可用 ✅

### 🚧 待完成

- 反饋迭代功能
- Session 歷史管理
- 標籤搜尋功能
- 工作區功能
- 完整測試

---

## 🎊 快速測試清單

測試 Inspire 功能時，請檢查：

- [ ] 輸入框可以輸入文字
- [ ] 字數統計正確顯示
- [ ] Ctrl+Enter 可以提交
- [ ] 載入動畫顯示（Shimmer 效果）
- [ ] 生成 3 張靈感卡
- [ ] 卡片資訊完整（主體、場景、風格、標籤）
- [ ] 點擊可以選擇卡片
- [ ] 選中狀態明顯（藍色邊框）
- [ ] JSON/Prompt 格式切換
- [ ] 複製按鈕可用
- [ ] Toast 提示顯示
- [ ] 重新開始功能

---

## 📞 需要幫助？

查看完整文檔：
- 規格: `../specs/002-web-frontend/spec.md`
- 任務: `../specs/002-web-frontend/current/tasks.md`
- MCP: `../specs/002-web-frontend/MCP_USAGE_GUIDE.md`

---

**開始測試您的 Inspire MVP！** ✨

訪問: http://localhost:3000

