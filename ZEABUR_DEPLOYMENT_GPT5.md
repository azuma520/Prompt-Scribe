# Zeabur 部署指南 - GPT-5 Mini

## 🎯 部署概述

本指南將協助您在 Zeabur 上部署啟用 GPT-5 Mini 的 Prompt-Scribe API。

---

## 📋 前置準備

### 確認事項

- ✅ 代碼已推送到 Git: `9a94e60`
- ✅ GPT-5 Mini 本地測試通過
- ✅ OpenAI API Key 有 GPT-5 訪問權限
- ✅ Supabase 配置正確

---

## 🔧 Zeabur 環境變數設置

### 步驟 1: 登入 Zeabur

1. 訪問 https://zeabur.com
2. 登入您的帳戶
3. 選擇 Prompt-Scribe 專案

### 步驟 2: 設置環境變數

進入專案設置 → 環境變數 (Environment Variables)

#### 必填變數

```bash
# OpenAI API Key
OPENAI_API_KEY=您的OpenAI-API-Key

# Supabase 配置  
SUPABASE_URL=您的Supabase-URL
SUPABASE_ANON_KEY=您的Supabase-Anon-Key
```

#### 可選變數（已有預設值）

```bash
# OpenAI 模型（預設: gpt-5-mini）
OPENAI_MODEL=gpt-5-mini

# 啟用 OpenAI 集成（預設: true）
ENABLE_OPENAI_INTEGRATION=true

# 日誌級別（預設: INFO）
LOG_LEVEL=INFO

# 調試模式（預設: false）
DEBUG=false
```

### 步驟 3: 觸發重新部署

1. 保存環境變數
2. Zeabur 會自動重新部署
3. 等待部署完成（約 2-3 分鐘）

---

## 🧪 驗證部署

### 測試 1: Health Check

```bash
curl https://your-app.zeabur.app/health
```

**預期回應**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": 1761013974
}
```

### 測試 2: OpenAI 配置檢查

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
      "model": "gpt-5-mini",
      "enabled": true
    }
  }
}
```

**檢查點**:
- ✅ `available: true`
- ✅ `model: "gpt-5-mini"`
- ✅ `enabled: true`

### 測試 3: 標籤推薦

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
    {
      "name": "long_hair",
      "score": 0.95
    },
    {
      "name": "blue_eyes", 
      "score": 0.95
    }
    // ... 更多標籤
  ],
  "metadata": {
    "source": "gpt-5-mini",
    "total_found": 10
  }
}
```

---

## 📊 部署後監控

### 檢查 Zeabur 日誌

在 Zeabur Dashboard → Logs 中查看：

**應該看到**:
```
🤖 GPT-5 Nano 客戶端初始化
  - API Key 已設置: ✅ 是
  - 模型: gpt-5-mini
  - 功能啟用: ✅ 是
  - GPT-5 系列: ✅ 是
```

**不應該看到**:
```
❌ API Key 未設置
❌ 功能啟用: 否
⚠️ 模型測試失敗
```

### 監控指標

| 指標 | 目標值 | 說明 |
|------|--------|------|
| 回應時間 | < 3秒 | API 回應速度 |
| 成功率 | > 95% | 請求成功率 |
| 錯誤率 | < 5% | API 錯誤率 |
| 成本 | ~$0.0003/請求 | GPT-5 Mini 成本 |

---

## 🐛 故障排查

### 問題 1: "API Key 未設置"

**檢查**:
1. Zeabur 環境變數是否正確設置？
2. 環境變數名稱是否正確？（`OPENAI_API_KEY`）
3. 是否有多餘的空格？

**解決**:
重新設置環境變數並重新部署

### 問題 2: "模型: gpt-4o-mini"

**原因**: 環境變數可能沒有設置 `OPENAI_MODEL`

**解決**:
```bash
# 在 Zeabur 添加
OPENAI_MODEL=gpt-5-mini
```

### 問題 3: "temperature 參數不支持"

**狀態**: ✅ 已修復
- 代碼已更新，GPT-5 使用正確的參數

### 問題 4: 回應為空或錯誤

**檢查**:
1. API Key 是否有 GPT-5 訪問權限？
2. OpenAI 帳戶餘額是否充足？
3. 查看 Zeabur 日誌中的詳細錯誤

---

## 📈 成功指標

### 立即驗證（部署後 5 分鐘）

- [ ] Health endpoint 返回 200
- [ ] OpenAI config 顯示 gpt-5-mini
- [ ] 標籤推薦返回有效結果
- [ ] 日誌顯示正確的模型初始化

### 短期監控（1 週內）

- [ ] API 回應時間穩定在 < 3秒
- [ ] 成功率 > 95%
- [ ] 沒有異常錯誤
- [ ] 成本在預期範圍內

### 長期評估（1 個月）

- [ ] 用戶滿意度提升
- [ ] 標籤質量改善
- [ ] 成本效益良好
- [ ] 考慮進一步優化

---

## 📚 相關文檔

| 文檔 | 用途 |
|------|------|
| `DEPLOY_READY_SUMMARY.md` | 部署準備總結 |
| `SECURITY_BEST_PRACTICES.md` | 安全最佳實踐 |
| `GPT5_TEST_PLAN.md` | 測試計劃 |
| `SETUP_GPT5_ENV.md` | 環境設置詳細指南 |

---

## 🎯 下一步行動

### 立即（今天）

1. ✅ 代碼已推送到 Git
2. ⬜ 在 Zeabur 設置環境變數
3. ⬜ 觸發重新部署
4. ⬜ 驗證部署結果

### 短期（本週）

1. ⬜ 監控 API 性能
2. ⬜ 收集用戶反饋
3. ⬜ 評估成本
4. ⬜ 微調參數（如需要）

### 中期（本月）

1. ⬜ 分析使用數據
2. ⬜ 優化 prompt
3. ⬜ 考慮參數調整
4. ⬜ 評估是否需要 Responses API

---

## 💡 專業建議

### GPT-5 Mini vs Nano 選擇

基於測試結果：

**gpt-5-mini** (當前選擇):
- ✅ 最佳標籤質量（10個標籤）
- ✅ 高信心度（0.9）
- ✅ 合理成本（284 tokens）
- ✅ **推薦用於生產環境**

**gpt-5-nano** (備選):
- ✅ 也能產生 10 個標籤
- ⚠️ Token 稍多（389）
- ✅ 成本更低
- ✅ 可用於高吞吐量場景

### 參數配置建議

```python
當前配置（已優化）:
  reasoning_effort: "low"    # ✅ 適合簡單分類
  verbosity: "low"           # ✅ 簡潔JSON輸出
  max_completion_tokens: 500 # ✅ 足夠標籤生成
```

**未來調整方向**:
- 如需更詳細的標籤，可嘗試 `verbosity: "medium"`
- 如需更深入的分析，可嘗試 `reasoning_effort: "medium"`

---

## 🎉 部署清單

### 在 Zeabur Dashboard 完成

- [ ] 設置 `OPENAI_API_KEY`
- [ ] 設置 `SUPABASE_URL`（可能已有）
- [ ] 設置 `SUPABASE_ANON_KEY`（可能已有）
- [ ] 保存並觸發重新部署
- [ ] 等待部署完成
- [ ] 測試 health endpoint
- [ ] 測試 OpenAI config endpoint
- [ ] 測試標籤推薦功能
- [ ] 檢查日誌確認模型為 gpt-5-mini

---

**準備好部署了！** 🚀

需要我協助設置 Zeabur 環境變數嗎？
