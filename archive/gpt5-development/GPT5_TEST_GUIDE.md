# GPT-5 Nano 測試指南

## 🚀 快速開始

### 1. 啟動測試伺服器

**方法 A: 使用 PowerShell 腳本（推薦）**
```powershell
powershell -ExecutionPolicy Bypass -File start_test_server.ps1
```

**方法 B: 手動啟動**
```bash
cd src/api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 運行 API 測試

在新的終端窗口中：
```bash
python test_gpt5_api.py
```

## 📋 測試端點

### 健康檢查
```bash
GET http://localhost:8000/health
```

### OpenAI 配置檢查
```bash
GET http://localhost:8000/api/llm/test-openai-config
```

**預期回應**:
```json
{
  "available": true,
  "config": {
    "api_key_set": true,
    "model": "gpt-5-nano",
    "enabled": true
  },
  "validation_stats": {
    "total_validations": 0,
    "successful": 0,
    "failed": 0,
    "success_rate": 0
  }
}
```

### 標籤推薦（核心功能）
```bash
POST http://localhost:8000/api/llm/recommend-tags
Content-Type: application/json

{
  "description": "一個長髮藍眼的動漫女孩，穿著校服，微笑著看向觀眾"
}
```

**預期回應**:
```json
{
  "tags": ["1girl", "long_hair", "blue_eyes", "school_uniform", "smiling", "looking_at_viewer"],
  "confidence": 0.85,
  "reasoning": "基於描述推薦的 Danbooru 風格標籤",
  "categories": ["CHARACTER", "APPEARANCE", "CLOTHING", "ACTION"],
  "validated_at": "2025-01-21T...",
  "schema_version": "1.0",
  "validation_method": "json_schema_v1",
  "source": "gpt-5-nano"
}
```

### 驗證統計
```bash
GET http://localhost:8000/api/llm/validation-stats
```

**預期回應**:
```json
{
  "total_validations": 5,
  "successful": 5,
  "failed": 0,
  "success_rate": 100.0,
  "schema_info": {
    "schema_version": "1.0",
    "required_fields": ["tags", "confidence"],
    "max_tags": 15,
    "min_tags": 1
  }
}
```

## 🧪 測試案例

### 測試案例 1: 基本動漫角色
```json
{
  "description": "一個長髮藍眼的動漫女孩"
}
```

### 測試案例 2: 英文描述
```json
{
  "description": "a beautiful anime girl with long blonde hair and green eyes"
}
```

### 測試案例 3: 場景描述
```json
{
  "description": "戶外場景，日落，城市風景"
}
```

### 測試案例 4: 風格標籤
```json
{
  "description": "masterpiece, high quality, detailed, anime style"
}
```

### 測試案例 5: 複雜描述
```json
{
  "description": "一位穿著白色連衣裙的金髮女孩站在櫻花樹下，夕陽映照，微風吹拂長髮，溫柔地微笑著"
}
```

## 🔧 使用 curl 測試

### Windows (PowerShell)
```powershell
# 健康檢查
Invoke-WebRequest -Uri http://localhost:8000/health

# 標籤推薦
$body = @{
    description = "一個長髮藍眼的動漫女孩"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/llm/recommend-tags `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Linux/Mac
```bash
# 健康檢查
curl http://localhost:8000/health

# 標籤推薦
curl -X POST http://localhost:8000/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description": "一個長髮藍眼的動漫女孩"}'
```

## 📊 使用 Swagger UI

訪問互動式 API 文檔：
```
http://localhost:8000/docs
```

在 Swagger UI 中，您可以：
1. 查看所有 API 端點
2. 直接測試 API
3. 查看請求/回應範例
4. 下載 OpenAPI 規範

## 🔍 驗證結構化輸出

測試腳本會自動驗證以下內容：

### ✅ 必要欄位
- `tags`: 字串陣列 (1-15 個)
- `confidence`: 數字 (0.0-1.0)

### ✅ 可選欄位
- `reasoning`: 字串
- `categories`: 字串陣列
- `suggestions`: 字串陣列

### ✅ 自動添加的欄位
- `validated_at`: ISO 8601 時間戳
- `schema_version`: "1.0"
- `validation_method`: "json_schema_v1"
- `source`: "gpt-5-nano"

### ✅ 標籤格式驗證
- 只允許字母、數字、底線
- 使用底線連接多個單詞 (如 `long_hair`)
- 不允許空格或特殊字符

## 🚨 故障排除

### 問題 1: 伺服器無法啟動
```
ModuleNotFoundError: No module named 'xxx'
```
**解決方案**: 安裝依賴
```bash
pip install -r src/api/requirements.txt
```

### 問題 2: OpenAI API 不可用
```json
{
  "available": false,
  "error": "GPT-5 Nano not available"
}
```
**解決方案**: 檢查環境變數
1. 確認 `OPENAI_API_KEY` 已設置
2. 確認 `ENABLE_OPENAI_INTEGRATION=true`
3. 重啟伺服器

### 問題 3: 驗證失敗
```
JSON Schema 驗證失敗: 'confidence' is a required property
```
**原因**: GPT-5 回應不符合預期格式
**解決方案**: 
1. 檢查 GPT-5 模型回應
2. 查看伺服器日誌
3. 系統會自動使用降級方案

### 問題 4: 連接超時
```
Connection timeout
```
**解決方案**:
1. 檢查伺服器是否正在運行
2. 確認端口 8000 未被占用
3. 檢查防火牆設置

## 📈 性能監控

### 查看驗證統計
```bash
GET http://localhost:8000/api/llm/validation-stats
```

### 重置統計
```bash
POST http://localhost:8000/api/llm/reset-validation-stats
```

## 🎯 預期結果

**正常情況** (OpenAI 可用):
- ✅ 使用 GPT-5 Nano 生成標籤
- ✅ 結構化驗證通過
- ✅ 返回 5-10 個相關標籤
- ✅ 信心度 0.6-0.95

**降級情況** (OpenAI 不可用):
- ⚠️  使用關鍵字匹配降級方案
- ✅ 返回基本標籤
- ✅ 信心度較低 (0.6)
- ✅ 標記 `fallback: true`

## 📚 相關文檔

- [GPT-5 結構化輸出優化報告](docs/api/GPT5_STRUCTURED_OUTPUT_OPTIMIZATION_COMPLETE.md)
- [GPT-5 Nano 配置指南](docs/api/GPT5_NANO_ZEABUR_CONFIG.md)
- [API 文檔](http://localhost:8000/docs)

---

**測試愉快！** 🚀

如有問題，請查看伺服器日誌或相關文檔。
