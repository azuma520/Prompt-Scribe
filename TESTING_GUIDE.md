# GPT-5 Mini 測試執行指南

## 🎯 快速開始

### 前置準備

1. **設置環境變數**:
   ```powershell
   # 編輯 setup_env_local.ps1（如果還沒填入 API Key）
   # 然後運行（或直接在終端設置環境變數）
   $env:OPENAI_API_KEY = "您的-API-Key"
   $env:SUPABASE_URL = "您的-Supabase-URL"
   $env:SUPABASE_ANON_KEY = "您的-Supabase-Key"
   ```

2. **確認環境**:
   ```powershell
   python diagnose_model.py
   ```

---

## 🧪 測試執行

### 測試 1: 場景測試（必做）

**用途**: 驗證各種使用場景的功能

```powershell
cd tests
python test_gpt5_scenarios.py
```

**預期輸出**:
```
📋 測試套件 A: 基礎功能測試
  [A1] 單一角色
    ✅ 通過
    - 標籤數: 8 (最少: 5) ✅
    - 信心度: 0.88 (最少: 0.80) ✅
    
測試套件 A 總結:
  總計: 5
  ✅ 通過: 5
  成功率: 100.0%

🎉 所有測試通過！
```

**時間**: ~5 分鐘（9 個測試案例）

---

### 測試 2: 性能測試（推薦）

**用途**: 評估回應時間和 Token 使用

```powershell
cd tests  
python test_gpt5_performance.py 10
```

**預期輸出**:
```
⚡ GPT-5 Mini 性能測試 (10 次請求)

⏱️  回應時間:
  - 平均: 2.35秒
  - 中位數: 2.28秒
  - 最快: 1.85秒
  - 最慢: 3.12秒

🏷️  標籤數量:
  - 平均: 9.5個
  - 範圍: 8-10個

📈 信心度:
  - 平均: 0.882

✅ 成功率: 100.0%

💰 成本估算:
  - 每請求: ~$0.000300
  - 預估 1,000 次: ~$0.30
  
總體評價:
  🏆 優秀 - GPT-5 Mini 表現卓越！
```

**時間**: ~3 分鐘（10 次請求）

**參數**:
- 默認 10 次請求
- 可指定次數: `python test_gpt5_performance.py 50`

---

### 測試 3: API 集成測試（部署後）

**用途**: 測試完整的 API 端點

```powershell
# 確保伺服器正在運行
python run_server.py  # 在另一個終端

# 然後在新終端執行
python test_api_integration.py
```

**測試內容**:
- Health endpoint
- OpenAI config endpoint
- Tag recommendation endpoint
- Error handling

**時間**: ~2 分鐘

---

## 📊 測試結果解讀

### 場景測試結果

#### 成功率 100%
```
🎉 完美！
下一步: 立即部署到 Zeabur
```

#### 成功率 80-99%
```
✅ 良好！
建議: 
  - 檢查失敗的案例
  - 可以部署，但需監控
```

#### 成功率 < 80%
```
⚠️ 需要修復
建議:
  - 檢查 API Key 和配置
  - 查看錯誤訊息
  - 聯繫支援
```

### 性能測試結果

#### 優秀（推薦部署）
```
回應時間: < 2.5秒
標籤數量: >= 10個
信心度: >= 0.9
成功率: >= 99%
```

#### 良好（可以部署）
```
回應時間: < 3秒
標籤數量: >= 8個
信心度: >= 0.85
成功率: >= 95%
```

#### 需優化（謹慎部署）
```
回應時間: >= 3秒
標籤數量: < 8個
信心度: < 0.85
成功率: < 95%
```

---

## 🐛 常見問題排查

### 問題 1: "OPENAI_API_KEY 未設置"

**解決**:
```powershell
# 在 PowerShell 中設置
$env:OPENAI_API_KEY = "您的-Key"

# 或編輯 setup_env_local.ps1 並運行
powershell -ExecutionPolicy Bypass -File setup_env_local.ps1
```

### 問題 2: "客戶端不可用"

**檢查**:
1. API Key 是否正確？
2. 網路連接是否正常？
3. OpenAI 服務是否可用？

