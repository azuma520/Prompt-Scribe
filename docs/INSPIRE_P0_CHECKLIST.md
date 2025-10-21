# ✅ Inspire Agent P0 實作檢查清單

**基於技術評審的關鍵補充**

**版本**: 1.0.0  
**日期**: 2025-10-21  
**狀態**: 實作前檢查清單

---

## 🎯 核心原則

### 評審結論

> **架構正確：** 理解 → 參考 → 創意 → 驗證 → 定稿 的五段式循環清晰、可運營。

### 三大 P0 補位

1. ✅ 資料庫契約與快取策略
2. ✅ 驗證器實作細節
3. ✅ 安全/合規邊界（NSFW/未成年人）

---

## 📋 P0 實作檢查清單（上線前必做）

### 1. 資料庫層（Day 1）

- [ ] **Tags 主表 Schema**
  - [ ] 必要欄位：`tag`, `category`, `post_count`, `aliases`, `conflicts`, `implied`, `nsfw_level`
  - [ ] 欄位約束：`category` 枚舉、`nsfw_level` 預設 `all-ages`
  - [ ] 索引：category, post_count DESC, nsfw_level, aliases GIN
  
- [ ] **Tag 共現表**
  - [ ] 欄位：`tag`, `other_tag`, `cooccur_count`, `confidence`
  - [ ] 約束：無自關聯、外鍵約束
  
- [ ] **派生視圖**
  - [ ] `popular_tags`（post_count >= 1000, nsfw_level = 'all-ages'）
  - [ ] `conflict_pairs`（UNNEST conflicts）
  - [ ] 刷新策略：每日凌晨自動刷新
  
- [ ] **Inspire Sessions 表**
  - [ ] 狀態機欄位：`current_phase`（6 個狀態）
  - [ ] 追蹤欄位：`total_cost`, `tool_call_count`, `quality_score`
  - [ ] 索引：user_id + created_at, phase, quality_score

**驗收標準：**
```sql
-- 測試查詢
SELECT COUNT(*) FROM tags WHERE nsfw_level = 'all-ages';  -- 應有大量結果
SELECT * FROM popular_tags LIMIT 10;                       -- 應返回熱門標籤
SELECT * FROM conflict_pairs WHERE tag_a = 'long_hair';   -- 應返回衝突
```

---

### 2. Redis 快取層（Day 1）

- [ ] **熱門標籤快取**
  - [ ] Key: `hot:tags:all`, `hot:tags:{category}`
  - [ ] 類型：Sorted Set（按 post_count）
  - [ ] TTL: 24 小時
  - [ ] 預載：TOP 100 全類別 + TOP 50 各類別
  
- [ ] **標籤組合快取**
  - [ ] Key: `combo:{tag}`
  - [ ] 類型：Sorted Set（按 cooccur_count）
  - [ ] TTL: 1 小時
  
- [ ] **別名快取**
  - [ ] Key: `alias:{alias}`
  - [ ] 類型：String（canonical tag）
  - [ ] TTL: 永久（直到資料庫更新）
  
- [ ] **封禁清單**
  - [ ] Key: `policy:blocklist`
  - [ ] 類型：Set
  - [ ] 內容：`loli, shota, child, kid, ...`（至少 20 個）
  
- [ ] **NSFW 清單**
  - [ ] Key: `policy:nsfw`
  - [ ] 類型：Set

**驗收標準：**
```bash
redis-cli ZCARD "hot:tags:all"           # 應返回 100
redis-cli SISMEMBER "policy:blocklist" "loli"  # 應返回 1
redis-cli GET "alias:longhair"           # 應返回 "long_hair"
```

---

### 3. 內容安全過濾器（Day 1-2）

- [ ] **封禁詞檢測**
  - [ ] 實現 `ContentSafetyFilter.is_blocked()`
  - [ ] 實現 `ContentSafetyFilter.filter_tags()`
  - [ ] 測試：輸入包含 `loli` → 被移除
  
