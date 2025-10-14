# 📁 Specs 001: SQLite to Supabase 文檔索引

**專案**: SQLite 資料遷移至 Supabase + API 開發  
**建立日期**: 2025-01-14  
**版本**: 2.0

---

## 📋 快速導覽

### 🎯 **我應該看哪個檔案？**

**如果您想要...**

| 需求 | 檔案位置 | 說明 |
|------|----------|------|
| **了解專案規格** | `spec.md` | 完整的功能規格文件 |
| **了解資料模型** | `data-model.md` | 資料庫結構和關係 |
| **查看 API 規格** | `contracts/api_endpoints_llm_optimized.yaml` | 最新的 LLM 友好 API 規格 ⭐ |
| **開始 API 開發** | `current/API_OPTIMIZATION_QUICKSTART.md` | API 開發快速開始指南 ⭐ |
| **查看開發計畫** | `current/plan_api_optimization.md` | 最新的 API 開發計畫 ⭐ |
| **查看任務清單** | `current/tasks_api_optimization.md` | 詳細的開發任務（18 個任務）⭐ |
| **了解技術決策** | `current/research_api_optimization.md` | 技術研究和決策分析 ⭐ |
| **查看計畫總結** | `current/API_OPTIMIZATION_SUMMARY.md` | API 優化計畫總結 ⭐ |
| **查看舊版計畫** | `archive/v1-migration-only/` | 僅資料遷移的原始計畫 |

---

## 📂 目錄結構

```
specs/001-sqlite-ags-db/
│
├── 📄 INDEX.md                      ← 本檔案（導覽索引）
├── 📄 README.md                     ← 專案概述
├── 📄 spec.md                       ← 功能規格（主規格）
├── 📄 data-model.md                 ← 資料模型
├── 📄 .env                          ← 環境配置（不追蹤）
│
├── 📁 current/                      ← 當前版本文檔（API 優化）⭐
│   ├── plan_api_optimization.md           (開發計畫)
│   ├── research_api_optimization.md       (技術研究)
│   ├── tasks_api_optimization.md          (任務清單)
│   ├── API_OPTIMIZATION_QUICKSTART.md     (快速開始)
│   └── API_OPTIMIZATION_SUMMARY.md        (計畫總結)
│
├── 📁 contracts/                    ← API 規格和資料庫 Schema
│   ├── database_schema.sql              (資料庫結構)
│   ├── api_endpoints.yaml               (舊版 API 規格)
│   └── api_endpoints_llm_optimized.yaml (新版 LLM 友好 API) ⭐
│
├── 📁 checklists/                   ← 檢查清單
│   └── requirements.md
│
└── 📁 archive/                      ← 歷史版本歸檔
    └── v1-migration-only/            ← V1: 僅資料遷移計畫
        ├── plan.md                      (原始開發計畫)
        ├── research.md                  (原始技術研究)
        ├── tasks.md                     (原始任務清單)
        ├── PLANNING_COMPLETE.md         (原始規劃完成報告)
        └── quickstart.md                (原始快速開始)
```

---

## 🎯 版本說明

### **V1: 資料遷移專案**（已完成 ✅）
**時間**: 2025-10-08 ~ 2025-01-14  
**範圍**: SQLite → Supabase 資料遷移  
**成果**: 140,782 筆標籤成功遷移  
**文檔位置**: `archive/v1-migration-only/`

**核心文檔**:
- `plan.md` - 遷移開發計畫
- `research.md` - 遷移技術研究
- `tasks.md` - 遷移任務清單（T001-T014）
- `quickstart.md` - 遷移快速開始
- `PLANNING_COMPLETE.md` - 規劃完成報告

**狀態**: ✅ 已完成，已歸檔

---

### **V2: API 優化專案**（當前 ⭐）
**時間**: 2025-01-14 ~  
**範圍**: LLM 友好的 API 設計和實作  
**目標**: 建立三層級 API，優先關鍵字搜尋  
**文檔位置**: `current/`

**核心文檔**:
- `plan_api_optimization.md` - API 開發計畫
- `research_api_optimization.md` - API 技術研究
- `tasks_api_optimization.md` - API 任務清單（T101-T503）
- `API_OPTIMIZATION_QUICKSTART.md` - API 快速開始
- `API_OPTIMIZATION_SUMMARY.md` - API 計畫總結

**狀態**: ⏳ 進行中

---

## 📚 不同版本的差異

### V1 vs V2 對比

| 面向 | V1 (資料遷移) | V2 (API 優化) |
|------|---------------|---------------|
| **焦點** | 資料遷移 | API 開發 |
| **任務範圍** | T001-T014 | T101-T503 |
| **主要技術** | Python 遷移腳本 | FastAPI + LLM 整合 |
| **交付物** | Supabase 資料庫 | LLM 友好的 API |
| **狀態** | ✅ 完成 | ⏳ 規劃完成，待實作 |
| **文檔位置** | `archive/v1-migration-only/` | `current/` |