**診斷**:
```powershell
python diagnose_model.py
```

### 問題 3: 測試超時

**可能原因**:
- 網路速度慢
- OpenAI API 負載高
- 防火牆阻擋

**解決**:
- 檢查網路連接
- 稍後再試
- 檢查防火牆設置

### 問題 4: JSON 解析失敗

**可能原因**:
- Prompt 需要優化
- verbosity 設置不當
- 模型回應格式錯誤

**解決**:
- 查看原始回應內容
- 調整 prompt
- 調整 verbosity 參數

---

## 📅 測試時間表

### 今天（2025-10-21 下午）

**時間**: 30 分鐘

```
14:00 - 14:10  場景測試（測試套件 A）
14:10 - 14:15  場景測試（測試套件 B）  
14:15 - 14:25  性能測試（10 次請求）
14:25 - 14:30  結果分析和記錄
```

**檢查點**:
- [ ] 所有基礎測試通過
- [ ] 性能指標達標
- [ ] 準備好部署

### 今天晚上（Zeabur 部署後）

**時間**: 15 分鐘

```
20:00 - 20:05  Zeabur 環境變數設置
20:05 - 20:10  等待部署完成
20:10 - 20:15  生產環境驗證測試
```

**檢查點**:
- [ ] 部署成功
- [ ] API 端點正常
- [ ] GPT-5 Mini 運行正常

### 明天（2025-10-22）

**時間**: 1 小時

```
上午:
  - 性能壓力測試（50 次請求）
  - 錯誤處理測試
  - 降級機制驗證

下午:
  - 收集使用數據
  - 分析性能趨勢
  - 評估成本
```

---

## 🎯 測試目標

### 短期目標（本週）

- [ ] 完成所有功能測試
- [ ] 驗證性能達標
- [ ] 確認成本在預算內
- [ ] 收集初步使用數據

### 中期目標（本月）

- [ ] 優化參數配置
- [ ] 改進 prompt
- [ ] 降低平均成本
- [ ] 提升標籤質量

### 長期目標（3 個月）

- [ ] 評估 Responses API 遷移
- [ ] A/B 測試不同模型
- [ ] 建立性能基準
- [ ] 持續優化

---

## 📚 相關文檔

| 文檔 | 用途 |
|------|------|
| `GPT5_TESTING_ROADMAP.md` | 完整測試路線圖 |
| `GPT5_TEST_PLAN.md` | 詳細測試計劃 |
| `SETUP_GPT5_ENV.md` | 環境設置 |
| `ZEABUR_DEPLOYMENT_CHECKLIST.md` | 部署清單 |

---

## 🚀 快速測試指令

### 一鍵執行所有測試

```powershell
# Windows PowerShell

# 1. 設置環境變數
$env:OPENAI_API_KEY = "您的-Key"

# 2. 運行所有測試
cd tests
python test_gpt5_scenarios.py
python test_gpt5_performance.py 10

# 3. 查看結果
Write-Host "測試完成！" -ForegroundColor Green
```

### Linux/macOS

```bash
# 1. 設置環境變數
export OPENAI_API_KEY="您的-Key"

# 2. 運行所有測試
cd tests
python3 test_gpt5_scenarios.py
python3 test_gpt5_performance.py 10

# 3. 查看結果
echo "測試完成！"
```

---

## 📊 測試報告模板

```markdown
# GPT-5 Mini 測試報告

測試日期: 2025-10-21
測試環境: 本地 / Zeabur
模型: gpt-5-mini

## 場景測試結果
- 套件 A (基礎): ___/5 通過
- 套件 B (進階): ___/4 通過
- 總成功率: ___%

## 性能測試結果
- 平均回應時間: ___秒
- 平均標籤數: ___個
- 平均信心度: ___
- 成功率: ___%

## 成本分析
- 每請求: $_____
- 預估每月 (10萬請求): $_____

## 問題列表
1. [問題]
2. [問題]

## 結論
⬜ 通過 - 建議部署
⬜ 有條件通過 - 需監控
⬜ 未通過 - 需修復
```

---

**準備好開始測試了嗎？** 🧪

運行: `python tests/test_gpt5_scenarios.py`
