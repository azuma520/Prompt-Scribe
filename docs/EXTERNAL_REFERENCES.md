# 📚 外部參考資源索引

**用途：** 在 Cursor 中快速訪問外部參考資料

---

## 🔗 OpenAI Agents SDK (Python)

### 主要資源

- **Repo**: https://github.com/openai/openai-agents-python
- **文檔**: https://openai.github.io/openai-agents-python/
- **Release**: v0.4.0 (2025-10-17)

### 必看範例

#### 1. 基礎 Agent 與 Handoffs
**文件**: https://github.com/openai/openai-agents-python/blob/main/examples/basic.py

**用途**: 學習如何創建 Agent 和實現 Agent 間切換

**關鍵代碼**:
```python
from agents import Agent, Runner, function_tool

agent = Agent(
    name="Assistant",
    instructions="You are helpful",
    handoffs=[other_agent]
)

result = await Runner.run(agent, "user input")
```

---

#### 2. Function/Tool 定義
**文件**: https://github.com/openai/openai-agents-python/blob/main/examples/functions.py

**用途**: 學習如何定義和使用工具

**關鍵代碼**:
```python
@function_tool
async def get_weather(city: str) -> str:
    """Get weather for a city"""
    return f"Weather in {city}"

agent = Agent(
    name="Data Agent",
    tools=[get_weather]
)
```

---

#### 3. Human-in-the-Loop
**文件**: https://github.com/openai/openai-agents-python/blob/main/examples/human_in_the_loop.py

**用途**: 學習如何實現人工確認機制

**應用場景**: 工具調用前需要用戶確認

---

#### 4. Guardrails (防護措施)
**文件**: https://github.com/openai/openai-agents-python/blob/main/examples/guardrails.py

**用途**: 學習輸入/輸出驗證

**應用場景**: 我們的 3 層防護系統

---

#### 5. Streaming (串流)
**文件**: https://github.com/openai/openai-agents-python/blob/main/examples/streaming.py

**用途**: 學習如何串流 Agent 輸出

**應用場景**: 未來前端實時顯示 Agent 思考過程

---

#### 6. Session Management
**文件**: https://github.com/openai/openai-agents-python/blob/main/examples/session_memory.py

**用途**: 學習 SDK 的 Session 管理

**關鍵代碼**:
```python
from agents import SQLiteSession

session = SQLiteSession("user_123", "conversations.db")

result = await Runner.run(agent, "Hello", session=session)
# Session 自動保存對話歷史
```

---

### SDK 核心概念文檔

#### Agent 設計指南
**URL**: https://lewlh.github.io/2025/04/22/APracticalGuideToBuildingAgents/

**重點章節**:
- Section 3: When to Use Agents（何時用 Agent）
- Section 4: Building Blocks（構建模塊）
- Section 5: Guardrails（防護措施）

**關鍵決策標準**:
```
用 Agent 當：
✅ 複雜決策（情緒→視覺轉換）
✅ 難以維護的規則（無限組合）
✅ 非結構化數據（自然語言）
```

---

## 🔗 OpenAI Agents SDK (JavaScript)

### 主要資源

- **Repo**: https://github.com/openai/openai-agents-js
- **文檔**: https://openai.github.io/openai-agents-js/

### 參考價值

**對我們有用：**
- ✅ 設計模式參考（與 Python SDK 相似）
- ✅ Voice Agent 範例（未來功能）
- ✅ 瀏覽器端 Agent 實現

**暫時不用：**
- ⏳ 當前專注 Python 後端實現
- ⏳ 未來考慮語音功能時再研究

---

## 📖 在 Cursor 中如何使用

### 方法 1: 直接引用 URL

```
@https://github.com/openai/openai-agents-python/blob/main/examples/basic.py
參考這個範例實現我們的 Agent
```

### 方法 2: 引用本文檔

```
@docs/EXTERNAL_REFERENCES.md
根據這裡的參考資源，實現工具定義
```

### 方法 3: 在代碼註釋中添加鏈接

