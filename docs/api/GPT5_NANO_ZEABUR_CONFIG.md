# 🤖 GPT-5 Nano 在 Zeabur 上的配置指南

> **更新日期**: 2025-10-20  
> **狀態**: Production Ready

---

## 📋 概述

本指南將協助您在 Zeabur 上正確配置 GPT-5 Nano 客戶端，包括環境變數設置、測試驗證和故障排除。

---

## 🔑 步驟 1: 獲取 OpenAI API Key

### 1.1 登入 OpenAI Platform

訪問: https://platform.openai.com/

### 1.2 創建 API Key

1. 點擊右上角個人頭像
2. 選擇 **API Keys**
3. 點擊 **Create new secret key**
4. 為 Key 命名（如: "prompt-scribe-prod"）
5. **複製並保存** - Key 只會顯示一次！

⚠️ **重要**: 請妥善保管您的 API Key，不要將其提交到 Git 或公開分享。

---

## ⚙️ 步驟 2: 在 Zeabur 配置環境變數

### 2.1 進入 Zeabur Dashboard

1. 訪問: https://dash.zeabur.com
2. 選擇您的專案
3. 選擇 `prompt-scribe-api` 服務

### 2.2 添加環境變數

點擊 **Variables** 標籤，添加以下環境變數：

#### 必需變數

| 變數名 | 值 | 說明 |
|-------|---|------|
| `OPENAI_API_KEY` | `sk-proj-...` | 您的 OpenAI API Key |
| `ENABLE_OPENAI_INTEGRATION` | `true` | 啟用 OpenAI 整合 |

#### 可選變數（使用預設值）

| 變數名 | 預設值 | 說明 |
|-------|-------|------|
| `OPENAI_MODEL` | `gpt-5-nano` | 使用的模型 |
| `OPENAI_MAX_TOKENS` | `500` | 最大生成 tokens |
| `OPENAI_TEMPERATURE` | `0.7` | 溫度參數（GPT-5 不支持） |
| `OPENAI_TIMEOUT` | `30` | API 超時時間（秒） |

### 2.3 模型選擇建議

#### GPT-5 系列（推薦）

| 模型 | 價格 | 速度 | 適用場景 |
|-----|------|------|---------|
| **gpt-5-nano** ⭐ | 最便宜 | 最快 | 標籤推薦（推薦） |
| `gpt-5-mini` | 中等 | 快 | 複雜推理 |
| `gpt-5` | 最貴 | 中等 | 高級任務 |

#### GPT-4 系列（備選）

| 模型 | 說明 |
|-----|------|
| `gpt-4o-mini` | 快速經濟模型 |
| `gpt-4o` | 多模態旗艦模型 |

**建議**: 使用 `gpt-5-nano` 以獲得最佳性價比！

### 2.4 保存配置

點擊 **Save** 按鈕，Zeabur 會自動重新部署服務。

---

## ✅ 步驟 3: 驗證配置

### 3.1 查看部署日誌

在 Zeabur Dashboard 的 **Logs** 標籤中，查找以下日誌：

```
============================================================
🤖 GPT-5 Nano 客戶端初始化
  - API Key 已設置: ✅ 是
  - 模型: gpt-5-nano
  - 最大 Tokens: 500
  - 超時時間: 30秒
  - 功能啟用: ✅ 是
  - OpenAI 庫: ✅ 已安裝
  - 模型類型: GPT-5 系列
  - 注意: GPT-5 不支持 temperature 參數
============================================================
✅ OpenAI 客戶端初始化成功
```

✅ 如果看到以上日誌，表示配置成功！

❌ 如果看到以下日誌：

```
⚠️ OpenAI API key 未設置 (請在環境變數中設置 OPENAI_API_KEY)
```

請返回步驟 2.2 檢查環境變數設置。

### 3.2 測試配置端點

使用 curl 測試配置：

```bash
curl -X GET "https://你的專案名稱.zeabur.app/api/llm/test-openai-config"
```

**成功回應範例**:

```json
{
  "status": "success",
  "message": "OpenAI 配置測試完成",
  "result": {
    "available": true,
    "error": null,
    "config": {
      "api_key_set": true,
      "model": "gpt-5-nano",
      "max_tokens": 500,
      "temperature": 0.7,
      "timeout": 30,
      "enabled": true
    },
    "test_response": "Hello, OpenAI!"
  }
}
```

### 3.3 測試標籤推薦

測試實際的標籤推薦功能：

```bash
curl -X POST "https://你的專案名稱.zeabur.app/api/llm/recommend-tags" \
  -H "Content-Type: application/json" \
  -d '{"description": "a cute girl with long hair", "max_tags": 5}'
```

**成功回應範例**:

```json
{
  "query": "a cute girl with long hair",
  "recommended_tags": [
    {
      "tag": "1girl",
      "confidence": 0.9,
      "popularity_tier": "very_popular"
    },
    {
      "tag": "long_hair",
      "confidence": 0.92,
      "popularity_tier": "very_popular"
    }
  ],
  "metadata": {
    "algorithm": "gpt-5-nano",
    "processing_time_ms": 1200.5
  }
}
```

✅ 如果 `metadata.algorithm` 是 `"gpt-5-nano"`，表示 GPT-5 Nano 正在正常工作！

