"""
Danbooru 標籤資料管線 - Phase 1 (純規則式分類)

主執行腳本，整合完整的資料處理流程：
1. 載入 CSV 檔案
2. 建立 tags_raw 資料表
3. 合併去重
4. 套用分類規則
5. 建立 tags_final 資料表
6. 驗證與報告
"""

import logging
import time
from pathlib import Path
import pandas as pd
import sqlite3
from typing import Tuple, List

# 匯入配置
from config import DATA_DIR, OUTPUT_DIR, DB_PATH, LOG_LEVEL, LOG_FILE


def setup_logging():
    """設定日誌系統"""
    # 確保輸出目錄存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 設定日誌格式
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 設定 handlers
    handlers = [
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
    
    # 設定基本配置
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


def load_csv_files(data_dir: Path) -> pd.DataFrame:
    """
    載入所有 CSV 檔案到 DataFrame
    
    Args:
        data_dir: 資料目錄路徑
    
    Returns:
        合併後的 DataFrame
    
    Raises:
        FileNotFoundError: 目錄不存在
    """
    logger = logging.getLogger(__name__)
    
    if not data_dir.exists():
        raise FileNotFoundError(f"資料目錄不存在: {data_dir}")
    
    csv_files = list(data_dir.glob('*.csv'))
    if not csv_files:
        logger.warning(f"目錄中沒有找到 CSV 檔案: {data_dir}")
        return pd.DataFrame()
    
    all_data = []
    for csv_file in csv_files:
        try:
            # 嘗試讀取檔案，檢查是否有標題
            # 先讀取前2行判斷
            sample = pd.read_csv(csv_file, encoding='utf-8', nrows=1)
            first_col = sample.columns[0]
            
            # 如果第一欄看起來像數據而非欄位名稱，則沒有標題
            has_header = True
            if first_col.replace('_', '').replace('-', '').isalnum():
                # 檢查第一欄是否為常見標籤名稱
                if first_col in ['1girl', '1boy', 'solo', 'highres', 'masterpiece']:
                    has_header = False
            
            # 重新讀取，使用正確的設定
            if has_header:
                df = pd.read_csv(csv_file, encoding='utf-8')
            else:
                # 沒有標題，手動指定欄位名稱
                df = pd.read_csv(csv_file, encoding='utf-8', header=None,
                               names=['name', 'danbooru_cat', 'post_count', 'aliases'])
                logger.info(f"  {csv_file.name}: 檢測到無標題，使用預設欄位名稱")
            
            df['source_file'] = csv_file.name
            all_data.append(df)
            logger.info(f"✓ 載入 {csv_file.name}: {len(df)} 筆記錄")
        except Exception as e:
            logger.error(f"✗ 無法載入 {csv_file.name}: {e}")
    
    if not all_data:
        return pd.DataFrame()
    
    combined_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"總計載入: {len(combined_df)} 筆記錄（來自 {len(csv_files)} 個檔案）")
    
    return combined_df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    標準化 DataFrame 欄位名稱
    
    Args:
        df: 原始 DataFrame
    
    Returns:
        標準化後的 DataFrame
    """
    logger = logging.getLogger(__name__)
    
    # 轉換為小寫以不區分大小寫
    df.columns = df.columns.str.lower().str.strip()
    
    # 欄位映射表
    column_map = {
        'category': 'danbooru_cat',
        'count': 'post_count',
        'tag': 'name',
        'tag_name': 'name'
    }
    
    # 套用映射
    df.rename(columns=column_map, inplace=True)
    
    # 補充缺失欄位（使用預設值）
    if 'post_count' not in df.columns:
        df['post_count'] = 0
        logger.info("補充缺失欄位: post_count")
    
    if 'danbooru_cat' not in df.columns:
        df['danbooru_cat'] = 0  # 預設為一般標籤
        logger.info("補充缺失欄位: danbooru_cat")
    
    # 只保留我們需要的欄位
    required_cols = ['name', 'danbooru_cat', 'post_count', 'source_file']
    df = df[[col for col in required_cols if col in df.columns]].copy()
    
    # 確保數據類型正確
    df['post_count'] = pd.to_numeric(df['post_count'], errors='coerce').fillna(0).astype(int)
    df['danbooru_cat'] = pd.to_numeric(df['danbooru_cat'], errors='coerce').fillna(0).astype(int)
    
    logger.info(f"欄位標準化完成: {list(df.columns)}")
    
    return df


def validate_records(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    驗證 DataFrame 中的記錄
    
    Args:
        df: 待驗證的 DataFrame
    
    Returns:
        (有效的 DataFrame, 驗證統計字典)
    """
    logger = logging.getLogger(__name__)
    
    original_count = len(df)
    
    # 驗證 name
    mask_name = (df['name'].notna()) & (df['name'].str.strip() != '')
    mask_name &= (df['name'].str.len() >= 1) & (df['name'].str.len() <= 200)
    
    # 驗證 danbooru_cat
    mask_cat = df['danbooru_cat'].isin([0, 1, 3, 4, 5])
    
    # 驗證 post_count
    mask_count = df['post_count'] >= 0
    
    # 合併所有驗證
    valid_mask = mask_name & mask_cat & mask_count
    
    # 記錄無效記錄
    invalid_df = df[~valid_mask]
    if len(invalid_df) > 0:
        logger.warning(f"發現 {len(invalid_df)} 筆無效記錄")
        for idx, row in invalid_df.head(10).iterrows():
            logger.debug(f"  無效記錄: {row.to_dict()}")
    
    valid_df = df[valid_mask].copy()
    
    stats = {
        'original_count': original_count,
        'valid_count': len(valid_df),
        'invalid_count': original_count - len(valid_df)
    }
    
    logger.info(f"驗證完成: {stats['valid_count']}/{stats['original_count']} 筆有效")
    
    return valid_df, stats


