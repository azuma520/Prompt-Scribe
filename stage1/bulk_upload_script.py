#!/usr/bin/env python3
"""
批量上傳 SQL 檔案到 Supabase
"""
import os
import glob
import time
import subprocess

def execute_sql_file(file_path):
    """執行單個 SQL 檔案"""
    try:
        # 使用 npx supabase db execute 執行 SQL 檔案
        cmd = ["npx", "supabase", "db", "execute", "--file", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print(f"✓ 成功執行: {os.path.basename(file_path)}")
            return True
        else:
            print(f"✗ 執行失敗: {os.path.basename(file_path)}")
            print(f"錯誤: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ 異常錯誤: {os.path.basename(file_path)} - {e}")
        return False

def bulk_upload():
    """批量上傳所有 SQL 檔案"""
    
    # 獲取所有 batch 檔案
    sql_files = sorted(glob.glob("stage1/output/batch_*.sql"))
    
    if not sql_files:
        print("錯誤：找不到任何 SQL 檔案")
        return
    
    total_files = len(sql_files)
    print(f"找到 {total_files} 個 SQL 檔案，開始批量上傳...")
    
    success_count = 0
    error_count = 0
    
    for i, sql_file in enumerate(sql_files, 1):
        print(f"\n[{i}/{total_files}] 處理: {os.path.basename(sql_file)}")
        
        if execute_sql_file(sql_file):
            success_count += 1
        else:
            error_count += 1
        
        # 每 10 個檔案暫停一下
        if i % 10 == 0:
            print(f"進度: {i}/{total_files}, 成功: {success_count}, 失敗: {error_count}")
            time.sleep(1)
    
    print(f"\n批量上傳完成！")
    print(f"總計: {total_files} 個檔案")
    print(f"成功: {success_count} 個")
    print(f"失敗: {error_count} 個")

if __name__ == "__main__":
    bulk_upload()










