# ✅ GPT-5 Nano 部署檢查清單

## 🚀 部署前檢查

### 1. 環境變數設置 ✅
- [x] `OPENAI_API_KEY` - 已設置在 Zeabur
- [x] `OPENAI_MODEL=gpt-5-nano` - 已配置
- [x] `OPENAI_MAX_TOKENS=500` - 已設置
- [x] `OPENAI_TEMPERATURE=0.7` - 已配置
- [x] `OPENAI_TIMEOUT=30` - 已設置
- [x] `ENABLE_OPENAI_INTEGRATION=true` - 已啟用

### 2. 代碼集成 ✅
- [x] `GPT5NanoClient` 類別已創建
- [x] 集成到 `recommend_tags` 端點
- [x] 錯誤處理和回退機制已實現
- [x] 測試端點已添加 (`/test-openai-config`)

### 3. 依賴檢查
- [ ] `openai` Python 庫需要安裝
- [ ] 更新 `requirements.txt`

## 📦 部署步驟

### 步驟 1: 更新依賴
```bash
# 在 requirements.txt 中添加
echo "openai>=1.0.0" >> requirements.txt
```

### 步驟 2: 重新部署到 Zeabur
```bash
# 推送代碼到 Git
git add .
git commit -m "feat: 集成 GPT-5 Nano 標籤推薦"
git push origin main

# Zeabur 會自動重新部署
```

### 步驟 3: 驗證部署
```bash
# 測試健康檢查
curl https://prompt-scribe-api.zeabur.app/health

# 測試 GPT-5 配置
curl https://prompt-scribe-api.zeabur.app/api/llm/test-openai-config

# 測試標籤推薦
curl -X POST https://prompt-scribe-api.zeabur.app/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description": "美食推薦"}'
```

## 🧪 測試計劃

### 單元測試
```bash
# 運行 GPT-5 Nano 測試
python -m pytest tests/test_gpt5_nano_integration.py -v
```

### 集成測試
1. **配置測試** - 驗證環境變數和連接
2. **功能測試** - 測試標籤推薦功能
3. **回退測試** - 測試 GPT-5 失敗時的回退機制
4. **性能測試** - 測試回應時間和成本

### 測試案例
```json
{
  "test_cases": [
    {
      "description": "美食推薦",
      "expected_tags": ["美食", "餐廳", "料理"],
      "expected_categories": ["生活", "飲食"]
    },
    {
      "description": "風景攝影",
      "expected_tags": ["風景", "攝影", "自然"],
      "expected_categories": ["攝影", "藝術"]
    },
    {
      "description": "科技產品",
      "expected_tags": ["科技", "產品", "電子"],
      "expected_categories": ["科技", "商業"]
    }
  ]
}
```

## 📊 監控指標

### 性能指標
- [ ] API 回應時間 < 3 秒
- [ ] GPT-5 Nano 調用成功率 > 95%
- [ ] 回退機制觸發率 < 5%

### 成本指標
- [ ] 每次調用成本 < $0.01
- [ ] 每日使用量監控
- [ ] Token 使用效率

### 品質指標
- [ ] 標籤相關性評分 > 0.8
- [ ] 用戶滿意度 > 85%
- [ ] 錯誤率 < 2%

## 🔧 故障排除

### 常見問題

#### 1. OpenAI API 金鑰無效
```
錯誤: Invalid API key
解決: 檢查 Zeabur 環境變數中的 API 金鑰
```

#### 2. GPT-5 Nano 模型不可用
```
錯誤: Model gpt-5-nano not found
解決: 暫時使用 gpt-4o-mini 作為替代
```

#### 3. 回應格式錯誤
```
錯誤: Failed to parse GPT-5 result
解決: 檢查 GPT-5 回應格式，加強 JSON 解析
```

#### 4. 超時問題
```
錯誤: Request timeout
解決: 增加 OPENAI_TIMEOUT 值或優化提示詞
```

## 🚀 部署後驗證

### 即時驗證
1. **健康檢查** - 確認 API 正常運行
2. **配置測試** - 驗證 GPT-5 Nano 配置
3. **功能測試** - 測試標籤推薦功能
4. **回退測試** - 測試錯誤處理

### 持續監控
1. **日誌監控** - 檢查錯誤和警告
2. **性能監控** - 追蹤回應時間
3. **成本監控** - 監控 API 使用量
4. **品質監控** - 評估推薦品質

## 📈 優化計劃

### 短期優化 (1-2 週)
- [ ] 實現快取機制
- [ ] 優化提示詞工程
- [ ] 添加使用量限制

### 中期優化 (1-2 月)
- [ ] 實現批量處理
- [ ] 添加 A/B 測試
- [ ] 優化成本控制

### 長期優化 (3-6 月)
- [ ] 考慮微調模型
- [ ] 實現多模型支援
- [ ] 添加個性化推薦

## 🎯 成功標準

### 技術標準
- ✅ GPT-5 Nano 集成成功
- ✅ 回退機制正常運作
- ✅ 錯誤處理完善
- ✅ 性能符合預期

### 業務標準
- 🎯 標籤推薦品質提升
- 🎯 用戶體驗改善
- 🎯 成本控制在預算內
- 🎯 系統穩定性良好

## 📞 支援資源

- [OpenAI API 文檔](https://platform.openai.com/docs)
- [Zeabur 部署指南](https://docs.zeabur.com)
- [FastAPI 文檔](https://fastapi.tiangolo.com)
- [專案 GitHub](https://github.com/your-repo)

---

## 🎉 部署完成檢查清單

- [ ] 所有環境變數已設置
- [ ] 代碼已推送並部署
- [ ] 測試已通過
- [ ] 監控已設置
- [ ] 文檔已更新
- [ ] 團隊已通知

**部署狀態**: 🟡 準備中  
**下一步**: 推送代碼並重新部署到 Zeabur
