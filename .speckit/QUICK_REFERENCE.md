# 🚀 README 優化快速參考

**用途**: 執行時快速查閱  
**完整計畫**: [README_OPTIMIZATION.plan](.speckit/README_OPTIMIZATION.plan)

---

## 📋 今天要做什麼？

### Phase 1: 緊急修正（優先！）⚡

```bash
# Task 1.1 - 修正 Placeholder (15min)
□ README.md 第 72 行：your-org → azuma520
□ README.md 第 94 行：your-project → 實際 URL
□ README.md 第 423-424, 451 行：GitHub 連結
□ 驗證：grep -r "your-org\|your-username" README.md

# Task 1.2 - 修正 Stage 2 (30min)
□ 重寫 stage2/README.md（標示已棄用，指向 src/api/）
□ 更新 README 中的 Stage 2 描述

# Task 1.3 - Live API 測試區塊 (30min)
□ 在 README 第 15 行後插入「立即試用」區塊
□ 包含 3 個 cURL 測試範例
□ 測試所有指令可執行

# Task 1.4 - 修正 Clone 指令 (5min)
□ README.md clone 指令
□ QUICK_START.md clone 指令
```

**完成 Phase 1 後你會得到**:
- ✅ README 可以直接 clone
- ✅ 新用戶可以立即測試 API
- ✅ 無 Stage 2 混淆

---

## 🔧 常用命令

### 檢查與驗證
```bash
# 檢查 placeholder
grep -r "your-org\|your-username\|your-project" README.md

# 檢查連結
markdown-link-check README.md

# 測試 API
curl https://prompt-scribe-api.vercel.app/health
```

### Git 操作
```bash
# 創建分支
git checkout -b docs/readme-optimization

# 提交單個 Phase
git add README.md stage2/README.md
git commit -m "docs: Phase 1 - fix placeholders and stage2 confusion"

# 查看變更
git diff README.md
```

---

## 📝 重要內容模板

### 1. Live API 測試區塊

```markdown
## 🚀 立即試用（5 秒開始）

### 生產環境
- **🌐 Live API**: https://prompt-scribe-api.vercel.app
- **📖 互動式文檔**: https://prompt-scribe-api.vercel.app/docs
- **❤️ 健康檢查**: https://prompt-scribe-api.vercel.app/health

### 一鍵測試
```bash
# 測試 1: 健康檢查
curl https://prompt-scribe-api.vercel.app/health

# 測試 2: 智能標籤推薦
curl -X POST https://prompt-scribe-api.vercel.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description":"cute girl in school uniform"}'
```
```

### 2. Stage 2 重寫內容

```markdown
# ⚠️ 重要通知：本目錄已棄用

## 階段二實作已完成並移至新位置

**實際路徑**: `src/api/`  
**當前狀態**: ✅ 已部署生產環境  
**Live API**: https://prompt-scribe-api.vercel.app

### 請查看
- 📂 **API 源碼**: [src/api/](../src/api/)
- 📖 **開發文檔**: [src/api/README.md](../src/api/README.md)
- 🚀 **部署指南**: [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
```

### 3. 環境變數表格

```markdown
## ⚙️ 環境變數配置

### 必需變數
| 變數名 | 說明 | 獲取方式 |
|--------|------|----------|
| `SUPABASE_URL` | Supabase 專案 URL | Dashboard → Settings → API |
| `SUPABASE_ANON_KEY` | 公開 API 金鑰 | Dashboard → Settings → API |

### 可選變數
| 變數名 | 預設值 | 說明 |
|--------|--------|------|
| `CACHE_STRATEGY` | `memory` | 快取策略 |
| `REDIS_ENABLED` | `false` | 啟用 Redis |
```

### 4. 部署對比矩陣

```markdown
| 方案 | 最適合 | 快取支援 | 難度 | 成本 |
|------|--------|----------|------|------|
| **Vercel** | 個人專案 | 僅記憶體 | ⭐ | $0-20 |
| **Railway** | 中小型應用 | Redis ✅ | ⭐⭐ | $15-25 |
| **Docker** | 完全控制 | 全功能 ✅ | ⭐⭐⭐ | 自訂 |
```

---

## ✅ 快速檢查清單

### 完成 Phase 1
- [ ] 所有 placeholder 已替換
- [ ] stage2/README.md 已重寫
- [ ] Live API 測試區塊已添加
- [ ] Clone 指令已修正
- [ ] 所有 cURL 測試通過

### 完成 Phase 2
- [ ] 環境變數表格已添加
- [ ] 部署對比矩陣已添加
- [ ] GitHub Actions badge 已添加

### 完成 Phase 3
- [ ] 「5 分鐘理解」區塊已添加
- [ ] FAQ 已添加
- [ ] QUICK_START 已整合
- [ ] README 結構已重組

### 完成 Phase 4
- [ ] 所有連結驗證通過
- [ ] CHANGELOG 已更新
- [ ] Git 已提交並標籤

---

## 🎯 效果驗證

### 立即測試
```bash
# 1. 按照新 README clone 專案（如果有協作者）
git clone https://github.com/azuma520/Prompt-Scribe.git

# 2. 複製 cURL 指令測試
# （應該可以直接執行）

# 3. 計時：從看到 README 到完成首次 API 測試
# 目標：< 5 分鐘
```

### 找新用戶測試
- 給一個從未見過專案的人
- 只給 README 連結
- 記錄卡住的地方
- 收集反饋

---

## 💡 執行技巧

### 小步前進
- 每完成一個 Task 就 commit
- 不要一次修改太多
- 隨時可以回退

### 頻繁驗證
- 每次修改後預覽 Markdown
- 測試所有新增的連結
- 執行所有新增的指令

### 尋求反饋
- Phase 1 完成後可以給人看
- 收集意見再繼續
- 不完美沒關係，持續改進

---

## 📞 遇到問題？

### 常見問題

**Q: 不確定某個 placeholder 要改成什麼？**
- 查看 Git remote URL：`git remote -v`
- 或保留但標註 `[YOUR_GITHUB_USERNAME]`

**Q: 不知道某個功能是否已實現？**
- 查看 `src/api/main.py` 確認路由
- 查看 CHANGELOG.md 確認版本

**Q: 時間不夠怎麼辦？**
- 優先完成 Phase 1（最重要）
- 其他可以分散到多天

### 需要幫助
- 查看完整計畫：[README_OPTIMIZATION.plan](.speckit/README_OPTIMIZATION.plan)
- 查看摘要：[OPTIMIZATION_SUMMARY.md](.speckit/OPTIMIZATION_SUMMARY.md)
- 建立 Issue 討論

---

**最後更新**: 2025-10-17  
**當前 Phase**: Phase 1 (緊急修正)  
**下一個任務**: Task 1.1 (修正 Placeholder)

💪 **加油！完成 Phase 1 就成功一大半了！**

