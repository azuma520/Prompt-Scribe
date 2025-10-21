# GPT-5 Mini 測試路線圖

## 🎯 測試目標

驗證 GPT-5 Mini 在 Prompt-Scribe 中的功能性、性能和可靠性。

---

## 📋 測試階段規劃

### 階段 1: 本地功能測試 (今天，30 分鐘)

**目標**: 確保 GPT-5 Mini 基本功能正常

#### 測試 1.1: 環境驗證

```powershell
# 設置環境變數
powershell -ExecutionPolicy Bypass -File setup_env_local.ps1

# 運行診斷
python diagnose_model.py
```

**檢查點**:
- [ ] API Key 已設置
- [ ] 模型顯示為 gpt-5-mini
- [ ] 功能啟用狀態為 true
- [ ] GPT-5 系列標記為 true

#### 測試 1.2: 標籤生成測試

```powershell
python test_gpt5_tag_generation.py
```

**檢查點**:
- [ ] gpt-5-mini 返回 8-10 個標籤
- [ ] JSON 格式正確
- [ ] 信心度 > 0.8
- [ ] Token 使用 < 500

#### 測試 1.3: API 伺服器測試

```powershell
# 終端 1: 啟動伺服器
python run_server.py

# 終端 2: 測試 API
curl http://127.0.0.1:8000/api/llm/test-openai-config
```

**檢查點**:
- [ ] 伺服器成功啟動
- [ ] 顯示模型為 gpt-5-mini
- [ ] 測試回應成功

---

### 階段 2: 功能完整性測試 (今天，1 小時)

**目標**: 測試各種使用場景

#### 測試場景設計

##### 場景 1: 簡單角色描述

```json
測試輸入:
{
  "description": "一個長髮藍眼的動漫女孩",
  "use_llm": true
}

預期輸出:
- 8-10 個標籤
- 包含: long_hair, blue_eyes, 1girl
- 信心度: > 0.85
- 回應時間: < 3 秒
```

##### 場景 2: 複雜場景描述

```json
測試輸入:
{
  "description": "戶外場景，日落時分，城市天台上，穿校服的女孩眺望遠方",
  "use_llm": true
}

預期輸出:
- 10-12 個標籤
- 包含場景標籤: outdoors, sunset, cityscape, rooftop
- 包含角色標籤: 1girl, school_uniform
- 包含動作標籤: looking_afar, standing
- 信心度: > 0.85
```

##### 場景 3: 藝術風格描述

```json
測試輸入:
{
  "description": "masterpiece, highly detailed, anime style artwork",
  "use_llm": true
}

預期輸出:
- 5-8 個標籤
- 包含質量標籤: masterpiece, high_quality, best_quality
- 包含風格標籤: anime_style, detailed
- 信心度: > 0.9
```

##### 場景 4: 混合中英文描述

```json
測試輸入:
{
  "description": "cute girl wearing kimono in cherry blossom garden",
  "use_llm": true
}

預期輸出:
- 8-10 個標籤
- 正確理解英文輸入
- 包含: cute, girl, kimono, cherry_blossoms, garden
- 信心度: > 0.85
```

##### 場景 5: 極簡描述

```json
測試輸入:
{
  "description": "貓耳女孩",
  "use_llm": true
}

預期輸出:
- 至少 5 個標籤
- 包含: cat_ears, 1girl, animal_ears
- 能夠擴展相關標籤
- 信心度: > 0.8
```

#### 執行測試

創建測試腳本：

```python
# test_scenarios.py
test_cases = [
    {
        "name": "簡單角色",
        "description": "一個長髮藍眼的動漫女孩",
        "expected_tags": ["long_hair", "blue_eyes", "1girl"],
        "min_tags": 8,
        "min_confidence": 0.85
    },
    {
        "name": "複雜場景",
        "description": "戶外場景，日落時分，城市天台上，穿校服的女孩眺望遠方",
        "expected_tags": ["outdoors", "sunset", "school_uniform"],
        "min_tags": 10,
        "min_confidence": 0.85
    },
    # ... 更多測試案例
]

for test_case in test_cases:
    result = await test_tag_generation(test_case)
    validate_result(result, test_case)
```

