# 數據遷移最佳實踐與解決方案

## 核心挑戰分析

### 遷移挑戰總結

#### 1. 批次大小限制（Token Limit）
**問題本質**：
- MCP `read_file` 工具限制：**25,000 tokens/次**
- 我們的 mini-batch (500筆)：約 18,000 tokens
- Tiny batch (1,500筆)：約 27,173 tokens（超出限制）

**根本原因**：
- SQL INSERT 語句冗長（每行包含完整列名和值）
- 數據包含大量文字和特殊字元
- Token 計算包括所有 SQL 語法開銷

#### 2. COPY FROM STDIN 不支援
**技術限制**：
```sql
-- PostgreSQL 最高效的批量導入方式
COPY tags FROM STDIN;
-- MCP execute_sql 不支援數據流輸入
```

**影響**：
- 無法使用最高效的批量導入方式
- 必須使用 INSERT 語句，效率降低 50-70%
- 增加網路傳輸開銷

#### 3. 檔案數量爆炸
**問題規模**：
- 總共生成：**4,716 個 SQL 檔案**
- Mini batches: 282 個
- Combined batches: 29 個
- Small batches: 57 個
- Tiny batches: 94 個
- 其他測試檔案: 4,254 個

**管理挑戰**：
- 難以追蹤上傳進度
- 批次執行順序控制
- 錯誤處理和重試機制

---

## 最佳實踐解決方案

### 方案 1: Supabase CLI + PostgreSQL COPY（推薦）⭐⭐⭐

#### 優勢
- ✅ **效率最高**：5-10 分鐘完成全部遷移
- ✅ **原生支援**：PostgreSQL COPY 命令
- ✅ **可靠性高**：專業的遷移工具
- ✅ **簡單易用**：3 條命令完成

#### 實施步驟

**1. 安裝 Supabase CLI**
```bash
# Windows (Scoop)
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# macOS/Linux (Homebrew)
brew install supabase/tap/supabase

# 或使用 npm
npm install -g supabase
```

**2. 登入並連結專案**
```bash
# 登入 Supabase
supabase login

# 連結到你的專案
supabase link --project-ref fumuvmbhmmzkenizksyq
```

**3. 方式 A：使用 PostgreSQL COPY（最快）**
```bash
# 使用環境變數設定連接
export PGHOST="db.fumuvmbhmmzkenizksyq.supabase.co"
export PGPORT="5432"
export PGUSER="postgres"
export PGPASS="your-password"
export PGDATABASE="postgres"

# 使用 psql COPY 命令
psql -c "\COPY tags(id, name, tag_type, category, post_count, created_at) FROM 'stage1/output/tags_data.csv' WITH (FORMAT csv, HEADER true)"
```

**4. 方式 B：使用 Supabase CLI 執行 SQL**
```bash
# 創建完整的 SQL 檔案
cat stage1/output/mini_batches/*.sql > complete_migration.sql

# 執行遷移
supabase db execute -f complete_migration.sql
```

**5. 方式 C：使用 ogr2ogr（針對 GeoJSON/大型數據）**
```bash
# 如果有地理數據或超大型 JSON
PG_USE_COPY=true ogr2ogr -f pgdump output.sql input.json
supabase db execute -f output.sql
```

#### 性能優化技巧

**優化 1：調整 PostgreSQL 參數**
```sql
-- 暫時提高批次大小（針對 FDW）
ALTER SERVER supabase_server OPTIONS (batch_size '10000');

-- 優化寫入性能
SET wal_buffers = '64MB';
SET max_wal_senders = 0;
SET statement_timeout = 0;
SET work_mem = '2GB';
```

**優化 2：暫時禁用觸發器**
```sql
-- 遷移前禁用觸發器
ALTER TABLE tags DISABLE TRIGGER ALL;

-- 執行遷移
\COPY tags FROM 'tags_data.csv' WITH CSV HEADER;

-- 遷移後重新啟用
ALTER TABLE tags ENABLE TRIGGER ALL;
```

**優化 3：使用 UNLOGGED 表（臨時）**
```sql
-- 創建臨時 UNLOGGED 表（更快）
CREATE UNLOGGED TABLE tags_temp (LIKE tags INCLUDING ALL);

-- 導入數據到臨時表
\COPY tags_temp FROM 'tags_data.csv' WITH CSV HEADER;

-- 排序並插入到正式表
INSERT INTO tags SELECT * FROM tags_temp ORDER BY id;

-- 刪除臨時表
DROP TABLE tags_temp;
```

---

### 方案 2: Supabase REST API 批量上傳

#### 優勢
- ✅ **程式化控制**：完整的錯誤處理
- ✅ **整合友好**：Python/JavaScript 原生支援
- ✅ **漸進式遷移**：支援斷點續傳

