import glob
import os
import sys

batch_dir = 'stage1/output/large_batches'
sql_files = sorted(glob.glob(f'{batch_dir}/batch_*.sql'))

# 如果指定了批次號，只處理該批次
if len(sys.argv) > 1:
    batch_num = int(sys.argv[1])
    sql_file = f'{batch_dir}/batch_{batch_num:04d}.sql'
    
    if not os.path.exists(sql_file):
        print(f'錯誤: 找不到批次文件 {sql_file}')
        sys.exit(1)
    
    print(f'讀取批次 {batch_num}...')
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    file_size = os.path.getsize(sql_file)
    print(f'文件大小: {file_size:,} bytes')
    print(f'SQL 長度: {len(sql_content):,} 字符')
    
    # 輸出到文件供 MCP 使用
    output_file = f'{batch_dir}/current_batch.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f'SQL 已保存到: {output_file}')
    print('請使用 MCP execute_sql 工具執行此文件')
else:
    # 列出所有批次
    print(f'共有 {len(sql_files)} 個批次')
    for i, sql_file in enumerate(sql_files, 1):
        file_size = os.path.getsize(sql_file)
        print(f'{i:2d}. {os.path.basename(sql_file)} ({file_size:,} bytes)')