**檢查點**:
- [ ] 所有場景返回有效結果
- [ ] 標籤數量符合預期
- [ ] 信心度達標
- [ ] JSON 格式正確
- [ ] 回應時間可接受

---

### 階段 3: 性能壓力測試 (明天，1 小時)

**目標**: 評估系統在負載下的表現

#### 測試 3.1: 並發請求測試

```python
# 同時發送 10 個請求
concurrent_requests = 10
results = await asyncio.gather(*[
    generate_tags(description) 
    for description in test_descriptions
])
```

**測量指標**:
- [ ] 平均回應時間
- [ ] 最慢回應時間
- [ ] 成功率
- [ ] 錯誤率

**目標**:
- 平均回應時間: < 3 秒
- 成功率: > 95%
- 錯誤率: < 5%

#### 測試 3.2: 持續負載測試

```python
# 連續發送 100 個請求
for i in range(100):
    result = await generate_tags(test_description)
    log_performance_metrics(result)
```

**測量指標**:
- [ ] Token 使用趨勢
- [ ] 成本累計
- [ ] 回應時間穩定性
- [ ] 記憶體使用

**目標**:
- Token 使用穩定（無異常增長）
- 成本可預測
- 回應時間穩定（< ±20% 波動）

---

### 階段 4: 錯誤處理測試 (明天，30 分鐘)

**目標**: 驗證系統的容錯能力

#### 測試 4.1: 無效輸入處理

```python
test_cases = [
    {"description": ""},           # 空字串
    {"description": None},         # None 值
    {"description": "a" * 10000},  # 超長文字
    {"description": "!@#$%^&*()"},# 特殊字符
]
```

**檢查點**:
- [ ] 適當的錯誤訊息
- [ ] 不會崩潰
- [ ] 返回降級方案

#### 測試 4.2: API 錯誤模擬

```python
# 模擬各種錯誤情況
scenarios = [
    "invalid_api_key",      # API Key 無效
    "rate_limit",           # 速率限制
    "network_timeout",      # 網路超時
    "malformed_response",   # 格式錯誤回應
]
```

**檢查點**:
- [ ] 錯誤記錄詳細
- [ ] 自動降級到 keyword matching
- [ ] 用戶收到有效回應

#### 測試 4.3: 降級機制測試

```python
# 禁用 OpenAI
os.environ["ENABLE_OPENAI_INTEGRATION"] = "false"

# 測試標籤推薦
result = await recommend_tags(description)
```

**檢查點**:
- [ ] 自動使用 keyword matching
- [ ] 仍返回有效結果
- [ ] 日誌記錄降級原因

---

### 階段 5: Zeabur 部署測試 (部署當天，30 分鐘)

**目標**: 驗證生產環境部署

#### 測試 5.1: 部署驗證

```bash
ZEABUR_URL="https://your-app.zeabur.app"

# 1. Health Check
curl $ZEABUR_URL/health

# 2. OpenAI Config
curl $ZEABUR_URL/api/llm/test-openai-config

# 3. Tag Recommendation
curl -X POST $ZEABUR_URL/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description": "test", "use_llm": true}'
```

**檢查點**:
- [ ] 所有端點返回 200
- [ ] 模型顯示為 gpt-5-mini
- [ ] 標籤推薦正常工作

#### 測試 5.2: 日誌檢查

在 Zeabur Dashboard → Logs 中檢查：

```
應該看到:
✅ 🤖 GPT-5 Nano 客戶端初始化
✅   - 模型: gpt-5-mini
✅   - GPT-5 系列: 是
✅   - 功能啟用: 是

不應該看到:
❌ API Key 未設置
❌ temperature 參數錯誤
❌ 回應長度: 0 字符
```

