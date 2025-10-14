# 🚀 Supabase MCP 部署指南

## 📋 概述

基於 [Supabase MCP 文檔](https://supabase.com/docs/guides/getting-started/mcp)，我們可以使用 Model Context Protocol (MCP) 來更簡單地連接和部署到 Supabase。

## 🎯 優勢

- ✅ **自動認證** - 無需手動配置 API Keys
- ✅ **直接集成** - 與 Cursor 無縫集成
- ✅ **安全** - 使用官方認證流程
- ✅ **簡化** - 不需要複雜的連接配置

## 🛠️ 設置步驟

### 步驟 1：配置 Cursor MCP

我們已經為您創建了 `.cursor/mcp.json` 配置文件：

```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp"
    }
  }
}
```

### 步驟 2：重啟 Cursor

1. 關閉 Cursor
2. 重新打開 Cursor
3. 等待 MCP 服務器連接

### 步驟 3：自動認證

1. Cursor 會自動提示您登錄 Supabase
2. 瀏覽器會打開 Supabase 登錄頁面
3. 登錄您的 Supabase 帳戶
4. 授權 Cursor 訪問您的專案

### 步驟 4：選擇專案範圍

- 選擇包含您要部署的專案的組織
- 確認專案訪問權限

## 🚀 部署流程

一旦 MCP 連接建立，您可以：

### 1. 直接查詢數據庫
```
請查詢我的 Supabase 專案中的 tags_final 表
```

### 2. 創建表結構
```
請為我的專案創建 tags_final 表，包含以下欄位...
```

### 3. 遷移數據
```
請幫我將本地 SQLite 數據遷移到 Supabase
```

### 4. 設置向量搜索
```
請為我的專案啟用 pgvector 並創建向量搜索功能
```

## 📊 當前狀態

### 已完成的準備工作
- ✅ 創建了完整的部署工具套件
- ✅ 準備了 SQLite 數據庫 (`stage1/output/tags.db`)
- ✅ 配置了 Cursor MCP 連接
- ✅ 診斷了連接問題

### 下一步行動
1. **重啟 Cursor** 以啟用 MCP 連接
2. **進行自動認證** 登錄 Supabase
3. **開始部署** 使用自然語言指令

## 🔧 備用方案

如果 MCP 連接有問題，我們仍然可以使用傳統的部署工具：

```bash
# 修復 API Keys 後運行
python stage1/supabase_tools/deploy_to_supabase.py
```

## 🎉 優勢總結

使用 MCP 方法的優勢：

- **更簡單** - 無需手動配置複雜的 API Keys
- **更安全** - 使用官方認證流程
- **更直觀** - 使用自然語言與 AI 交互
- **更強大** - 直接集成到 Cursor 工作流程中

## 📚 參考文檔

- [Supabase MCP 官方文檔](https://supabase.com/docs/guides/getting-started/mcp)
- [Cursor MCP 文檔](https://docs.cursor.com/integrations/mcp)

---

**準備好了嗎？請重啟 Cursor 並開始使用 MCP 進行部署！** 🎯