#### 實施代碼

**Python 實現**
```python
import requests
import pandas as pd
import time
from tqdm import tqdm

# 配置
SUPABASE_URL = "https://fumuvmbhmmzkenizksyq.supabase.co"
SUPABASE_KEY = "your-service-role-key"  # 使用 Service Role Key

# REST API endpoint
url = f"{SUPABASE_URL}/rest/v1/tags"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"  # 減少回傳數據
}

# 讀取數據
df = pd.read_csv('stage1/output/tags_data.csv')
total_rows = len(df)

# 批次上傳設定
BATCH_SIZE = 1000  # 每批 1000 筆
uploaded = 0
failed_batches = []

# 斷點續傳支援
checkpoint_file = 'upload_checkpoint.txt'

# 讀取上次進度
try:
    with open(checkpoint_file, 'r') as f:
        uploaded = int(f.read().strip())
    print(f"從檢查點繼續: {uploaded}/{total_rows}")
except FileNotFoundError:
    uploaded = 0

# 批次上傳
for i in tqdm(range(uploaded, total_rows, BATCH_SIZE)):
    batch = df[i:i+BATCH_SIZE].to_dict('records')
    
    try:
        response = requests.post(url, json=batch, headers=headers, timeout=30)
        
        if response.status_code == 201:
            uploaded = i + len(batch)
            # 更新檢查點
            with open(checkpoint_file, 'w') as f:
                f.write(str(uploaded))
        else:
            print(f"批次 {i//BATCH_SIZE + 1} 失敗: {response.status_code}")
            failed_batches.append(i)
            
    except Exception as e:
        print(f"批次 {i//BATCH_SIZE + 1} 錯誤: {e}")
        failed_batches.append(i)
        time.sleep(5)  # 錯誤後等待

print(f"完成! 上傳: {uploaded}/{total_rows}")
if failed_batches:
    print(f"失敗批次: {failed_batches}")
```

**JavaScript/TypeScript 實現**
```typescript
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import csv from 'csv-parser'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

async function bulkInsert() {
  const BATCH_SIZE = 1000
  let batch: any[] = []
  let totalInserted = 0

  const stream = fs.createReadStream('tags_data.csv')
    .pipe(csv())

  for await (const row of stream) {
    batch.push(row)

    if (batch.length >= BATCH_SIZE) {
      const { error } = await supabase
        .from('tags')
        .insert(batch)
      
      if (error) {
        console.error('Batch insert failed:', error)
      } else {
        totalInserted += batch.length
        console.log(`Inserted: ${totalInserted}`)
      }
      
      batch = []
    }
  }

  // 插入剩餘數據
  if (batch.length > 0) {
    await supabase.from('tags').insert(batch)
    totalInserted += batch.length
  }

  console.log(`Total inserted: ${totalInserted}`)
}

bulkInsert()
```

---

### 方案 3: MCP 自動化微批次（現有工具）

#### 優勢
- ✅ **無需額外安裝**：使用現有 MCP 工具
- ✅ **安全性高**：MCP 提供的抽象層
- ✅ **已驗證**：測試成功上傳 500 筆

#### 改進策略

**策略 1：分塊讀取 SQL 檔案**
```python
import os
from pathlib import Path

def read_sql_in_chunks(file_path, max_tokens=20000):
    """
    將大型 SQL 檔案分塊讀取，確保每塊不超過 token 限制
    """
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 粗略估算 tokens（1 token ≈ 4 字元）
            line_tokens = len(line) // 4
            
            if current_tokens + line_tokens > max_tokens:
                chunks.append(''.join(current_chunk))
                current_chunk = [line]
                current_tokens = line_tokens
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
    
    if current_chunk:
        chunks.append(''.join(current_chunk))
    
    return chunks

# 使用範例
sql_file = "stage1/output/mini_batches/batch_0001.sql"
chunks = read_sql_in_chunks(sql_file, max_tokens=20000)

for i, chunk in enumerate(chunks):
    print(f"執行 chunk {i+1}/{len(chunks)}")
    # 使用 MCP execute_sql 執行
    # execute_sql(chunk)
```

