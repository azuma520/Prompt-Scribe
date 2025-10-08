# 規格文件：[FEATURE_NAME]

**規格編號 (Spec ID):** SPEC-[YYYY]-[NUMBER]

**版本 (Version):** [MAJOR].[MINOR].[PATCH]

**狀態 (Status):** [Draft | In Review | Approved | Implemented | Deprecated]

**作者 (Author):** [AUTHOR_NAME]

**建立日期 (Created):** [YYYY-MM-DD]

**最後更新 (Last Updated):** [YYYY-MM-DD]

---

## 憲法符合性檢查 (Constitution Compliance Check)

- [ ] 符合「兩階段混合式架構」原則（明確標示屬於階段一或階段二）
- [ ] 符合「LLM 職責分離」原則（若涉及 AI，已明確區分 IDE LLM 與資料層 LLM）
- [ ] 符合「規格驅動開發」原則（本規格先於實作）
- [ ] 符合「資料優先」原則（已定義資料模型與驗證邏輯）
- [ ] 符合「模組化與可讀性」原則（設計清晰、職責單一）

---

## 1. 概述 (Overview)

### 1.1 目標 (Objective)

[清楚說明此功能或模組要解決的問題]

### 1.2 範圍 (Scope)

**包含 (In Scope):**
- [功能或模組包含的內容]

**不包含 (Out of Scope):**
- [明確排除的內容]

### 1.3 架構階段定位 (Architecture Stage)

- [ ] 階段一：本地資料管線
- [ ] 階段二：雲端應用後端
- [ ] 跨階段（需說明如何解耦）

---

## 2. 需求 (Requirements)

### 2.1 功能需求 (Functional Requirements)

| ID | 需求描述 | 優先級 | 驗收標準 |
|----|----------|--------|----------|
| FR-01 | [需求描述] | [High/Medium/Low] | [如何驗證] |
| FR-02 | [需求描述] | [High/Medium/Low] | [如何驗證] |

### 2.2 非功能需求 (Non-Functional Requirements)

| ID | 類別 | 需求描述 | 標準 |
|----|------|----------|------|
| NFR-01 | 效能 (Performance) | [描述] | [具體指標] |
| NFR-02 | 可靠性 (Reliability) | [描述] | [具體指標] |
| NFR-03 | 可維護性 (Maintainability) | [描述] | [具體指標] |

---

## 3. 資料模型 (Data Model)

### 3.1 資料結構

```python
# 使用程式碼區塊清楚定義資料結構
# 例如：Python dataclass, TypeScript interface, SQL schema

@dataclass
class ExampleEntity:
    id: str
    name: str
    created_at: datetime
    # ...
```

### 3.2 資料流向

```
[來源] → [處理步驟1] → [處理步驟2] → [目的地]
```

### 3.3 資料驗證規則

- **輸入驗證：** [定義輸入資料的驗證規則]
- **輸出驗證：** [定義輸出資料的驗證規則]
- **一致性檢查：** [定義資料一致性檢查邏輯]

---

## 4. 介面定義 (Interface Definition)

### 4.1 函式/API 簽名

```python
def function_name(
    param1: Type1,
    param2: Type2,
) -> ReturnType:
    """
    功能說明
    
    Args:
        param1: 參數說明
        param2: 參數說明
    
    Returns:
        返回值說明
    
    Raises:
        Exception1: 異常情況說明
    """
    pass
```

### 4.2 相依性 (Dependencies)

**內部相依：**
- [列出專案內部的模組相依]

**外部相依：**
- [列出第三方套件相依，包含版本需求]

---

## 5. LLM 使用聲明 (LLM Usage Declaration)

### 5.1 IDE LLM 使用

- [ ] 不使用
- [ ] 用於程式碼生成輔助
- [ ] 用於文件撰寫輔助
- [ ] 用於測試案例生成

### 5.2 資料層 LLM 使用

- [ ] 不使用
- [ ] 使用（必須填寫以下資訊）

**若使用資料層 LLM，必須定義：**
- **用途：** [例如：標籤生成、內容分類、摘要生成]
- **模型選擇：** [例如：GPT-4, Claude-3-Opus]
- **輸入格式：** [定義傳入 LLM 的資料格式]
- **輸出格式：** [定義 LLM 回傳的資料格式]
- **記錄機制：** [說明如何記錄 LLM 推理結果]
- **失敗處理：** [說明 LLM API 失敗時的處理邏輯]

---

## 6. 測試策略 (Testing Strategy)

### 6.1 單元測試

- **測試覆蓋率目標：** ≥ 80%
- **關鍵測試案例：**
  - [測試案例1]
  - [測試案例2]

### 6.2 整合測試

- [定義整合測試範圍]

### 6.3 資料品質測試

- **輸入資料測試：** [測試各種輸入情況]
- **輸出資料驗證：** [驗證輸出符合預期]
- **邊界條件測試：** [測試極端情況]

---

## 7. 實作計畫 (Implementation Plan)

### 7.1 階段劃分

| 階段 | 任務 | 預估時間 | 優先級 |
|------|------|----------|--------|
| 階段 1 | [任務描述] | [時數/天數] | [High/Medium/Low] |
| 階段 2 | [任務描述] | [時數/天數] | [High/Medium/Low] |

### 7.2 風險與對策

| 風險 | 可能性 | 影響程度 | 對策 |
|------|--------|----------|------|
| [風險描述] | [High/Medium/Low] | [High/Medium/Low] | [對策描述] |

---

## 8. 驗收標準 (Acceptance Criteria)

- [ ] 所有功能需求已實作並通過測試
- [ ] 所有非功能需求符合標準
- [ ] 程式碼通過 Code Review
- [ ] 單元測試覆蓋率 ≥ 80%
- [ ] 資料驗證邏輯已實作並測試
- [ ] 文件已完成（程式碼註解、API 文件）
- [ ] 符合憲法所有相關原則

---

## 9. 變更記錄 (Change Log)

| 版本 | 日期 | 變更內容 | 作者 |
|------|------|----------|------|
| 1.0.0 | YYYY-MM-DD | 初始版本 | [作者] |

---

## 10. 參考資料 (References)

- [相關規格文件]
- [外部技術文件]
- [相關決策記錄]

---

**規格結束 (End of Specification)**
