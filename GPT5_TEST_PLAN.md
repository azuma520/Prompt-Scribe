# GPT-5 Mini 測試計劃

## 🎯 測試目標

驗證 GPT-5 Mini 集成是否正常工作，確保能夠為 Danbooru 標籤推薦任務提供高質量的結果。

---

## 📋 測試階段

### 階段 1: 環境驗證 ✅

**目的**: 確認環境變數和 API Key 正確設置

**步驟**:
```powershell
# 1. 設置環境變數
powershell -ExecutionPolicy Bypass -File setup_env_local.ps1

# 2. 運行診斷工具
python diagnose_model.py
```

**預期結果**:
```
✅ API Key 已設置
✅ 模型: gpt-5-mini
✅ 功能啟用: 是
✅ OpenAI 客戶端: 已初始化
✅ 可用性: 可用
```

---

### 階段 2: 模型連接測試 🔄

**目的**: 驗證能否成功連接 GPT-5 Mini 並獲得回應

**步驟**:
```powershell
# 運行連接測試
python -c "from src.api.services.gpt5_nano_client import GPT5NanoClient; import asyncio; client = GPT5NanoClient(); print(asyncio.run(client.test_connection()))"
```

**預期結果**:
- HTTP 200 OK
- 回應內容不為空
- Token 使用正常
- 成本計算正確

**檢查點**:
- [ ] API 調用成功
- [ ] 回應包含有效的 JSON
- [ ] `reasoning_effort` 和 `verbosity` 參數被正確使用
- [ ] 沒有 `temperature` 參數錯誤

---

### 階段 3: 標籤推薦功能測試 🏷️

**目的**: 驗證實際的標籤推薦功能

#### 測試案例 1: 簡單描述

**輸入**:
```
"一個長髮藍眼的動漫女孩"
```

**預期輸出**:
```json
{
  "tags": ["1girl", "long_hair", "blue_eyes", "solo", "anime_style"],
  "confidence": 0.85,
  "reasoning": "Based on the description, these tags capture the key visual elements",
  "categories": ["CHARACTER", "APPEARANCE", "STYLE"]
}
```

**檢查點**:
- [ ] 返回 5-10 個標籤
- [ ] 標籤格式正確（使用下劃線）
- [ ] Confidence 在 0.6-0.95 範圍內
- [ ] JSON 格式有效

#### 測試案例 2: 複雜場景

**輸入**:
```
"戶外場景，日落，城市風景，一個穿校服的女孩站在天台上"
```

**預期輸出**:
```json
{
  "tags": ["1girl", "school_uniform", "outdoors", "sunset", "cityscape", "rooftop", "standing", "sky"],
  "confidence": 0.88,
  "reasoning": "Scene includes character, clothing, location, time of day, and action",
  "categories": ["CHARACTER", "CLOTHING", "SCENE", "ACTION"]
}
```

**檢查點**:
- [ ] 包含場景標籤（outdoors, sunset, cityscape）
- [ ] 包含服裝標籤（school_uniform）
- [ ] 包含動作標籤（standing）
- [ ] 分類正確

#### 測試案例 3: 藝術風格

**輸入**:
```
"masterpiece, high quality, detailed artwork"
```

**預期輸出**:
```json
{
  "tags": ["masterpiece", "high_quality", "highly_detailed", "best_quality", "absurdres"],
  "confidence": 0.90,
  "reasoning": "Quality and detail modifiers for high-quality artwork",
  "categories": ["STYLE", "QUALITY"]
}
```

**檢查點**:
- [ ] 識別質量標籤
- [ ] 正確的藝術風格標籤
- [ ] 高信心度

---

### 階段 4: 性能測試 ⚡

**目的**: 評估回應時間和成本

**測試**:
```powershell
# 運行性能測試
python test_gpt5_performance.py
```

**測量指標**:
- 平均回應時間: 目標 < 3 秒
- Token 使用量: 目標 < 1000 tokens/請求
- 成本: 目標 < $0.001/請求

