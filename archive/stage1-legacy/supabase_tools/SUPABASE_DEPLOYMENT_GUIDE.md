# 🚀 Supabase 部署指南

## 📋 概述

本指南將幫助您將 `tags.db` 數據庫部署到 Supabase，包括：
- 數據遷移 (SQLite → PostgreSQL)
- 向量資料庫設置 (pgvector)
- API 端點創建
- 嵌入向量生成

## 🎯 部署目標

- **主分類**: 96.56% 覆蓋率
- **總標籤數**: 約 100 萬個標籤
- **向量搜索**: 語義相似度搜索
- **REST API**: 自動生成的 API 端點

## 📦 前置條件

### 1. Supabase 專案
- ✅ 已創建 Supabase 專案
- ✅ 獲取專案 URL 和 API Keys
- ✅ 選擇資料庫區域 (推薦: `us-east-1`)

### 2. 環境配置
創建 `.env` 文件：
```env
# Supabase 配置
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# OpenAI 配置 (用於嵌入向量生成)
OPENAI_API_KEY=sk-proj-your-openai-key

# 專案配置
PROJECT_NAME=prompt-scribe-tags
DATABASE_REGION=us-east-1
```

### 3. Python 依賴
```bash
pip install -r stage1/supabase_tools/requirements.txt
```

## 🚀 快速部署

### 方法一：一鍵部署
```bash
python stage1/supabase_tools/deploy_to_supabase.py
```

### 方法二：分步部署
```bash
# 1. 檢查環境
python stage1/supabase_tools/check_env.py

# 2. 遷移數據
python stage1/supabase_tools/migrate_to_supabase.py

# 3. 設置向量資料庫
python stage1/supabase_tools/setup_vector_db.py

# 4. 創建 API 端點
python stage1/supabase_tools/create_api_endpoints.py

# 5. 生成嵌入向量 (可選)
python stage1/supabase_tools/generate_embeddings.py
```

## 📊 部署後驗證

### 1. 檢查數據遷移
```sql
-- 在 Supabase SQL Editor 中執行
SELECT COUNT(*) FROM tags_final;
SELECT main_category, COUNT(*) FROM tags_final GROUP BY main_category;
```

### 2. 測試 API 端點
```bash
# 測試基本查詢
curl -H "apikey: YOUR_ANON_KEY" \
     -H "Authorization: Bearer YOUR_ANON_KEY" \
     "https://your-project.supabase.co/rest/v1/tag_summary?select=*&limit=5"
```

### 3. 檢查向量功能
```sql
-- 檢查嵌入向量
SELECT COUNT(*) FROM tag_embeddings;
SELECT * FROM tag_embeddings LIMIT 5;
```

## 🔧 API 使用示例

### 文本搜索
```javascript
const { data } = await supabase.rpc('search_tags_by_text', {
  search_query: 'anime',
  category_filter: 'CHARACTER_RELATED',
  min_confidence: 0.8,
  limit_count: 20
});
```

### 向量搜索
```javascript
const { data } = await supabase.rpc('search_similar_tags', {
  query_embedding: [0.1, 0.2, ...], // 1536 維向量
  match_threshold: 0.7,
  match_count: 10
});
```

### 分類統計
```javascript
const { data } = await supabase.rpc('get_category_statistics');
```

## 📈 性能優化

### 1. 索引優化
- 主分類索引
- 子分類索引
- 信心度索引
- 使用次數索引
- 向量相似度索引

### 2. 查詢優化
- 使用適當的 LIMIT
- 添加信心度過濾
- 利用分類過濾

### 3. 緩存策略
- Supabase 自動緩存
- 客戶端緩存
- CDN 緩存

## 🔐 安全配置

### 1. RLS 策略
- 匿名用戶可讀取所有標籤
- 服務角色有完整權限
- 嵌入向量表保護

### 2. API 限制
- 速率限制
- 請求大小限制
- CORS 配置

## 🐛 故障排除

### 常見問題

#### 1. 連接失敗
```
❌ 無法連接到 Supabase
```
**解決方案**: 檢查 `.env` 文件中的 URL 和密鑰

#### 2. 權限錯誤
```
❌ 權限不足
```
**解決方案**: 確保使用 `SERVICE_ROLE_KEY` 進行管理操作

#### 3. 嵌入生成失敗
```
❌ OpenAI API 錯誤
```
**解決方案**: 檢查 API Key 和配額限制

#### 4. 數據遷移失敗
```
❌ 數據類型不匹配
```
**解決方案**: 檢查 SQLite 數據格式，可能需要數據清理

### 日誌查看
```bash
# 查看 Supabase 日誌
# 在 Supabase Dashboard → Logs 中查看
```

## 📚 相關文檔

- [Supabase 官方文檔](https://supabase.com/docs)
- [pgvector 文檔](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)

## 🎉 部署完成後

1. **查看 Dashboard**: 在 Supabase 專案中查看數據
2. **測試 API**: 使用 API 文檔測試端點
3. **監控使用**: 查看 API 使用量和性能
4. **擴展功能**: 根據需要添加新功能

## 💡 下一步建議

1. **前端整合**: 創建 Web 界面
2. **自動化**: 設置 CI/CD 流程
3. **監控**: 設置錯誤追蹤和性能監控
4. **備份**: 設置定期備份策略

---

**🎯 部署成功後，您將擁有一個功能完整的 AI 標籤管理系統！**
