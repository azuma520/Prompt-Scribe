# 🔧 故障排除指南

## 🎯 目的
提供常見問題的快速解決方案，幫助開發團隊快速定位和解決問題。

---

## 🚨 常見問題分類

### 1. 環境配置問題
### 2. 依賴管理問題  
### 3. 編碼問題
### 4. 測試問題
### 5. 部署問題
### 6. 外部服務問題

---

## 🔍 環境配置問題

### 問題: ModuleNotFoundError

#### 症狀
```bash
ModuleNotFoundError: No module named 'src.api'
```

#### 可能原因
1. 缺少 `__init__.py` 文件
2. Python 路徑設置不正確
3. 虛擬環境未激活
4. 相對導入路徑錯誤

#### 解決步驟
1. **檢查目錄結構**:
   ```bash
   # 確保所有目錄都有 __init__.py
   find . -name "__init__.py" -type f
   ```

2. **設置 Python 路徑**:
   ```bash
   # 方法 1: 設置環境變數
   export PYTHONPATH="${PYTHONPATH}:/path/to/project"
   
   # 方法 2: 在代碼中設置
   import sys
   sys.path.insert(0, '/path/to/project')
   ```

3. **檢查虛擬環境**:
   ```bash
   # 激活虛擬環境
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   
   # 確認 Python 路徑
   which python
   ```

4. **使用絕對導入**:
   ```python
   # ❌ 避免相對導入
   from ..services.gpt5_nano_client import GPT5NanoClient
   
   # ✅ 使用絕對導入
   from src.api.services.gpt5_nano_client import GPT5NanoClient
   ```

#### 預防措施
- [ ] 確保所有 Python 包都有 `__init__.py` 文件
- [ ] 使用虛擬環境隔離依賴
- [ ] 設置正確的 `PYTHONPATH`
- [ ] 使用絕對導入路徑

---

### 問題: 環境變數未設置

#### 症狀
```bash
KeyError: 'OPENAI_API_KEY'
```

#### 可能原因
1. 環境變數未設置
2. 環境變數名稱錯誤
3. 環境變數值為空
4. 環境變數未導出

#### 解決步驟
1. **檢查環境變數**:
   ```bash
   # 檢查所有環境變數
   env | grep OPENAI
   
   # 檢查特定變數
   echo $OPENAI_API_KEY
   ```

2. **設置環境變數**:
   ```bash
   # 臨時設置
   export OPENAI_API_KEY="your-api-key"
   
   # 永久設置 (添加到 ~/.bashrc 或 ~/.profile)
   echo 'export OPENAI_API_KEY="your-api-key"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **在代碼中驗證**:
   ```python
   import os
   
   def validate_environment():
       required_vars = ['OPENAI_API_KEY', 'OPENAI_MODEL']
       missing = [var for var in required_vars if not os.getenv(var)]
       if missing:
           raise EnvironmentError(f"Missing: {missing}")
   ```

4. **使用 .env 文件**:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # 加載 .env 文件
   ```

#### 預防措施
- [ ] 創建 `.env.example` 文件
- [ ] 在啟動時驗證環境變數
- [ ] 使用環境變數管理工具
- [ ] 文檔化所有必要的環境變數

---

## 🔍 編碼問題

### 問題: Unicode 編碼錯誤

#### 症狀
```bash
UnicodeEncodeError: 'cp950' codec can't encode character '\U0001f680'
```

#### 可能原因
1. Windows 系統編碼限制
2. 使用了不支持的 Unicode 字符
3. 文件編碼設置不正確
4. 終端編碼設置問題

#### 解決步驟
1. **設置文件編碼**:
   ```python
   # -*- coding: utf-8 -*-
   ```

2. **避免使用 emoji**:
   ```python
   # ❌ 避免
   print("🚀 開始測試")
   
   # ✅ 推薦
   print("開始測試")
   print("[INFO] 開始測試")
   ```

3. **設置終端編碼**:
   ```bash
   # Windows PowerShell
   chcp 65001
   
   # 或設置環境變數
   set PYTHONIOENCODING=utf-8
   ```

4. **使用 ASCII 字符**:
   ```python
   # 使用簡單的 ASCII 字符
   STATUS_PASS = "[PASS]"
   STATUS_FAIL = "[FAIL]"
   STATUS_INFO = "[INFO]"
   ```