**檢查點**:
- [ ] 回應時間可接受
- [ ] Token 使用在合理範圍
- [ ] 成本計算正確

---

### 階段 5: 錯誤處理測試 🛡️

**目的**: 驗證錯誤處理機制

#### 測試案例 1: API Key 無效

**操作**: 使用無效的 API Key
**預期**: 返回降級方案（keyword matching）

#### 測試案例 2: 網路錯誤

**操作**: 模擬網路中斷
**預期**: 適當的錯誤訊息和降級處理

#### 測試案例 3: 回應格式錯誤

**操作**: 如果 LLM 返回無效 JSON
**預期**: JSON 驗證失敗，記錄錯誤，返回降級方案

---

### 階段 6: 集成測試 🔗

**目的**: 測試與完整 API 的集成

**步驟**:
```powershell
# 1. 啟動伺服器
python run_server.py

# 2. 測試 API 端點
python test_api.py
```

**API 測試案例**:

#### 1. Health Check
```bash
curl http://127.0.0.1:8000/health
```

#### 2. OpenAI Config Test
```bash
curl http://127.0.0.1:8000/api/llm/test-openai-config
```

#### 3. Tag Recommendation
```bash
curl -X POST http://127.0.0.1:8000/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{
    "description": "一個長髮藍眼的動漫女孩",
    "use_llm": true
  }'
```

**檢查點**:
- [ ] Health endpoint 返回 200
- [ ] Config test 顯示 GPT-5 Mini
- [ ] Tag recommendation 返回有效結果
- [ ] 回應時間 < 5 秒

---

## 📊 成功標準

### 必須通過 (Critical)

- ✅ 環境變數正確設置
- ✅ API Key 有效且有 GPT-5 權限
- ✅ 模型連接成功
- ✅ 能返回有效的 JSON 結構
- ✅ 標籤格式符合 Danbooru 規範

### 應該通過 (Important)

- ✅ 平均回應時間 < 3 秒
- ✅ JSON 驗證成功率 > 95%
- ✅ 標籤質量高（相關性強）
- ✅ 錯誤處理正常

### 希望達成 (Nice to Have)

- ✅ 回應時間 < 2 秒
- ✅ JSON 驗證成功率 = 100%
- ✅ 成本 < $0.0005/請求

---

## 🐛 問題排查

### 問題 1: "temperature 參數不支持" 錯誤

**原因**: GPT-5 不支持 temperature
**解決**: 已在代碼中修復，使用 reasoning_effort 和 verbosity

### 問題 2: 回應為空

**檢查**:
1. API Key 是否有效
2. 模型名稱是否正確（gpt-5-mini）
3. 是否使用了正確的參數

### 問題 3: JSON 解析失敗

**檢查**:
1. Prompt 是否明確要求 JSON 格式
2. verbosity 設置是否為 "low"
3. 查看原始回應內容

---

## 📝 測試記錄

### 測試日期: ____________________

| 測試階段 | 狀態 | 註記 |
|---------|------|------|
| 環境驗證 | ⬜ 通過 / ⬜ 失敗 | |
| 模型連接 | ⬜ 通過 / ⬜ 失敗 | |
| 標籤推薦 | ⬜ 通過 / ⬜ 失敗 | |
| 性能測試 | ⬜ 通過 / ⬜ 失敗 | |
| 錯誤處理 | ⬜ 通過 / ⬜ 失敗 | |
| 集成測試 | ⬜ 通過 / ⬜ 失敗 | |

### 總體評估

- ⬜ **通過** - 可以部署到生產環境
- ⬜ **有條件通過** - 需要小修正
- ⬜ **未通過** - 需要重大修正

### 備註:

```
[在此記錄測試過程中的任何問題或觀察]
```

---

**測試者**: ____________________
**日期**: ____________________
**版本**: GPT-5 Mini Integration v1.0
