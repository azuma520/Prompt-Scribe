# Feature: SQLite 資料遷移至 Supabase

**Feature Number**: 001  
**Branch**: `001-sqlite-ags-db`  
**Status**: 規格完成，已通過品質驗證  
**Created**: 2025-10-14

---

## 📋 概述

將階段一產出的 SQLite 資料庫（tags.db）完整遷移至 Supabase 雲端平台，實現：
- 完整資料遷移（140,782 個標籤）
- 向量嵌入生成（支援語意搜尋）
- REST API 存取
- 為多使用者應用做準備

---

## 📁 檔案結構

```
specs/001-sqlite-ags-db/
├── README.md                    # 本檔案
├── spec.md                      # 完整規格文件
└── checklists/
    └── requirements.md          # 品質檢查清單（已通過）
```

---

## ✅ 規格狀態

### 品質驗證結果

**狀態**: ✅ **已通過所有品質檢查**

| 檢查項目 | 狀態 | 說明 |
|---------|------|------|
| 內容品質 | ✅ PASS | 專注使用者價值，無實作細節 |
| 需求完整性 | ✅ PASS | 所有需求明確且可測試 |
| 成功標準 | ✅ PASS | 可量化、技術無關 |
| 使用者場景 | ✅ PASS | 涵蓋三大主要流程 |
| 範圍界定 | ✅ PASS | 清楚定義包含/不包含 |
| 風險管理 | ✅ PASS | 識別風險並提供對策 |
| 文件完整性 | ✅ PASS | 所有必要章節完整 |

詳細檢查清單請參閱：[checklists/requirements.md](./checklists/requirements.md)

---

## 🎯 關鍵指標

### 資料規模
- **總標籤數**: 140,782
- **已分類標籤**: 135,941 (96.56%)
- **資料庫大小**: 315 MB

### 效能目標
- **遷移時間**: < 30 分鐘
- **API 回應**: < 2 秒 (P95)
- **語意搜尋**: < 3 秒 (P95)

### 品質目標
- **資料完整性**: 100%
- **向量生成率**: ≥ 99%
- **測試覆蓋率**: ≥ 80%

---

## 📚 核心需求

### 功能需求 (10 項)
1. 完整遷移 tags_final 表資料
2. 保持分類資訊完整性
3. 生成向量嵌入
4. 提供基本查詢 API
5. 提供語意搜尋功能
6. 驗證資料完整性
7. 記錄遷移過程
8. 支援批次處理
9. 提供狀態查詢
10. 提供回滾機制

### 非功能需求 (9 項)
- 效能、可靠性、安全性、可維護性、可擴展性、成本效益

詳見：[spec.md](./spec.md)

---

## 👥 使用者場景

### 場景 1: 資料管理員執行遷移
- 配置連線資訊
- 執行遷移工具
- 驗證資料完整性
- 檢視遷移報告

### 場景 2: 開發者透過 API 查詢
- 透過 REST API 查詢標籤
- 取得標籤詳細資訊
- 使用分頁與篩選

### 場景 3: 使用者進行語意搜尋
- 輸入自然語言查詢
- 取得相關標籤結果
- 結果按相關性排序

---

## 🗺️ 實作計畫

### 預估時間
**總計**: 42 小時（約 5-6 工作天）

### 階段劃分
1. **環境準備與驗證** (4h) - High Priority
2. **資料庫結構建立** (4h) - High Priority
3. **基本資料遷移** (8h) - High Priority
4. **向量嵌入生成** (8h) - Medium Priority
5. **API 端點設定** (6h) - High Priority
6. **驗證與測試** (8h) - High Priority
7. **文件與部署** (4h) - Medium Priority

### 里程碑
- **M1**: 環境就緒 (Day 1)
- **M2**: 資料結構就緒 (Day 2)
- **M3**: 資料遷移完成 (Day 3-4)
- **M4**: 功能完整 (Day 5)
- **M5**: 上線就緒 (Day 6)

---

## 🔧 技術架構

### 資料流
```
tags.db (SQLite)
    ↓
[讀取與驗證]
    ↓
[批次轉換]
    ↓
[上傳至 Supabase] → tags_final 表
    ↓
[生成向量嵌入] → tag_embeddings 表
    ↓
[驗證完整性]
    ↓
[產生報告]
```

### 核心資料表
1. **tags_final**: 主要標籤資料
2. **tag_embeddings**: 向量嵌入（1536 維）
3. **migration_log**: 遷移記錄

### API 端點
1. `GET /rest/v1/tags_final` - 查詢標籤
2. `POST /rest/v1/rpc/search_similar_tags` - 語意搜尋
3. `GET /rest/v1/rpc/get_category_statistics` - 統計資訊

---

## 📝 下一步行動

### 選項 1: 澄清規格細節（如需要）
```bash
/speckit.clarify
```

### 選項 2: 創建實作計畫（推薦）
```bash
/speckit.plan
```

本規格已完成並通過所有品質檢查，建議直接進入計畫階段。

---

## 📞 聯絡資訊

**Feature Owner**: 專案團隊  
**Specification Date**: 2025-10-14  
**Branch**: 001-sqlite-ags-db  
**Status**: ✅ Ready for Planning

---

## 📚 參考資料

- [完整規格文件](./spec.md)
- [品質檢查清單](./checklists/requirements.md)
- [專案開發憲法](../../.specify/memory/constitution.md)
- [階段二策略規劃](../../.specify/plans/PLAN-2025-002-PHASE2-STRATEGY.md)
- [Supabase 部署指南](../../stage1/supabase_tools/SUPABASE_DEPLOYMENT_GUIDE.md)

---

**最後更新**: 2025-10-14  
**更新者**: AI Assistant

