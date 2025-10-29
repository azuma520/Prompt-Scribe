# 🚀 Prompt-Scribe 向量資料庫嵌入生成實施計畫

**專案**: Prompt-Scribe  
**模組**: 標籤向量化系統  
**版本**: 1.0.0  
**日期**: 2025-01-27  
**狀態**: 規劃階段

---

## 📊 **資料庫分析結果**

### **當前狀態**
- **總標籤數**: 1,000 個
- **資料庫結構**: ✅ 完整（包含所有必要欄位）
- **Embedding 狀態**: 全部為空，準備生成
- **使用次數分佈**: 均為 400 次（測試資料）

### **關鍵發現**
1. **小規模資料集** - 適合快速實施和測試
2. **完整元數據** - 包含分類、信心度等豐富資訊
3. **零成本預估** - 測試階段成本極低
4. **單一批次策略** - 建議批次大小 50

---

## 🎯 **實施策略**

### **階段 1: 基礎設施準備 (Day 1)**

#### **1.1 環境優化**
```python
# 優化嵌入生成配置
EMBEDDING_CONFIG = {
    "model": "text-embedding-3-small",  # 成本效益最佳
    "batch_size": 50,                    # 適合小資料集
    "max_retries": 3,                    # 錯誤重試
    "timeout": 30,                       # 請求超時
    "rate_limit": 100                    # 每分鐘請求限制
}
```

#### **1.2 資料預處理**
```python
# 標籤清理和標準化
def preprocess_tag(tag_name: str) -> str:
    """清理和標準化標籤名稱"""
    # 移除特殊字符
    # 統一大小寫
    # 處理多語言標籤
    return cleaned_tag
```

#### **1.3 錯誤處理機制**
```python
# 完整的錯誤處理和重試機制
class EmbeddingGenerator:
    def __init__(self):
        self.retry_count = 0
        self.failed_tags = []
        self.success_count = 0
```

### **階段 2: 核心嵌入生成 (Day 2)**

#### **2.1 批次處理實現**
```python
# 智能批次處理
def generate_embeddings_batch(tags: List[str], batch_size: int = 50):
    """批次生成嵌入向量"""
    batches = [tags[i:i+batch_size] for i in range(0, len(tags), batch_size)]
    
    for batch_idx, batch in enumerate(batches):
        try:
            # 生成嵌入
            embeddings = await generate_batch_embeddings(batch)
            
            # 更新資料庫
            await update_database_embeddings(batch, embeddings)
            
            # 記錄進度
            log_progress(batch_idx + 1, len(batches))
            
        except Exception as e:
            handle_batch_error(batch, e)
```

#### **2.2 進度追蹤**
```python
# 實時進度監控
class ProgressTracker:
    def __init__(self, total_tags: int):
        self.total = total_tags
        self.processed = 0
        self.failed = 0
        self.start_time = time.time()
    
    def update(self, success: bool):
        self.processed += 1
        if not success:
            self.failed += 1
        
        # 計算進度和預估時間
        progress = (self.processed / self.total) * 100
        eta = self.calculate_eta()
        
        print(f"Progress: {progress:.1f}% ({self.processed}/{self.total})")
        print(f"ETA: {eta}")
```

### **階段 3: 品質驗證 (Day 3)**

#### **3.1 嵌入品質檢查**
```python
# 嵌入向量驗證
def validate_embeddings(embeddings: List[List[float]]) -> Dict:
    """驗證嵌入向量品質"""
    validation_results = {
        "dimension_check": check_dimensions(embeddings),
        "similarity_check": check_similarity_distribution(embeddings),
        "outlier_detection": detect_outliers(embeddings),
        "quality_score": calculate_quality_score(embeddings)
    }
    return validation_results
```

#### **3.2 語義搜尋測試**
```python
# 測試語義搜尋功能
def test_semantic_search():
    """測試語義搜尋準確性"""
    test_queries = [
        "beautiful girl",
        "anime character", 
        "fantasy art",
        "nature landscape"
    ]
    
    for query in test_queries:
        results = semantic_search(query, top_k=5)
        print(f"Query: {query}")
        print(f"Results: {[r['name'] for r in results]}")
```

---

## 🛠️ **技術實現細節**

### **1. 嵌入生成腳本**

