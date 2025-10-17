# 🐛 伺服器除錯指南

## 問題診斷

### 當前狀況
- ❌ localhost:3000 顯示空白頁面
- ❌ 之前顯示 Internal Server Error
- ✅ 編譯成功，無語法錯誤
- ⚠️ 端口衝突問題

## 解決方案

### 方案 1: 使用新端口
```bash
cd d:\Prompt-Scribe\prompt-scribe-web
npm run dev -- -p 3002
```
然後訪問: http://localhost:3002

### 方案 2: 清除端口並重啟
```bash
# 1. 停止所有 Node.js 進程
taskkill /f /im node.exe

# 2. 等待 5 秒
timeout /t 5

# 3. 重新啟動
npm run dev
```

### 方案 3: 檢查特定文件
可能的問題文件：
- src/app/layout.tsx
- src/app/providers.tsx  
- src/app/inspire/page.tsx
- src/lib/hooks/useInspiration.ts

### 方案 4: 簡化測試
```bash
# 創建最簡單的測試頁面
echo "export default function Test() { return <h1>Hello World</h1>; }" > src/app/test/page.tsx
```

## 快速修復

### 立即嘗試
1. 訪問 http://localhost:3002
2. 如果不行，訪問 http://localhost:3001
3. 檢查瀏覽器控制台錯誤

### 如果還是有問題
1. 清除瀏覽器快取
2. 重新啟動瀏覽器
3. 檢查防火牆設置
