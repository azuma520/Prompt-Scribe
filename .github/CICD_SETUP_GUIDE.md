# CI/CD 設置指南

**建立日期**: 2025-10-15  
**目的**: 自動化測試和部署流程

---

## 📋 已建立的 Workflows

### 1. `api-tests.yml` - API 自動化測試 ⭐

**觸發條件**:
- Push 到 main/develop/001-sqlite-ags-db 分支
- Pull Request 到 main/develop
- 只在 `src/api/**` 變更時執行

**執行內容**:
```
✅ Python 多版本測試（3.9-3.13）
✅ 單元測試（test_cache.py）
✅ 效能測試（test_load_performance.py）
✅ 代碼覆蓋率報告
✅ 上傳測試結果到 Codecov
```

**預期時間**: 3-5 分鐘

### 2. `api-deploy.yml` - 部署工作流程

**觸發條件**:
- Push 到 main 分支
- 手動觸發（workflow_dispatch）

**執行內容**:
```
✅ 快速測試驗證
✅ 建置檢查
✅ 部署準備
⏸️ 實際部署（需配置）
```

**支援平台**:
- Vercel（已註解範例）
- Railway（已註解範例）
- Docker（已註解範例）

### 3. `performance-check.yml` - 效能監控

**觸發條件**:
- 每天 UTC 2:00 AM
- 手動觸發

**執行內容**:
```
✅ 執行完整效能測試
✅ 生成效能報告
✅ 檢查效能回歸
⚠️ 效能下降時自動建立 Issue
```

---

## 🚀 啟用 CI/CD

### Step 1: GitHub Secrets 設置

在 GitHub 倉庫設置 → Secrets → Actions 中添加:

**必要**（用於整合測試）:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

**可選**（用於部署）:
```
# Vercel
VERCEL_TOKEN=your-vercel-token
ORG_ID=your-org-id
PROJECT_ID=your-project-id

# Railway
RAILWAY_TOKEN=your-railway-token

# Docker Hub
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-password
```

### Step 2: 啟用 Actions

1. 進入 GitHub 倉庫
2. 點擊 "Actions" 標籤
3. 選擇啟用 GitHub Actions
4. Workflows 會自動偵測 `.github/workflows/` 中的文件

### Step 3: 測試 CI/CD

```bash
# 觸發測試
git add .
git commit -m "test: trigger CI/CD"
git push

# 查看結果
# GitHub → Actions 標籤
```

---

## 📊 CI/CD 執行流程

### Push 到功能分支
```
1. api-tests.yml 觸發
2. 執行單元測試和效能測試
3. 生成測試報告
4. 如果失敗，阻止合併
```

### Pull Request
```
1. api-tests.yml 執行（所有測試）
2. integration-test 執行（如果有 Supabase）
3. lint 執行（代碼品質檢查）
4. 在 PR 中留言測試結果
5. 所有檢查通過才能合併
```

### 合併到 main
```
1. 所有測試重新執行
2. api-deploy.yml 觸發
3. 部署到生產環境（如配置）
4. 通知完成
```

### 每日效能檢查
```
1. performance-check.yml 每天執行
2. 生成效能報告
3. 如果效能下降，建立 Issue
4. 主動發現問題
```

---

## 🎯 效益

### 自動化測試
- ✅ 每次提交自動測試
- ✅ 及早發現問題
- ✅ 防止破壞性變更
- ✅ 多 Python 版本驗證

### 代碼品質
- ✅ 自動格式檢查
- ✅ 自動類型檢查
- ✅ 覆蓋率追蹤
- ✅ 持續改善

### 效能監控
- ✅ 每日效能檢查
- ✅ 自動回歸偵測
- ✅ 效能趨勢追蹤
- ✅ 主動告警

### 部署自動化
- ✅ 一鍵部署
- ✅ 部署前驗證
- ✅ 回滾機制
- ✅ 部署記錄

---

## 📝 最佳實踐

### 開發流程

```bash
# 1. 建立功能分支
git checkout -b feature/new-feature

# 2. 開發和測試
# 本地運行: pytest tests/ -v

# 3. 提交變更
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 4. CI/CD 自動執行
# GitHub Actions 自動測試

# 5. 建立 Pull Request
# 等待所有檢查通過

# 6. 合併到 main
# 自動部署（如已配置）
```

### 測試策略

```
本地開發:
- 快速測試: pytest tests/test_cache.py
- 完整測試: pytest tests/ -v

Push 前:
- 運行完整測試套件
- 確保所有測試通過

CI/CD:
- 自動執行所有測試
- 多版本驗證
- 效能檢查
```

---

## 🔧 故障排除

### 測試失敗

**問題**: CI/CD 測試失敗  
**檢查**:
1. 查看 GitHub Actions 日誌
2. 本地重現問題：`pytest tests/ -v`
3. 修復後重新提交

### 部署失敗

**問題**: 部署工作流程失敗  
**檢查**:
1. 確認 Secrets 已設置
2. 確認平台配置正確
3. 查看部署日誌

### 效能下降

**問題**: 每日效能檢查發現回歸  
**處理**:
1. 查看 Issue（自動建立）
2. 比對近期變更
3. 識別瓶頸並優化

---

## 📈 監控指標

### 測試健康度
- 通過率趨勢
- 失敗測試類型
- 測試執行時間

### 代碼品質
- 覆蓋率變化
- Linting 問題數
- 類型檢查通過率

### 效能趨勢
- P90/P95/P99 延遲
- 吞吐量變化
- 快取命中率

---

## ✅ 下一步

1. **設置 GitHub Secrets**
   - 添加 Supabase 憑證
   - 添加部署憑證（如需要）

2. **測試 CI/CD**
   - 提交小變更測試
   - 驗證所有工作流程

3. **配置部署**
   - 選擇部署平台
   - 取消註解相應步驟
   - 測試部署流程

4. **監控設置**
   - 啟用通知
   - 設置告警規則
   - 定期查看報告

---

**CI/CD 已準備就緒！** 🎉

提交變更後，GitHub Actions 將自動執行。