```python
# 參考: https://github.com/openai/openai-agents-python/blob/main/examples/functions.py
@function_tool
async def understand_intent(...):
    pass
```

---

## 🎯 常見實現模式速查

### Pattern 1: 定義 Agent

**參考**: basic.py

```python
from agents import Agent, Runner

agent = Agent(
    name="Inspire",
    instructions="你是親切的創作夥伴...",
    tools=[tool1, tool2],
    handoffs=[other_agent]  # 可選
)
```

---

### Pattern 2: 定義工具

**參考**: functions.py

```python
@function_tool
async def tool_name(
    param1: str,
    param2: int = 0
) -> dict:
    """清楚的工具描述
    
    Args:
        param1: 參數說明
        param2: 可選參數
    """
    # 實現
    return {"result": "value"}
```

---

### Pattern 3: 運行 Agent

**參考**: basic.py

```python
# 簡單運行
result = await Runner.run(agent, "user input")

# 帶 Session
session = SQLiteSession("user_id")
result = await Runner.run(agent, "input", session=session)

# 限制輪次
result = await Runner.run(agent, "input", max_turns=10)
```

---

### Pattern 4: 處理結果

```python
result = await Runner.run(agent, "input")

# 訪問最終輸出
print(result.final_output)

# 訪問所有訊息
for msg in result.messages:
    print(msg)

# 檢查是否有 handoff
if result.handoff:
    print(f"Handed off to {result.handoff.agent.name}")
```

---

## 🛡️ Guardrails 參考

**參考**: guardrails.py

### 輸入驗證

```python
from agents import InputGuardrail

def validate_input(input: str) -> tuple[bool, str]:
    if len(input) > 1000:
        return False, "輸入過長"
    return True, ""

guardrail = InputGuardrail(validate_input)
```

### 輸出驗證

```python
from agents import OutputGuardrail

def validate_output(output: str) -> tuple[bool, str]:
    if "forbidden" in output.lower():
        return False, "輸出包含禁止內容"
    return True, ""
```

---

## 📝 SDK 文檔快速連結

### Python SDK

- **API Reference**: https://openai.github.io/openai-agents-python/reference/
- **Guides**: https://openai.github.io/openai-agents-python/guides/
- **Examples**: https://github.com/openai/openai-agents-python/tree/main/examples

### 特定主題

- **Tools**: https://openai.github.io/openai-agents-python/guides/tools/
- **Handoffs**: https://openai.github.io/openai-agents-python/guides/handoffs/
- **Sessions**: https://openai.github.io/openai-agents-python/guides/sessions/
- **Streaming**: https://openai.github.io/openai-agents-python/guides/streaming/

---

## 🎓 學習路徑建議

### 第 1 天: 基礎

1. 閱讀 Agent 設計指南前 3 章
2. 運行 `examples/basic.py`
3. 理解 Agent 循環原理

### 第 2 天: 工具

1. 研究 `examples/functions.py`
2. 學習 `@function_tool` 裝飾器
3. 實現第一個工具

### 第 3 天: 進階

1. 研究 `examples/human_in_the_loop.py`
2. 學習 `examples/guardrails.py`
3. 理解 Session 管理

---

## 💡 快速問答

### Q: 如何在 Cursor 中快速查看 SDK 範例？

A: 使用 @-mention:
```
@https://github.com/openai/openai-agents-python/blob/main/examples/basic.py
```

### Q: 如何確保遵循 SDK 最佳實踐？

A: 參考 `.cursorrules` 文件，Cursor 會自動遵循

### Q: 如何找到特定功能的實現？

A: 查閱本文檔的「常見實現模式速查」章節

---

## 🔄 保持更新

SDK 更新時，檢查：
- Release notes: https://github.com/openai/openai-agents-python/releases
- Changelog: https://github.com/openai/openai-agents-python/blob/main/CHANGELOG.md

---

**最後更新**: 2025-10-21  
**SDK 版本**: Python v0.4.0, JS v0.1.10  
**維護者**: Prompt-Scribe Team