#### 測試 5.3: 端到端測試

使用實際的用戶場景：

```bash
# 測試案例 1: 簡單描述
curl -X POST $ZEABUR_URL/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description": "一個長髮藍眼的動漫女孩", "use_llm": true}'

# 測試案例 2: 複雜場景  
curl -X POST $ZEABUR_URL/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description": "戶外場景，日落，城市風景", "use_llm": true}'
```

**檢查點**:
- [ ] 返回 8-10 個標籤
- [ ] 標籤格式符合 Danbooru
- [ ] 回應時間 < 3 秒
- [ ] 成本在預期範圍

---

### 階段 6: 性能監控 (持續 1 週)

**目標**: 收集生產環境數據

#### 監控指標

**性能指標**:
```yaml
每小時監控:
  - 請求數量
  - 平均回應時間
  - 成功率
  - 錯誤率

每日監控:
  - 總請求數
  - Token 使用總量
  - 總成本
  - 用戶反饋
```

#### 數據收集

創建監控腳本：

```python
# monitor_gpt5_usage.py
metrics = {
    "total_requests": 0,
    "successful": 0,
    "failed": 0,
    "total_tokens": 0,
    "total_cost": 0.0,
    "avg_response_time": 0.0,
    "avg_tags_per_request": 0.0
}

# 定期記錄到 Supabase 或日誌文件
```

**檢查點**:
- [ ] 數據收集正常
- [ ] 趨勢分析可用
- [ ] 異常警報設置

---

## 🧪 詳細測試案例

### 測試套件 A: 基礎功能 (必須通過)

| ID | 測試案例 | 輸入 | 預期標籤數 | 預期信心度 |
|----|---------|------|-----------|-----------|
| A1 | 單一角色 | "1girl" | 5-8 | > 0.85 |
| A2 | 角色特徵 | "長髮藍眼女孩" | 8-10 | > 0.85 |
| A3 | 場景描述 | "戶外，日落" | 5-8 | > 0.8 |
| A4 | 服裝描述 | "校服" | 5-8 | > 0.8 |
| A5 | 動作描述 | "微笑，看向鏡頭" | 5-8 | > 0.8 |

### 測試套件 B: 進階功能 (應該通過)

| ID | 測試案例 | 輸入 | 特殊要求 |
|----|---------|------|---------|
| B1 | 複雜組合 | "戶外場景，日落，城市，穿校服的女孩站在天台" | 需正確識別所有元素 |
| B2 | 藝術風格 | "masterpiece, high quality, detailed" | 需識別質量標籤 |
| B3 | 英文輸入 | "cute girl in kimono" | 需支持英文 |
| B4 | 混合語言 | "1girl wearing 和服 in 櫻花 garden" | 需處理混合語言 |
| B5 | 多角色 | "兩個女孩在咖啡廳" | 需識別 2girls |

### 測試套件 C: 邊界測試 (可選通過)

| ID | 測試案例 | 輸入 | 處理方式 |
|----|---------|------|---------|
| C1 | 空輸入 | "" | 返回錯誤或預設標籤 |
| C2 | 超長輸入 | 500 字描述 | 處理或截斷 |
| C3 | 特殊字符 | "!@#$%^&*()" | 優雅處理 |
| C4 | 無意義輸入 | "asdfghjkl" | 返回降級方案 |
| C5 | 極短輸入 | "cat" | 返回相關標籤 |

---

## 📊 測試工具

### 工具 1: 自動化測試腳本

創建 `tests/test_gpt5_scenarios.py`:

```python
import pytest
import asyncio
from src.api.services.gpt5_nano_client import GPT5NanoClient

@pytest.mark.asyncio
async def test_simple_character_description():
    """測試簡單角色描述"""
    client = GPT5NanoClient()
    
    result = await client.generate_tags("一個長髮藍眼的動漫女孩")
    
    assert result is not None
    assert len(result['tags']) >= 8
    assert result['confidence'] > 0.85
    assert 'long_hair' in result['tags']
    assert 'blue_eyes' in result['tags']

@pytest.mark.asyncio  
async def test_complex_scene():
    """測試複雜場景"""
    client = GPT5NanoClient()
    
    result = await client.generate_tags(
        "戶外場景，日落時分，城市天台上，穿校服的女孩眺望遠方"
    )
    
    assert result is not None
    assert len(result['tags']) >= 10
    assert result['confidence'] > 0.85
    
    # 檢查必要的場景標籤
    tags = result['tags']
    assert any('outdoor' in tag for tag in tags)
    assert any('sunset' in tag for tag in tags)
    assert any('school' in tag for tag in tags)

# 運行測試
# pytest tests/test_gpt5_scenarios.py -v
```

### 工具 2: 性能測試腳本

創建 `tests/test_gpt5_performance.py`:

```python
import time
import asyncio
from statistics import mean, stdev

async def performance_test():
    """性能測試"""
    client = GPT5NanoClient()
    
    test_descriptions = [
        "一個長髮藍眼的動漫女孩",
        "戶外場景，日落",
        "masterpiece, high quality",
        # ... 10 個測試描述
    ]
    
    response_times = []
    token_usage = []
    tag_counts = []
    
    for desc in test_descriptions:
        start = time.time()
        result = await client.generate_tags(desc)
        elapsed = time.time() - start
        
        response_times.append(elapsed)
        if result:
            tag_counts.append(len(result.get('tags', [])))
    
    # 統計分析
    print(f"平均回應時間: {mean(response_times):.2f}秒")
    print(f"回應時間標準差: {stdev(response_times):.2f}秒")
    print(f"平均標籤數: {mean(tag_counts):.1f}")
    print(f"最快回應: {min(response_times):.2f}秒")
    print(f"最慢回應: {max(response_times):.2f}秒")

# 運行
# python tests/test_gpt5_performance.py
```

### 工具 3: 成本追蹤腳本

創建 `tests/monitor_gpt5_costs.py`:

```python
async def cost_monitoring():
    """成本監控"""
    client = GPT5NanoClient()
    
    total_cost = 0.0
    total_tokens = 0
    request_count = 0
    
    # 測試 100 次請求
    for i in range(100):
        result = await client.generate_tags(test_description)
        
        # 從日誌或回應中獲取 token 使用
        # 計算成本
        cost = calculate_cost(result)
        total_cost += cost
        request_count += 1
    
    print(f"100 次請求統計:")
    print(f"  總成本: ${total_cost:.4f}")
    print(f"  平均成本: ${total_cost/request_count:.6f}/請求")
    print(f"  預估每月成本 (10萬請求): ${total_cost*1000:.2f}")
```

---

## 📈 測試指標和目標

### 功能性指標

| 指標 | 目標 | 測量方式 |
|------|------|---------|
| 成功率 | > 95% | 成功請求 / 總請求 |
| JSON 驗證率 | 100% | 有效 JSON / 總回應 |
| 標籤數量 | 8-10 個 | 平均每次請求 |
| 信心度 | > 0.85 | 平均 confidence 值 |

### 性能指標

| 指標 | 目標 | 測量方式 |
|------|------|---------|
| 回應時間 | < 3 秒 | 平均回應時間 |
| P95 回應時間 | < 5 秒 | 95% 請求的回應時間 |
| Token 使用 | < 500/請求 | 平均 token 數 |
| 成本 | < $0.0005/請求 | 平均成本 |

### 可靠性指標

| 指標 | 目標 | 測量方式 |
|------|------|---------|
| 錯誤率 | < 5% | 錯誤請求 / 總請求 |
| 超時率 | < 1% | 超時請求 / 總請求 |
| 降級率 | < 10% | 使用降級 / 總請求 |
| 可用性 | > 99% | 正常時間 / 總時間 |

