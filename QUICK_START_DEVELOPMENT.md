# 🚀 Prompt-Scribe 開發快速啟動指南

## ⚠️ **重要原則**

### **後端啟動：永遠使用 `run_server.py`**
```bash
# ✅ 正確做法
python run_server.py

# ❌ 錯誤做法 - 會導致模組導入錯誤
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### **前端啟動：在正確目錄中運行**
```bash
# ✅ 正確做法
cd prompt-scribe-web
npm run dev

# ❌ 錯誤做法 - 會找不到 package.json
npm run dev  # 在根目錄運行
```

---

## 🎯 **完整開發流程**

### **1. 啟動後端服務器**
```bash
# 在專案根目錄 D:\Prompt-Scribe\
python run_server.py
```

**驗證後端運行**：
```bash
# 檢查端口
Test-NetConnection -ComputerName localhost -Port 8000

# 或訪問健康檢查
curl http://localhost:8000/health
```

### **2. 啟動前端服務器**
```bash
# 切換到前端目錄
cd prompt-scribe-web

# 啟動開發服務器
npm run dev
```

**驗證前端運行**：
- 訪問：http://localhost:3001/inspire-agent
- 如果 3000 端口被占用，會自動使用 3001

### **3. 測試完整流程**
1. 打開瀏覽器訪問前端頁面
2. 點擊範例按鈕或輸入描述
3. 查看右側面板是否顯示創意方向
4. 選擇方向並查看最終結果

---

## 🔧 **常見問題解決**

### **問題 1：後端無法啟動**
```
ERROR: Error loading ASGI app. Could not import module "api.main".
```

**解決方案**：
- 確保使用 `python run_server.py`
- 不要直接運行 `uvicorn`

### **問題 2：前端 API 調用失敗**
```
Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

**解決方案**：
- 檢查後端是否運行在 8000 端口
- 確認 `NEXT_PUBLIC_API_URL` 環境變數

### **問題 3：模組導入錯誤**
```
ModuleNotFoundError: No module named 'config'
```

**解決方案**：
- 使用 `run_server.py` 啟動
- 不要修改相對導入路徑

---

## 📁 **目錄結構**

```
D:\Prompt-Scribe\                    # 專案根目錄
├── run_server.py                   # 後端啟動腳本 ⭐
├── src\
│   └── api\                        # 後端代碼目錄
│       ├── main.py                 # 主應用
│       ├── config.py               # 配置
│       └── routers\                # 路由
├── prompt-scribe-web\              # 前端代碼目錄 ⭐
│   ├── package.json                # 前端配置
│   └── app\
│       └── inspire-agent\          # Inspire Agent 頁面
└── DEVELOPMENT_PRINCIPLES.md       # 詳細開發原則
```

---

## 🎯 **開發檢查清單**

### **啟動前檢查**
- [ ] 在正確的目錄中（根目錄 vs prompt-scribe-web）
- [ ] 使用正確的啟動命令
- [ ] 檢查端口是否被占用

### **運行中檢查**
- [ ] 後端健康檢查：http://localhost:8000/health
- [ ] 前端頁面：http://localhost:3001/inspire-agent
- [ ] 控制台無錯誤信息

### **功能測試**
- [ ] 範例按鈕點擊有響應
- [ ] 右側面板顯示創意方向
- [ ] 選擇方向後能生成最終結果

---

## 📚 **相關文件**

- `DEVELOPMENT_PRINCIPLES.md` - 詳細開發原則
- `prompt-scribe-web/INSPIRE_AGENT_FRONTEND_SETUP.md` - 前端設置指南
- `run_server.py` - 後端啟動腳本
- `README.md` - 專案總覽

---

**記住**：正確的啟動方式是一切正常運行的基礎！ 🎯