- [ ] **Moderation API 整合**
  - [ ] 實現 `ContentSafetyFilter.check_user_input()`
  - [ ] API 層調用（所有 `/inspire/*` 端點）
  - [ ] 測試：敏感輸入 → 拒絕並返回錯誤
  
- [ ] **安全替代方案**
  - [ ] 實現 `suggest_safe_alternative()`
  - [ ] 三個固定方向：光影意象、自然元素、抽象幾何
  - [ ] 測試：觸發封禁 → 返回替代方案

**驗收標準：**
```python
# 測試封禁
result = await safety_filter.filter_tags(["1girl", "loli", "cute"])
assert "loli" not in result[0]  # safe_tags
assert "loli" in result[1]      # removed_tags

# 測試 Moderation
is_safe, reason = await safety_filter.check_user_input("a cute loli girl")
assert is_safe == False
assert "child" in reason.lower() or "loli" in reason.lower()
```

---

### 4. 工具 I/O 契約（Day 2-4）

- [ ] **understand_intent**
  - [ ] 輸出只包含 6 個鍵（嚴格）
  - [ ] `clarity_level` 枚舉驗證
  - [ ] `confidence` 範圍 0-1
  - [ ] 單元測試：5 個案例
  
- [ ] **generate_ideas**
  - [ ] 輸出 `ideas` 為陣列，2-3 個元素
  - [ ] 每個 idea 包含 6 個鍵（嚴格）
  - [ ] `main_tags` 至少 10 個
  - [ ] 單元測試：3 個案例
  
- [ ] **validate_quality**
  - [ ] 輸出嚴格符合契約（8 個頂層鍵）
  - [ ] `score` 範圍 0-100
  - [ ] `quick_fixes` 包含 remove/add/replace
  - [ ] 單元測試：10 個案例（含邊界情況）
  
- [ ] **finalize_prompt**
  - [ ] 輸出嚴格符合契約
  - [ ] `positive_prompt` 長度 <500 字
  - [ ] `negative_prompt` 包含固定前綴
  - [ ] 單元測試：5 個案例

**驗收標準：**
- 所有合約測試通過（`tests/test_inspire_contracts.py`）
- 未知鍵被忽略或返回 422
- 缺失必要鍵返回 400

---

### 5. 驗證器可執行邏輯（Day 4）

- [ ] **正規化函數**
  - [ ] `_normalize_tags()`：去重、小寫、解析別名
  - [ ] 測試：`["1girl", "1Girl", "longhair"]` → `["1girl", "long_hair"]`
  
- [ ] **有效性檢查**
  - [ ] `_check_validity()`：批量 SQL 查詢
  - [ ] 無效標籤 → 分數 -35
  - [ ] 建議相似標籤（similarity > 0.3）
  - [ ] 測試：10/10 通過
  
- [ ] **衝突檢查**
  - [ ] `_check_conflicts()`：使用 conflict_pairs 視圖
  - [ ] 嚴重衝突 → 分數 -25
  - [ ] `quick_fixes.remove` 包含流行度較低者
  - [ ] 測試：`["long_hair", "short_hair"]` → 檢測到衝突
  
- [ ] **冗餘檢查**
  - [ ] `_check_redundancy()`：檢查別名關係
  - [ ] 冗餘對 → 分數 -5
  - [ ] 測試：`["long_hair", "longhair"]` → 檢測到冗餘
  
- [ ] **平衡檢查**
  - [ ] `_check_balance()`：類別分佈至少 3 類
  - [ ] 不足 → 分數 -20，建議補充
  - [ ] 測試：只有 CHARACTER 和 SCENE → 建議添加 MOOD
  
- [ ] **流行度檢查**
  - [ ] `_check_popularity()`：冷門比例 <40%
  - [ ] 超標 → 分數 -5
  - [ ] 測試：50% 冷門標籤 → 警告

