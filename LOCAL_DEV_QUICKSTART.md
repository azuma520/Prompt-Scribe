# 🚀 本地開發快速開始指南

> **Prompt-Scribe API 本地開發環境快速設置**

---

## ⚡ 快速啟動 (30 秒)

### 1. 激活虛擬環境
```bash
venv\Scripts\activate
```

### 2. 啟動本地伺服器
```bash
python local_test.py
```

### 3. 訪問 API
- **根端點**: http://localhost:8000/
- **健康檢查**: http://localhost:8000/health
- **API 文檔**: http://localhost:8000/docs

---

## 🔧 環境信息

### 系統要求
- **Python**: 3.13+
- **作業系統**: Windows 10/11
- **記憶體**: 最少 4GB
- **硬碟空間**: 最少 1GB

### 已安裝依賴
```
fastapi==0.119.0
uvicorn[standard]==0.37.0
pydantic==2.12.2
supabase==2.22.0
httpx==0.28.1
pydantic-settings==2.11.0
python-dotenv==1.1.1
```

---

## 📊 可用端點

| 端點 | 方法 | URL | 描述 |
|------|------|-----|------|
| **根端點** | GET | `/` | 歡迎訊息 |
| **健康檢查** | GET | `/health` | 服務狀態 |
| **測試端點** | GET | `/api/v1/test` | 功能測試 |

---

## 🛠️ 開發命令

### 基本命令
```bash
# 啟動伺服器
python local_test.py

# 使用 uvicorn (替代方案)
uvicorn local_test:app --host 0.0.0.0 --port 8000 --reload

# 檢查虛擬環境
python --version
pip list
```

### 開發工具
```bash
# 安裝開發依賴 (可選)
pip install black isort flake8 pytest

# 格式化代碼 (可選)
black local_test.py
isort local_test.py

# 檢查代碼品質 (可選)
flake8 local_test.py
```

---

## 🔍 故障排除

### 常見問題

#### 1. `uvicorn` 命令未找到
```bash
# 解決方案
venv\Scripts\activate
pip install uvicorn[standard]
```

#### 2. 模組導入錯誤
```bash
# 確保在正確目錄
cd D:\Prompt-Scribe

# 確保虛擬環境已激活
venv\Scripts\activate
```

#### 3. 端口被占用
```bash
# 檢查端口使用情況
netstat -ano | findstr 8000

# 使用不同端口
uvicorn local_test:app --port 8001
```

#### 4. 環境變數問題
```bash
# 檢查 .env 文件是否存在
dir .env

# 重新創建 .env 文件
copy env.example .env
```

---

## 📈 性能指標

### 基準測試
- **啟動時間**: < 3 秒
- **響應時間**: < 100ms
- **記憶體使用**: ~50MB
- **CPU 使用**: < 5%

### 監控命令
```bash
# 查看進程
tasklist | findstr python

# 查看網路連接
netstat -ano | findstr 8000

# 查看日誌輸出
# (在運行伺服器的終端中查看)
```

---

## 🎯 下一步

### 開發建議
1. **添加新端點**: 在 `local_test.py` 中添加新的路由
2. **測試功能**: 使用瀏覽器或 Postman 測試 API
3. **調試問題**: 查看終端機日誌輸出
4. **部署準備**: 準備好後部署到生產環境

### 相關文檔
- [完整設置指南](.speckit/LOCAL_DEVELOPMENT_SETUP.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [專案結構](PROJECT_STRUCTURE.md)

---

## 🎊 狀態檢查

### ✅ 環境就緒檢查
- [ ] Python 3.13+ 已安裝
- [ ] 虛擬環境已創建並激活
- [ ] 依賴包已安裝
- [ ] `.env` 文件已配置
- [ ] 本地伺服器可啟動
- [ ] 基本端點可訪問

### 🚀 準備開發
當所有項目都勾選後，您就可以開始本地開發了！

---

**快速開始完成！開始您的 API 開發之旅！** 🚀
