<!--
Sync Impact Report:
- Version: Initial → 1.0.0
- Creation Date: 2025-10-08
- Modified Principles: N/A (Initial Creation)
- Added Sections: All (Initial Constitution)
- Removed Sections: N/A
- Templates Status:
  ✅ plan-template.md (created)
  ✅ spec-template.md (created)
  ✅ tasks-template.md (created)
  ✅ commands/*.md (created)
- Follow-up TODOs: None
-->

# 專案開發憲法 (Project Constitution)

**專案名稱 (Project Name):** Prompt-Scribe

**憲法版本 (Constitution Version):** 1.0.0

**批准日期 (Ratification Date):** 2025-10-08

**最後修訂日期 (Last Amended Date):** 2025-10-08

---

## 前言 (Preamble)

本憲法是 **Prompt-Scribe** 專案的最高指導原則。所有後續的規格文件、開發計畫、程式碼實作及決策，都必須嚴格遵守本憲法所定義的核心原則。本憲法確保專案在技術架構、開發流程、品質標準等方面保持一致性與可預測性。

---

## 第一部分：核心原則 (Core Principles)

### 原則一：兩階段混合式架構 (Two-Stage Hybrid Architecture)

**宣告 (Declaration):**

專案 **必須 (MUST)** 嚴格區分兩個主要開發與運行階段：

1. **階段一：本地資料管線 (Local Data Pipeline)**
   - 使用 Python 作為主要開發語言
   - 使用 SQLite 作為本地資料庫引擎
   - 專注於在本機完成高效的資料處理
   - 產出可攜式的「黃金資料資產」(Golden Data Asset)，具體為 `tags.db` 檔案
   - 此階段的所有處理必須能夠在單機環境完整執行，不依賴雲端服務

2. **階段二：雲端應用後端 (Cloud Application Backend)**
   - 將階段一產出的資料資產遷移至 Supabase (PostgreSQL)
   - 支援向量化 (Vectorization) 功能以實現語意搜尋
   - 提供 RESTful API 服務
   - 支援多使用者應用場景
   - 此階段依賴雲端基礎設施，但資料來源始終為階段一的產出

**原則說明 (Rationale):**

此架構設計確保：
- **資料主權 (Data Sovereignty):** 核心資料處理在本地完成，使用者擁有完整控制權
- **可擴展性 (Scalability):** 雲端階段可獨立擴展，不影響本地資料處理的穩定性
- **成本效益 (Cost Efficiency):** 本地處理減少雲端運算成本
- **開發靈活性 (Development Flexibility):** 兩階段可獨立開發與測試
- **資料可攜性 (Data Portability):** 黃金資料資產可自由遷移至不同雲端平台

**禁止事項 (Prohibited Actions):**
- 禁止在階段一引入雲端依賴（除非為可選的 LLM API 呼叫）
- 禁止跨階段的耦合設計
- 禁止繞過階段一直接在雲端進行原始資料處理

---

### 原則二：LLM 職責分離原則 (LLM Role Separation Principle)

**宣告 (Declaration):**

專案中的 AI 角色 **必須 (MUST)** 嚴格分離，以確保系統的穩定性、可審計性與可維護性：

1. **IDE LLM (本機智能助手，例如 Cursor AI)**
   - 職責：理解人類指令、生成專案程式碼、維護技術文件
   - 範圍：程式碼生成、重構建議、文件撰寫、架構設計輔助
   - 特性：互動式、輔助性、不產生最終資料產品
   - 典型代表：Cursor AI、GitHub Copilot、Claude in IDE

2. **資料層 LLM (雲端 API，用於資料處理)**
   - 職責：對資料內容進行語意分析、分類、標記與推理
   - 範圍：Prompt 標籤生成、內容摘要、語意向量化、分類建議
   - 特性：批次處理、結果可記錄、輸入輸出可追溯
   - 典型代表：OpenAI API、Anthropic API、本地部署的開源模型
   - **強制要求：** 所有推理結果必須被完整記錄，包括：
     - 輸入內容的摘要或雜湊值
     - 使用的模型與參數
     - 輸出結果
     - 時間戳記

**原則說明 (Rationale):**

此分離原則確保：
- **責任明確 (Clear Accountability):** 程式碼品質由 IDE LLM 負責，資料品質由資料層 LLM 負責
- **可審計性 (Auditability):** 資料層的所有 AI 決策都有完整記錄，可追溯與驗證
- **穩定性 (Stability):** IDE LLM 的變更不會影響已產生的資料
- **可替換性 (Replaceability):** 任一 LLM 可獨立替換，不影響另一層
- **成本控制 (Cost Control):** 可針對不同層級選擇適當的 LLM 服務等級

**禁止事項 (Prohibited Actions):**
- 禁止使用 IDE LLM 直接處理生產資料
- 禁止資料層 LLM 的推理結果未被記錄
- 禁止混淆兩種 LLM 的職責界限

---

### 原則三：開發與品質原則 (Development and Quality Principles)

**宣告 (Declaration):**

專案開發 **必須 (MUST)** 遵循以下三大核心方法論：

1. **規格驅動 (Spec-Driven Development, SDD)**
   - 所有功能實作必須源於明確的規格文件
   - 規格文件必須先於程式碼編寫
   - 規格變更必須經過版本控制與審查
   - 實作完成後必須進行規格符合性驗證

2. **資料優先 (Data-First Approach)**
   - 資料處理的正確性是最高優先級
   - 資料一致性優先於功能豐富度
   - 資料模型設計必須優先於 API 設計
   - 資料驗證必須在每個處理階段執行
   - 資料品質問題必須立即修復，不可延後

3. **模組化與可讀性 (Modularity and Readability)**
   - 程式碼必須結構清晰，單一職責
   - 必須有適當的註解，說明「為什麼」而非「做什麼」
   - 函式與類別命名必須自我解釋
   - 複雜邏輯必須附帶範例與測試
   - 外部依賴必須最小化且明確聲明

**原則說明 (Rationale):**

此三大原則確保：
- **可維護性 (Maintainability):** 規格驅動與良好的程式碼結構降低維護成本
- **可靠性 (Reliability):** 資料優先確保系統產出的可信度
- **協作效率 (Collaboration Efficiency):** 清晰的規格與程式碼降低溝通成本
- **長期價值 (Long-term Value):** 高品質的程式碼與資料可持續演進

**強制實踐 (Mandatory Practices):**
- 每個功能必須有對應的規格文件於 `.specify/specs/` 目錄
- 每個資料處理步驟必須有驗證邏輯
- 每個模組必須有單元測試覆蓋率 ≥ 80%
- 每個公開介面必須有文件字串 (docstring)

---

## 第二部分：治理與修訂 (Governance and Amendment)

### 修訂程序 (Amendment Procedure)

1. **提案階段 (Proposal Phase)**
   - 任何專案成員可提出憲法修訂提案
   - 提案必須包含：修訂理由、影響範圍、實施計畫
   - 提案必須以 Pull Request 形式提交

2. **審查階段 (Review Phase)**
   - 專案維護者 (Maintainer) 必須在 7 個工作日內回應
   - 必須評估對現有規格、程式碼、計畫的影響
   - 必須徵求核心貢獻者的意見

3. **批准階段 (Approval Phase)**
   - 需要專案維護者的明確批准
   - 批准後更新版本號與修訂日期
   - 更新同步影響報告

4. **傳播階段 (Propagation Phase)**
   - 更新所有受影響的模板與文件
   - 通知所有活躍貢獻者
   - 記錄於專案變更日誌

### 版本政策 (Versioning Policy)

憲法版本遵循語意化版本規範 (Semantic Versioning)：

- **主版本 (MAJOR):** 向後不相容的治理或原則移除/重新定義
- **次版本 (MINOR):** 新增原則/章節，或實質性擴展指導方針
- **修訂版本 (PATCH):** 澄清說明、用詞調整、錯字修正、非語意性優化

### 合規審查 (Compliance Review)

- **頻率：** 每季度進行一次合規審查
- **範圍：** 檢查所有新增規格、程式碼是否符合憲法原則
- **記錄：** 審查結果記錄於 `.specify/memory/compliance-log.md`
- **行動：** 發現不符合項目必須在下一個開發週期內修正

### 例外處理 (Exception Handling)

在極特殊情況下，可申請原則例外：
- 必須提供詳細的技術或業務理由
- 必須評估風險與替代方案
- 必須獲得專案維護者明確批准
- 必須記錄於 `.specify/memory/exceptions-log.md`
- 例外有效期不得超過一個開發週期

---

## 第三部分：執行與監督 (Execution and Oversight)

### 規格文件要求

所有功能開發必須遵循 SDD 流程：
1. 撰寫規格文件於 `.specify/specs/`
2. 規格必須包含：目標、範圍、資料模型、介面定義、驗收標準
3. 規格必須經過審查後才能開始實作

### 程式碼審查要求

所有程式碼提交必須：
- 通過自動化測試（單元測試、整合測試）
- 符合程式碼風格指南
- 包含必要的註解與文件
- 經過至少一位其他開發者的審查

### 資料品質保證

所有資料處理邏輯必須：
- 包含輸入驗證
- 包含輸出驗證
- 記錄處理日誌
- 提供錯誤處理與回滾機制

---

## 附錄 (Appendix)

### 詞彙表 (Glossary)

- **黃金資料資產 (Golden Data Asset):** 經過完整處理、驗證並可直接用於生產環境的資料產品
- **規格驅動開發 (Spec-Driven Development, SDD):** 先撰寫規格文件，再進行實作的開發方法論
- **IDE LLM:** 整合於開發環境中的大型語言模型，用於輔助程式碼撰寫
- **資料層 LLM:** 用於資料內容分析與處理的大型語言模型 API

### 參考文件 (References)

- 規格模板：`.specify/templates/spec-template.md`
- 計畫模板：`.specify/templates/plan-template.md`
- 任務模板：`.specify/templates/tasks-template.md`

---

**憲法結束 (End of Constitution)**

*本憲法自批准日期起生效。所有專案參與者必須熟悉並遵守本憲法。*