#### 預防措施
- [ ] 在測試腳本中避免使用 emoji
- [ ] 設置正確的文件編碼
- [ ] 使用跨平台兼容的字符
- [ ] 在 CI/CD 中測試不同操作系統

---

## 🔍 測試問題

### 問題: pytest 找不到測試文件

#### 症狀
```bash
ERROR: file or directory not found: tests/test_gpt5_nano_integration.py
```

#### 可能原因
1. pytest 配置不完整
2. 測試文件路徑錯誤
3. 測試發現機制問題
4. 工作目錄不正確

#### 解決步驟
1. **檢查 pytest 配置**:
   ```toml
   # pyproject.toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_paths = ["src"]
   python_files = ["test_*.py", "*_test.py"]
   ```

2. **創建 pytest.ini**:
   ```ini
   [pytest]
   testpaths = tests
   python_paths = src
   addopts = -v --tb=short
   ```

3. **檢查測試文件結構**:
   ```
   tests/
     __init__.py
     test_gpt5_nano_integration.py
     conftest.py
   ```

4. **使用正確的運行方式**:
   ```bash
   # 從專案根目錄運行
   pytest tests/test_gpt5_nano_integration.py
   
   # 或指定路徑
   pytest tests/ -v
   ```

#### 預防措施
- [ ] 設置完整的 pytest 配置
- [ ] 使用一致的測試目錄結構
- [ ] 在 CI/CD 中運行測試
- [ ] 定期檢查測試覆蓋率

---

### 問題: Mock 測試失敗

#### 症狀
```bash
AttributeError: 'MagicMock' object has no attribute 'choices'
```

#### 可能原因
1. Mock 設置不正確
2. 異步函數 Mock 問題
3. Mock 層級設置錯誤
4. 測試隔離不完整

#### 解決步驟
1. **正確設置 Mock**:
   ```python
   @patch('src.api.services.gpt5_nano_client.openai')
   async def test_generate_tags_success(self, mock_openai):
       # 設置 Mock 回應
       mock_response = MagicMock()
       mock_response.choices = [MagicMock()]
       mock_response.choices[0].message.content = '{"tags": ["test"]}'
       
       # 設置異步 Mock
       mock_client = MagicMock()
       mock_openai.OpenAI.return_value = mock_client
       mock_client.chat.completions.acreate = AsyncMock(
           return_value=mock_response
       )
   ```

2. **使用 AsyncMock**:
   ```python
   from unittest.mock import AsyncMock
   
   # 對於異步函數使用 AsyncMock
   mock_func = AsyncMock(return_value=expected_result)
   ```

3. **檢查 Mock 層級**:
   ```python
   # 確保 Mock 的層級正確
   with patch('module.function') as mock_func:
       # 測試邏輯
   ```

#### 預防措施
- [ ] 學習 Mock 最佳實踐
- [ ] 使用 AsyncMock 處理異步函數
- [ ] 確保測試隔離
- [ ] 定期檢查 Mock 設置

---

## 🔍 部署問題

### 問題: 外部服務連接失敗

#### 症狀
```bash
ConnectionError: Failed to connect to OpenAI API
```

#### 可能原因
1. 網路連接問題
2. API 金鑰無效
3. 服務不可用
4. 防火牆阻擋

#### 解決步驟
1. **檢查網路連接**:
   ```bash
   # 測試網路連接
   ping api.openai.com
   curl -I https://api.openai.com
   ```

2. **驗證 API 金鑰**:
   ```python
   import openai
   
   # 測試 API 金鑰
   try:
       client = openai.OpenAI(api_key="your-key")
       response = client.models.list()
       print("API 金鑰有效")
   except Exception as e:
       print(f"API 金鑰無效: {e}")
   ```

3. **實現重試機制**:
   ```python
   import asyncio
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
   async def call_openai_with_retry(prompt):
       return await openai_client.chat.completions.acreate(...)
   ```

4. **添加健康檢查**:
   ```python
   @router.get("/health")
   async def health_check():
       try:
           # 測試外部服務
           await test_external_services()
           return {"status": "healthy"}
       except Exception as e:
           return {"status": "unhealthy", "error": str(e)}
   ```

#### 預防措施
- [ ] 實現重試機制
- [ ] 添加健康檢查端點
- [ ] 監控外部服務狀態
- [ ] 準備回退方案

---

## 🔍 外部服務問題

### 問題: OpenAI API 限制

#### 症狀
```bash
RateLimitError: Rate limit exceeded
```

