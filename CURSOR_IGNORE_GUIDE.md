# Cursor Ignore 配置指南

## 📝 什麼是 .cursorignore？

`.cursorignore` 是 Cursor IDE 的檔案索引控制文件，類似於 `.gitignore`，但用途不同：

| 檔案 | 用途 | 影響 |
|------|------|------|
| `.gitignore` | 控制 Git 版本控制 | 哪些檔案不被提交到 Git |
| `.cursorignore` | 控制 Cursor AI 索引 | 哪些檔案不被 AI 索引和搜索 |

## 🎯 為什麼需要 .cursorignore？

### 1. **提升 AI 回應品質**
- 排除無關檔案，讓 AI 專注於重要程式碼
- 減少上下文雜訊
- 提高回應準確性

### 2. **提升性能**
- 減少索引的檔案數量
- 加快語義搜索速度
- 降低記憶體使用

### 3. **保護敏感資訊**
- 排除 `.env` 檔案
- 排除包含 API Key 的配置
- 防止敏感資料被 AI 處理

## 📁 當前配置

### 根目錄 `.cursorignore`

主要排除：
- archive/ 目錄（歷史檔案）
- 所有 CSV 資料檔案
- 資料庫檔案（.db, .sqlite）
- Python 緩存（__pycache__）
- IDE 配置（.vscode, .idea）
- 環境變數（.env）
- 日誌檔案（.log）

### stage1/.cursorignore

stage1 特定排除：
- archive/（41 個歷史檔案）
- data/raw/*.csv（原始資料）
- output/*.log（執行日誌）
- output/*.db（資料庫）
- 所有 __pycache__ 目錄

## 📊 影響統計

### 專案總覽

| 項目 | 數量 | 說明 |
|------|------|------|
| 總檔案數 | ~100 個 | 包含所有檔案 |
| 被 cursorignore | ~65 個 | 不被 AI 索引 |
| AI 可見檔案 | ~35 個 | 核心程式碼和文檔 |

## 💡 最佳實踐

### 應該忽略

✅ 大型資料檔案（CSV, JSON）  
✅ 資料庫檔案（.db, .sqlite）  
✅ 日誌檔案（.log）  
✅ 測試緩存（__pycache__）  
✅ 依賴套件（node_modules, venv）  
✅ 歷史/歸檔檔案  
✅ 環境變數（.env）  

### 不應該忽略

❌ 核心程式碼檔案  
❌ 重要文檔（README, 設計文檔）  
❌ 測試檔案（test_*.py）  
❌ 配置檔案（config.py）  
❌ 需要 AI 理解的程式碼  

---

**配置完成！** 您的 Cursor IDE 現在更智能、更快速、更安全！

詳細說明請參考：`stage1/docs/CURSOR_IGNORE_SETUP.md`