**策略 2：創建進度追蹤系統**
```python
import json
from datetime import datetime

class UploadProgressTracker:
    def __init__(self, checkpoint_file='upload_progress.json'):
        self.checkpoint_file = checkpoint_file
        self.progress = self.load_progress()
    
    def load_progress(self):
        try:
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'total_batches': 282,
                'uploaded_batches': [],
                'failed_batches': [],
                'last_update': None
            }
    
    def save_progress(self):
        self.progress['last_update'] = datetime.now().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def mark_uploaded(self, batch_id):
        if batch_id not in self.progress['uploaded_batches']:
            self.progress['uploaded_batches'].append(batch_id)
            self.save_progress()
    
    def mark_failed(self, batch_id, error):
        self.progress['failed_batches'].append({
            'batch_id': batch_id,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
        self.save_progress()
    
    def get_pending_batches(self):
        all_batches = set(range(1, self.progress['total_batches'] + 1))
        uploaded = set(self.progress['uploaded_batches'])
        return sorted(all_batches - uploaded)

# 使用範例
tracker = UploadProgressTracker()
pending = tracker.get_pending_batches()
print(f"待上傳批次: {len(pending)}")
```

**策略 3：智能重試機制**
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    delay = base_delay * (2 ** attempt)  # 指數退避
                    print(f"重試 {attempt + 1}/{max_retries}，等待 {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=2)
def upload_batch_with_mcp(batch_sql):
    # 使用 MCP execute_sql
    # result = mcp_execute_sql(batch_sql)
    pass
```

---

## 技術限制應對策略

### 限制 1: MCP Token 限制 (25K)

#### 解決方案 A：動態批次大小調整
```python
def calculate_optimal_batch_size(sample_records, target_tokens=20000):
    """
    根據樣本數據動態計算最佳批次大小
    """
    # 取樣本計算平均 token 數
    sample_sql = generate_insert_sql(sample_records[:10])
    avg_tokens_per_record = len(sample_sql) // (4 * 10)  # 粗略估算
    
    # 計算最佳批次大小（留 20% 緩衝）
    optimal_size = int((target_tokens * 0.8) / avg_tokens_per_record)
    
    return max(100, min(optimal_size, 1000))  # 限制在 100-1000 之間
```

#### 解決方案 B：壓縮 SQL 語法
```python
def generate_compact_insert_sql(records, table_name='tags'):
    """
    生成緊湊的 INSERT 語句，減少 token 使用
    """
    if not records:
        return ""
    
    # 只在第一行寫列名
    columns = list(records[0].keys())
    column_str = ','.join(columns)
    
    # 批量值
    values = []
    for record in records:
        value_list = [f"'{v}'" if isinstance(v, str) else str(v) 
                     for v in record.values()]
        values.append(f"({','.join(value_list)})")
    
    # 單一 INSERT 語句（更緊湊）
    sql = f"INSERT INTO {table_name}({column_str}) VALUES\n"
    sql += ",\n".join(values) + ";"
    
    return sql
```

### 限制 2: COPY FROM STDIN 不支援

#### 解決方案：使用 postgres_fdw + COPY
```sql
-- 步驟 1：創建外部表連接
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER remote_server
  FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (
    host 'db.fumuvmbhmmzkenizksyq.supabase.co',
    port '5432',
    dbname 'postgres'
  );

CREATE USER MAPPING FOR current_user
  SERVER remote_server
  OPTIONS (
    user 'postgres',
    password 'your-password'
  );

-- 步驟 2：創建外部表
CREATE FOREIGN TABLE tags_remote (
  id BIGINT,
  name TEXT,
  tag_type TEXT,
  category TEXT,
  post_count INTEGER,
  created_at TIMESTAMP
)
SERVER remote_server
OPTIONS (
  schema_name 'public',
  table_name 'tags'
);

-- 步驟 3：優化批次大小
ALTER SERVER remote_server OPTIONS (batch_size '10000');

-- 步驟 4：批量插入
INSERT INTO tags_remote
SELECT * FROM local_tags;
```

---

## 完整自動化方案

### 端到端自動化腳本

```python
#!/usr/bin/env python3
"""
Supabase 數據遷移自動化工具
支援多種遷移方式和完整的錯誤處理
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import requests
from tqdm import tqdm

class SupabaseMigrator:
    def __init__(self, 
                 supabase_url: str, 
                 supabase_key: str,
                 method: str = 'rest_api'):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.method = method
        self.progress_file = 'migration_progress.json'
    
    def migrate(self, 
                csv_file: str, 
                table_name: str = 'tags',
                batch_size: int = 1000):
        """執行遷移"""
        
        if self.method == 'rest_api':
            return self._migrate_via_rest_api(csv_file, table_name, batch_size)
        elif self.method == 'cli':
            return self._migrate_via_cli(csv_file, table_name)
        elif self.method == 'mcp':
            return self._migrate_via_mcp(csv_file, table_name, batch_size)
        else:
            raise ValueError(f"不支援的方法: {self.method}")
    
    def _migrate_via_rest_api(self, csv_file, table_name, batch_size):
        """REST API 方式遷移"""
        print(f"使用 REST API 遷移數據...")
        
        # 讀取數據
        df = pd.read_csv(csv_file)
        total_rows = len(df)
        
        # REST API endpoint
        url = f"{self.supabase_url}/rest/v1/{table_name}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # 載入進度
        progress = self._load_progress()
        uploaded = progress.get('uploaded_rows', 0)
        
        # 批次上傳
        for i in tqdm(range(uploaded, total_rows, batch_size)):
            batch = df[i:i+batch_size].to_dict('records')
            
            try:
                response = requests.post(
                    url, 
                    json=batch, 
                    headers=headers, 
                    timeout=60
                )
                response.raise_for_status()
                
                uploaded = i + len(batch)
                self._save_progress({'uploaded_rows': uploaded})
                
            except Exception as e:
                print(f"\n錯誤: {e}")
                return False
        
        print(f"\n完成! 總共上傳 {total_rows} 筆數據")
        return True
    
    def _migrate_via_cli(self, csv_file, table_name):
        """CLI 方式遷移（最快）"""
        print(f"使用 Supabase CLI 遷移數據...")
        
        # 生成 COPY 命令
        copy_cmd = f"""
        \\COPY {table_name} FROM '{csv_file}' WITH (
            FORMAT csv,
            HEADER true,
            DELIMITER ',',
            ENCODING 'UTF8'
        );
        """
        
        # 執行命令
        import subprocess
        result = subprocess.run(
            ['supabase', 'db', 'execute', '-c', copy_cmd],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("遷移成功!")
            return True
        else:
            print(f"錯誤: {result.stderr}")
            return False
    
    def _load_progress(self) -> Dict:
        """載入進度"""
        try:
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_progress(self, progress: Dict):
        """保存進度"""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Supabase 數據遷移工具')
    parser.add_argument('--csv', required=True, help='CSV 檔案路徑')
    parser.add_argument('--table', default='tags', help='目標表名')
    parser.add_argument('--method', 
                       choices=['rest_api', 'cli', 'mcp'],
                       default='rest_api',
                       help='遷移方式')
    parser.add_argument('--batch-size', type=int, default=1000, 
                       help='批次大小')
    
    args = parser.parse_args()
    
    # 從環境變數獲取配置
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("錯誤: 請設定 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 環境變數")
        sys.exit(1)
    
    # 執行遷移
    migrator = SupabaseMigrator(supabase_url, supabase_key, args.method)
    success = migrator.migrate(args.csv, args.table, args.batch_size)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

---

## 推薦實施路徑

### 🎯 最佳實踐流程

1. **準備階段**（5 分鐘）
   ```bash
   # 安裝 Supabase CLI
   npm install -g supabase
   
   # 登入並連結專案
   supabase login
   supabase link --project-ref fumuvmbhmmzkenizksyq
   ```

2. **遷移執行**（5-10 分鐘）
   ```bash
   # 方式 1：直接使用 COPY（最快）
   supabase db execute -c "\COPY tags FROM 'stage1/output/tags_data.csv' WITH CSV HEADER"
   
   # 方式 2：使用自動化腳本
   python migrate_to_supabase.py \
     --csv stage1/output/tags_data.csv \
     --method cli
   ```

3. **驗證階段**（2 分鐘）
   ```sql
   -- 檢查記錄數
   SELECT COUNT(*) FROM tags;
   -- 預期: 140,782
   
   -- 檢查數據範圍
   SELECT MIN(id), MAX(id) FROM tags;
   
   -- 抽樣驗證
   SELECT * FROM tags LIMIT 10;
   ```

4. **優化階段**（可選）
   ```sql
   -- 創建索引
   CREATE INDEX idx_tags_name ON tags(name);
   CREATE INDEX idx_tags_category ON tags(category);
   
   -- 分析表統計
   ANALYZE tags;
   ```

---

## 總結

### ✅ 推薦方案排序

1. **Supabase CLI + COPY** - 最快、最可靠
2. **REST API 批量上傳** - 靈活、可控
3. **MCP 微批次** - 無需安裝、安全

### 📊 性能對比

| 方案 | 預估時間 | 可靠性 | 複雜度 | 推薦度 |
|------|---------|--------|--------|--------|
| CLI + COPY | 5-10 分鐘 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| REST API | 30-60 分鐘 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| MCP 微批次 | 1-2 小時 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

### 🚀 立即行動

選擇 **Supabase CLI** 方案，3 條命令完成遷移：
```bash
supabase login
supabase link --project-ref fumuvmbhmmzkenizksyq
supabase db execute -c "\COPY tags FROM 'stage1/output/tags_data.csv' WITH CSV HEADER"
```

---

*最後更新: 2025-01-13*  
*數據規模: 140,782 筆*  
*基於: Supabase 官方文檔和最佳實踐*
