# 🚨 P0 關鍵問題與解決方案

**發現時間**: 2025-10-21  
**嚴重度**: P0（阻塞 MVP）  
**狀態**: 解決方案已制定

---

## 🔥 問題 1: asyncio.run() 在 FastAPI 中會失敗

### 問題描述

**原設計：**
```python
@function_tool
def search_examples(...):
    # 工具是同步的
    result = asyncio.run(db.async_query(...))  # ❌ 會失敗！
    return result

# FastAPI 端點
@app.post("/api/inspire/start")
async def start_inspire(...):
    result = await Runner.run(agent, ...)  # 已經在 async 環境
    # 內部調用工具時，asyncio.run() 會報錯：
    # RuntimeError: This event loop is already running
```

---

### 解決方案 A: 使用同步 Supabase 客戶端（推薦）⭐

**發現：** 現有 SupabaseService 已經是同步的！

```python
# src/api/services/supabase_client.py

class SupabaseService:
    def __init__(self):
        # 使用同步 create_client
        self._client = create_client(url, key)  # 同步版本
    
    # 方法看起來是 async，但內部調用是同步的
    async def get_tags_by_names(self, names):
        # self.client.table() 是同步調用
        result = self.client.table('tags_final')\
            .select('*')\
            .in_('name', names)\
            .execute()  # 同步執行
        
        return result.data
```

**關鍵發現：**
- ✅ Supabase Python 客戶端本身就是**同步的**
- ✅ SupabaseService 的 async 只是包裝層（為了與 FastAPI 一致）
- ✅ 內部調用是同步的（沒有 await）

**工具可以直接調用：**
```python
@function_tool
def search_examples(...):
    # 直接調用（同步）✅
    result = db.client.table('tags_final').select('*').execute()
    return process(result.data)

# 不需要 asyncio.run()！
```

**驗證：**
```python
# 測試
db = get_supabase_service()
result = db.client.table('tags_final').select('*').limit(1).execute()
print(result.data)  # 直接可用，同步調用
```

---

### 解決方案 B: 如果真需要 async（備用）

**方案 B1：在獨立線程運行**
```python
import threading
import asyncio

def run_async_safely(coro):
    """在新線程中運行 async 函數"""
    result_container = []
    
    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        result_container.append(result)
    
    thread = threading.Thread(target=runner)
    thread.start()
    thread.join()
    
    return result_container[0]

@function_tool
def tool_name(...):
    result = run_async_safely(async_function(...))
    return result
```

**方案 B2：改用 SDK 的 async Runner（如果 SDK 支援）**
- 需要研究 SDK 文檔
- 可能需要整個端點改為同步

---

### 結論：使用方案 A ✅

**原因：**
- ✅ Supabase 客戶端本身是同步的
- ✅ 不需要 asyncio.run()
- ✅ 零額外成本
- ✅ 立即可用

**行動：**
- 更新工具定義（直接調用 db.client）
- 測試整合

---

## 🗄️ 問題 2: 生產環境 Session 存儲

### 問題描述

**原設計：**
```python
session = SQLiteSession("user_123", "conversations.db")
```

**問題：**
```
本地開發：✅ 檔案存在，可持久化
生產環境（Docker/Zeabur）：
  ❌ 容器重啟 → 檔案丟失
  ❌ 多實例 → 無法共享
  ❌ 水平擴展 → Session 不同步
```

---

### 解決方案：環境切換（開發 SQLite，生產 Redis）

**檢查 SDK 支援：**
```python
from agents import SQLiteSession, RedisSession  # SDK 都支援

# 開發環境
session = SQLiteSession("user_123", "conversations.db")

# 生產環境
session = RedisSession.from_url(
    session_id="user_123",
    url="redis://localhost:6379/0"
)
```

**自動切換：**
```python
# src/api/services/inspire_session_manager.py

import os
from agents import SQLiteSession

# 檢查是否有 Redis（SDK 可能需要可選依賴）
try:
    from agents.extensions.memory import RedisSession
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class InspireSessionManager:
    def __init__(self):
        self.env = os.getenv("ENVIRONMENT", "development")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    def create_session(self, session_id: str):
        """根據環境創建適當的 Session"""
        
        if self.env == "production" and REDIS_AVAILABLE and self.redis_url:
            logger.info(f"[Production] Using RedisSession")
            return RedisSession.from_url(
                session_id=session_id,
                url=self.redis_url
            )
        else:
            logger.info(f"[Development] Using SQLiteSession")
            return SQLiteSession(
                session_id=session_id,
                db_path="data/conversations.db"
            )
```

---

### 生產配置

**環境變數：**
```bash
# .env.production
ENVIRONMENT=production
REDIS_URL=redis://red-xxxx.railway.app:6379/0
```

**Zeabur/Railway 配置：**
- 添加 Redis 服務
- 設置環境變數
- 重啟應用

---

### 安裝 Redis 支援

**檢查 SDK 文檔：**
```bash
# 如果需要額外安裝
pip install 'openai-agents[redis]'
```

**或手動安裝：**
```bash
pip install redis
```

---

## 📋 P0 修復清單

### 修復 1: 更新工具定義

- [ ] 所有工具直接調用 db.client（同步）
- [ ] 不使用 asyncio.run()
- [ ] 測試工具在 FastAPI 環境中運行

### 修復 2: Session 環境切換

- [ ] 實現 InspireSessionManager.create_session()
- [ ] 支援 SQLite（開發）和 Redis（生產）
- [ ] 環境變數配置
- [ ] 更新部署文檔

### 修復 3: 測試整合

- [ ] 在 FastAPI 環境中測試工具調用
- [ ] 驗證無 event loop 錯誤
- [ ] 測試 Session 切換

---

## 🎯 立即行動（今晚，2-3h）

### 步驟 1: 創建正確的工具定義（1h）

**檔案：** `src/api/tools/inspire_tools.py`

```python
# 使用同步 Supabase 客戶端
# 不使用 asyncio.run()
```

### 步驟 2: 創建 Session 管理器（30min）

**檔案：** `src/api/services/inspire_session_manager.py`

```python
# 環境自動切換
# SQLite（開發）或 Redis（生產）
```

### 步驟 3: 測試整合（30min）

**檔案：** `tests/test_inspire_fastapi_integration.py`

```python
# 測試在 FastAPI 環境中調用工具
# 驗證無 event loop 錯誤
```

### 步驟 4: 更新文檔（30min）

- 更新 Session 存儲策略
- 添加生產環境配置
- 記錄問題和解決方案

---

## 🚀 開始修復

**準備好了嗎？我現在立即創建修復代碼！** ✅

