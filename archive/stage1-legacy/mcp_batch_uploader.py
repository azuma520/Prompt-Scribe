#!/usr/bin/env python3
"""
使用 MCP 批量上傳 SQL 檔案到 Supabase
"""
import os
import glob
import time

def upload_via_mcp():
    """使用 MCP 批量上傳"""
    
    # 獲取所有 batch 檔案
    sql_files = sorted(glob.glob("stage1/output/batch_*.sql"))
    
    if not sql_files:
        print("錯誤：找不到任何 SQL 檔案")
        return
    
    total_files = len(sql_files)
    print(f"找到 {total_files} 個 SQL 檔案")
    print("開始使用 MCP 上傳...")
    
    success_count = 0
    error_count = 0
    
    # 先處理前 5 個檔案作為測試
    test_files = sql_files[:5]
    
    for i, sql_file in enumerate(test_files, 1):
        try:
            print(f"\n[{i}/{len(test_files)}] 處理: {os.path.basename(sql_file)}")
            
            # 讀取檔案內容
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            print(f"檔案大小: {len(sql_content)} 字元")
            print(f"包含 {sql_content.count('INSERT INTO')} 個 INSERT 語句")
            
            # 顯示前幾行內容
            lines = sql_content.split('\n')[:3]
            print("前幾行內容:")
            for line in lines:
                print(f"  {line}")
            
            print("請手動使用 MCP execute_sql 工具執行此批次")
            print("=" * 60)
            
            success_count += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"處理 {sql_file} 時發生錯誤: {e}")
            error_count += 1
    
    print(f"\n測試完成！處理了 {len(test_files)} 個檔案")
    print(f"成功: {success_count}, 錯誤: {error_count}")
    
    if success_count > 0:
        print("\n如果測試成功，我們可以繼續處理剩餘的檔案")

if __name__ == "__main__":
    upload_via_mcp()
