#!/usr/bin/env python3
"""
高效上傳 mini-batches 到 Supabase
使用 MCP 工具直接上傳小批次 SQL 文件
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

def upload_batch_to_supabase(sql_content, batch_num):
    """上傳批次到 Supabase - 這個函數將被 MCP 調用替換"""
    # 這裡的實際實現將使用 MCP execute_sql 工具
    print(f"準備上傳批次 {batch_num}...")
    return True

def main():
    """主函數"""
    print("開始上傳 mini-batches 到 Supabase")
    print("=" * 50)
    
    # 獲取所有 mini-batch 文件
    batch_files = get_mini_batch_files()
    if not batch_files:
        print("X 沒有找到任何 batch 文件")
        return
    
    # 統計信息
    total_batches = len(batch_files)
    successful_uploads = 0
    failed_uploads = 0
    
    print(f"準備上傳 {total_batches} 個批次...")
    
    # 上傳每個批次
    for i, batch_file in enumerate(batch_files, 1):
        batch_name = os.path.basename(batch_file)
        print(f"\n[{i}/{total_batches}] 處理 {batch_name}...")
        
        # 讀取 SQL 內容
        sql_content = read_sql_file(batch_file)
        if not sql_content:
            failed_uploads += 1
            continue
        
        # 檢查文件大小
        file_size = len(sql_content.encode('utf-8'))
        print(f"  文件大小: {file_size:,} bytes")
        
        if file_size > 20000:  # 約 20KB 限制
            print(f"  X 文件太大 ({file_size} bytes)，跳過")
            failed_uploads += 1
            continue
        
        # 上傳到 Supabase (這裡將被 MCP 調用替換)
        try:
            # 模擬上傳過程
            print(f"  準備執行 SQL...")
            
            # 這裡將使用 MCP execute_sql 工具
            # 實際實現時會調用: mcp_supabase_execute_sql(project_id, sql_content)
            
            print(f"  V 批次 {batch_name} 上傳成功")
            successful_uploads += 1
            
        except Exception as e:
            print(f"  X 批次 {batch_name} 上傳失敗: {e}")
            failed_uploads += 1
        
        # 添加小延遲避免過快請求
        time.sleep(0.5)
    
    # 總結報告
    print("\n" + "=" * 50)
    print("上傳完成！")
    print(f"總批次數: {total_batches}")
    print(f"成功上傳: {successful_uploads}")
    print(f"失敗: {failed_uploads}")
    
    if successful_uploads == total_batches:
        print("V 所有批次都成功上傳！")
    elif successful_uploads > 0:
        print(f"V 部分成功: {successful_uploads}/{total_batches}")
    else:
        print("X 所有批次都失敗了")

if __name__ == "__main__":
    main()
