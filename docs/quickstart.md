# Prompt-Scribe 快速入門指南

歡迎使用 Prompt-Scribe！本指南將幫助您快速了解並開始使用本專案。

## 📖 什麼是 Prompt-Scribe？

Prompt-Scribe 是一個設計用於收集、標記、分析與服務化 AI Prompt 的系統。專案採用兩階段混合式架構：

1. **階段一（本地）**：在您的電腦上處理資料，產出可攜式的資料庫
2. **階段二（雲端）**：將資料上傳至雲端，提供 API 與多使用者服務

## 🎯 核心理念

### 資料主權優先
您的資料由您掌控。核心處理在本地完成，您可以選擇是否要上傳至雲端。

### 規格驅動開發
所有功能都基於明確的規格文件，確保開發的一致性與可預測性。

### AI 職責分離
- **開發助手 AI**（如 Cursor）：幫助您寫程式碼
- **資料處理 AI**（API）：分析您的 Prompt 內容

兩者職責明確分離，所有資料處理 AI 的決策都會被記錄。

## 🚀 10 分鐘快速開始

### 步驟 1：環境準備

確保您已安裝：
- Python 3.11 或更高版本
- Git

```bash
# 檢查 Python 版本
python --version

# 應顯示 Python 3.11.x 或更高
```

### 步驟 2：下載專案

```bash
# Clone 專案
git clone https://github.com/your-username/Prompt-Scribe.git
cd Prompt-Scribe
```

### 步驟 3：設定階段一（本地處理）

```bash
# 進入階段一目錄
cd stage1

# 安裝依賴
pip install -r requirements.txt
```

### 步驟 4：準備您的資料

將您的 Prompt 資料放入 `stage1/data/raw/` 目錄。

支援格式：
- JSON：`{"prompts": [{"content": "..."}, ...]}`
- CSV：包含 `content` 欄位
- TXT：每行一個 Prompt

### 步驟 5：執行處理

```bash
python src/main.py
```

處理完成後，您會在 `stage1/data/output/` 找到 `tags.db` 檔案。

### 步驟 6：檢視結果

```bash
# 使用 SQLite 工具檢視資料庫
sqlite3 data/output/tags.db

# 查看 Prompt 數量
sqlite> SELECT COUNT(*) FROM prompts;

# 查看標籤
sqlite> SELECT * FROM tags LIMIT 10;
```

## 🔧 進階設定

### 啟用 AI 標記功能（可選）

如果您想使用 AI 自動標記 Prompt：

1. 取得 API 金鑰（OpenAI 或 Anthropic）

2. 建立 `.env` 檔案：

```bash
cd stage1
cp .env.example .env
```

3. 編輯 `.env`：

```
OPENAI_API_KEY=your_key_here
ENABLE_LLM_TAGGING=true
```

4. 再次執行處理

**重要：** 所有 AI 的分析決策都會被記錄在 `llm_inference_log` 表中。

## 📊 階段二：雲端部署（可選）

如果您需要：
- API 服務
- 多人協作
- 語意搜尋

可以繼續進行階段二的雲端部署。詳見 [階段二文件](../stage2/README.md)。

## 📚 深入學習

### 理解專案架構

- [專案開發憲法](../.specify/memory/constitution.md) - 專案的最高指導原則
- [階段一詳細文件](../stage1/README.md)
- [階段二詳細文件](../stage2/README.md)

### 參與開發

- [規格模板](../.specify/templates/spec-template.md) - 撰寫新功能規格
- [貢獻指南](../README.md#貢獻指南) - 如何貢獻程式碼

## ❓ 常見問題

### Q: 我的資料安全嗎？

A: 階段一的所有處理都在您的電腦本地完成。只有當您主動執行階段二時，資料才會上傳至雲端。

### Q: 一定要使用 AI 標記功能嗎？

A: 不一定。AI 標記是可選功能。您可以手動標記或使用其他方法。

### Q: 可以客製化處理流程嗎？

A: 可以！請先撰寫規格文件，然後按照規格實作。詳見[開發指南](../stage1/README.md#開發指南)。

### Q: 我只想用階段一，不想上雲，可以嗎？

A: 完全可以！階段一就是為此設計的。`tags.db` 是完整的 SQLite 資料庫，您可以直接使用。

## 🤝 需要幫助？

- [提出 Issue](https://github.com/your-username/Prompt-Scribe/issues)
- [查看文件](../README.md)
- [閱讀憲法](../.specify/memory/constitution.md)

## 🎉 下一步

現在您已經成功運行 Prompt-Scribe！

建議的後續步驟：
1. 閱讀[專案開發憲法](../.specify/memory/constitution.md)理解專案理念
2. 探索 `tags.db` 的資料結構
3. 客製化資料處理流程以符合您的需求
4. （可選）設定階段二的雲端服務

祝您使用愉快！ 🚀