```python
#!/usr/bin/env python3
"""
Prompt-Scribe 標籤嵌入生成器
基於 OpenAI text-embedding-3-small 模型
"""

import asyncio
import time
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from supabase import create_client, Client
import os
from dotenv import load_dotenv

class TagEmbeddingGenerator:
    """標籤嵌入生成器"""
    
    def __init__(self):
        load_dotenv()
        
        # 初始化客戶端
        self.openai_client = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.supabase: Client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_SERVICE_KEY']
        )
        
        # 配置
        self.model = "text-embedding-3-small"
        self.batch_size = 50
        self.max_retries = 3
        self.timeout = 30
        
        # 統計
        self.stats = {
            "total_tags": 0,
            "processed": 0,
            "failed": 0,
            "start_time": None
        }
    
    async def generate_all_embeddings(self):
        """生成所有標籤的嵌入向量"""
        print("Starting embedding generation...")
        
        # 獲取所有標籤
        tags_response = self.supabase.table('tags_final').select('id, name').execute()
        tags = tags_response.data
        
        self.stats["total_tags"] = len(tags)
        self.stats["start_time"] = time.time()
        
        print(f"Found {len(tags)} tags to process")
        
        # 分批處理
        batches = [tags[i:i+self.batch_size] for i in range(0, len(tags), self.batch_size)]
        
        for batch_idx, batch in enumerate(batches):
            print(f"\nProcessing batch {batch_idx + 1}/{len(batches)}")
            
            try:
                await self.process_batch(batch)
                self.print_progress()
                
            except Exception as e:
                print(f"Batch {batch_idx + 1} failed: {e}")
                self.stats["failed"] += len(batch)
        
        self.print_final_stats()
    
    async def process_batch(self, batch: List[Dict]):
        """處理單一批次"""
        tag_names = [tag['name'] for tag in batch]
        
        # 生成嵌入向量
        embeddings = await self.generate_embeddings(tag_names)
        
        # 更新資料庫
        await self.update_database(batch, embeddings)
        
        self.stats["processed"] += len(batch)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """生成嵌入向量"""
        for attempt in range(self.max_retries):
            try:
                response = await self.openai_client.embeddings.create(
                    model=self.model,
                    input=texts,
                    timeout=self.timeout
                )
                
                return [data.embedding for data in response.data]
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指數退避
    
    async def update_database(self, tags: List[Dict], embeddings: List[List[float]]):
        """更新資料庫"""
        updates = []
        for tag, embedding in zip(tags, embeddings):
            updates.append({
                "id": tag['id'],
                "embedding": embedding
            })
        
        # 批量更新
        for update in updates:
            self.supabase.table('tags_final').update({
                "embedding": update['embedding']
            }).eq('id', update['id']).execute()
    
    def print_progress(self):
        """打印進度"""
        progress = (self.stats["processed"] / self.stats["total_tags"]) * 100
        elapsed = time.time() - self.stats["start_time"]
        eta = (elapsed / self.stats["processed"]) * (self.stats["total_tags"] - self.stats["processed"])
        
        print(f"Progress: {progress:.1f}% ({self.stats['processed']}/{self.stats['total_tags']})")
        print(f"ETA: {eta:.0f}s")
    
    def print_final_stats(self):
        """打印最終統計"""
        total_time = time.time() - self.stats["start_time"]
        success_rate = (self.stats["processed"] / self.stats["total_tags"]) * 100
        
        print("\n" + "="*50)
        print("EMBEDDING GENERATION COMPLETED")
        print("="*50)
        print(f"Total tags: {self.stats['total_tags']}")
        print(f"Processed: {self.stats['processed']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Total time: {total_time:.0f}s")
        print(f"Average time per tag: {total_time/self.stats['total_tags']:.2f}s")

# 主執行函數
async def main():
    generator = TagEmbeddingGenerator()
    await generator.generate_all_embeddings()

if __name__ == "__main__":
    asyncio.run(main())
```

### **2. 語義搜尋測試腳本**

