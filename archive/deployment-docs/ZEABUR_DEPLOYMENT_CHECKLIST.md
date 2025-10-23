# Zeabur 部署清單 ✅

## 🎯 目標

在 Zeabur 上部署啟用 GPT-5 Mini 的 Prompt-Scribe API

---

## ✅ 已完成的準備工作

### 代碼準備
- [x] GPT-5 Mini 代碼集成完成
- [x] 所有測試通過
- [x] 專案結構整理完成
- [x] 代碼已推送到 GitHub (commit: `bdf4e87`)

### 文檔準備
- [x] 部署指南已完成
- [x] 環境設置指南已完成
- [x] 安全最佳實踐已完成
- [x] 測試計劃已完成

---

## 📋 Zeabur 部署步驟

### 步驟 1: 登入 Zeabur Dashboard

1. 訪問 https://zeabur.com
2. 登入您的帳戶
3. 找到 Prompt-Scribe 專案

### 步驟 2: 設置環境變數 ⚠️ **關鍵步驟**

#### 必填環境變數

進入專案 → Settings → Environment Variables

```bash
# 1. OpenAI API Key（從您的安全儲存複製）
OPENAI_API_KEY=您的-OpenAI-API-Key

# 2. Supabase URL（可能已設置）
SUPABASE_URL=https://fumuvmbhmmzkenizksyq.supabase.co

# 3. Supabase Anon Key（從您的安全儲存複製）
SUPABASE_ANON_KEY=您的-Supabase-Anon-Key
```

#### 可選環境變數（已有預設值）

```bash
# OpenAI 模型（預設: gpt-5-mini）
OPENAI_MODEL=gpt-5-mini

# 啟用 OpenAI 集成（預設: true）
ENABLE_OPENAI_INTEGRATION=true
```

### 步驟 3: 保存並部署

1. 點擊 "Save" 保存環境變數
2. Zeabur 會自動觸發重新部署
3. 等待部署完成（約 2-3 分鐘）
4. 查看部署日誌確認成功

### 步驟 4: 驗證部署

#### 測試 1: Health Check

```bash
curl https://your-app.zeabur.app/health
```

**預期回應**:
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "timestamp": 1761013974
}
```

#### 測試 2: OpenAI 配置檢查

```bash
curl https://your-app.zeabur.app/api/llm/test-openai-config
```

**預期回應**:
```json
{
  "status": "success",
  "result": {
    "available": true,
    "config": {
      "model": "gpt-5-mini",    ← 確認這裡！
      "enabled": true
    }
  }
}
```

#### 測試 3: GPT-5 Mini 標籤推薦

```bash
curl -X POST https://your-app.zeabur.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{
    "description": "一個長髮藍眼的動漫女孩",
    "use_llm": true
  }'
```

**預期回應**:
```json
{
  "recommendations": [
    {"name": "long_hair", "score": 0.95},
    {"name": "blue_eyes", "score": 0.95},
    {"name": "1girl", "score": 0.90},
    // ... 約 10 個標籤
  ],
  "metadata": {
    "source": "gpt-5-mini",  ← 確認使用 GPT-5!
    "llm_used": true
  }
}
```

---

## 🔍 檢查 Zeabur 日誌

### 應該看到的日誌

```
🤖 GPT-5 Nano 客戶端初始化
  - API Key 已設置: ✅ 是
  - 模型: gpt-5-mini          ← 確認！
  - 功能啟用: ✅ 是
  - GPT-5 系列: ✅ 是        ← 確認！
  
📡 調用 OpenAI API
  - 模型: gpt-5-mini
  - Max completion tokens: 500  ← GPT-5 參數
  - Reasoning effort: low       ← GPT-5 參數
  - Verbosity: low              ← GPT-5 參數
  - Temperature: N/A (GPT-5 不支持)

✅ API 回應成功
📦 回應內容:
  - 長度: 250-350 字符        ← 正常範圍
  - Tags: 8-10 個             ← 預期數量
```

### 不應該看到的錯誤

```
❌ API Key 未設置
❌ temperature 參數不支持
❌ max_tokens 參數不支持
⚠️ 回應長度: 0 字符
```

---

## ⚠️ 常見問題排查

### 問題 1: 日誌顯示 "API Key 未設置"

**解決**:
1. 確認在 Zeabur Dashboard 中設置了 `OPENAI_API_KEY`
2. 確認環境變數名稱拼寫正確
3. 點擊 "Redeploy" 重新部署

### 問題 2: 日誌顯示 "model: gpt-4o-mini"

**解決**:
```bash
# 在 Zeabur 添加環境變數
OPENAI_MODEL=gpt-5-mini

# 然後重新部署
```

### 問題 3: "temperature 參數不支持" 錯誤

**狀態**: ✅ 應該已修復
- 如果仍出現，確認代碼是最新版本
- 檢查 Git commit: `bdf4e87`

### 問題 4: 標籤推薦返回錯誤

**檢查**:
1. OpenAI API Key 是否有效？
2. 帳戶餘額是否充足？
3. 查看詳細日誌錯誤訊息

---

## 📊 成功標準

### 必須達成 (Critical)

- [ ] Health endpoint 返回 200
- [ ] OpenAI config 顯示 `model: "gpt-5-mini"`
- [ ] 標籤推薦返回 8-10 個標籤
- [ ] JSON 驗證成功
- [ ] 沒有錯誤日誌

### 應該達成 (Important)

- [ ] 回應時間 < 3 秒
- [ ] 標籤質量高（相關性強）
- [ ] 信心度 > 0.85
- [ ] Token 使用合理（< 500）

---

## 📚 參考資料

### 部署相關

- `ZEABUR_DEPLOYMENT_GPT5.md` - 詳細部署指南
- `DEPLOY_READY_SUMMARY.md` - 部署準備總結
- `SETUP_GPT5_ENV.md` - 環境設置指南

### 技術文檔

- `docs/api/GPT5_MINI_IMPLEMENTATION_COMPLETE.md` - 完整技術報告
- `SECURITY_BEST_PRACTICES.md` - 安全指南

### 測試工具（本地）

- `diagnose_model.py` - 診斷工具
- `run_server.py` - 本地伺服器

---

## 🎯 部署後行動

### 立即（部署後 10 分鐘內）

1. [ ] 測試所有 API 端點
2. [ ] 檢查日誌確認無錯誤
3. [ ] 驗證 GPT-5 Mini 正常工作
4. [ ] 記錄初始性能數據

### 短期（1 週內）

1. [ ] 監控 API 性能
2. [ ] 收集使用數據
3. [ ] 評估成本
4. [ ] 記錄用戶反饋

### 長期（1 個月）

1. [ ] 分析性能趨勢
2. [ ] 優化參數配置
3. [ ] 考慮進一步改進
4. [ ] 更新文檔

---

## 🎉 準備完成！

### 當前狀態

```yaml
代碼: ✅ 已推送到 GitHub
文檔: ✅ 完整
測試: ✅ 通過
安全: ✅ 保護完善
結構: ✅ 整潔有序
```

### 您現在需要做的

**唯一剩下的步驟**:

1. 登入 Zeabur Dashboard
2. 設置環境變數（見上方）
3. 保存並等待部署
4. 測試驗證

**預計時間**: 10 分鐘

---

**一切準備就緒，等待您的部署！** 🚀