def create_tags_raw_table(df: pd.DataFrame, db_path: Path) -> int:
    """
    建立 tags_raw 資料表並插入資料
    
    Args:
        df: 驗證後的 DataFrame
        db_path: 資料庫檔案路徑
    
    Returns:
        插入的記錄數
    """
    logger = logging.getLogger(__name__)
    
    # 確保輸出目錄存在
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 連接資料庫
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 建立表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags_raw (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT NOT NULL,
            name TEXT NOT NULL,
            danbooru_cat INTEGER,
            post_count INTEGER DEFAULT 0,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 插入資料
    df_to_insert = df[['source_file', 'name', 'danbooru_cat', 'post_count']].copy()
    df_to_insert.to_sql('tags_raw', conn, if_exists='append', index=False)
    
    # 建立索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_raw_name ON tags_raw(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_raw_cat ON tags_raw(danbooru_cat)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_raw_source ON tags_raw(source_file)")
    
    conn.commit()
    
    # 驗證插入
    count = cursor.execute("SELECT COUNT(*) FROM tags_raw").fetchone()[0]
    logger.info(f"✓ tags_raw 表建立完成: {count} 筆記錄")
    
    conn.close()
    
    return count


def merge_and_deduplicate(db_path: Path) -> pd.DataFrame:
    """
    合併去重處理
    
    Args:
        db_path: 資料庫檔案路徑
    
    Returns:
        去重後的 DataFrame
    """
    logger = logging.getLogger(__name__)
    
    conn = sqlite3.connect(db_path)
    
    # 使用 SQL 進行聚合
    query = """
    SELECT 
        name,
        danbooru_cat,
        SUM(post_count) as post_count,
        COUNT(DISTINCT source_file) as source_count
    FROM tags_raw
    GROUP BY name, danbooru_cat
    ORDER BY post_count DESC
    """
    
    df_merged = pd.read_sql_query(query, conn)
    
    # 處理同一個 name 有多個 danbooru_cat 的情況
    # 選擇 post_count 最高的那個
    df_merged = df_merged.sort_values('post_count', ascending=False)
    df_merged = df_merged.drop_duplicates(subset=['name'], keep='first')
    
    conn.close()
    
    logger.info(f"合併去重完成: {len(df_merged)} 個唯一標籤")
    
    return df_merged


def apply_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    套用分類規則至 DataFrame
    
    Args:
        df: 合併去重後的 DataFrame
    
    Returns:
        添加分類欄位的 DataFrame
    """
    from data_rules import classify_tag
    
    logger = logging.getLogger(__name__)
    
    # 初始化分類欄位
    df['main_category'] = None
    df['sub_category'] = None
    
    # 只對一般標籤（danbooru_cat=0）進行分類
    mask = df['danbooru_cat'] == 0
    general_tags = df[mask]
    
    logger.info(f"開始分類 {len(general_tags)} 個一般標籤...")
    
    # 套用分類函式
    classifications = general_tags['name'].apply(classify_tag)
    
    # 拆分主分類和副分類
    df.loc[mask, 'main_category'] = [c[0] for c in classifications]
    df.loc[mask, 'sub_category'] = [c[1] for c in classifications]
    
    # 統計覆蓋率
    classified_count = df[mask & df['main_category'].notna()].shape[0]
    total_general = len(general_tags)
    coverage = classified_count / total_general if total_general > 0 else 0
    
    logger.info(f"分類完成:")
    logger.info(f"  已分類: {classified_count}/{total_general} ({coverage:.1%})")
    logger.info(f"  未分類: {total_general - classified_count}")
    
    # 統計副分類覆蓋率
    sub_cat_count = df[mask & df['sub_category'].notna()].shape[0]
    logger.info(f"  副分類: {sub_cat_count} 個標籤有副分類")
    
    return df


def create_tags_final_table(df: pd.DataFrame, db_path: Path) -> int:
    """
    建立 tags_final 資料表並插入資料
    
    Args:
        df: 分類後的 DataFrame
        db_path: 資料庫檔案路徑
    
    Returns:
        插入的記錄數
    """
    logger = logging.getLogger(__name__)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 建立表（如果存在則刪除舊表）
    cursor.execute("DROP TABLE IF EXISTS tags_final")
    cursor.execute("""
        CREATE TABLE tags_final (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            danbooru_cat INTEGER NOT NULL,
            
            -- 階層式分類欄位
            main_category TEXT,
            sub_category TEXT,
            
            -- 統計欄位
            post_count INTEGER DEFAULT 0,
            source_count INTEGER DEFAULT 1,
            
            -- 時間戳記
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- 約束
            CHECK (danbooru_cat BETWEEN 0 AND 5),
            CHECK (post_count >= 0),
            CHECK (source_count >= 1)
        )
    """)
    
    # 插入資料
    df_to_insert = df[[
        'name', 'danbooru_cat', 'main_category', 'sub_category',
        'post_count', 'source_count'
    ]].copy()
    
    df_to_insert.to_sql('tags_final', conn, if_exists='append', index=False)
    
    # 建立索引
    logger.info("建立索引...")
    cursor.execute("CREATE UNIQUE INDEX idx_tags_final_name ON tags_final(name)")
    cursor.execute("CREATE INDEX idx_tags_final_danbooru_cat ON tags_final(danbooru_cat)")
    cursor.execute("CREATE INDEX idx_tags_final_main_cat ON tags_final(main_category)")
    cursor.execute("CREATE INDEX idx_tags_final_sub_cat ON tags_final(sub_category)")
    cursor.execute("CREATE INDEX idx_tags_final_main_sub ON tags_final(main_category, sub_category)")
    cursor.execute("CREATE INDEX idx_tags_final_post_count ON tags_final(post_count DESC)")
    
    conn.commit()
    
    # 驗證插入
    count = cursor.execute("SELECT COUNT(*) FROM tags_final").fetchone()[0]
    logger.info(f"✓ tags_final 表建立完成: {count} 筆記錄")
    
    conn.close()
    
    return count


def generate_classification_report(df: pd.DataFrame, output_path: Path):
    """
    產生分類統計報告
    
    Args:
        df: 分類後的 DataFrame
        output_path: 報告輸出路徑
    """
    logger = logging.getLogger(__name__)
    
    # 確保輸出目錄存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Danbooru 標籤分類統計報告\n")
        f.write("=" * 80 + "\n\n")
        
        # 總體統計
        total = len(df)
        general_tags = df[df['danbooru_cat'] == 0]
        total_general = len(general_tags)
        
        f.write("## 總體統計\n")
        f.write(f"  總標籤數: {total}\n")
        f.write(f"  一般標籤數 (danbooru_cat=0): {total_general}\n")
        f.write(f"  其他類別標籤數: {total - total_general}\n\n")
        
        # 主分類分佈
        f.write("## 主分類分佈\n")
        main_cat_dist = general_tags['main_category'].value_counts()
        for cat, count in main_cat_dist.items():
            pct = count / total_general * 100
            f.write(f"  {cat}: {count} ({pct:.1f}%)\n")
        
        # 未分類標籤
        unclassified = general_tags[general_tags['main_category'].isna()]
        unclassified_count = len(unclassified)
        f.write(f"  未分類: {unclassified_count} ({unclassified_count/total_general*100:.1f}%)\n\n")
        
        # 覆蓋率
        classified_count = total_general - unclassified_count
        coverage = classified_count / total_general if total_general > 0 else 0
        f.write(f"## 主分類覆蓋率: {coverage:.1%}\n\n")
        
        # 副分類分佈
        f.write("## 副分類分佈\n")
        sub_cat_dist = general_tags[general_tags['sub_category'].notna()]['sub_category'].value_counts()
        for cat, count in sub_cat_dist.items():
            f.write(f"  {cat}: {count}\n")
        f.write("\n")
        
        # TOP 未分類標籤
        f.write("## TOP 20 未分類標籤（按使用次數排序）\n")
        top_unclassified = unclassified.nlargest(20, 'post_count')[['name', 'post_count']]
        for idx, row in top_unclassified.iterrows():
            f.write(f"  {row['name']}: {row['post_count']} 次\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("報告結束\n")
    
    logger.info(f"✓ 分類報告已生成: {output_path}")


def main():
    """主執行流程"""
    # 設定日誌
    logger = setup_logging()
    
    start_time = time.time()
    
    logger.info("=" * 80)
    logger.info("Danbooru 標籤資料管線 - Phase 1 (純規則式分類)")
    logger.info("=" * 80)
    
    try:
        # 步驟 1: 載入資料
        logger.info("\n[1/7] 載入 CSV 檔案...")
        df = load_csv_files(DATA_DIR)
        
        if df.empty:
            logger.error("沒有載入任何資料，終止執行")
            return
        
        # 步驟 2: 標準化欄位
        logger.info("\n[2/7] 標準化欄位...")
        df = standardize_columns(df)
        
        # 步驟 3: 驗證資料
        logger.info("\n[3/7] 驗證資料...")
        df, stats = validate_records(df)
        
        # 步驟 4: 建立 tags_raw
        logger.info("\n[4/7] 建立 tags_raw 表...")
        create_tags_raw_table(df, DB_PATH)
        
        # 步驟 5: 合併去重
        logger.info("\n[5/7] 合併去重...")
        df_merged = merge_and_deduplicate(DB_PATH)
        
        # 步驟 6: 套用分類
        logger.info("\n[6/7] 套用分類規則...")
        df_classified = apply_classification(df_merged)
        
        # 步驟 7: 建立 tags_final
        logger.info("\n[7/7] 建立 tags_final 表...")
        create_tags_final_table(df_classified, DB_PATH)
        
        # 產生報告
        logger.info("\n產生分類報告...")
        report_path = OUTPUT_DIR / 'classification_report.txt'
        generate_classification_report(df_classified, report_path)
        
        # 完成
        elapsed = time.time() - start_time
        logger.info("\n" + "=" * 80)
        logger.info(f"✓ 管線執行完成！耗時: {elapsed:.1f} 秒")
        logger.info(f"✓ 資料庫已產出: {DB_PATH}")
        logger.info(f"✓ 分類報告已產出: {OUTPUT_DIR / 'classification_report.txt'}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.exception(f"管線執行失敗: {e}")
        raise


if __name__ == '__main__':
    main()

