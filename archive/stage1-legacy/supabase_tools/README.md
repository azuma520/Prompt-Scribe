# 🚀 Supabase 部署工具

## 📋 快速開始

### 1. 環境設置

創建 `.env` 文件（在專案根目錄）：
```env
# Supabase 配置
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# OpenAI 配置 (用於嵌入向量生成)
OPENAI_API_KEY=sk-proj-your-openai-key-here

# 專案配置
PROJECT_NAME=prompt-scribe-tags
DATABASE_REGION=us-east-1
```

### 2. 安裝依賴
```bash
pip install -r stage1/supabase_tools/requirements.txt
```

### 3. 一鍵部署
```bash
python stage1/supabase_tools/deploy_to_supabase.py
```

### 4. 測試部署
```bash
python stage1/supabase_tools/test_deployment.py
```

## 📁 工具說明

| 工具 | 說明 |
|------|------|
| `check_env.py` | 檢查 Supabase 環境配置 |
| `migrate_to_supabase.py` | 遷移 SQLite 數據到 PostgreSQL |
| `setup_vector_db.py` | 設置 pgvector 向量資料庫 |
| `generate_embeddings.py` | 生成 OpenAI 嵌入向量 |
| `create_api_endpoints.py` | 創建 API 端點和文檔 |
| `deploy_to_supabase.py` | 一鍵部署主腳本 |
| `test_deployment.py` | 部署測試工具 |

## 📚 詳細文檔

- [部署指南](SUPABASE_DEPLOYMENT_GUIDE.md)
- [API 文檔](output/API_DOCUMENTATION.md) (部署後生成)

## 🎯 部署後功能

✅ **數據遷移**: SQLite → PostgreSQL  
✅ **向量搜索**: 語義相似度搜索  
✅ **REST API**: 自動生成的 API 端點  
✅ **分類統計**: 實時統計和分析  
✅ **文本搜索**: 模糊匹配搜索  
✅ **安全策略**: RLS 行級安全  

## 🔧 故障排除

### 常見問題

1. **連接失敗**: 檢查 `.env` 文件中的 URL 和密鑰
2. **權限錯誤**: 確保使用 `SERVICE_ROLE_KEY` 進行管理操作
3. **依賴缺失**: 運行 `pip install -r requirements.txt`

### 獲取幫助

查看詳細的 [部署指南](SUPABASE_DEPLOYMENT_GUIDE.md) 或運行測試工具診斷問題。