```python
#!/usr/bin/env python3
"""
語義搜尋測試腳本
驗證嵌入向量品質和搜尋準確性
"""

import os
import numpy as np
from typing import List, Dict
from supabase import create_client, Client
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio

class SemanticSearchTester:
    """語義搜尋測試器"""
    
    def __init__(self):
        load_dotenv()
        
        self.supabase: Client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_SERVICE_KEY']
        )
        
        self.openai_client = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    async def test_search_queries(self):
        """測試搜尋查詢"""
        test_queries = [
            "beautiful anime girl",
            "fantasy landscape",
            "cute character",
            "dark atmosphere",
            "nature scene"
        ]
        
        print("Testing semantic search...")
        print("="*50)
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = await self.semantic_search(query, top_k=5)
            
            print("Top results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['name']} (similarity: {result['similarity']:.3f})")
    
    async def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """語義搜尋"""
        # 生成查詢嵌入
        query_embedding = await self.generate_query_embedding(query)
        
        # 搜尋相似標籤
        results = self.supabase.rpc('search_similar_tags', {
            'query_embedding': query_embedding,
            'match_threshold': 0.7,
            'match_count': top_k
        }).execute()
        
        return results.data
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """生成查詢嵌入向量"""
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        return response.data[0].embedding

# 主執行函數
async def main():
    tester = SemanticSearchTester()
    await tester.test_search_queries()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📅 **實施時程**

### **Week 1: 核心功能開發**

| 日期 | 任務 | 預估時間 | 負責人 |
|------|------|----------|--------|
| Day 1 | 環境準備和資料預處理 | 4h | AI Assistant |
| Day 2 | 嵌入生成核心功能 | 6h | AI Assistant |
| Day 3 | 批次處理和錯誤處理 | 4h | AI Assistant |
| Day 4 | 品質驗證和測試 | 4h | AI Assistant |
| Day 5 | 整合測試和優化 | 2h | AI Assistant |

### **Week 2: 整合和優化**

| 日期 | 任務 | 預估時間 | 負責人 |
|------|------|----------|--------|
| Day 6 | Inspire Agent 整合 | 4h | AI Assistant |
| Day 7 | 性能優化和監控 | 3h | AI Assistant |
| Day 8 | 文檔和部署 | 3h | AI Assistant |

---

## 💰 **成本估算**

### **開發階段**
- **API 調用**: ~1,000 次嵌入生成 = $0.10
- **測試調用**: ~500 次搜尋測試 = $0.05
- **總開發成本**: ~$0.15

### **生產階段**
- **月使用量**: 10,000 次搜尋 = $1.00
- **年使用量**: 120,000 次搜尋 = $12.00

---

## 🎯 **成功指標**

### **技術指標**
- ✅ 嵌入生成成功率 > 95%
- ✅ 平均搜尋延遲 < 200ms
- ✅ 搜尋準確率 > 80%
- ✅ 系統可用性 > 99%

### **業務指標**
- ✅ Inspire Agent 搜尋功能正常
- ✅ 用戶體驗提升
- ✅ 成本控制在預算內

---

## 🚨 **風險評估**

### **技術風險**
1. **API 限制** - OpenAI 速率限制
   - **緩解**: 實施重試機制和速率控制
2. **嵌入品質** - 向量品質不穩定
   - **緩解**: 品質驗證和測試

### **業務風險**
1. **成本超標** - 使用量超出預期
   - **緩解**: 成本監控和限制
2. **性能問題** - 搜尋速度慢
   - **緩解**: 索引優化和快取

---

## 📋 **檢查清單**

### **開發前**
- [ ] 環境變數設定完成
- [ ] 資料庫連線驗證
- [ ] API 金鑰測試
- [ ] 開發環境準備

### **開發中**
- [ ] 嵌入生成功能實現
- [ ] 批次處理機制
- [ ] 錯誤處理和重試
- [ ] 進度追蹤和日誌

### **測試階段**
- [ ] 單元測試通過
- [ ] 整合測試通過
- [ ] 性能測試達標
- [ ] 品質驗證通過

### **部署前**
- [ ] 生產環境配置
- [ ] 監控系統就緒
- [ ] 文檔完整
- [ ] 回滾計劃準備

---

## 🚀 **立即行動**

### **今天可以開始**
1. **創建嵌入生成腳本** - 基於上述模板
2. **測試小批量生成** - 10 個標籤測試
3. **驗證資料庫更新** - 確認嵌入向量正確儲存

### **明天目標**
1. **完整批次處理** - 處理所有 1,000 個標籤
2. **品質驗證** - 測試語義搜尋功能
3. **性能優化** - 調整批次大小和重試機制

---

**準備開始實施！** 🎯✨
