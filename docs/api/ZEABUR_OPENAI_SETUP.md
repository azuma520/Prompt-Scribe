# 🔑 Zeabur 環境變數設置指南 - OpenAI GPT-5 Nano

## 📋 設置步驟

### 1. 🔑 獲取 OpenAI API 金鑰

1. 前往 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登入您的帳戶
3. 點擊 "Create new secret key"
4. 複製生成的 API 金鑰（格式：`sk-...`）

⚠️ **重要**: 金鑰只會顯示一次，請妥善保存！

### 2. 🌐 在 Zeabur 設置環境變數

#### 方法一：透過 Zeabur Dashboard
1. 登入 [Zeabur Dashboard](https://dash.zeabur.com)
2. 選擇您的 Prompt-Scribe 專案
3. 進入 **Environment Variables** 頁面
4. 添加以下環境變數：

```bash
# OpenAI 配置
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-5-nano
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7
OPENAI_TIMEOUT=30
ENABLE_OPENAI_INTEGRATION=true
```

#### 方法二：透過 Zeabur CLI
```bash
# 安裝 Zeabur CLI
npm install -g @zeabur/cli

# 登入
zeabur login

# 設置環境變數
zeabur env set OPENAI_API_KEY=sk-your-actual-api-key-here
zeabur env set OPENAI_MODEL=gpt-5-nano
zeabur env set OPENAI_MAX_TOKENS=500
zeabur env set OPENAI_TEMPERATURE=0.7
zeabur env set OPENAI_TIMEOUT=30
zeabur env set ENABLE_OPENAI_INTEGRATION=true
```

### 3. 🔄 重新部署

設置環境變數後，需要重新部署應用：

```bash
# 透過 Zeabur Dashboard
# 點擊 "Redeploy" 按鈕

# 或透過 CLI
zeabur deploy
```

## 🛡️ 安全注意事項

### ✅ 正確做法
- ✅ 只在 Zeabur 環境變數中設置
- ✅ 使用 `ENABLE_OPENAI_INTEGRATION=true` 控制開關
- ✅ 定期輪換 API 金鑰
- ✅ 監控 API 使用量

### ❌ 錯誤做法
- ❌ 不要在代碼中硬編碼 API 金鑰
- ❌ 不要提交到 Git 倉庫
- ❌ 不要在客戶端暴露 API 金鑰
- ❌ 不要分享 API 金鑰

## 🔍 驗證設置

### 1. 檢查環境變數
在您的 API 中添加測試端點：

```python
# 在 src/api/routers/llm/recommendations.py 中添加
@router.get("/test-openai-config")
async def test_openai_config():
    """測試 OpenAI 配置"""
    import os
    
    config = {
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "openai_model": os.getenv("OPENAI_MODEL"),
        "openai_max_tokens": os.getenv("OPENAI_MAX_TOKENS"),
        "openai_temperature": os.getenv("OPENAI_TEMPERATURE"),
        "openai_timeout": os.getenv("OPENAI_TIMEOUT"),
        "integration_enabled": os.getenv("ENABLE_OPENAI_INTEGRATION")
    }
    
    return {
        "status": "success",
        "config": config,
        "message": "OpenAI 配置檢查完成"
    }
```

### 2. 測試 API 調用
```bash
# 測試配置
curl https://prompt-scribe-api.zeabur.app/api/llm/test-openai-config

# 測試 GPT-5 Nano 調用
curl -X POST https://prompt-scribe-api.zeabur.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description": "美食推薦"}'
```

## 💰 成本控制

### 1. 設置使用限制
在 OpenAI Dashboard 中：
1. 前往 [Usage Limits](https://platform.openai.com/account/billing/limits)
2. 設置月度使用限制（建議 $10-50）
3. 設置每分鐘請求限制

### 2. 監控使用量
```python
# 添加使用量追蹤
import logging

def track_openai_usage(response):
    """追蹤 OpenAI API 使用量"""
    if hasattr(response, 'usage'):
        usage = response.usage
        logging.info(f"OpenAI 使用量 - 輸入: {usage.prompt_tokens}, "
                    f"輸出: {usage.completion_tokens}, "
                    f"總計: {usage.total_tokens}")
        
        # 估算成本（GPT-5 Nano 價格待確認）
        estimated_cost = usage.total_tokens * 0.00001  # 假設價格
        logging.info(f"估算成本: ${estimated_cost:.4f}")
```

## 🚀 部署檢查清單

### 部署前檢查
- [ ] OpenAI API 金鑰已設置
- [ ] 所有環境變數已配置
- [ ] 功能開關已啟用
- [ ] 使用限制已設置
- [ ] 監控機制已就緒

### 部署後驗證
- [ ] 環境變數測試通過
- [ ] GPT-5 Nano API 調用成功
- [ ] 錯誤處理正常運作
- [ ] 回退機制有效
- [ ] 使用量監控正常

## 🔧 故障排除

### 常見問題

#### 1. API 金鑰無效
```
錯誤: Invalid API key
解決: 檢查金鑰格式是否正確（以 sk- 開頭）
```

#### 2. 環境變數未設置
```
錯誤: OPENAI_API_KEY not found
解決: 確認在 Zeabur 中正確設置了環境變數
```

#### 3. 模型不可用
```
錯誤: Model gpt-5-nano not found
解決: 確認模型名稱正確，或暫時使用 gpt-4o-mini
```

#### 4. 請求超時
```
錯誤: Request timeout
解決: 增加 OPENAI_TIMEOUT 值或檢查網路連接
```

## 📞 支援資源

- [Zeabur 環境變數文檔](https://docs.zeabur.com/environment-variables)
- [OpenAI API 文檔](https://platform.openai.com/docs)
- [OpenAI 定價](https://openai.com/pricing)
- [Zeabur 支援](https://docs.zeabur.com/support)

## 🎯 下一步

設置完成後，我們就可以開始：
1. 實現 GPT5NanoClient 類別
2. 集成到現有推薦系統
3. 測試和優化
4. 部署到生產環境

準備好了嗎？讓我們開始實作！🚀