### 保留在根目錄的共用文檔

這些文檔對兩個版本都適用：
- `spec.md` - 整體功能規格
- `data-model.md` - 資料模型（遷移和 API 都需要）
- `README.md` - 專案概述
- `contracts/` - API 規格和資料庫 Schema

---

## 🔍 文檔查找指南

### 查看當前開發計畫
```bash
# API 開發計畫
cat specs/001-sqlite-ags-db/current/plan_api_optimization.md

# API 任務清單
cat specs/001-sqlite-ags-db/current/tasks_api_optimization.md

# API 快速開始
cat specs/001-sqlite-ags-db/current/API_OPTIMIZATION_QUICKSTART.md
```

### 查看歷史資料遷移計畫
```bash
# 遷移計畫
cat specs/001-sqlite-ags-db/archive/v1-migration-only/plan.md

# 遷移任務
cat specs/001-sqlite-ags-db/archive/v1-migration-only/tasks.md
```

### 查看共用規格
```bash
# 功能規格
cat specs/001-sqlite-ags-db/spec.md

# 資料模型
cat specs/001-sqlite-ags-db/data-model.md

# API 規格（最新）
cat specs/001-sqlite-ags-db/contracts/api_endpoints_llm_optimized.yaml
```

---

## 🎯 工作流程建議

### 開始 API 開發時

**步驟 1**: 閱讀當前文檔
```
1. current/API_OPTIMIZATION_SUMMARY.md       (快速了解)
2. current/plan_api_optimization.md          (詳細計畫)
3. current/tasks_api_optimization.md         (任務清單)
4. current/API_OPTIMIZATION_QUICKSTART.md    (開始實作)
```

**步驟 2**: 參考規格和合約
```
1. spec.md                                    (整體規格)
2. contracts/api_endpoints_llm_optimized.yaml (API 規格)
3. data-model.md                              (資料結構)
```

**步驟 3**: 開始開發
```
按照 tasks_api_optimization.md 中的任務順序：
T101 → T102 → T103 → ...
```

### 參考歷史資料遷移經驗時

```
查看 archive/v1-migration-only/ 下的文檔
了解遷移過程的決策和經驗
```

---

## 📊 檔案分類總結

### 當前活躍文檔（7 個）
```
current/                         (5 個 API 相關)
spec.md                          (1 個主規格)
data-model.md                    (1 個資料模型)
```

### 共用資源（4 個）
```
contracts/                       (3 個規格檔案)
checklists/                      (1 個檢查清單)
```

### 歷史歸檔（5 個）
```
archive/v1-migration-only/       (5 個遷移相關)
```

### 配置檔案（2 個）
```
.env                             (環境配置)
README.md                        (概述)
```

**總計**: 18 個檔案，組織清晰

---

## ✅ 整理原則

### 🎯 **當前版本** (`current/`)
- 正在進行的開發計畫
- 最新的技術決策
- 活躍的任務清單
- **使用頻率**: 每天

### 📦 **歷史版本** (`archive/v1-*/`)
- 已完成的專案階段
- 歷史決策記錄
- 經驗教訓總結
- **使用頻率**: 偶爾參考

### 📄 **共用文檔** (根目錄)
- 不隨版本變化的規格
- 資料模型和結構
- API 規格合約
- **使用頻率**: 經常

---

## 🚀 下一步

### 開始 API 開發
```bash
# 1. 閱讀快速開始
cat specs/001-sqlite-ags-db/current/API_OPTIMIZATION_QUICKSTART.md

# 2. 查看任務清單
cat specs/001-sqlite-ags-db/current/tasks_api_optimization.md

# 3. 開始第一個任務
# T101: 建立 API 專案結構
```

### 參考文檔時
```
當前計畫  → current/
歷史經驗  → archive/v1-migration-only/
規格合約  → 根目錄和 contracts/
```

---

## 📝 維護建議

### 新增文檔時
- **新的 API 相關**: 放入 `current/`
- **新的規格**: 放在根目錄
- **完成的階段**: 移到 `archive/vX-*/`

### 版本管理
- 每個主要階段完成後，移到 `archive/`
- 使用清晰的版本命名（v1, v2, v3）
- 保持 `current/` 目錄簡潔

---

## 🎊 整理完成

**specs/001-sqlite-ags-db/ 目錄現在非常清晰！**

**結構**:
- ✅ 當前活躍文檔在 `current/`
- ✅ 歷史文檔在 `archive/`
- ✅ 共用規格在根目錄
- ✅ 清晰的索引和導覽

**下一步**: 開始 API 開發！所有文檔都已準備就緒！🚀
