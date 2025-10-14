#!/usr/bin/env python3
"""
資料庫架構遷移 - 新增 LLM 分類追蹤欄位
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def migrate_database(db_path: str = "output/tags.db"):
    """執行資料庫遷移"""
    
    logger.info(f"開始遷移資料庫: {db_path}")
    
    if not Path(db_path).exists():
        logger.error(f"資料庫檔案不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 檢查欄位是否已存在
        cursor.execute("PRAGMA table_info(tags_final)")
        columns = [row[1] for row in cursor.fetchall()]
        
        new_columns = {
            'classification_source': 'TEXT',
            'classification_confidence': 'REAL',
            'classification_reasoning': 'TEXT',
            'classification_timestamp': 'TIMESTAMP'
        }
        
        added_columns = []
        
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                logger.info(f"新增欄位: {col_name} ({col_type})")
                cursor.execute(f"ALTER TABLE tags_final ADD COLUMN {col_name} {col_type}")
                added_columns.append(col_name)
            else:
                logger.info(f"欄位已存在，跳過: {col_name}")
        
        # 建立索引（如果需要）
        if 'classification_source' in added_columns:
            logger.info("建立索引: idx_classification_source")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_classification_source 
                ON tags_final(classification_source)
            """)
        
        if 'classification_confidence' in added_columns:
            logger.info("建立索引: idx_classification_confidence")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_classification_confidence 
                ON tags_final(classification_confidence)
            """)
        
        conn.commit()
        
        logger.info(f"✓ 遷移完成！新增 {len(added_columns)} 個欄位")
        
        # 驗證
        cursor.execute("PRAGMA table_info(tags_final)")
        all_columns = [row[1] for row in cursor.fetchall()]
        logger.info(f"tags_final 表目前有 {len(all_columns)} 個欄位")
        
        return True
        
    except Exception as e:
        logger.error(f"遷移失敗: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def verify_migration(db_path: str = "output/tags.db"):
    """驗證遷移結果"""
    
    logger.info(f"\n驗證遷移結果...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 檢查欄位
        cursor.execute("PRAGMA table_info(tags_final)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_columns = {
            'classification_source': 'TEXT',
            'classification_confidence': 'REAL',
            'classification_reasoning': 'TEXT',
            'classification_timestamp': 'TIMESTAMP'
        }
        
        all_ok = True
        for col_name, col_type in required_columns.items():
            if col_name in columns:
                logger.info(f"✓ {col_name} ({columns[col_name]})")
            else:
                logger.error(f"✗ {col_name} 欄位不存在")
                all_ok = False
        
        # 檢查索引
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='tags_final'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        logger.info(f"\n索引列表: {', '.join(indexes)}")
        
        if all_ok:
            logger.info("\n✓ 資料庫遷移驗證通過")
        else:
            logger.error("\n✗ 資料庫遷移驗證失敗")
        
        return all_ok
        
    finally:
        conn.close()


def main():
    """主函數"""
    print("="*80)
    print("資料庫架構遷移 - LLM 分類追蹤欄位")
    print("="*80)
    print()
    
    # 執行遷移
    success = migrate_database()
    
    if success:
        # 驗證遷移
        verify_migration()
    else:
        print("\n✗ 遷移失敗")
        return 1
    
    print("\n" + "="*80)
    print("遷移完成")
    print("="*80)
    return 0


if __name__ == "__main__":
    exit(main())