**驗收標準：**
```python
# 完整測試
tags = ["invalid_tag", "long_hair", "short_hair", "1girl"]
result = await validator.validate(tags, check_aspects=["validity", "conflicts", "balance"])

assert result["score"] == 40  # 100 - 35(invalid) - 25(conflict)
assert "invalid_tag" in result["quick_fixes"]["remove"]
assert "long_hair" in result["quick_fixes"]["remove"] or "short_hair" in result["quick_fixes"]["remove"]
```

---

### 6. 語氣 Linter（Day 2-7）

- [ ] **禁語檢測**
  - [ ] 14 個禁語模式（正則）
  - [ ] 命中 → 記錄 violation
  
- [ ] **語氣指標**
  - [ ] 首句長度 ≤ 18 字
  - [ ] 句子數 ≤ 3
  - [ ] 總長度 ≤ 80 字
  - [ ] Emoji 數 ≤ 1
  
- [ ] **整合到 API**
  - [ ] 所有回應經過 Linter
  - [ ] Violation rate < 2%
  - [ ] 記錄指標到監控

**驗收標準：**
```python
# 測試禁語
linter = InspireToneLinter()
is_valid, violations, metrics = linter.lint("感謝您的輸入，根據系統分析...")
assert is_valid == False
assert len(violations) >= 2

# 測試合格回應
is_valid, violations, metrics = linter.lint("收到！給你三個方向 🎨")
assert is_valid == True
assert metrics["emoji_count"] == 1
```

---

### 7. 狀態機與中止條件（Day 6）

- [ ] **狀態定義**
  - [ ] 6 個狀態：understanding, exploring, refining, finalizing, completed, aborted
  - [ ] 狀態轉換邏輯
  
- [ ] **中止條件（5 個）**
  - [ ] 成本超限（>= $0.015）
  - [ ] 輪次超限（>= 15 turns）
  - [ ] 超時（>= 120 秒）
  - [ ] 工具調用過多（單工具 >= 5 次）
  - [ ] 收斂（連續 3 次反饋相同）
  
- [ ] **中止處理**
  - [ ] 取當前最佳結果
  - [ ] 友好提示（不暴露技術細節）
  - [ ] 記錄 abort_reason

**驗收標準：**
```python
# 測試成本中止
state = InspireStateMachine(session_id, db, limits={"max_cost": 0.001})
state.total_cost = 0.0015
should_abort, reason = state.should_abort()
assert should_abort == True
assert "成本" in reason

# 測試收斂
state.last_feedback = ["要更夢幻", "要更夢幻", "要更夢幻"]
should_abort, reason = state.should_abort()
assert should_abort == True
assert "收斂" in reason
```

---

### 8. E2E 金樣測試（Day 6）

- [ ] **金樣 A：清晰輸入**
  - [ ] 2 輪內完成
  - [ ] 分數 >= 85
  - [ ] 包含使用者提到的元素
  
- [ ] **金樣 B：模糊輸入**
  - [ ] 4-5 輪完成
  - [ ] 分數 >= 80
  - [ ] 澄清 → 生成 → 精煉 → 定稿
  
- [ ] **金樣 C：風險內容**
  - [ ] 立即拒絕
  - [ ] 提供 3 個安全替代
  - [ ] 語氣友好不說教

**驗收標準：**
- 3/3 金樣測試通過
- CI 自動運行
- 任何回歸立即發現

---

### 9. 語氣與格式一致性（Day 2-7）

- [ ] **固定模板**
  - [ ] 三卡方向卡片（`format_direction_cards()`）
  - [ ] 定稿輸出（`format_final_output()`）
  - [ ] 澄清問題（`format_clarification()`）
  - [ ] 品質修正提示（`format_quality_fix_notice()`）
  
- [ ] **快速調整控件**
  - [ ] 4 個控件映射（更夢幻、更寫實、少人像、加夜景）
  - [ ] `apply_quick_adjustment()` 實現
  - [ ] 測試：每個控件正確添加/移除標籤
  
