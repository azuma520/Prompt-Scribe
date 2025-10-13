# API 合約文件 (API Contracts)

**版本 (Version):** 1.0.0

**建立日期 (Created):** 2025-10-08

---

## 概述 (Overview)

本目錄用於存放 API 合約文件。

**Phase 1 注意事項:**
Phase 1 (純規則式分類) 不包含任何 API 介面，所有處理都是本地腳本執行。

API 合約將在後續階段添加：
- **Phase 2**: LLM 增強（可能添加內部 API）
- **階段二**: 雲端部署（RESTful API 或 GraphQL）

---

## Phase 1: 本地腳本介面

### 主要執行介面

```bash
# 執行完整資料管線
python run_pipeline.py

# 輸入: stage1/data/raw/*.csv
# 輸出: stage1/output/tags.db
#      stage1/output/classification_report.txt
```

### 函式介面 (Python API)

Phase 1 提供的主要函式：

```python
# 載入 CSV 檔案
def load_csv_files(data_dir: Path) -> pd.DataFrame:
    """載入所有 CSV 檔案到 DataFrame"""
    pass

# 套用分類規則
def classify_tag(tag_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    根據規則對標籤進行分類
    
    Args:
        tag_name: 標籤名稱
    
    Returns:
        (main_category, sub_category) 的元組
    """
    pass

# 驗證輸出
def validate_output(db_path: Path) -> List[str]:
    """驗證輸出資料品質，返回錯誤列表"""
    pass
```

---

## 未來擴展 (Future Extensions)

### Phase 2: LLM 增強 API (計畫中)

可能的內部 API：

```python
# LLM 分類介面
def classify_with_llm(
    tag_names: List[str],
    model: str = "gpt-4-turbo"
) -> List[Tuple[str, str, float]]:
    """
    使用 LLM 進行批次分類
    
    Args:
        tag_names: 標籤名稱列表
        model: LLM 模型名稱
    
    Returns:
        [(main_category, sub_category, confidence), ...]
    """
    pass
```

### 階段二: RESTful API (計畫中)

可能的端點：

```
GET  /api/tags                    # 列出所有標籤
GET  /api/tags/:name              # 查詢單個標籤
GET  /api/tags/search?q=uniform   # 搜尋標籤
GET  /api/categories              # 列出所有分類
GET  /api/stats                   # 取得統計資訊
```

詳細的 OpenAPI/GraphQL Schema 將在實作時提供。

---

**合約文件結束 (End of Contracts Document)**

