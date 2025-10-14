#!/usr/bin/env python3
"""
分類層級系統 - 數據庫遷移腳本 (Phase 1)
為 tags_final 表添加次要分類欄位
"""

import sqlite3
import os

def backup_database():
    """備份當前數據庫"""
    db_path = 'output/tags.db'
    backup_path = 'output/tags_backup_before_hierarchy.db'
    
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"[OK] 數據庫已備份到: {backup_path}")
    else:
        print(f"[INFO] 備份已存在: {backup_path}")

def check_existing_columns():
    """檢查是否已有新欄位"""
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    # 獲取表結構
    columns = cursor.execute("PRAGMA table_info(tags_final)").fetchall()
    column_names = [col[1] for col in columns]
    
    new_columns = [
        'secondary_category',
        'secondary_sub_category', 
        'secondary_confidence',
        'secondary_reasoning',
        'is_ambiguous',
        'classification_note'
    ]
    
    existing = [col for col in new_columns if col in column_names]
    missing = [col for col in new_columns if col not in column_names]
    
    conn.close()
    
    return existing, missing

def migrate_database():
    """執行數據庫遷移"""
    print("="*80)
    print("分類層級系統 - 數據庫遷移 (Phase 1)")
    print("="*80)
    
    # 1. 備份數據庫
    print("\n[1/4] 備份數據庫...")
    backup_database()
    
    # 2. 檢查現有欄位
    print("\n[2/4] 檢查現有欄位...")
    existing, missing = check_existing_columns()
    
    if existing:
        print(f"[INFO] 已存在的欄位: {', '.join(existing)}")
    
    if not missing:
        print("[OK] 所有新欄位已存在，無需遷移")
        return
    
    print(f"[INFO] 需要添加的欄位: {', '.join(missing)}")
    
    # 3. 添加新欄位
    print("\n[3/4] 添加新欄位...")
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    try:
        # 次要分類欄位
        if 'secondary_category' in missing:
            cursor.execute('ALTER TABLE tags_final ADD COLUMN secondary_category TEXT')
            print("  [+] secondary_category")
        
        if 'secondary_sub_category' in missing:
            cursor.execute('ALTER TABLE tags_final ADD COLUMN secondary_sub_category TEXT')
            print("  [+] secondary_sub_category")
        
        if 'secondary_confidence' in missing:
            cursor.execute('ALTER TABLE tags_final ADD COLUMN secondary_confidence REAL')
            print("  [+] secondary_confidence")
        
        if 'secondary_reasoning' in missing:
            cursor.execute('ALTER TABLE tags_final ADD COLUMN secondary_reasoning TEXT')
            print("  [+] secondary_reasoning")
        
        # 分類屬性欄位
        if 'is_ambiguous' in missing:
            cursor.execute('ALTER TABLE tags_final ADD COLUMN is_ambiguous BOOLEAN DEFAULT 0')
            print("  [+] is_ambiguous")
        
        if 'classification_note' in missing:
            cursor.execute('ALTER TABLE tags_final ADD COLUMN classification_note TEXT')
            print("  [+] classification_note")
        
        conn.commit()
        print("[OK] 所有新欄位已成功添加")
        
    except Exception as e:
        print(f"[ERROR] 遷移失敗: {e}")
        conn.rollback()
        conn.close()
        return False
    
    # 4. 驗證遷移
    print("\n[4/4] 驗證遷移...")
    columns = cursor.execute("PRAGMA table_info(tags_final)").fetchall()
    
    print("\n完整表結構:")
    for col in columns:
        col_id, name, type_, notnull, default, pk = col
        print(f"  {name:30} {type_:10} {'PRIMARY KEY' if pk else ''}")
    
    # 統計
    total_tags = cursor.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
    classified_tags = cursor.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
    
    print(f"\n數據庫統計:")
    print(f"  總標籤數: {total_tags:,}")
    print(f"  已分類標籤: {classified_tags:,}")
    print(f"  覆蓋率: {classified_tags/total_tags*100:.2f}%")
    
    conn.close()
    
    print("\n" + "="*80)
    print("遷移完成！")
    print("="*80)
    print("\n下一步:")
    print("  1. 識別模糊分類標籤 (Phase 2)")
    print("  2. 添加次要分類 (Phase 3)")
    print("  3. 實施 API 支持 (Phase 4)")
    
    return True

def rollback_migration():
    """回滾遷移（如果需要）"""
    backup_path = 'output/tags_backup_before_hierarchy.db'
    db_path = 'output/tags.db'
    
    if os.path.exists(backup_path):
        import shutil
        shutil.copy2(backup_path, db_path)
        print(f"[OK] 已從備份恢復: {db_path}")
    else:
        print(f"[ERROR] 備份文件不存在: {backup_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        print("執行回滾...")
        rollback_migration()
    else:
        migrate_database()

