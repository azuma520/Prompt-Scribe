"""
配置檔案：定義所有可配置的參數
"""

from pathlib import Path

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent

# 資料目錄
DATA_DIR = PROJECT_ROOT / 'data' / 'raw'
OUTPUT_DIR = PROJECT_ROOT / 'output'

# 確保目錄存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 資料庫路徑
DB_PATH = OUTPUT_DIR / 'tags.db'

# 日誌設定
LOG_LEVEL = 'INFO'
LOG_FILE = OUTPUT_DIR / 'pipeline.log'

