import os
import glob

# 找到所有 batch SQL 文件
sql_files = sorted(glob.glob('stage1/output/batch_*.sql'))
total_batches = len(sql_files)

print(f'找到 {total_batches} 個 SQL 批次文件')
print('正在逐批上傳到 Supabase...')
print('(這個腳本需要配合 MCP execute_sql 工具手動執行)')
print()

# 列出前 10 個批次作為示例
print('前 10 個批次文件:')
for i, file in enumerate(sql_files[:10], 1):
    file_size = os.path.getsize(file)
    print(f'  {i}. {os.path.basename(file)} ({file_size:,} bytes)')

print(f'\n... 還有 {total_batches - 10} 個批次')
print(f'\n建議: 由於批次數量過多 ({total_batches} 個)，')
print('建議使用以下更高效的方法之一:')
print()
print('方案 A: 使用 psycopg2 直接連接 (需要解決 DNS 問題)')
print('方案 B: 使用 Supabase CLI 的 db push 功能')
print('方案 C: 將 CSV 文件直接上傳到 Supabase Storage，然後使用 COPY 命令')
print('方案 D: 減少批次大小，合併成更大的批次 (例如每批 1000-5000 筆)')

