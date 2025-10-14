# SPEC-001: SQLite 資料遷移至 Supabase + API 開發

**專案編號**: 001  
**分支**: `001-sqlite-ags-db`  
**建立日期**: 2025-10-14  
**最後更新**: 2025-01-14

---

## 📊 專案狀態

### 版本歷史
- ✅ **V1 (資料遷移)**: 已完成（140,782 筆標籤成功遷移）
- ⏳ **V2 (API 開發)**: 規劃完成，準備實作

### 當前階段
- **階段**: V2 - API 優化與開發
- **狀態**: Planning Complete → Ready for Implementation
- **下一步**: 開始 T101（建立 API 專案結構）

---

## 🚀 快速導覽

### 📖 **我應該看哪個檔案？**

| 如果您想... | 請閱讀... |
|-------------|----------|
| **快速了解整個專案** | `INDEX.md` ⭐ |
| **查看完整規格** | `spec.md` |
| **查看資料模型** | `data-model.md` |
| **開始 API 開發** | `current/API_OPTIMIZATION_QUICKSTART.md` ⭐ |
| **查看開發計畫** | `current/plan_api_optimization.md` ⭐ |
| **查看任務清單** | `current/tasks_api_optimization.md` ⭐ |
| **查看 API 規格** | `contracts/api_endpoints_llm_optimized.yaml` ⭐ |
| **了解歷史決策** | `archive/v1-migration-only/` |

**👉 建議先閱讀**: `INDEX.md` - 完整的文檔導覽

---

## 📂 目錄結構

```
specs/001-sqlite-ags-db/
│
├── 📄 INDEX.md                  ← 完整導覽（推薦閱讀）⭐
├── 📄 README.md                 ← 本檔案（快速說明）
├── 📄 spec.md                   ← 主規格文件
├── 📄 data-model.md             ← 資料模型
│
├── 📁 current/                  ← V2: API 優化（當前版本）⭐
│   ├── plan_api_optimization.md         (開發計畫)
│   ├── research_api_optimization.md     (技術研究)
│   ├── tasks_api_optimization.md        (任務清單 - 22 個任務)
│   ├── API_OPTIMIZATION_QUICKSTART.md   (快速開始指南)
│   └── API_OPTIMIZATION_SUMMARY.md      (計畫總結)
│
├── 📁 contracts/                ← API 規格和資料庫 Schema
│   ├── database_schema.sql              (資料庫結構)
│   ├── api_endpoints.yaml               (舊版 API 規格)
│   └── api_endpoints_llm_optimized.yaml (新版 LLM 友好 API) ⭐
│
├── 📁 checklists/               ← 檢查清單
│   └── requirements.md
│
└── 📁 archive/                  ← 歷史版本歸檔
    └── v1-migration-only/       ← V1: 僅資料遷移（已完成）
        ├── plan.md              (遷移計畫)
        ├── research.md          (遷移研究)
        ├── tasks.md             (遷移任務 T001-T014)
        ├── quickstart.md        (遷移快速開始)
        └── PLANNING_COMPLETE.md (規劃完成報告)
```

---

## 🎯 版本差異

### V1: 資料遷移專項 ✅
```
時間範圍: 2025-10-08 ~ 2025-01-14
焦點: SQLite → Supabase 資料遷移
成果: 140,782 筆標籤成功遷移
任務: T001-T014 (14 個任務，全部完成)
文檔: archive/v1-migration-only/
```

### V2: API 優化專項 ⏳
```
時間範圍: 2025-01-14 ~
焦點: LLM 友好的 API 開發
策略: 關鍵字搜尋優先，延後向量化
任務: T101-T503 (22 個任務，準備開始)
文檔: current/
```

---

## 🚀 立即開始

### Option 1: 開始 API 開發（推薦）
```bash
# 1. 閱讀快速開始指南
cat specs/001-sqlite-ags-db/current/API_OPTIMIZATION_QUICKSTART.md

# 2. 查看任務清單
cat specs/001-sqlite-ags-db/current/tasks_api_optimization.md

# 3. 開始第一個任務 T101
```

### Option 2: 查看完整計畫
```bash
# 閱讀開發計畫
cat specs/001-sqlite-ags-db/current/plan_api_optimization.md
```

### Option 3: 了解歷史（參考用）
```bash
# 查看遷移階段的經驗
cat specs/001-sqlite-ags-db/archive/v1-migration-only/plan.md
```

---

## 📞 相關資源

### 專案文檔
- [專案主 README](../../README.md)
- [遷移完成報告](../../docs/migration/FINAL_COMPLETION_REPORT.md)
- [API 規劃完成報告](../../docs/api-planning/API_OPTIMIZATION_PLANNING_COMPLETE.md)

### 實作資源
- [資料庫測試套件](../../tests/database/README.md)
- [遷移模組](../../src/migration/)
- [資料庫 SQL 腳本](../../scripts/)

---

**最後更新**: 2025-01-14  
**狀態**: ✅ 規劃完成，準備實作