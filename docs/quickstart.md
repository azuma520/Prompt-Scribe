# Prompt-Scribe 快速入門指南

歡迎使用 Prompt-Scribe！本指南將幫助您快速了解並開始使用本專案。

## 📖 什麼是 Prompt-Scribe？

Prompt-Scribe 是一個專為 Danbooru 風格圖像標籤設計的資料處理與分類系統。專案採用兩階段混合式架構：

1. **階段一（本地）**：在您的電腦上處理標籤資料，產出可攜式的 SQLite 資料庫
2. **階段二（雲端）**：將資料上傳至雲端 (Supabase)，提供 API 與語意搜尋服務

## 🎯 核心理念

### 資料主權優先
您的資料由您掌控。核心處理在本地完成，您可以選擇是否要上傳至雲端。

### 規格驅動開發
所有功能都基於明確的規格文件，確保開發的一致性與可預測性。

### AI 職責分離
- **開發助手 AI**（如 Cursor）：幫助您寫程式碼
- **資料處理 AI**（API，Phase 2）：進行語意分類

兩者職責明確分離。**Phase 1 不使用任何 LLM**，採用純規則式分類。

## 🚀 5 分鐘快速開始（Phase 1 - 規則式分類）

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

# 安裝依賴（僅需 pandas，無需 LLM API）
pip install -r requirements.txt
```

### 步驟 4：準備您的資料

將 Danbooru 標籤 CSV 檔案放入 `stage1/data/raw/` 目錄。

**必要欄位:**
- `name`: 標籤名稱（例如 `school_uniform`）
- `category` 或 `danbooru_cat`: Danbooru 分類 ID (0-5)
- `post_count`: 使用次數（可選，預設為 0）

**範例 CSV:**
```csv
name,category,post_count
school_uniform,0,15234
from_above,0,8921
1girl,0,123456
```

### 步驟 5：執行資料管線

```bash
# 執行完整管線（載入、合併、分類、驗證）
python run_pipeline.py
```

處理完成後，您會在 `stage1/output/` 找到：
- `tags.db`: SQLite 資料庫
- `classification_report.txt`: 分類統計報告

**預期執行時間:** 10 萬筆標籤約 2-5 分鐘

### 步驟 6：檢視結果

```bash
# 使用 SQLite 工具檢視資料庫
sqlite3 output/tags.db

# 查看標籤總數
sqlite> SELECT COUNT(*) FROM tags_final;

# 查看分類分佈
sqlite> SELECT main_category, COUNT(*) as count 
        FROM tags_final 
        WHERE danbooru_cat = 0 
        GROUP BY main_category;

# 查看服裝相關標籤
sqlite> SELECT name, post_count 
        FROM tags_final 
        WHERE main_category = 'CHARACTER_RELATED' 
          AND sub_category = 'CLOTHING'
        ORDER BY post_count DESC 
        LIMIT 10;
```

**檢視分類報告:**
```bash
# Windows
type output\classification_report.txt

# Linux/Mac
cat output/classification_report.txt
```

## 🔧 進階設定

### 自訂分類規則

Phase 1 使用規則式分類，您可以編輯 `data_rules.py` 來客製化分類邏輯：

```python
# data_rules.py
MAIN_CATEGORY_RULES = {
    'CHARACTER_RELATED': [
        'girl', 'boy', 'woman', 'man',
        'hair', 'eyes', 'uniform', 'dress',
        # 添加您的關鍵字...
    ],
    'COMPOSITION': [
        'from_above', 'from_below', 'close-up',
        # 添加您的關鍵字...
    ],
    # ... 其他分類
}
```

**修改後重新執行:**
```bash
python run_pipeline.py
```

### 調整覆蓋率目標

在 `config.py` 中可調整驗證門檻：

```python
# config.py
MIN_MAIN_CATEGORY_COVERAGE = 0.90  # 主分類最低覆蓋率 90%
MIN_SUB_CATEGORY_COVERAGE = 0.40   # 副分類最低覆蓋率 40%
```

### Phase 2: LLM 增強（未來）

如果您需要更高的分類準確度，可在 Phase 2 啟用 LLM：

- LLM 將補充規則式分類未覆蓋的標籤
- 所有 LLM 推理結果會記錄在 `llm_inference_log` 表中
- 詳見 [Phase 2 計畫](../specs/main/plan.md#phase-2-llm-增強)

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

### Q: Phase 1 使用 AI 嗎？

A: **不使用**。Phase 1 採用純規則式分類，完全本地執行，無需 API 金鑰，無網路連線需求，零成本。

### Q: 規則式分類的準確度如何？

A: 目標主分類覆蓋率 ≥ 90%。實際準確度取決於關鍵字字典的完善程度，可持續優化。

### Q: 我的資料安全嗎？

A: 階段一的所有處理都在您的電腦本地完成。沒有任何資料上傳，完全離線可用。

### Q: 可以客製化分類規則嗎？

A: 可以！編輯 `data_rules.py` 添加或修改關鍵字。所有規則都是透明可見的 Python 字典。

### Q: 我只想用階段一，不想上雲，可以嗎？

A: 完全可以！階段一就是為此設計的。`tags.db` 是完整的 SQLite 資料庫，您可以直接使用或遷移至任何平台。

### Q: Phase 1 的效能如何？

A: 10 萬筆標籤約 2-5 分鐘（中等效能筆電）。記憶體使用 < 200 MB。

### Q: 如何提升分類覆蓋率？

A: 1) 執行管線後檢視 `classification_report.txt`，2) 查看未分類的高頻標籤，3) 在 `data_rules.py` 添加對應關鍵字，4) 重新執行。

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

