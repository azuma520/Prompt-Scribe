import sys
import os

if len(sys.argv) < 2:
    print('使用方法: python read_batch_sql.py <batch_number>')
    print('例如: python read_batch_sql.py 1')
    sys.exit(1)

batch_num = int(sys.argv[1])
batch_file = f'stage1/output/large_batches/batch_{batch_num:04d}.sql'

if not os.path.exists(batch_file):
    print(f'錯誤: 找不到批次文件 {batch_file}')
    sys.exit(1)

with open(batch_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 輸出 SQL 內容（供 MCP 工具使用）
print(sql_content)

