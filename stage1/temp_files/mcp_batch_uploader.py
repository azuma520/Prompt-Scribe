"""
這個腳本需要配合 MCP execute_sql 工具使用
由於 Python 腳本無法直接調用 MCP 工具，
這個腳本會輸出每個批次的信息，
然後由外部程序（AI Agent）逐批執行
"""
import glob
import os

batch_dir = 'stage1/output/large_batches'
sql_files = sorted(glob.glob(f'{batch_dir}/batch_*.sql'))

print(f'=== 批次上傳計畫 ===')
print(f'總批次數: {len(sql_files)}')
print(f'批次大小: 每批約 5,000 筆記錄')
print(f'預計總記錄數: 140,782 筆')
print()

# 列出所有批次
for i, sql_file in enumerate(sql_files, 1):
    file_size = os.path.getsize(sql_file)
    print(f'{i:2d}. {os.path.basename(sql_file):20s} {file_size:>10,} bytes')

print()
print('準備開始上傳...')
print('請使用 MCP execute_sql 工具逐批執行')

