# LLM 增強設定指南

## 📋 概述

本指南將協助您設定並執行 LLM 增強功能，使用 Qwen3 Next 80B A3B Thinking 模型通過 OpenRouter API 批次分類未分類標籤。

## 🎯 目標

- **danbooru_cat=0 覆蓋率**: 47.36% → 65-70%
- **整體覆蓋率**: 84.6% → 91-93%
- **處理標籤**: ~114 個超高頻未分類標籤
- **預估成本**: $2-5

## 📝 步驟 1: 獲取 API Key

1. 前往 [OpenRouter](https://openrouter.ai/)
2. 註冊或登入帳號
3. 前往 [Keys](https://openrouter.ai/keys) 頁面
4. 建立新的 API Key
5. 複製 API Key（格式：`sk-or-v1-...`）

## ⚙️ 步驟 2: 設定環境變數

在 `stage1` 目錄建立 `.env` 檔案：

```bash
# .env
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
QWEN_MODEL=qwen/qwen3-next-80b-a3b-thinking
OPENROUTER_REFERER=https://github.com/prompt-scribe
OPENROUTER_TITLE=Prompt-Scribe Tag Classifier
BATCH_SIZE=20
MAX_RETRIES=3
TEMPERATURE=0.1
```

**注意**：
- 將 `your-actual-api-key-here` 替換為您的實際 API Key
- `.env` 檔案已被 gitignore，不會被提交到 Git

## 🔧 步驟 3: 執行資料庫遷移

```bash
cd stage1
python migrate_db_for_llm.py
```

這會新增以下欄位到 `tags_final` 表：
- `classification_source` - 分類來源（例如：'qwen3_80b'）
- `classification_confidence` - 置信度分數 (0-1)
- `classification_reasoning` - 分類理由
- `classification_timestamp` - 分類時間戳記

## 🧪 步驟 4: 小規模測試（10 個標籤）

```bash
python test_qwen_classifier.py
```

這會測試以下 10 個代表性標籤：
- `thighhighs`, `navel`, `jewelry`, `cleavage`, `nipples`
- `dated`, `username`, `zzz`, `colored_tips`, `off_shoulder`

**預期結果**：
- 成功率：100%
- 平均置信度：>0.7
- 分類結果合理

**驗證項目**：
- [ ] API 連接正常
- [ ] JSON 解析成功
- [ ] 分類結果符合預期
- [ ] 置信度分數合理
- [ ] reasoning 欄位有意義

**預期成本**：< $0.01

## 🚀 步驟 5: 批次處理超高頻標籤

確認測試通過後，執行完整批次處理：

```bash
python qwen_classifier.py
```

這會處理所有 `post_count >= 1,000,000` 的未分類標籤（~114 個）。

**處理策略**：
- 每批次 20 個標籤
- 最多重試 3 次
- 批次間延遲 1 秒

**監控指標**：
- 成功率
- 平均置信度
- 處理速度
- 成本估算

**預期時間**：2-3 小時  
**預期成本**：$2-5

## 🔍 步驟 6: 審查分類結果

```bash
python review_llm_results.py
```

這會生成審查報告，包含：
- 按置信度分組的標籤
- 按主分類的分佈
- 潛在問題檢查
- 相似標籤一致性檢查

**需要審查的項目**：
- 置信度 < 0.5 的標籤
- 分類不一致的相似標籤
- 沒有理由的分類

## 📊 步驟 7: 驗證覆蓋率提升

```bash
python quick_stats.py
```

這會顯示最新的覆蓋率統計。

**預期結果**：
- danbooru_cat=0 覆蓋率：→ 65-70%
- 整體覆蓋率：→ 91-93%
- 推薦系統盲區：→ <12%

## 🔧 故障排除

### 問題：API Key 無效
```
❌ 錯誤：未設定 OPENROUTER_API_KEY
```

**解決方法**：
1. 檢查 `.env` 檔案是否存在於 `stage1` 目錄
2. 確認 API Key 格式正確（`sk-or-v1-...`）
3. 確認沒有多餘的空格或引號

### 問題：JSON 解析失敗
```
JSON 解析錯誤: Expecting value
```

**解決方法**：
1. 檢查模型回應格式
2. 可能是模型輸出格式改變，檢查最新回應
3. 增加錯誤處理和重試

### 問題：API 限流
```
請求異常: Rate limit exceeded
```

**解決方法**：
1. 增加 `retry_delay` 參數
2. 減少 `batch_size`
3. 檢查 OpenRouter 帳號額度

### 問題：置信度過低
```
發現 X 個標籤置信度極低 (<0.3)
```

**解決方法**：
1. 審查這些標籤
2. 考慮手動分類
3. 或調整 prompt 使其更明確

## 📈 成本控制

### 預算設定

在執行前設定成本上限：

```python
# 在 qwen_classifier.py 中可以添加成本追蹤
MAX_BUDGET = 10.0  # USD
current_cost = 0.0
```

### 成本估算公式

```
成本 = (輸入 tokens + 輸出 tokens) × 模型價格
```

Qwen3 Next 80B 價格（OpenRouter）：
- 輸入：$0.60 / 1M tokens
- 輸出：$0.60 / 1M tokens

**估算**：
- 每個標籤約 200 tokens（輸入 + 輸出）
- 100 個標籤 = 20,000 tokens
- 成本 = 20,000 × $0.60 / 1,000,000 = $0.012

實際成本可能因 reasoning 長度而變化。

## ✅ 完成檢查清單

- [ ] 步驟 1: 獲取 API Key
- [ ] 步驟 2: 設定 .env 檔案
- [ ] 步驟 3: 執行資料庫遷移
- [ ] 步驟 4: 小規模測試通過
- [ ] 步驟 5: 批次處理完成
- [ ] 步驟 6: 審查結果
- [ ] 步驟 7: 驗證覆蓋率提升

## 📞 支援

如遇問題，請檢查：
1. 日誌檔案：`output/pipeline.log`
2. 資料庫：`output/tags.db`
3. API 狀態：[OpenRouter Status](https://status.openrouter.ai/)

---

**準備好了嗎？讓我們開始吧！** 🚀