#### 可能原因
1. API 調用頻率過高
2. Token 使用量超限
3. 帳戶額度不足
4. 並發請求過多

#### 解決步驟
1. **實現速率限制**:
   ```python
   import asyncio
   from asyncio import Semaphore
   
   class RateLimitedClient:
       def __init__(self, max_concurrent=5):
           self.semaphore = Semaphore(max_concurrent)
       
       async def call_api(self, prompt):
           async with self.semaphore:
               return await self._make_request(prompt)
   ```

2. **添加請求間隔**:
   ```python
   import time
   
   async def call_with_delay():
       await asyncio.sleep(1)  # 1 秒延遲
       return await api_call()
   ```

3. **監控使用量**:
   ```python
   def track_usage(response):
       if hasattr(response, 'usage'):
           usage = response.usage
           logger.info(f"Token usage: {usage.total_tokens}")
           # 檢查是否接近限制
           if usage.total_tokens > 80000:  # 假設限制為 100k
               logger.warning("Approaching token limit")
   ```

4. **實現回退機制**:
   ```python
   async def recommend_tags_with_fallback(description):
       try:
           return await gpt5_client.generate_tags(description)
       except RateLimitError:
           logger.warning("Rate limit exceeded, using fallback")
           return await keyword_matching(description)
   ```

#### 預防措施
- [ ] 設置合理的請求頻率
- [ ] 監控 API 使用量
- [ ] 實現回退機制
- [ ] 設置使用量告警

---

## 🛠️ 調試工具和技巧

### 1. 日誌調試
```python
import logging

# 設置詳細日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 在關鍵位置添加日誌
logger = logging.getLogger(__name__)
logger.debug(f"Processing request: {request}")
logger.info(f"API call result: {result}")
logger.error(f"Error occurred: {error}")
```

### 2. 斷點調試
```python
# 使用 pdb 調試
import pdb; pdb.set_trace()

# 或使用 ipdb (更友好的界面)
import ipdb; ipdb.set_trace()
```

### 3. 性能分析
```python
import time
import cProfile

# 簡單計時
start_time = time.time()
result = await some_function()
elapsed = time.time() - start_time
print(f"Function took {elapsed:.2f} seconds")

# 詳細性能分析
cProfile.run('your_function()')
```

### 4. 網路調試
```bash
# 檢查網路連接
curl -v https://api.openai.com/v1/models

# 檢查 DNS 解析
nslookup api.openai.com

# 檢查防火牆
telnet api.openai.com 443
```

---

## 📋 問題報告模板

### 問題描述
```
問題標題: [簡短描述問題]
嚴重程度: [Critical/High/Medium/Low]
影響範圍: [描述影響的功能或用戶]
```

### 環境信息
```
操作系統: [Windows/Linux/macOS]
Python 版本: [3.x.x]
依賴版本: [列出相關依賴版本]
部署環境: [開發/測試/生產]
```

### 錯誤信息
```
完整的錯誤堆疊追蹤
相關日誌信息
```

### 重現步驟
```
1. 步驟 1
2. 步驟 2
3. 步驟 3
```

### 預期行為
```
描述預期的正常行為
```

### 實際行為
```
描述實際發生的問題
```

### 已嘗試的解決方案
```
列出已經嘗試過的解決方案
```

---

## 📚 相關資源

### 官方文檔
- [Python 官方文檔](https://docs.python.org/)
- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [pytest 文檔](https://docs.pytest.org/)
- [OpenAI API 文檔](https://platform.openai.com/docs)

### 調試工具
- [Python 調試器 (pdb)](https://docs.python.org/3/library/pdb.html)
- [ipdb 調試器](https://github.com/gotcha/ipdb)
- [logging 模組](https://docs.python.org/3/library/logging.html)

### 最佳實踐
- [Python 最佳實踐](https://docs.python.org/3/tutorial/)
- [測試最佳實踐](https://docs.pytest.org/en/stable/goodpractices.html)
- [錯誤處理最佳實踐](https://docs.python.org/3/tutorial/errors.html)

---

## 📝 更新記錄

| 日期 | 版本 | 更新內容 | 作者 |
|------|------|----------|------|
| 2025-10-17 | 1.0.0 | 初始版本 | AI Assistant |

---

**記住**: 遇到問題時，先查看此指南，如果沒有找到解決方案，請記錄問題並更新此文檔。
