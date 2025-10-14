"""
批次執行器 - 用於自動上傳數據到 Supabase
這個腳本會輸出每個批次的 SQL 內容，供外部 MCP 工具執行
"""
import glob
import os
import sys

batch_dir = 'stage1/output/mini_batches'
sql_files = sorted(glob.glob(f'{batch_dir}/batch_*.sql'))

if len(sys.argv) > 1:
    # 執行指定批次
    start_batch = int(sys.argv[1])
    end_batch = int(sys.argv[2]) if len(sys.argv) > 2 else start_batch
    
    print(f'執行批次 {start_batch} 到 {end_batch}')
    
    for batch_num in range(start_batch, end_batch + 1):
        sql_file = f'{batch_dir}/batch_{batch_num:04d}.sql'
        
        if not os.path.exists(sql_file):
            print(f'警告: 找不到批次 {batch_num}')
            continue
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f'\n=== 批次 {batch_num}/{len(sql_files)} ===')
        print(f'文件: {os.path.basename(sql_file)}')
        print(f'大小: {len(sql_content):,} 字符')
        print('SQL 內容已準備好執行')
        print('---')
else:
    # 列出所有批次
    print(f'共有 {len(sql_files)} 個批次')
    print('使用方法:')
    print('  python batch_executor.py <start> [end]')
    print('  例如: python batch_executor.py 1 10  # 執行批次 1-10')
    print('  例如: python batch_executor.py 1     # 只執行批次 1')