- [ ] **負面 Prompt 模板**
  - [ ] 4 個模板（default, artistic, realistic, abstract）
  - [ ] 所有包含固定前綴：`nsfw, child, loli, shota, gore, ...`
  - [ ] 根據風格自動選擇

**驗收標準：**
- 所有回應使用統一模板
- 語氣 Lint 通過率 > 98%
- 負面 Prompt 一致性 100%

---

### 10. 參數建議規範化（Day 5）

- [ ] **4 個預設模板**
  - [ ] anime_dreamy: CFG 8.0, Steps 35
  - [ ] realistic: CFG 6.0, Steps 32
  - [ ] abstract_surreal: CFG 7.5, Steps 45
  - [ ] artistic_painterly: CFG 7.0, Steps 35
  
- [ ] **話術統一**
  - [ ] 動漫夢幻：「建議 CFG 7-9，想更柔可降到 6.5」
  - [ ] 寫實：「建議較低 CFG (5-7) 保持自然」
  - [ ] 抽象：「建議多試幾次，Steps 可提高到 40-60」
  
- [ ] **根據風格自動選擇**
  - [ ] `get_parameter_preset(style)` 實現
  - [ ] 測試：輸入包含 "dreamy" → 返回 anime_dreamy 預設

---

## 📊 量化指標（P1 - 可測可評）

### 語言三指標

- [ ] **簡潔度**
  - [ ] 平均每回合字數 ≤ 80
  - [ ] 首句 ≤ 18 字
  - [ ] 監控儀表板顯示

- [ ] **互動效率**
  - [ ] S1 清晰輸入：≤ 2 輪
  - [ ] S2 模糊輸入：≤ 4 輪
  - [ ] S3 抽象概念：≤ 6 輪
  - [ ] 平均：3-4 輪

- [ ] **一致性**
  - [ ] 語氣 Lint 通過率 > 98%
  - [ ] 模板使用率 > 95%
  - [ ] 禁語命中率 < 2%

---

### 自動評測（Regression Tests）

- [ ] **10 個場景斷言**
  - [ ] 每個場景 3 條 must_include
  - [ ] 每個場景 3 條 must_not_include
  - [ ] 工具預算限制（max_generate, max_search, max_total）
  
- [ ] **CI 整合**
  - [ ] 每次 commit 自動運行
  - [ ] 任何場景失敗 → 阻擋 merge
  - [ ] Slack/Discord 通知

**評測腳本：**
```python
# tests/test_inspire_regression.py
import json

def test_scenario_assertions():
    """測試所有場景斷言"""
    
    with open("tests/inspire_assertions.jsonl") as f:
        for line in f:
            spec = json.loads(line)
            
            if "scenario" not in spec:
                continue  # 跳過指標定義
            
            # 運行場景
            result = run_scenario(spec["scenario"])
            
            # 檢查 must_include
            for phrase in spec.get("must_include", []):
                assert phrase in result["response"], f"缺少必要語句：{phrase}"
            
            # 檢查 must_not_include
            for phrase in spec.get("must_not_include", []):
                assert phrase not in result["response"], f"包含禁語：{phrase}"
            
            # 檢查工具預算
            for tool, max_count in spec.get("tool_budget", {}).items():
                if tool == "max_total":
                    assert result["total_tool_calls"] <= max_count
                else:
                    actual = result["tool_calls"].get(tool.replace("max_", ""), 0)
                    assert actual <= max_count, f"{tool} 超限：{actual} > {max_count}"
```

---

## 🚀 一週 MVP 時程（Day-by-Day）

### Day 1: 資料層 ✅（6-8h）
- PostgreSQL Schema
- Redis 快取
- 內容安全過濾器（初版）

### Day 2: 理解工具 ✅（4-6h）
- understand_intent（簡化版）
- 3 問題澄清
- Moderation API 整合

