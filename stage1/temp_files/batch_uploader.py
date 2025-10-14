#!/usr/bin/env python3
"""
高效批次上傳器
使用 MCP Supabase 工具批量上傳數據
"""

import os
import glob
import time
from pathlib import Path

def get_mini_batch_files():
    """獲取所有 mini-batch 文件"""
    mini_batch_dir = "stage1/output/mini_batches"
    if not os.path.exists(mini_batch_dir):
        print(f"X 找不到 mini-batch 目錄: {mini_batch_dir}")
        return []
    
    batch_files = glob.glob(os.path.join(mini_batch_dir, "batch_*.sql"))
    batch_files.sort()  # 按順序排列
    
    print(f"找到 {len(batch_files)} 個 mini-batch 文件")
    return batch_files

def read_sql_file(file_path):
    """讀取 SQL 文件內容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"X 讀取文件失敗 {file_path}: {e}")
        return None

def create_combined_batch(start_batch, end_batch, batch_files):
    """創建合併批次文件"""
    combined_sql = ""
    batch_count = 0
    
    for i in range(start_batch - 1, min(end_batch, len(batch_files))):
        batch_file = batch_files[i]
        batch_name = os.path.basename(batch_file)
        
        sql_content = read_sql_file(batch_file)
        if sql_content:
            combined_sql += sql_content + "\n"
            batch_count += 1
    
    if combined_sql:
        combined_file = f"stage1/output/combined_batch_{start_batch:04d}_{end_batch:04d}.sql"
        with open(combined_file, 'w', encoding='utf-8') as f:
            f.write(combined_sql)
        
        file_size = len(combined_sql.encode('utf-8'))
        print(f"V 創建合併批次: {combined_file}")
        print(f"  包含 {batch_count} 個原始批次")
        print(f"  文件大小: {file_size:,} bytes")
        
        return combined_file
    
    return None

def main():
    """主函數"""
    print("高效批次上傳器")
    print("=" * 50)
    
    # 獲取所有 mini-batch 文件
    batch_files = get_mini_batch_files()
    if not batch_files:
        print("X 沒有找到任何 batch 文件")
        return
    
    total_batches = len(batch_files)
    print(f"總共有 {total_batches} 個 mini-batch 文件")
    
    # 創建合併批次（每 10 個批次合併為一個）
    batch_size = 10
    combined_files = []
    
    for start in range(1, total_batches + 1, batch_size):
        end = min(start + batch_size - 1, total_batches)
        combined_file = create_combined_batch(start, end, batch_files)
        if combined_file:
            combined_files.append(combined_file)
    
    print(f"\nV 創建了 {len(combined_files)} 個合併批次文件")
    print("現在可以使用 MCP 工具上傳這些合併批次")
    
    # 顯示合併批次統計
    print(f"\n合併批次統計：")
    for i, combined_file in enumerate(combined_files[:5]):  # 只顯示前 5 個
        if os.path.exists(combined_file):
            file_size = os.path.getsize(combined_file)
            print(f"  {os.path.basename(combined_file)}: {file_size:,} bytes")
    
    if len(combined_files) > 5:
        print(f"  ... 還有 {len(combined_files) - 5} 個合併批次")
    
    print(f"\n下一步：")
    print("1. 使用 MCP execute_sql 工具上傳這些合併批次")
    print("2. 每個合併批次包含 10 個原始批次")
    print("3. 總共需要上傳 {len(combined_files)} 次")

if __name__ == "__main__":
    main()
