# 🚀 GPT-5 Nano 快速開始指南

> **5 分鐘內完成配置和測試**

---

## ✅ 檢查清單

### 步驟 1: 準備 API Key (2 分鐘)

1. 訪問 https://platform.openai.com/api-keys
2. 創建新的 API Key
3. 複製並保存（只顯示一次！）

### 步驟 2: 配置 Zeabur (2 分鐘)

1. 訪問 https://dash.zeabur.com
2. 選擇 `prompt-scribe-api` 服務
3. 點擊 **Variables** 標籤
4. 添加以下環境變數：

```
OPENAI_API_KEY=sk-proj-你的金鑰
ENABLE_OPENAI_INTEGRATION=true
OPENAI_MODEL=gpt-5-nano
```

5. 點擊 **Save** → Zeabur 自動重新部署

### 步驟 3: 驗證配置 (1 分鐘)

```bash
# 測試配置
curl https://你的專案.zeabur.app/api/llm/test-openai-config

# 測試標籤推薦
curl -X POST https://你的專案.zeabur.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description": "cute girl with long hair"}'
```

---

## 📊 預期結果

### ✅ 配置成功

在 Zeabur Logs 中看到：

```
🤖 GPT-5 Nano 客戶端初始化
  - API Key 已設置: ✅ 是
  - 模型: gpt-5-nano
  - 功能啟用: ✅ 是
✅ OpenAI 客戶端初始化成功
```

### ✅ API 測試成功

```json
{
  "result": {
    "available": true,
    "test_response": "Hello, OpenAI!"
  }
}
```

### ✅ 標籤推薦成功

```json
{
  "metadata": {
    "algorithm": "gpt-5-nano"  // ← 確認使用 GPT-5
  }
}
```

---

## 💰 成本預估

| 使用量 | 月度成本 |
|--------|---------|
| 1,000 次 | $0.15 - $0.20 |
| 10,000 次 | $1.50 - $2.00 |
| 100,000 次 | $15.00 - $20.00 |

**結論**: 非常經濟！🎉

---

## 🔧 故障排除

### 問題 1: API Key 未識別

```
⚠️ OpenAI API key 未設置
```

**解決**: 檢查 Zeabur Variables，確認 `OPENAI_API_KEY` 正確

### 問題 2: 連接失敗

```
❌ OpenAI 連接錯誤
```

**解決**: 
1. 驗證 API Key 有效性
2. 檢查 https://status.openai.com/
3. 確認 API 額度充足

### 問題 3: 使用降級方案

```json
{
  "metadata": {
    "algorithm": "keyword_matching_fallback"
  }
}
```

**原因**: GPT-5 未啟用，系統自動使用關鍵字匹配

**解決**: 確認 `ENABLE_OPENAI_INTEGRATION=true`

---

## 📚 詳細文檔

- [完整配置指南](docs/api/GPT5_NANO_ZEABUR_CONFIG.md)
- [優化完成報告](docs/api/GPT5_NANO_OPTIMIZATION_COMPLETE.md)
- [測試腳本使用](tests/test_gpt5_nano_live.py)

---

## 💡 最佳實踐

✅ 使用 `gpt-5-nano` (最經濟)  
✅ 設置合理的 `max_tokens` (300-500)  
✅ 啟用 Redis 快取  
✅ 監控使用量和成本  
✅ 實施降級方案  

❌ 不要使用 `gpt-5` (太貴)  
❌ 不要設置過高的 `max_tokens`  
❌ 不要忽略錯誤處理  

---

**需要協助？** 查看 [故障排除指南](docs/api/GPT5_NANO_ZEABUR_CONFIG.md#故障排除) 🚑

**最後更新**: 2025-10-20

