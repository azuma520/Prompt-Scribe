# 🚀 Prompt-Scribe 快速開始指南

**5 分鐘內啟動並運行！**

---

## 選項 1: Docker（最簡單）⭐⭐⭐

```bash
# 1. 克隆專案
git clone https://github.com/azuma520/Prompt-Scribe.git
cd Prompt-Scribe

# 2. 配置環境變數（編輯 .env 文件）
# 設置 SUPABASE_URL 和 SUPABASE_ANON_KEY

# 3. 啟動（包含 API + Redis）
docker-compose up -d

# 4. 測試
curl http://localhost:8000/health
# 或訪問: http://localhost:8000/docs
```

✅ **完成！API 已在 http://localhost:8000 運行**

---

## 選項 2: 本地開發

```bash
# 1. 安裝依賴
cd src/api
pip install -r requirements.txt

# 2. 設置環境變數
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_ANON_KEY=your-anon-key

# 3. 啟動
uvicorn main:app --reload

# 4. 測試
curl http://localhost:8000/health
```

✅ **完成！訪問 http://localhost:8000/docs 查看 API**

---

## 選項 3: 一鍵部署到雲端

### Vercel（推薦）

```bash
# 1. 安裝 Vercel CLI
npm i -g vercel

# 2. 部署
vercel --prod

# 3. 設置環境變數
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
```

✅ **完成！API 已部署到全球 CDN**

### Railway

```bash
# 1. 安裝 Railway CLI
npm i -g @railway/cli

# 2. 部署
railway up

# 3. 添加 Redis（可選）
railway add redis
```

✅ **完成！完整功能已部署**

---

## 🧪 快速測試

### 測試 1: 健康檢查

```bash
curl http://localhost:8000/health
```

預期輸出:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": 1697123456
}
```

### 測試 2: 標籤推薦

```bash
curl -X POST http://localhost:8000/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{"description": "cute girl in school uniform"}'
```

預期輸出:
```json
{
  "recommended_tags": [
    {"tag": "1girl", "confidence": 0.95},
    {"tag": "solo", "confidence": 0.90},
    {"tag": "school_uniform", "confidence": 0.88},
    ...
  ]
}
```

### 測試 3: 智能組合（V2.0 新功能）

```bash
curl -X POST http://localhost:8000/api/llm/suggest-combinations \
  -H "Content-Type: application/json" \
  -d '{"tags": ["1girl", "long_hair"]}'
```

✅ **所有測試通過！系統正常運行**

---

## 📚 下一步

### 學習更多

- **完整功能**: 查看 [README.md](README.md)
- **API 文檔**: http://localhost:8000/docs
- **部署指南**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **測試**: [src/api/tests/TESTING_GUIDE.md](src/api/tests/TESTING_GUIDE.md)

### 開始開發

- **API 結構**: 查看 [src/api/README.md](src/api/README.md)
- **專案結構**: 查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **優化計畫**: 查看 [OPTIMIZATION_ROADMAP.md](OPTIMIZATION_ROADMAP.md)

---

**開始使用 Prompt-Scribe！** 🎉

有問題? 查看 [README.md](README.md) 或訪問 [GitHub Issues](https://github.com/your-org/prompt-scribe/issues)