### Day 3: 創意生成 ✅（5-7h）
- generate_ideas（熱門池版）
- 快速調整控件
- 單元測試

### Day 4: 品質驗證 ✅（6-8h）
- validate_quality（完整）
- quick_fixes 邏輯
- 單元測試（10 案例）

### Day 5: 定稿工具 ✅（3-5h）
- finalize_prompt
- 模板整合
- 參數建議

### Day 6: 測試與整合 ✅（6-8h）
- E2E 金樣測試
- 合約測試
- 狀態機
- CI 設置

### Day 7: 前端 + 上線準備 ✅（8-10h）
- 前端三卡展示
- 一鍵修復
- 完整流程測試
- 監控儀表板

**總計：** 38-52 小時（5-7 個工作日）

---

## 📁 相關檔案

### 設計文檔
- `INSPIRE_AGENT_OVERVIEW.md` - 總覽
- `INSPIRE_AGENT_DESIGN.md` - 技術設計
- `INSPIRE_CONVERSATION_EXAMPLES.md` - 對話範例（已更新）
- `INSPIRE_IMPLEMENTATION_PLAN.md` - 實施計劃
- `INSPIRE_IMPLEMENTATION_DETAILS.md` - 實作細節
- `INSPIRE_AGENT_DECISIONS_LOG.md` - 決策記錄

### 實作檔案
- `src/api/services/inspire_tone_linter.py` - 語氣檢查器（新）
- `src/api/config/tag_mappings.py` - Tag 映射與控件（新）
- `src/api/templates/inspire_response_templates.py` - 回應模板（新）
- `docs/inspire_dialogue_examples.jsonl` - Few-shot 範例（新）
- `tests/inspire_assertions.jsonl` - 評測規格（新）

---

## 🎯 上線標準

### 功能完整性
- [ ] 5 個工具全部實現
- [ ] 3 層防護全部生效
- [ ] 狀態機正常運作
- [ ] 所有中止條件測試通過

### 品質標準
- [ ] 金樣 A 分數 >= 85
- [ ] 金樣 B 分數 >= 80
- [ ] 語氣 Lint 通過率 >= 98%
- [ ] 合約測試 100% 通過

### 安全標準
- [ ] 封禁詞 100% 攔截
- [ ] Moderation API 整合
- [ ] 安全替代方案測試通過
- [ ] 負面 Prompt 一致性 100%

### 性能標準
- [ ] 平均回應時間 < 3 秒
- [ ] 平均成本 < $0.001
- [ ] 平均輪次 3-4 輪
- [ ] 完成率 > 85%

---

## ✨ 延伸功能（P2 - 迭代期）

### 個人化學習
- [ ] `user_tag_weights` 表
- [ ] 採納行為追蹤
- [ ] 偏好向量計算
- [ ] 下次優先採樣

### 教學模式
- [ ] 「顯示推理」開關
- [ ] 解釋為何添加/刪除標籤
- [ ] 提升學習價值

### 行銷整合
- [ ] 自動同步到 NocoDB/Trello
- [ ] Preset 分享功能
- [ ] 社群範例庫

---

## 🔍 檢查點

### 開始實作前
- [ ] 所有 P0 檢查清單項目已審閱
- [ ] 資料庫 Schema 已確認
- [ ] 封禁清單已準備
- [ ] 開發環境已設置（OpenAI Agents SDK 已安裝）

### 實作過程中
- [ ] 每日檢查進度
- [ ] 每個工具完成後運行單元測試
- [ ] 每個 Day 結束前運行相關金樣測試
- [ ] 語氣 Lint 持續監控

### 上線前
- [ ] 所有 P0 項目完成
- [ ] 所有測試通過
- [ ] 性能指標達標
- [ ] 安全檢查通過
- [ ] 文檔完整

---

**這份檢查清單確保 MVP 品質，可直接執行！** ✅

**最後更新：** 2025-10-21  
**維護者：** Prompt-Scribe Team

