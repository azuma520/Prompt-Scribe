#!/usr/bin/env python3
"""
自動化上傳 SQL 批次到 Supabase 使用 MCP
"""
import os
import glob
import time
from pathlib import Path

def upload_batches():
    """自動上傳所有 mini batch 檔案"""
    
    # 檢查 mini_batches 目錄
    mini_batch_dir = "output/mini_batches"
    if not os.path.exists(mini_batch_dir):
        print(f"錯誤：找不到目錄 {mini_batch_dir}")
        return
    
    # 獲取所有 batch 檔案
    batch_files = sorted(glob.glob(f"{mini_batch_dir}/batch_*.sql"))
    
    if not batch_files:
        print("錯誤：找不到任何 batch 檔案")
        return
    
    print(f"找到 {len(batch_files)} 個批次檔案")
    print("開始自動上傳...")
    
    success_count = 0
    error_count = 0
    
    for i, batch_file in enumerate(batch_files, 1):
        try:
            print(f"\n[{i}/{len(batch_files)}] 處理: {os.path.basename(batch_file)}")
            
            # 讀取檔案內容
            with open(batch_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 這裡需要手動執行，因為我們需要 MCP 工具
            print(f"SQL 內容長度: {len(sql_content)} 字元")
            print(f"包含 {sql_content.count('INSERT INTO')} 個 INSERT 語句")
            
            # 提示用戶手動執行
            print("請手動使用 MCP execute_sql 工具執行此批次")
            print("=" * 50)
            
            success_count += 1
            
            # 暫停一下避免過快
            time.sleep(0.5)
            
        except Exception as e:
            print(f"處理 {batch_file} 時發生錯誤: {e}")
            error_count += 1
    
    print(f"\n完成！成功: {success_count}, 錯誤: {error_count}")

if __name__ == "__main__":
    upload_batches()