---

## 🔄 測試流程

### 每日測試流程（開發階段）

```bash
# 早上（10 分鐘）
1. python diagnose_model.py              # 診斷配置
2. python tests/test_gpt5_scenarios.py   # 功能測試
3. 檢查日誌，記錄問題

# 下午（5 分鐘）
1. 測試新的場景或修改
2. 更新測試案例
3. 記錄改進建議

# 晚上（5 分鐘）
1. 查看一天的使用統計
2. 評估成本
3. 規劃明天的測試
```

### 週測試流程（生產階段）

```bash
# 每週一
1. 運行完整測試套件
2. 分析一週的性能數據
3. 生成週報告
4. 規劃優化方向
```

---

## 📝 測試記錄模板

### 測試執行記錄

```markdown
## 測試日期: 2025-10-21

### 階段 1: 本地功能測試
- [ ] 環境驗證: ⬜ 通過 / ⬜ 失敗
- [ ] 標籤生成: ⬜ 通過 / ⬜ 失敗  
- [ ] API 伺服器: ⬜ 通過 / ⬜ 失敗

### 階段 2: 功能完整性
- [ ] 場景 1: ⬜ 通過 / ⬜ 失敗
- [ ] 場景 2: ⬜ 通過 / ⬜ 失敗
- [ ] 場景 3: ⬜ 通過 / ⬜ 失敗
- [ ] 場景 4: ⬜ 通過 / ⬜ 失敗
- [ ] 場景 5: ⬜ 通過 / ⬜ 失敗

### 階段 3: 性能測試
- [ ] 並發測試: ⬜ 通過 / ⬜ 失敗
- [ ] 負載測試: ⬜ 通過 / ⬜ 失敗

### 階段 4: 錯誤處理
- [ ] 無效輸入: ⬜ 通過 / ⬜ 失敗
- [ ] API 錯誤: ⬜ 通過 / ⬜ 失敗
- [ ] 降級機制: ⬜ 通過 / ⬜ 失敗

### 階段 5: Zeabur 部署
- [ ] 部署驗證: ⬜ 通過 / ⬜ 失敗
- [ ] 日誌檢查: ⬜ 通過 / ⬜ 失敗
- [ ] 端到端: ⬜ 通過 / ⬜ 失敗

### 性能數據

平均回應時間: _____秒
平均標籤數: _____個
平均信心度: _____
成功率: _____%
總成本: $_____

### 問題記錄

[記錄任何發現的問題]

### 改進建議

[記錄優化建議]

測試人員: _________
日期: _________
```

---

## 🎯 測試優先級

### P0 - 必須通過（阻塞部署）

- ✅ 環境變數正確設置
- ✅ API Key 有效
- ✅ GPT-5 Mini 連接成功
- ✅ 基本標籤推薦功能正常
- ✅ JSON 格式驗證通過

### P1 - 應該通過（影響用戶體驗）

- ✅ 標籤數量達標（8-10 個）
- ✅ 回應時間可接受（< 3 秒）
- ✅ 信心度達標（> 0.85）
- ✅ 錯誤處理正常

### P2 - 希望通過（優化項目）

- ✅ 性能穩定
- ✅ 成本在預算內
- ✅ 支持複雜場景
- ✅ 降級機制完善

---

## 📅 測試時間表

### 今天（2025-10-21）

**上午**:
- [x] 完成代碼開發
- [x] 本地測試通過
- [x] 專案整理

**下午** (現在):
- [ ] 規劃測試（當前）
- [ ] 執行階段 1-2 測試
- [ ] 在 Zeabur 設置環境變數

**晚上**:
- [ ] 驗證 Zeabur 部署
- [ ] 執行階段 5 測試
- [ ] 記錄初始結果

### 明天（2025-10-22）

- [ ] 執行階段 3 性能測試
- [ ] 執行階段 4 錯誤處理測試
- [ ] 開始階段 6 持續監控

