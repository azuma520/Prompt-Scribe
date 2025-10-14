#!/usr/bin/env python3
"""
分塊上傳器
將大型 SQL 文件分塊讀取並上傳
"""

import os
import glob
import re

def get_tiny_batch_files():
    """獲取所有 tiny batch 文件"""
    output_dir = "stage1/output"
    if not os.path.exists(output_dir):
        print(f"X 找不到輸出目錄: {output_dir}")
        return []
    
    batch_files = glob.glob(os.path.join(output_dir, "tiny_batch_*.sql"))
    batch_files.sort()  # 按順序排列
    
    print(f"找到 {len(batch_files)} 個 tiny batch 文件")
    return batch_files

def split_sql_file(file_path, chunk_size=100):
    """將 SQL 文件分割成小塊"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按行分割
        lines = content.split('\n')
        chunks = []
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            
            # 確保 chunk 是完整的 SQL 語句
            if chunk_content.strip():
                chunks.append(chunk_content)
        
        return chunks
    
    except Exception as e:
        print(f"X 讀取文件失敗 {file_path}: {e}")
        return []

def create_chunked_files():
    """創建分塊文件"""
    batch_files = get_tiny_batch_files()
    if not batch_files:
        print("X 沒有找到任何 batch 文件")
        return []
    
    chunked_files = []
    
    for batch_file in batch_files:
        batch_name = os.path.basename(batch_file)
        print(f"處理 {batch_name}...")
        
        chunks = split_sql_file(batch_file, chunk_size=100)
        
        for i, chunk in enumerate(chunks):
            chunk_file = f"stage1/output/chunks/{batch_name.replace('.sql', '')}_chunk_{i:03d}.sql"
            
            # 確保 chunks 目錄存在
            os.makedirs(os.path.dirname(chunk_file), exist_ok=True)
            
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            
            chunked_files.append(chunk_file)
        
        print(f"  V 分割成 {len(chunks)} 個塊")
    
    return chunked_files

def main():
    """主函數"""
    print("分塊上傳器")
    print("=" * 50)
    
    # 創建分塊文件
    chunked_files = create_chunked_files()
    
    if chunked_files:
        print(f"\nV 創建了 {len(chunked_files)} 個分塊文件")
        print("現在可以使用 MCP 工具上傳這些分塊")
        
        # 顯示前幾個分塊的統計
        print(f"\n分塊統計：")
        for i, chunk_file in enumerate(chunked_files[:10]):  # 顯示前 10 個
            if os.path.exists(chunk_file):
                file_size = os.path.getsize(chunk_file)
                print(f"  {os.path.basename(chunk_file)}: {file_size:,} bytes")
        
        if len(chunked_files) > 10:
            print(f"  ... 還有 {len(chunked_files) - 10} 個分塊")
        
        print(f"\n下一步：")
        print("1. 使用 MCP execute_sql 工具上傳這些分塊")
        print("2. 每個分塊包含約 100 行 SQL")
        print(f"3. 總共需要上傳 {len(chunked_files)} 次")
    else:
        print("X 沒有創建任何分塊文件")

if __name__ == "__main__":
    main()
