"""
自動執行所有批次上傳
這個腳本會讀取所有批次 SQL 文件並輸出執行計劃
"""
import glob
import os

batch_dir = 'stage1/output/mini_batches'
sql_files = sorted(glob.glob(f'{batch_dir}/batch_*.sql'))

print(f'=== 批次上傳執行計劃 ===')
print(f'總批次數: {len(sql_files)}')
print(f'每批記錄數: ~500 筆')
print(f'預計總記錄數: 140,782 筆')
print()

# 由於 Python 腳本無法直接調用 MCP 工具，
# 我們需要在外部（AI Agent）逐批執行
# 這個腳本會輸出所有批次的路徑

print('所有批次文件列表:')
for i, sql_file in enumerate(sql_files, 1):
    file_size = os.path.getsize(sql_file)
    rel_path = os.path.relpath(sql_file)
    print(f'{i:3d}. {rel_path} ({file_size:,} bytes)')
    
print()
print('建議執行策略:')
print('1. 先執行前 10 個批次測試')
print('2. 驗證數據是否正確插入')
print('3. 然後批量執行剩餘批次')
print()
print('或者使用 Supabase 的 COPY FROM 功能直接導入 CSV')