### 本週

- [ ] 收集一週使用數據
- [ ] 分析性能趨勢
- [ ] 評估成本效益
- [ ] 生成測試報告

---

## 🛠️ 測試工具清單

### 已創建的工具

| 工具 | 用途 | 位置 |
|------|------|------|
| `diagnose_model.py` | 環境和配置診斷 | 根目錄 |
| `test_gpt5_tag_generation.py` | 標籤生成測試 | `archive/gpt5-development/` |
| `test_gpt5_detailed_error.py` | 錯誤診斷 | `archive/gpt5-development/` |
| `run_server.py` | 本地伺服器啟動 | 根目錄 |

### 需要創建的工具

| 工具 | 用途 | 優先級 |
|------|------|--------|
| `tests/test_gpt5_scenarios.py` | 場景測試套件 | P0 |
| `tests/test_gpt5_performance.py` | 性能測試 | P1 |
| `tests/monitor_gpt5_costs.py` | 成本監控 | P2 |
| `tests/test_gpt5_error_handling.py` | 錯誤處理測試 | P1 |

---

## 📋 測試前檢查清單

### 本地測試前

- [ ] 環境變數已設置（`OPENAI_API_KEY`）
- [ ] 虛擬環境已激活
- [ ] 依賴已安裝（`pip install -r requirements.txt`）
- [ ] Supabase 連接正常

### Zeabur 測試前

- [ ] 環境變數已在 Zeabur 設置
- [ ] 代碼已推送到 GitHub
- [ ] Zeabur 部署成功
- [ ] 有 Zeabur URL 可供測試

---

## 🎯 成功標準

### 功能測試成功標準

```yaml
階段 1 (本地功能):
  通過率: 100%
  
階段 2 (功能完整性):
  測試套件 A: 100% 通過
  測試套件 B: > 80% 通過
  測試套件 C: > 60% 通過
  
階段 3 (性能):
  平均回應時間: < 3秒
  P95 回應時間: < 5秒
  成功率: > 95%
  
階段 4 (錯誤處理):
  降級機制: 正常
  錯誤記錄: 完整
  用戶體驗: 良好
  
階段 5 (Zeabur 部署):
  部署成功: ✅
  所有端點: 正常
  日誌: 無錯誤
```

### 生產就緒標準

**必須全部滿足**:
- ✅ 所有 P0 測試通過
- ✅ > 80% P1 測試通過
- ✅ 性能指標達標
- ✅ 安全檢查通過
- ✅ 文檔完整

---

## 📊 測試報告模板

```markdown
# GPT-5 Mini 測試報告

## 測試概況
- 測試日期: _______________
- 測試環境: 本地 / Zeabur
- 測試人員: _______________

## 測試結果

### 功能測試
- 通過: _____ / _____
- 失敗: _____
- 成功率: _____%

### 性能測試
- 平均回應時間: _____秒
- 平均標籤數: _____個
- 平均信心度: _____
- Token 使用: _____

### 成本分析
- 測試請求數: _____
- 總 Token 使用: _____
- 總成本: $_____
- 平均成本: $_____/請求

## 問題列表
1. [問題描述]
2. [問題描述]

## 改進建議
1. [建議]
2. [建議]

## 結論
⬜ 通過 - 可以部署
⬜ 有條件通過 - 需要小修正
⬜ 未通過 - 需要重大修正
```

---

## 🎊 測試規劃完成

### 下一步行動

**立即（今天下午）**:
1. [ ] 創建測試腳本
2. [ ] 執行本地測試
3. [ ] 記錄測試結果

**今天晚上**:
4. [ ] 在 Zeabur 設置環境變數
5. [ ] 驗證部署
6. [ ] 執行生產環境測試

**明天**:
7. [ ] 性能測試
8. [ ] 錯誤處理測試
9. [ ] 開始持續監控

---

**測試計劃已完成！準備開始執行測試了嗎？** 🧪
