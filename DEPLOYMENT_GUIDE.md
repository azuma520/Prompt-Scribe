# 🚀 部署指南

**版本**: v2.0 - P2 優化版  
**更新日期**: 2025-10-15

---

## 📋 支援的部署平台

### 1. Vercel（推薦用於小型到中型流量）⭐⭐⭐

**優勢**:
- ✅ 全球邊緣部署（180+ 位置）
- ✅ 零配置 HTTPS
- ✅ 自動擴展
- ✅ GitHub 集成
- ✅ 免費額度（100GB 流量/月）

**限制**:
- ⚠️ 無狀態（只能使用記憶體快取）
- ⚠️ 函數執行時間限制（30秒）
- ⚠️ 記憶體限制（512MB）

**部署步驟**:
```bash
# 1. 安裝 Vercel CLI
npm i -g vercel

# 2. 登入
vercel login

# 3. 部署
vercel --prod

# 4. 設置環境變數
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
```

**環境變數**:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
CACHE_STRATEGY=memory
REDIS_ENABLED=false
```

---

### 2. Railway（推薦用於中型到大型流量）⭐⭐⭐

**優勢**:
- ✅ 支援 Redis（持久化快取）
- ✅ 無伺服器限制
- ✅ 簡單配置
- ✅ 自動部署
- ✅ 多區域部署

**成本**: $5-20/月

**部署步驟**:
```bash
# 1. 安裝 Railway CLI
npm i -g @railway/cli

# 2. 登入
railway login

# 3. 部署
railway up

# 4. 添加 Redis
railway add redis
```

**配置**: 已包含在 `railway.toml`

---

### 3. Docker + 自主機（完全控制）⭐⭐

**優勢**:
- ✅ 完全控制
- ✅ 成本可控
- ✅ 支援所有功能
- ✅ 可自定義優化

**部署步驟**:
```bash
# 1. 克隆專案
git clone https://github.com/azuma520/Prompt-Scribe.git
cd Prompt-Scribe

# 2. 設置環境變數
cp .env.example .env
# 編輯 .env 文件

# 3. 啟動服務
docker-compose up -d

# 4. 檢查狀態
curl http://localhost:8000/health
```

---

### 4. Cloudflare Workers（實驗性）⭐

**優勢**:
- ✅ 極快速度（全球邊緣）
- ✅ 超低延遲
- ✅ 高可用性

**限制**:
- ⚠️ 需要大量改造
- ⚠️ 不支援標準 Python
- ⚠️ 複雜配置

**狀態**: 未實作（需要重寫為 JavaScript/WebAssembly）

---

## 🌍 多區域部署建議

### 全球用戶（推薦）⭐⭐⭐

**架構**: Vercel 邊緣 + Supabase 多區域

```
用戶請求 → Vercel 邊緣函數（最近的節點）
           ↓
           Supabase（自動路由到最近的區域）
```

**優勢**:
- 全球延遲 < 100ms
- 自動負載平衡
- 高可用性

**成本**: $0-10/月

### 亞洲用戶為主

**架構**: Railway 亞洲 + Redis

```
用戶請求 → Railway（新加坡/東京）
           ↓
           Redis（本地快取）
           ↓
           Supabase（亞洲區域）
```

**優勢**:
- 亞洲優化
- 持久化快取
- 完整功能

**成本**: $10-25/月

### 企業部署

**架構**: 自主機 + 多區域

```
Load Balancer → API 實例（多個區域）
                ↓
                Redis Cluster（分散式快取）
                ↓
                Supabase（企業版）
```

**投入**: 高  
**控制**: 完全  
**成本**: $50+/月

---

## 📊 效能基準測試

### Vercel 效能
```
全球平均延遲: 120ms
P95 延遲: 350ms
吞吐量: 1000+ req/s
可用性: 99.9%
```

### Railway 效能
```
區域延遲: 50-200ms
P95 延遲: 400ms
吞吐量: 500+ req/s
可用性: 99.5%
```

### 自主機效能
```
延遲: 依地理位置
P95 延遲: 自定義
吞吐量: 依硬件
可用性: 依管理
```

---

## 🔧 部署配置詳解

### 環境變數

**必需**:
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your-key
```

**快取配置**:
```bash
# 記憶體快取（Vercel）
CACHE_STRATEGY=memory
REDIS_ENABLED=false

# Redis 快取（Railway/Docker）
CACHE_STRATEGY=redis
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0

# 混合快取（Docker）
CACHE_STRATEGY=hybrid
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0
HYBRID_L1_TTL=300
HYBRID_L2_TTL=3600
```

**進階配置**:
```bash
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=30
DB_CONNECTION_POOL_SIZE=10
```

### 健康檢查端點

**基本檢查**:
```
GET /health
```

**詳細檢查**:
```
GET /cache/health
GET /cache/stats
```

**預期回應**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "cache_status": "healthy",
  "timestamp": 1697123456
}
```

---

## 🚨 故障排除

### 常見問題

**1. 502 Bad Gateway**
- 檢查環境變數
- 確認 Supabase 連接
- 查看部署日誌

**2. 快取錯誤**
- Redis 連接失敗 → 自動降級到記憶體
- 記憶體不足 → 增加實例記憶體

**3. 效能問題**
- 檢查 `/cache/stats`
- 調整快取 TTL
- 考慮升級實例

### 監控建議

**基本監控**:
- 健康檢查（每分鐘）
- 響應時間（P95 < 500ms）
- 錯誤率（< 1%）

**進階監控**:
- 快取命中率（> 80%）
- 記憶體使用率（< 80%）
- 資料庫連接數

---

## 🎯 推薦部署方案

### 個人專案/Demo
**方案**: Vercel 免費版  
**成本**: $0  
**流量**: < 100GB/月  
**延遲**: 100-300ms  

### 小型應用
**方案**: Vercel Pro  
**成本**: $20/月  
**流量**: 1TB/月  
**延遲**: 50-200ms  

### 中型應用
**方案**: Railway + Redis  
**成本**: $15-25/月  
**功能**: 完整（持久化快取）  
**延遲**: 100-400ms  

### 大型應用
**方案**: 自主機 + 負載平衡  
**成本**: $50+/月  
**功能**: 完全客製化  
**延遲**: 自定義  

---

## ✅ 部署檢查清單

### 部署前
- [ ] 環境變數設置完成
- [ ] Supabase 連接測試通過
- [ ] 本地測試通過
- [ ] CI/CD 管道通過

### 部署後
- [ ] 健康檢查通過（`/health`）
- [ ] API 端點測試通過
- [ ] 快取系統正常（`/cache/health`）
- [ ] 效能測試達標（< 500ms P95）
- [ ] 監控系統配置完成

### 上線準備
- [ ] 文檔更新
- [ ] 團隊培訓完成
- [ ] 回滾計畫準備
- [ ] 監控告警設置

---

## 📞 支援和維護

### 日常維護
- 每週檢查健康狀態
- 每月查看效能報告
- 每季檢查依賴更新

### 緊急回應
1. 檢查 `/health` 端點
2. 查看部署平台日誌
3. 檢查 Supabase 狀態
4. 必要時回滾到上一版本

---

**部署文檔已準備就緒！** 🎉

選擇適合的部署方案並開始部署。建議先用 Vercel 快速驗證，再根據需求升級到 Railway 或自主機。