---

## 💰 步驟 4: 成本監控

### 4.1 理解成本結構

**GPT-5 Nano 定價 (2025)**:
- Input: $0.00002 / 1K tokens
- Output: $0.00008 / 1K tokens

**單次標籤推薦預估**:
- Prompt tokens: ~300
- Completion tokens: ~150
- **總成本: ~$0.00018** (非常便宜！)

**月度成本預估**:
- 1,000 次調用: **$0.18**
- 10,000 次調用: **$1.80**
- 100,000 次調用: **$18.00**

### 4.2 查看使用量日誌

在 Zeabur Dashboard 的 **Logs** 中，每次 API 調用後會顯示：

```
💰 API 使用量統計:
  - Prompt tokens: 287
  - Completion tokens: 142
  - Total tokens: 429
  - Input cost: $0.000006
  - Output cost: $0.000011
  - Total cost: $0.000017 USD
  - 月度成本預估:
    • 1,000 次調用: $0.02
    • 10,000 次調用: $0.17
```

### 4.3 在 OpenAI Dashboard 監控

1. 訪問: https://platform.openai.com/usage
2. 查看實時使用量和成本
3. 設置用量限制和警告

---

## 🔧 故障排除

### 問題 1: API Key 未被識別

**症狀**:
```
⚠️ OpenAI API key 未設置
```

**解決方案**:
1. 檢查 Zeabur Variables 中 `OPENAI_API_KEY` 是否正確設置
2. 確認沒有多餘的空格或換行
3. 重新部署服務

### 問題 2: OpenAI 連接失敗

**症狀**:
```
❌ OpenAI 連接錯誤
  - 可能原因:
    1. 網路連接問題
    2. API 金鑰無效
    3. OpenAI 服務暫時不可用
```

**解決方案**:
1. 驗證 API Key 是否正確
2. 檢查 OpenAI Status: https://status.openai.com/
3. 確認 Zeabur 沒有網路限制
4. 檢查 API Key 是否有足夠的額度

### 問題 3: 速率限制

**症狀**:
```
❌ OpenAI 速率限制
```

**解決方案**:
1. 減少請求頻率
2. 實施請求佇列
3. 考慮升級 OpenAI 方案
4. 使用降級方案（關鍵字匹配）

### 問題 4: 模型不存在

**症狀**:
```
❌ OpenAI API 錯誤
  - 狀態碼: 404
  - 錯誤訊息: model not found
```

**解決方案**:
1. 確認模型名稱正確（`gpt-5-nano` 而不是 `gpt5-nano`）
2. 檢查您的 OpenAI 帳戶是否有權訪問該模型
3. 嘗試使用 `gpt-4o-mini` 作為備選

### 問題 5: JSON 解析失敗

**症狀**:
```
❌ JSON 解析失敗
Raw response: ...
```

**解決方案**:
1. 檢查 Prompt 是否清楚要求 JSON 格式
2. 增加 `max_tokens` 避免回應被截斷
3. 使用 `response_format={"type": "json_object"}` (API 參數)

---

## 📊 效能優化建議

### 1. 啟用快取

在 Zeabur 添加 Redis 服務：

```bash
# 在 Zeabur Dashboard
1. 點擊 "Add Service"
2. 選擇 "Redis"
3. 添加環境變數
```

環境變數:
```
CACHE_STRATEGY=hybrid
REDIS_ENABLED=true
REDIS_URL=<Zeabur Redis URL>
```

### 2. 調整超時時間

對於複雜請求，增加超時時間：

```
OPENAI_TIMEOUT=60
```

### 3. 優化 Token 使用

減少不必要的 Prompt 內容：

```
OPENAI_MAX_TOKENS=300  # 標籤推薦通常不需要 500
```

---

## 🎯 最佳實踐

### 1. 安全性

- ✅ 使用環境變數存儲 API Key
- ✅ 不要將 API Key 提交到 Git
- ✅ 定期輪換 API Key
- ✅ 設置 IP 白名單（如果可能）

### 2. 成本控制

- ✅ 使用 GPT-5 Nano 而不是更貴的模型
- ✅ 設置月度預算限制
- ✅ 監控使用量趨勢
- ✅ 實施請求快取

### 3. 可靠性

- ✅ 實施降級方案（關鍵字匹配）
- ✅ 添加重試機制
- ✅ 記錄詳細日誌
- ✅ 設置警報通知

### 4. 效能

- ✅ 使用 Redis 快取
- ✅ 優化 Prompt 長度
- ✅ 批次處理請求
- ✅ 監控響應時間

---

## 📚 相關資源

- [OpenAI API 文檔](https://platform.openai.com/docs)
- [GPT-5 Model Card](https://platform.openai.com/docs/models/gpt-5)
- [OpenAI Pricing](https://openai.com/pricing)
- [Zeabur 文檔](https://zeabur.com/docs)
- [專案 README](../../README.md)

---

## 💡 需要協助？

如果您遇到問題：

1. 查看 Zeabur 部署日誌
2. 使用測試端點驗證配置
3. 參考故障排除部分
4. 聯繫開發團隊

---

**最後更新**: 2025-10-20  
**維護者**: Prompt-Scribe Team  
**狀態**: ✅ 生產就緒

