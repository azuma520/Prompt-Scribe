# 🎯 Inspire Agent 最終實施指南

**基於最終討論的明確立場**

**版本**: 1.0.0  
**日期**: 2025-10-21  
**原則**: **保持 Agent 靈活決策，不過度限制**

---

## 💡 核心原則

### Agent 的價值在於靈活決策

```
❌ 傳統系統：if-else 規則，僵化
✅ Agent 系統：理解情境，靈活應對
```

**我們的立場：**
- ✅ 給 Agent 工具和指南
- ✅ 定義紅線（安全、品質）
- ❌ 不強制具體話術
- ❌ 不限制創意空間
- ❌ 不過度規範流程

---

## 🛠️ 工具與限制的平衡

### 什麼要「嚴格」？

#### 1. 內容安全（硬性紅線）

```python
# 絕對不能生成
BLOCKED = ["loli", "shota", "child", ...]

# 檢測到 → 立即移除
# 不是建議，是強制
```

**原因：** 法律合規，無討論空間

---

#### 2. 品質驗證（必須執行）

```python
# finalize 之前必須
validate_quality(tags)

# score < 70 → 必須修正
# 不是建議，是流程
```

**原因：** 確保輸出可用

---

#### 3. 工具 I/O 契約（技術必須）

```python
# 工具返回格式必須嚴格
{
  "tag": str,      # 只這 4 個鍵
  "category": str,
  "popularity": int,
  "usage_hint": str
}

# 不能自創鍵名
```

**原因：** 技術穩定性

---

### 什麼要「靈活」？

#### 1. 對話語氣（靈活，只記錄）

```python
# 語氣 Lint → mode="log_only"
linter.lint(reply)  # 只記錄指標
# 不攔截，不強制

# Agent 自己決定怎麼說
```

**原因：** 自然對話需要靈活性

---

#### 2. 工具使用順序（Agent 決定）

```python
# 不強制流程
# Agent 自己判斷：
- 要不要搜尋？
- 要不要澄清？
- 何時該收斂？

# 我們只定義「絕對要做」（如驗證品質）
# 其他由 Agent 靈活決定
```

**原因：** 不同情況需要不同策略

---

#### 3. 使用者調整（完全自由）

```python
使用者可以說任何話：
- "要更夢幻"
- "加點魔法"
- "改成男生"
- "不要這麼可愛，要帥氣"
- ...

Agent 自己理解和執行
不需要固定按鈕映射
```

**原因：** LLM 的自然語言理解就是優勢

---

## 📚 文件定位調整

### 1. JSONL Few-Shot 範例

**用途：**
- ✅ **測試參考**（自動回歸測試）
- ✅ **開發參考**（理解流程）
- ❌ **不用於強制 Agent 行為**

**System Prompt 中：**
- ✅ 放 1-2 個最簡單的範例（示範語氣和工具使用）
- ❌ 不放全部 10 個（太長，過度限制）

---

### 2. 語氣 Linter

**用途：**
- ✅ **記錄指標**（簡潔度、一致性）
- ✅ **定期分析**（人工優化）
- ❌ **不攔截回應**（保持靈活）

**模式：** `log_only`

---

### 3. Tag 映射與快速調整

**快速調整（QUICK_ADJUSTMENTS）：**
- ✅ 保留在代碼中（作為參考資料）
- ❌ 不在前端顯示固定按鈕
- ✅ Agent 自己理解使用者的自由文字調整

**Tag 別名（TAG_ALIAS_MAP）：**
- ✅ 保留（技術必須，解析別名）

---

### 4. 評測策略

**CI 自動測試（3 個核心）：**
```python
# 每次 git push 自動跑
- S1: 清晰輸入（快樂路徑）
- S2: 模糊輸入（澄清流程）
- S8: 風險內容（安全關鍵）

成本：$0.0015/次
```

**人工測試（7 個場景）：**
```python
# 你手動跑（每週一次）
- S3, S4, S5, S6, S7, S9, S10

# 檢查：
- 語氣是否自然
- 創意是否多樣
- 體驗是否順暢
```

---

### 5. 參數建議

**完全移除 usage_tips** ✅

```python
# finalize_prompt 輸出
{
  "parameters": {
    "cfg_scale": 7.5,      # 給預設值
    "steps": 30,
    "sampler": "DPM++ 2M Karras"
  }
  # 不給 usage_tips
}
```

**前端顯示：**
```
參數：CFG 7.5｜Steps 30｜Sampler DPM++ 2M Karras

（不給任何建議，讓使用者自己調整）
```

---

## 📝 需要調整的文件清單

讓我調整以下文件：

### 1. `inspire_response_templates.py` ✅（已調整）
- 移除 `usage_tips`

### 2. `INSPIRE_P0_CHECKLIST.md`
- 調整語氣 Linter 為 log_only
- 調整評測策略為 3 個 CI + 7 個人工
- 移除參數建議檢查項

### 3. `INSPIRE_IMPLEMENTATION_DETAILS.md`
- 添加「靈活決策」說明
- 調整快速調整控件的定位

### 4. `tag_mappings.py`
- 添加註釋說明控件為參考資料

讓我開始調整：

<function_calls>
<invoke name="search_replace">
<parameter name="file_path">src/api/config/tag_mappings.py
