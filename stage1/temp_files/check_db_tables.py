import sqlite3
from pathlib import Path

DB_PATH = Path('data/raw/danbooru_tags.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
print("資料庫表:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")
conn.close()

