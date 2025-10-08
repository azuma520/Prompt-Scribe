# Prompt-Scribe - 階段二：雲端應用後端

這是 Prompt-Scribe 專案的階段二實作，負責將階段一的產出遷移至雲端並提供 API 服務。

## 📋 概述

階段二負責：
- 將 `tags.db` 遷移至 Supabase (PostgreSQL)
- 實作內容向量化功能
- 提供 RESTful API 服務
- 支援多使用者應用場景

## 🏗️ 架構

```
tags.db → 遷移腳本 → Supabase (PostgreSQL) → pgvector → API
```

## 📁 目錄結構

```
stage2/
├── supabase/               # Supabase 設定
│   ├── migrations/         # 資料庫遷移腳本
│   ├── functions/          # Edge Functions
│   └── config.toml         # Supabase 設定
├── api/                    # API 實作
│   ├── routes/             # API 路由
│   ├── services/           # 業務邏輯
│   └── middleware/         # 中介軟體
├── docs/                   # API 文件
└── README.md               # 本文件
```

## ⏳ 開發狀態

**目前狀態：** 等待階段一完成

階段二的開發將在階段一產出 `tags.db` 後開始。

## 🎯 主要功能（規劃中）

### 1. 資料遷移
- 從 SQLite 遷移至 PostgreSQL
- 資料完整性驗證
- 可重複執行的遷移腳本

### 2. 向量化
- 使用 OpenAI Embeddings 生成向量
- 儲存至 pgvector 擴展
- 支援語意搜尋

### 3. API 服務
- RESTful API endpoints
- 認證與授權
- 速率限制
- API 文件（OpenAPI/Swagger）

### 4. 多使用者支援
- 使用者管理
- 權限控制
- 資料隔離

## 📚 相關文件

- [專案開發憲法](../.specify/memory/constitution.md)
- [階段二規格文件](../.specify/specs/)（待建立）
- [雲端遷移計畫](../.specify/plans/)（待建立）

---

**本階段將在階段一完成後開始實作，嚴格遵循憲法原則。**

