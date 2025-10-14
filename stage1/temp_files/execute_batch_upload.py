import glob
import os

# 這個腳本會列出所有需要執行的 SQL 文件
# 實際執行需要配合 MCP execute_sql 工具

batch_dir = 'stage1/output/large_batches'
sql_files = sorted(glob.glob(f'{batch_dir}/batch_*.sql'))

print(f'共有 {len(sql_files)} 個批次需要上傳')
print()

for i, sql_file in enumerate(sql_files, 1):
    file_size = os.path.getsize(sql_file)
    print(f'批次 {i:2d}/{len(sql_files)}: {os.path.basename(sql_file)} ({file_size:,} bytes)')
    
    # 讀取 SQL 內容
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 這裡需要使用 MCP execute_sql 工具執行
    # 由於這是 Python 腳本，無法直接調用 MCP 工具
    # 需要在主程序中逐批調用
    
    print(f'  SQL 長度: {len(sql_content):,} 字符')
    print(f'  預計記錄數: ~{sql_content.count("VALUES") + sql_content.count(",\\n(")}')
    print()

print('請使用 MCP execute_sql 工具逐批執行這些 SQL 文件')
print('或者使用自動化腳本配合 MCP 工具')

